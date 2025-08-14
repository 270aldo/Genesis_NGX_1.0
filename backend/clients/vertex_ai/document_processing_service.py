"""
Document Processing Service for Vertex AI Client.

This module handles document and multimodal processing functionality,
providing services for document analysis and multimodal content processing.
"""

import asyncio
import base64
from typing import Any, Dict, List, Optional, Union

from core.logging_config import get_logger
from infrastructure.adapters.telemetry_adapter import (
    get_telemetry_adapter,
    measure_execution_time,
)

from .cache import CacheManager
from .connection import ConnectionPool
from .decorators import with_retries

logger = get_logger(__name__)
telemetry_adapter = get_telemetry_adapter()

try:
    from google.cloud import documentai_v1 as documentai
    from vertexai.generative_models import GenerationConfig, GenerativeModel, Part

    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

    class GenerativeModel:
        pass

    class Part:
        pass

    class GenerationConfig:
        pass

    class documentai:
        class DocumentProcessorServiceClient:
            pass

        class RawDocument:
            pass

        class ProcessRequest:
            pass


class DocumentProcessingService:
    """
    Service responsible for document and multimodal processing.

    This service handles:
    - Document analysis and OCR
    - Multimodal content processing (images, text, etc.)
    - Content extraction and structured output
    - Error handling and retries
    """

    def __init__(
        self,
        model_name: str,
        cache_manager: CacheManager = None,
        connection_pool: ConnectionPool = None,
        document_processor_id: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the document processing service."""
        self.model_name = model_name
        self.cache_manager = cache_manager
        self.connection_pool = connection_pool
        self.document_processor_id = document_processor_id
        self.model = None
        self.document_client = None
        self.stats = {
            "multimodal_requests": 0,
            "document_requests": 0,
            "successful_processes": 0,
            "failed_processes": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "latency_ms": [],
        }

    async def initialize(self) -> bool:
        """Initialize the document processing services."""
        try:
            if not VERTEX_AI_AVAILABLE:
                logger.warning("Vertex AI not available - using mock mode")
                return False

            # Initialize multimodal model
            self.model = GenerativeModel(model_name=self.model_name)

            # Initialize document processing client if processor ID is provided
            if self.document_processor_id:
                self.document_client = documentai.DocumentProcessorServiceClient()

            logger.info(
                f"Document processing service initialized with model: {self.model_name}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize document processing service: {e}")
            return False

    def _get_cache_key(
        self,
        content_type: str,
        content_hash: str,
        prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Generate cache key for processing request."""
        import hashlib

        cache_content = (
            f"{content_type}|{content_hash}|{prompt or ''}|{self.model_name}"
        )
        cache_hash = hashlib.md5(cache_content.encode()).hexdigest()
        return f"doc_process:{self.model_name}:{cache_hash}"

    def _create_image_part(
        self, image_data: Union[str, bytes], mime_type: str = "image/jpeg"
    ) -> Part:
        """Create image part for multimodal processing."""
        if isinstance(image_data, str):
            # Assume base64 encoded
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data

        return Part.from_data(image_bytes, mime_type=mime_type)

    def _extract_content_hash(self, content: Union[str, bytes, Dict[str, Any]]) -> str:
        """Extract hash from content for caching."""
        import hashlib

        if isinstance(content, dict):
            content_str = str(content)
        elif isinstance(content, bytes):
            content_str = base64.b64encode(content).decode()
        else:
            content_str = str(content)

        return hashlib.md5(content_str.encode()).hexdigest()[:16]

    @measure_execution_time("vertex_ai.document_processing.process_multimodal")
    @with_retries(max_retries=3, base_delay=1.0, backoff_factor=2)
    async def process_multimodal(
        self,
        content_parts: List[Dict[str, Any]],
        prompt: str = "Analyze this content and describe what you see.",
        temperature: float = 0.7,
        max_output_tokens: Optional[int] = None,
        skip_cache: bool = False,
    ) -> Dict[str, Any]:
        """
        Process multimodal content (text, images, etc.).

        Args:
            content_parts: List of content parts (text, images, etc.)
            prompt: Analysis prompt
            temperature: Temperature for generation
            max_output_tokens: Maximum output tokens limit
            skip_cache: If True, skip cache and always call API

        Returns:
            Dict[str, Any]: Analysis results and metadata
        """
        if not self.model:
            raise RuntimeError("Document processing service not initialized")

        self.stats["multimodal_requests"] += 1

        # Generate cache key
        content_hash = self._extract_content_hash(content_parts)
        cache_key = self._get_cache_key("multimodal", content_hash, prompt)

        # Try cache first (unless skipped)
        if not skip_cache and self.cache_manager:
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self.stats["cache_hits"] += 1
                return cached_result

        self.stats["cache_misses"] += 1

        span_attributes = {
            "service.content_parts_count": len(content_parts),
            "service.prompt_length": len(prompt),
            "service.temperature": temperature,
            "service.model_name": self.model_name,
        }

        span = telemetry_adapter.start_span(
            "DocumentProcessingService.process_multimodal", attributes=span_attributes
        )

        try:
            start_time = asyncio.get_event_loop().time()

            if VERTEX_AI_AVAILABLE:
                # Prepare content parts for Vertex AI
                parts = [prompt]

                for part in content_parts:
                    if part.get("type") == "text":
                        parts.append(part["content"])
                    elif part.get("type") == "image":
                        image_part = self._create_image_part(
                            part["content"], part.get("mime_type", "image/jpeg")
                        )
                        parts.append(image_part)
                    elif part.get("type") == "image_base64":
                        # Handle base64 encoded images
                        image_data = part["content"]
                        if "," in image_data:  # Remove data URL prefix if present
                            image_data = image_data.split(",", 1)[1]
                        image_part = self._create_image_part(
                            image_data, part.get("mime_type", "image/jpeg")
                        )
                        parts.append(image_part)

                # Create generation config
                generation_config = GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                )

                # Make API call
                response = await self.model.generate_content_async(
                    contents=parts, generation_config=generation_config
                )

                result = {
                    "analysis": (
                        response.text if hasattr(response, "text") else str(response)
                    ),
                    "content_parts_processed": len(content_parts),
                    "model_name": self.model_name,
                    "usage": {
                        "prompt_tokens": getattr(response, "usage_metadata", {}).get(
                            "prompt_token_count", 0
                        ),
                        "completion_tokens": getattr(
                            response, "usage_metadata", {}
                        ).get("candidates_token_count", 0),
                    },
                    "timestamp": start_time,
                }

            else:
                # Mock multimodal processing
                await asyncio.sleep(0.2)  # Simulate processing delay

                content_types = [part.get("type", "unknown") for part in content_parts]
                result = {
                    "analysis": f"Mock analysis of multimodal content: {content_types}. Prompt: {prompt[:50]}...",
                    "content_parts_processed": len(content_parts),
                    "model_name": self.model_name,
                    "usage": {
                        "prompt_tokens": len(prompt.split()),
                        "completion_tokens": 20,
                    },
                    "timestamp": start_time,
                }

            # Record latency
            latency = int((asyncio.get_event_loop().time() - start_time) * 1000)
            self.stats["latency_ms"].append(latency)
            self.stats["successful_processes"] += 1

            # Cache the result
            if not skip_cache and self.cache_manager:
                await self.cache_manager.set(cache_key, result)

            telemetry_adapter.record_counter(
                "vertex_ai_requests",
                1,
                {"model": self.model_name, "type": "multimodal_processing"},
            )

            span.set_attribute("service.success", True)
            span.set_attribute("service.analysis_length", len(result["analysis"]))

            return result

        except Exception as e:
            self.stats["failed_processes"] += 1
            logger.error(f"Error in multimodal processing: {e}")

            telemetry_adapter.record_counter(
                "vertex_ai_errors",
                1,
                {
                    "model": self.model_name,
                    "type": "multimodal_processing",
                    "error": str(type(e).__name__),
                },
            )

            span.set_attribute("service.success", False)
            span.set_attribute("service.error", str(e))

            raise

        finally:
            span.end()

    @measure_execution_time("vertex_ai.document_processing.process_document")
    @with_retries(max_retries=3, base_delay=1.0, backoff_factor=2)
    async def process_document(
        self,
        document_content: bytes,
        mime_type: str = "application/pdf",
        skip_cache: bool = False,
    ) -> Dict[str, Any]:
        """
        Process document using Document AI.

        Args:
            document_content: Document content as bytes
            mime_type: MIME type of the document
            skip_cache: If True, skip cache and always call API

        Returns:
            Dict[str, Any]: Document processing results
        """
        if not self.document_client or not self.document_processor_id:
            raise RuntimeError("Document AI client not initialized")

        self.stats["document_requests"] += 1

        # Generate cache key
        content_hash = self._extract_content_hash(document_content)
        cache_key = self._get_cache_key("document", content_hash, mime_type=mime_type)

        # Try cache first (unless skipped)
        if not skip_cache and self.cache_manager:
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self.stats["cache_hits"] += 1
                return cached_result

        self.stats["cache_misses"] += 1

        span_attributes = {
            "service.document_size_bytes": len(document_content),
            "service.mime_type": mime_type,
            "service.processor_id": self.document_processor_id,
        }

        span = telemetry_adapter.start_span(
            "DocumentProcessingService.process_document", attributes=span_attributes
        )

        try:
            start_time = asyncio.get_event_loop().time()

            if VERTEX_AI_AVAILABLE:
                # Create raw document
                raw_document = documentai.RawDocument(
                    content=document_content, mime_type=mime_type
                )

                # Create process request
                request = documentai.ProcessRequest(
                    name=self.document_processor_id, raw_document=raw_document
                )

                # Process document
                result = await self.document_client.process_document(request=request)

                # Extract text and structured data
                document = result.document
                extracted_text = document.text

                # Extract key-value pairs
                form_fields = []
                if hasattr(document, "pages"):
                    for page in document.pages:
                        if hasattr(page, "form_fields"):
                            for field in page.form_fields:
                                field_data = {
                                    "field_name": getattr(field, "field_name", {})
                                    .get("text_anchor", {})
                                    .get("content", ""),
                                    "field_value": getattr(field, "field_value", {})
                                    .get("text_anchor", {})
                                    .get("content", ""),
                                }
                                form_fields.append(field_data)

                response = {
                    "extracted_text": extracted_text,
                    "form_fields": form_fields,
                    "page_count": (
                        len(document.pages) if hasattr(document, "pages") else 0
                    ),
                    "mime_type": mime_type,
                    "processor_id": self.document_processor_id,
                    "timestamp": start_time,
                }

            else:
                # Mock document processing
                await asyncio.sleep(0.3)  # Simulate processing delay

                response = {
                    "extracted_text": f"Mock extracted text from {mime_type} document ({len(document_content)} bytes)",
                    "form_fields": [
                        {"field_name": "Name", "field_value": "Mock Name"},
                        {"field_name": "Date", "field_value": "2025-01-01"},
                    ],
                    "page_count": 1,
                    "mime_type": mime_type,
                    "processor_id": self.document_processor_id,
                    "timestamp": start_time,
                }

            # Record latency
            latency = int((asyncio.get_event_loop().time() - start_time) * 1000)
            self.stats["latency_ms"].append(latency)
            self.stats["successful_processes"] += 1

            # Cache the result
            if not skip_cache and self.cache_manager:
                await self.cache_manager.set(cache_key, response)

            telemetry_adapter.record_counter(
                "vertex_ai_requests",
                1,
                {"type": "document_processing", "mime_type": mime_type},
            )

            span.set_attribute("service.success", True)
            span.set_attribute(
                "service.extracted_text_length", len(response["extracted_text"])
            )

            return response

        except Exception as e:
            self.stats["failed_processes"] += 1
            logger.error(f"Error processing document: {e}")

            telemetry_adapter.record_counter(
                "vertex_ai_errors",
                1,
                {"type": "document_processing", "error": str(type(e).__name__)},
            )

            span.set_attribute("service.success", False)
            span.set_attribute("service.error", str(e))

            raise

        finally:
            span.end()

    async def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        avg_latency = (
            sum(self.stats["latency_ms"]) / len(self.stats["latency_ms"])
            if self.stats["latency_ms"]
            else 0
        )
        success_rate = (
            (
                self.stats["successful_processes"]
                / (self.stats["multimodal_requests"] + self.stats["document_requests"])
            )
            * 100
            if (self.stats["multimodal_requests"] + self.stats["document_requests"]) > 0
            else 0
        )

        return {
            "service": "document_processing",
            "model_name": self.model_name,
            "stats": {
                **self.stats,
                "avg_latency_ms": avg_latency,
                "success_rate_percent": success_rate,
                "total_requests": self.stats["multimodal_requests"]
                + self.stats["document_requests"],
            },
            "cache_stats": (
                await self.cache_manager.get_stats() if self.cache_manager else {}
            ),
        }
