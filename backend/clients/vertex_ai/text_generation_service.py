"""
Text Generation Service for Vertex AI Client.

This module handles all text generation functionality,
providing a focused service for content generation with caching and telemetry.
"""

import asyncio
from typing import Any, AsyncGenerator, Dict, Optional

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
    from vertexai.generative_models import GenerationConfig, GenerativeModel

    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

    class GenerativeModel:
        pass

    class GenerationConfig:
        pass


class TextGenerationService:
    """
    Service responsible for text generation using Vertex AI models.

    This service handles:
    - Content generation with various parameters
    - Streaming content generation
    - Caching and performance optimization
    - Error handling and retries
    """

    def __init__(
        self,
        model_name: str,
        cache_manager: CacheManager,
        connection_pool: ConnectionPool,
        **kwargs,
    ):
        """Initialize the text generation service."""
        self.model_name = model_name
        self.cache_manager = cache_manager
        self.connection_pool = connection_pool
        self.model = None
        self.stats = {
            "requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
            "latency_ms": {},
        }

    async def initialize(self) -> bool:
        """Initialize the text generation model."""
        try:
            if not VERTEX_AI_AVAILABLE:
                logger.warning("Vertex AI not available - using mock mode")
                return False

            self.model = GenerativeModel(model_name=self.model_name)
            logger.info(
                f"Text generation service initialized with model: {self.model_name}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize text generation service: {e}")
            return False

    def _get_cache_key(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Generate cache key for request."""
        import hashlib

        content = f"{prompt}|{system_instruction or ''}|{temperature}|{max_output_tokens or ''}|{top_p or ''}|{top_k or ''}"
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"text_gen:{self.model_name}:{content_hash}"

    @measure_execution_time("vertex_ai.text_generation.generate_content")
    @with_retries(max_retries=3, base_delay=1.0, backoff_factor=2)
    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        cache_namespace: Optional[str] = None,
        skip_cache: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate text content using the language model with advanced caching.

        Args:
            prompt: Input prompt for the model
            system_instruction: System instruction (optional)
            temperature: Temperature for generation (0.0-1.0)
            max_output_tokens: Maximum output tokens limit
            top_p: Top-p parameter for sampling
            top_k: Top-k parameter for sampling
            cache_namespace: Namespace for grouping related keys
            skip_cache: If True, skip cache and always call API

        Returns:
            Dict[str, Any]: Generated response and metadata
        """
        if not self.model:
            raise RuntimeError("Text generation service not initialized")

        self.stats["requests"] += 1

        # Generate cache key
        cache_key = self._get_cache_key(
            prompt, system_instruction, temperature, max_output_tokens, top_p, top_k
        )

        # Try cache first (unless skipped)
        if not skip_cache:
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self.stats["cache_hits"] += 1
                return cached_result

        self.stats["cache_misses"] += 1

        # Create span for telemetry
        span_attributes = {
            "service.prompt_length": len(prompt),
            "service.temperature": temperature,
            "service.has_system_instruction": system_instruction is not None,
            "service.model_name": self.model_name,
        }

        if max_output_tokens is not None:
            span_attributes["service.max_output_tokens"] = max_output_tokens
        if top_p is not None:
            span_attributes["service.top_p"] = top_p
        if top_k is not None:
            span_attributes["service.top_k"] = top_k

        span = telemetry_adapter.start_span(
            "TextGenerationService.generate_content", attributes=span_attributes
        )

        try:
            # Create generation config
            generation_config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                top_p=top_p,
                top_k=top_k,
            )

            # Prepare content
            contents = [prompt]
            if system_instruction:
                contents.insert(0, system_instruction)

            # Make API call
            start_time = asyncio.get_event_loop().time()

            if VERTEX_AI_AVAILABLE:
                response = await self.model.generate_content_async(
                    contents=contents, generation_config=generation_config
                )

                result = {
                    "content": (
                        response.text if hasattr(response, "text") else str(response)
                    ),
                    "model_name": self.model_name,
                    "usage": {
                        "prompt_tokens": getattr(response, "usage_metadata", {}).get(
                            "prompt_token_count", 0
                        ),
                        "completion_tokens": getattr(
                            response, "usage_metadata", {}
                        ).get("candidates_token_count", 0),
                    },
                    "finish_reason": "completed",
                    "timestamp": start_time,
                }
            else:
                # Mock response for testing
                await asyncio.sleep(0.1)  # Simulate API delay
                result = {
                    "content": f"Mock response for: {prompt[:50]}...",
                    "model_name": self.model_name,
                    "usage": {
                        "prompt_tokens": len(prompt.split()),
                        "completion_tokens": 10,
                    },
                    "finish_reason": "completed",
                    "timestamp": start_time,
                }

            # Record latency
            latency = int((asyncio.get_event_loop().time() - start_time) * 1000)
            self.stats["latency_ms"].setdefault(self.model_name, []).append(latency)

            # Cache the result
            if not skip_cache:
                await self.cache_manager.set(cache_key, result)

            telemetry_adapter.record_counter(
                "vertex_ai_requests",
                1,
                {"model": self.model_name, "type": "text_generation"},
            )

            span.set_attribute("service.success", True)
            span.set_attribute("service.response_length", len(result["content"]))

            return result

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error generating content: {e}")

            telemetry_adapter.record_counter(
                "vertex_ai_errors",
                1,
                {
                    "model": self.model_name,
                    "type": "text_generation",
                    "error": str(type(e).__name__),
                },
            )

            span.set_attribute("service.success", False)
            span.set_attribute("service.error", str(e))

            raise

        finally:
            span.end()

    async def generate_content_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate streaming text content.

        Args:
            prompt: Input prompt for the model
            system_instruction: System instruction (optional)
            temperature: Temperature for generation (0.0-1.0)
            max_output_tokens: Maximum output tokens limit
            top_p: Top-p parameter for sampling
            top_k: Top-k parameter for sampling

        Yields:
            Dict[str, Any]: Streaming response chunks
        """
        if not self.model:
            raise RuntimeError("Text generation service not initialized")

        try:
            # Create generation config
            generation_config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                top_p=top_p,
                top_k=top_k,
            )

            # Prepare content
            contents = [prompt]
            if system_instruction:
                contents.insert(0, system_instruction)

            if VERTEX_AI_AVAILABLE:
                # Stream from Vertex AI
                stream = await self.model.generate_content_async(
                    contents=contents, generation_config=generation_config, stream=True
                )

                async for chunk in stream:
                    if hasattr(chunk, "text") and chunk.text:
                        yield {
                            "content": chunk.text,
                            "type": "content",
                            "model_name": self.model_name,
                            "finish_reason": None,
                        }

                # Final chunk
                yield {
                    "content": "",
                    "type": "finish",
                    "model_name": self.model_name,
                    "finish_reason": "completed",
                }
            else:
                # Mock streaming response
                words = prompt.split()[:10]  # Use first 10 words for mock
                for i, word in enumerate(words):
                    await asyncio.sleep(0.1)
                    yield {
                        "content": f"{word} ",
                        "type": "content",
                        "model_name": self.model_name,
                        "finish_reason": None,
                    }

                yield {
                    "content": "",
                    "type": "finish",
                    "model_name": self.model_name,
                    "finish_reason": "completed",
                }

        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            yield {
                "content": "",
                "type": "error",
                "error": str(e),
                "model_name": self.model_name,
            }

    async def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            "service": "text_generation",
            "model_name": self.model_name,
            "stats": self.stats.copy(),
            "cache_stats": (
                await self.cache_manager.get_stats() if self.cache_manager else {}
            ),
        }
