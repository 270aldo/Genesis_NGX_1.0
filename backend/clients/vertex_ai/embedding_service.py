"""
Embedding Service for Vertex AI Client.

This module handles all embedding generation functionality,
providing a focused service for text embeddings with batch processing and caching.
"""

import asyncio
from typing import Any, Dict, List

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
    import vertexai
    from vertexai.language_models import TextEmbeddingModel

    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

    class TextEmbeddingModel:
        pass


class EmbeddingService:
    """
    Service responsible for generating text embeddings using Vertex AI.

    This service handles:
    - Single text embedding generation
    - Batch embedding processing
    - Caching and performance optimization
    - Error handling and retries
    """

    def __init__(
        self,
        embedding_model_name: str = "text-embedding-004",
        cache_manager: CacheManager = None,
        connection_pool: ConnectionPool = None,
        batch_size: int = 100,
        **kwargs,
    ):
        """Initialize the embedding service."""
        self.embedding_model_name = embedding_model_name
        self.cache_manager = cache_manager
        self.connection_pool = connection_pool
        self.batch_size = batch_size
        self.model = None
        self.stats = {
            "requests": 0,
            "embeddings_generated": 0,
            "batch_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
            "latency_ms": [],
        }

    async def initialize(self) -> bool:
        """Initialize the embedding model."""
        try:
            if not VERTEX_AI_AVAILABLE:
                logger.warning("Vertex AI not available - using mock mode")
                return False

            self.model = TextEmbeddingModel.from_pretrained(self.embedding_model_name)
            logger.info(
                f"Embedding service initialized with model: {self.embedding_model_name}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            return False

    def _get_cache_key(self, text: str, task_type: str = "retrieval") -> str:
        """Generate cache key for embedding request."""
        import hashlib

        content = f"{text}|{task_type}|{self.embedding_model_name}"
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"embedding:{self.embedding_model_name}:{content_hash}"

    def _get_batch_cache_key(
        self, texts: List[str], task_type: str = "retrieval"
    ) -> str:
        """Generate cache key for batch embedding request."""
        import hashlib

        # Sort texts to ensure consistent cache keys
        sorted_texts = sorted(texts)
        content = f"{'|'.join(sorted_texts)}|{task_type}|{self.embedding_model_name}"
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"batch_embedding:{self.embedding_model_name}:{content_hash}"

    @measure_execution_time("vertex_ai.embedding.generate_embedding")
    @with_retries(max_retries=3, base_delay=1.0, backoff_factor=2)
    async def generate_embedding(
        self, text: str, task_type: str = "retrieval", skip_cache: bool = False
    ) -> Dict[str, Any]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text for embedding
            task_type: Task type for embedding ("retrieval", "classification", etc.)
            skip_cache: If True, skip cache and always call API

        Returns:
            Dict[str, Any]: Embedding vector and metadata
        """
        if not self.model:
            raise RuntimeError("Embedding service not initialized")

        self.stats["requests"] += 1

        # Generate cache key
        cache_key = self._get_cache_key(text, task_type)

        # Try cache first (unless skipped)
        if not skip_cache and self.cache_manager:
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self.stats["cache_hits"] += 1
                return cached_result

        self.stats["cache_misses"] += 1

        span_attributes = {
            "service.text_length": len(text),
            "service.task_type": task_type,
            "service.model_name": self.embedding_model_name,
        }

        span = telemetry_adapter.start_span(
            "EmbeddingService.generate_embedding", attributes=span_attributes
        )

        try:
            start_time = asyncio.get_event_loop().time()

            if VERTEX_AI_AVAILABLE:
                # Make API call
                embeddings = await self.model.get_embeddings_async(
                    [text], task=task_type
                )

                if embeddings and embeddings[0]:
                    embedding_vector = embeddings[0].values
                else:
                    raise ValueError("Empty embedding response")

                result = {
                    "embedding": embedding_vector,
                    "text": text,
                    "model_name": self.embedding_model_name,
                    "task_type": task_type,
                    "dimensions": len(embedding_vector),
                    "timestamp": start_time,
                }
            else:
                # Mock embedding for testing
                await asyncio.sleep(0.05)  # Simulate API delay
                import random

                embedding_vector = [random.uniform(-1.0, 1.0) for _ in range(768)]

                result = {
                    "embedding": embedding_vector,
                    "text": text,
                    "model_name": self.embedding_model_name,
                    "task_type": task_type,
                    "dimensions": len(embedding_vector),
                    "timestamp": start_time,
                }

            # Record latency
            latency = int((asyncio.get_event_loop().time() - start_time) * 1000)
            self.stats["latency_ms"].append(latency)
            self.stats["embeddings_generated"] += 1

            # Cache the result
            if not skip_cache and self.cache_manager:
                await self.cache_manager.set(cache_key, result)

            telemetry_adapter.record_counter(
                "vertex_ai_requests",
                1,
                {"model": self.embedding_model_name, "type": "embedding"},
            )

            span.set_attribute("service.success", True)
            span.set_attribute("service.embedding_dimensions", len(embedding_vector))

            return result

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error generating embedding: {e}")

            telemetry_adapter.record_counter(
                "vertex_ai_errors",
                1,
                {
                    "model": self.embedding_model_name,
                    "type": "embedding",
                    "error": str(type(e).__name__),
                },
            )

            span.set_attribute("service.success", False)
            span.set_attribute("service.error", str(e))

            raise

        finally:
            span.end()

    @measure_execution_time("vertex_ai.embedding.batch_generate_embeddings")
    @with_retries(max_retries=3, base_delay=1.0, backoff_factor=2)
    async def batch_generate_embeddings(
        self, texts: List[str], task_type: str = "retrieval", skip_cache: bool = False
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.

        Args:
            texts: List of input texts for embedding
            task_type: Task type for embedding
            skip_cache: If True, skip cache and always call API

        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not texts:
            return []

        if not self.model:
            raise RuntimeError("Embedding service not initialized")

        self.stats["batch_requests"] += 1

        # Check cache for batch
        cache_key = self._get_batch_cache_key(texts, task_type)

        if not skip_cache and self.cache_manager:
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self.stats["cache_hits"] += 1
                return cached_result

        self.stats["cache_misses"] += 1

        span_attributes = {
            "service.batch_size": len(texts),
            "service.task_type": task_type,
            "service.model_name": self.embedding_model_name,
        }

        span = telemetry_adapter.start_span(
            "EmbeddingService.batch_generate_embeddings", attributes=span_attributes
        )

        try:
            start_time = asyncio.get_event_loop().time()

            # Process in chunks if needed
            all_embeddings = []

            for i in range(0, len(texts), self.batch_size):
                chunk = texts[i : i + self.batch_size]

                if VERTEX_AI_AVAILABLE:
                    embeddings = await self.model.get_embeddings_async(
                        chunk, task=task_type
                    )
                    chunk_vectors = [emb.values for emb in embeddings]
                else:
                    # Mock embeddings for testing
                    await asyncio.sleep(0.1)  # Simulate API delay
                    import random

                    chunk_vectors = [
                        [random.uniform(-1.0, 1.0) for _ in range(768)] for _ in chunk
                    ]

                all_embeddings.extend(chunk_vectors)

            # Record metrics
            latency = int((asyncio.get_event_loop().time() - start_time) * 1000)
            self.stats["latency_ms"].append(latency)
            self.stats["embeddings_generated"] += len(texts)

            # Cache the result
            if not skip_cache and self.cache_manager:
                await self.cache_manager.set(cache_key, all_embeddings)

            telemetry_adapter.record_counter(
                "vertex_ai_requests",
                1,
                {
                    "model": self.embedding_model_name,
                    "type": "batch_embedding",
                    "batch_size": len(texts),
                },
            )

            span.set_attribute("service.success", True)
            span.set_attribute("service.embeddings_count", len(all_embeddings))

            return all_embeddings

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error generating batch embeddings: {e}")

            telemetry_adapter.record_counter(
                "vertex_ai_errors",
                1,
                {
                    "model": self.embedding_model_name,
                    "type": "batch_embedding",
                    "error": str(type(e).__name__),
                },
            )

            span.set_attribute("service.success", False)
            span.set_attribute("service.error", str(e))

            raise

        finally:
            span.end()

    async def batch_embeddings(
        self, texts: List[str], task_type: str = "retrieval"
    ) -> Dict[str, Any]:
        """
        Generate batch embeddings with detailed response.

        Args:
            texts: List of input texts for embedding
            task_type: Task type for embedding

        Returns:
            Dict[str, Any]: Detailed response with embeddings and metadata
        """
        start_time = asyncio.get_event_loop().time()

        embeddings = await self.batch_generate_embeddings(texts, task_type)

        return {
            "embeddings": embeddings,
            "model_name": self.embedding_model_name,
            "task_type": task_type,
            "count": len(embeddings),
            "dimensions": len(embeddings[0]) if embeddings else 0,
            "processing_time_ms": int(
                (asyncio.get_event_loop().time() - start_time) * 1000
            ),
            "timestamp": start_time,
        }

    async def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        avg_latency = (
            sum(self.stats["latency_ms"]) / len(self.stats["latency_ms"])
            if self.stats["latency_ms"]
            else 0
        )

        return {
            "service": "embedding",
            "model_name": self.embedding_model_name,
            "stats": {
                **self.stats,
                "avg_latency_ms": avg_latency,
                "total_latency_samples": len(self.stats["latency_ms"]),
            },
            "cache_stats": (
                await self.cache_manager.get_stats() if self.cache_manager else {}
            ),
        }
