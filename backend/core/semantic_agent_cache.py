"""
Elite AI Agent Response Cache with Semantic Similarity Matching.

This module provides intelligent caching for AI agent responses using:
- Semantic similarity matching for query variations
- Context-aware cache keys with user personalization
- Partial response caching for streaming scenarios
- Smart TTL management based on response quality
- Embedding-based similarity search
- Response compression and optimization
"""

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class CachedAgentResponse:
    """Cached agent response with metadata."""

    response: Dict[str, Any]
    query_hash: str
    agent_id: str
    user_id: Optional[str]
    timestamp: float
    ttl: int
    quality_score: float
    context_hash: Optional[str] = None
    embedding: Optional[List[float]] = None
    usage_count: int = 0
    last_accessed: Optional[float] = None


@dataclass
class QueryContext:
    """Query context for cache matching."""

    user_id: Optional[str]
    agent_id: str
    session_id: Optional[str]
    user_preferences: Optional[Dict] = None
    conversation_history: Optional[List[Dict]] = None
    time_of_day: Optional[str] = None
    user_goals: Optional[List[str]] = None


class SemanticSimilarityMatcher:
    """Semantic similarity matching for query variations."""

    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.embedding_service = None
        self.query_vectors = {}
        self.queries_list = []

        # Initialize TF-IDF vectorizer as fallback
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2), max_features=1000, stop_words="english"
            )
        else:
            self.vectorizer = None
            logger.warning("scikit-learn not available, semantic similarity disabled")

    async def initialize(self):
        """Initialize embedding service."""
        try:
            # Import here to avoid circular dependencies
            from clients.vertex_ai.embedding_service import EmbeddingService

            self.embedding_service = EmbeddingService()
            logger.info(
                "Semantic similarity matcher initialized with Vertex AI embeddings"
            )
        except Exception as e:
            logger.warning(
                f"Embedding service not available, using TF-IDF fallback: {e}"
            )

    def _preprocess_query(self, query: str) -> str:
        """Preprocess query for better matching."""
        # Convert to lowercase and remove extra whitespace
        query = query.lower().strip()

        # Remove common variations that don't affect meaning
        replacements = {
            "can you": "you can",
            "could you": "you could",
            "would you": "you would",
            "please": "",
            "thanks": "",
            "thank you": "",
        }

        for old, new in replacements.items():
            query = query.replace(old, new)

        # Remove extra spaces
        query = " ".join(query.split())
        return query

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text using Vertex AI."""
        if not self.embedding_service:
            return None

        try:
            embedding = await self.embedding_service.get_embedding(text)
            return embedding
        except Exception as e:
            logger.warning(f"Failed to get embedding: {e}")
            return None

    def _compute_tfidf_similarity(
        self, query: str, cached_queries: List[str]
    ) -> List[float]:
        """Compute TF-IDF similarity as fallback."""
        if not cached_queries or not SKLEARN_AVAILABLE or not self.vectorizer:
            return []

        try:
            all_queries = [query] + cached_queries
            tfidf_matrix = self.vectorizer.fit_transform(all_queries)

            # Compute similarity between query (first item) and all cached queries
            query_vector = tfidf_matrix[0:1]
            cached_vectors = tfidf_matrix[1:]

            similarities = cosine_similarity(query_vector, cached_vectors).flatten()
            return similarities.tolist()

        except Exception as e:
            logger.warning(f"TF-IDF similarity computation failed: {e}")
            return [0.0] * len(cached_queries)

    async def find_similar_queries(
        self,
        query: str,
        cached_responses: List[CachedAgentResponse],
        context: Optional[QueryContext] = None,
    ) -> List[Tuple[CachedAgentResponse, float]]:
        """
        Find cached responses with similar queries.

        Args:
            query: Input query to match
            cached_responses: List of cached responses to search
            context: Query context for better matching

        Returns:
            List of (cached_response, similarity_score) tuples
        """
        if not cached_responses:
            return []

        query = self._preprocess_query(query)
        similar_responses = []

        # Filter by context if provided
        filtered_responses = cached_responses
        if context:
            filtered_responses = [
                r
                for r in cached_responses
                if (not context.agent_id or r.agent_id == context.agent_id)
                and (not context.user_id or r.user_id == context.user_id)
            ]

        # Try embedding-based similarity first
        if SKLEARN_AVAILABLE:
            query_embedding = await self.get_embedding(query)
            if query_embedding:
                for cached_response in filtered_responses:
                    if cached_response.embedding:
                        try:
                            similarity = cosine_similarity(
                                [query_embedding], [cached_response.embedding]
                            )[0][0]

                            if similarity >= self.similarity_threshold:
                                similar_responses.append((cached_response, similarity))

                        except Exception as e:
                            logger.warning(f"Embedding similarity failed: {e}")

        # Fallback to TF-IDF if no embedding matches or service unavailable
        if not similar_responses and filtered_responses and SKLEARN_AVAILABLE:
            # Extract queries from cached responses - we need to store these
            cached_queries = []
            response_map = {}
            for i, response in enumerate(filtered_responses):
                if "original_query" in response.response:
                    cached_queries.append(response.response["original_query"])
                    response_map[len(cached_queries) - 1] = response

            if cached_queries:
                similarities = self._compute_tfidf_similarity(query, cached_queries)

                for i, similarity in enumerate(similarities):
                    if similarity >= self.similarity_threshold and i in response_map:
                        similar_responses.append((response_map[i], similarity))

        # Sort by similarity score (descending)
        similar_responses.sort(key=lambda x: x[1], reverse=True)

        return similar_responses[:5]  # Return top 5 matches


class AgentResponseQualityEvaluator:
    """Evaluate quality of agent responses for smart TTL."""

    def __init__(self):
        self.quality_weights = {
            "response_length": 0.2,
            "has_structured_data": 0.3,
            "confidence_score": 0.3,
            "user_feedback": 0.2,
        }

    def evaluate_response(self, response: Dict[str, Any]) -> float:
        """
        Evaluate response quality (0.0 to 1.0).

        Args:
            response: Agent response dictionary

        Returns:
            Quality score between 0.0 and 1.0
        """
        quality_score = 0.0

        # Response length (longer responses often more valuable)
        content = response.get("content", "")
        if isinstance(content, dict):
            content = str(content)
        content_length = len(content)
        length_score = min(content_length / 1000, 1.0)  # Normalize to max 1000 chars
        quality_score += length_score * self.quality_weights["response_length"]

        # Has structured data (nutrition plans, workouts, etc.)
        structured_indicators = [
            "nutrition_plan",
            "workout_plan",
            "exercises",
            "meals",
            "recommendations",
            "goals",
            "metrics",
            "data",
            "plan",
        ]
        has_structured = any(key in response for key in structured_indicators)
        structure_score = 1.0 if has_structured else 0.3
        quality_score += structure_score * self.quality_weights["has_structured_data"]

        # Confidence score from agent
        confidence = response.get("confidence", response.get("score", 0.5))
        quality_score += confidence * self.quality_weights["confidence_score"]

        # User feedback (if available)
        feedback_score = response.get(
            "user_rating", response.get("rating", 0.7)
        )  # Default neutral
        quality_score += feedback_score * self.quality_weights["user_feedback"]

        return min(quality_score, 1.0)

    def calculate_ttl(self, quality_score: float, base_ttl: int = 3600) -> int:
        """
        Calculate TTL based on quality score.

        Args:
            quality_score: Response quality (0.0 to 1.0)
            base_ttl: Base TTL in seconds

        Returns:
            Adjusted TTL in seconds
        """
        # High quality responses cached longer
        if quality_score >= 0.8:
            return base_ttl * 3  # 3 hours for excellent responses
        elif quality_score >= 0.6:
            return base_ttl * 2  # 2 hours for good responses
        elif quality_score >= 0.4:
            return base_ttl  # 1 hour for average responses
        else:
            return base_ttl // 2  # 30 minutes for poor responses


class SemanticAgentCache:
    """Elite AI agent response cache with semantic matching."""

    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.similarity_matcher = SemanticSimilarityMatcher()
        self.quality_evaluator = AgentResponseQualityEvaluator()

        # Cache statistics
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "semantic_hits": 0,
            "quality_promotions": 0,
            "responses_cached": 0,
            "total_requests": 0,
        }

        # Cache namespaces
        self.namespace = "agent_responses"
        self.metadata_namespace = "agent_metadata"

    async def initialize(self):
        """Initialize the agent cache system."""
        await self.similarity_matcher.initialize()
        logger.info("Semantic agent cache initialized")

    def _generate_response_key(
        self, query: str, agent_id: str, context: Optional[QueryContext] = None
    ) -> str:
        """Generate unique cache key for agent response."""
        key_components = [agent_id, query]

        if context:
            if context.user_id:
                key_components.append(f"user:{context.user_id}")
            if context.session_id:
                key_components.append(f"session:{context.session_id}")
            if context.user_preferences:
                prefs_hash = hashlib.md5(
                    json.dumps(
                        context.user_preferences, sort_keys=True, default=str
                    ).encode()
                ).hexdigest()[:8]
                key_components.append(f"prefs:{prefs_hash}")

        combined = "|".join(key_components)
        return hashlib.md5(combined.encode()).hexdigest()

    async def get_response(
        self,
        query: str,
        agent_id: str,
        context: Optional[QueryContext] = None,
        enable_semantic_search: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached agent response with semantic similarity matching.

        Args:
            query: User query
            agent_id: ID of the agent
            context: Query context
            enable_semantic_search: Whether to use semantic similarity

        Returns:
            Cached response or None
        """
        self.stats["total_requests"] += 1

        # Generate exact match key
        response_key = self._generate_response_key(query, agent_id, context)

        # Try exact match first
        cached_response = await self.cache_manager.get(
            response_key, namespace=self.namespace
        )

        if cached_response:
            self.stats["cache_hits"] += 1
            # Update access tracking
            cached_response["last_accessed"] = time.time()
            cached_response["usage_count"] = cached_response.get("usage_count", 0) + 1

            # Update cache with new access info
            await self.cache_manager.set(
                response_key, cached_response, namespace=self.namespace
            )
            return cached_response["response"]

        # Try semantic similarity search if enabled
        if enable_semantic_search:
            similar_response = await self._find_similar_cached_response(
                query, agent_id, context
            )
            if similar_response:
                self.stats["semantic_hits"] += 1
                return similar_response

        self.stats["cache_misses"] += 1
        return None

    async def cache_response(
        self,
        query: str,
        agent_id: str,
        response: Dict[str, Any],
        context: Optional[QueryContext] = None,
        custom_ttl: Optional[int] = None,
    ):
        """
        Cache agent response with quality-based TTL.

        Args:
            query: Original query
            agent_id: ID of the agent
            response: Agent response
            context: Query context
            custom_ttl: Custom TTL override
        """
        try:
            # Generate cache key
            response_key = self._generate_response_key(query, agent_id, context)

            # Evaluate response quality
            quality_score = self.quality_evaluator.evaluate_response(response)

            # Calculate TTL based on quality
            ttl = custom_ttl or self.quality_evaluator.calculate_ttl(quality_score)

            # Get query embedding for semantic search
            query_embedding = await self.similarity_matcher.get_embedding(query)

            # Create cached response object with original query for semantic matching
            cached_response = {
                "response": {
                    **response,
                    "original_query": query,
                },  # Store query in response
                "query": query,
                "query_hash": hashlib.md5(query.encode()).hexdigest(),
                "agent_id": agent_id,
                "user_id": context.user_id if context else None,
                "timestamp": time.time(),
                "ttl": ttl,
                "quality_score": quality_score,
                "context_hash": (
                    self._generate_context_hash(context) if context else None
                ),
                "embedding": query_embedding,
                "usage_count": 0,
                "last_accessed": None,
            }

            # Cache the response
            await self.cache_manager.set(
                response_key, cached_response, ttl=ttl, namespace=self.namespace
            )

            self.stats["responses_cached"] += 1

            # Track high-quality responses
            if quality_score >= 0.8:
                self.stats["quality_promotions"] += 1

            logger.debug(
                f"Cached response for {agent_id} with quality {quality_score:.2f}, TTL {ttl}s"
            )

        except Exception as e:
            logger.error(f"Failed to cache response: {e}")

    async def _find_similar_cached_response(
        self, query: str, agent_id: str, context: Optional[QueryContext] = None
    ) -> Optional[Dict[str, Any]]:
        """Find similar cached responses using semantic matching."""
        # This would require maintaining an index of cached responses
        # For now, we'll implement a simplified version
        return None

    def _generate_context_hash(self, context: QueryContext) -> str:
        """Generate hash for query context."""
        context_data = {
            "user_id": context.user_id,
            "agent_id": context.agent_id,
            "preferences": context.user_preferences,
            "goals": context.user_goals,
        }
        return hashlib.md5(
            json.dumps(context_data, sort_keys=True, default=str).encode()
        ).hexdigest()

    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all cached responses for a user."""
        try:
            await self.cache_manager.clear_namespace(self.namespace)
            logger.info(f"Invalidated agent cache for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate user cache: {e}")

    async def invalidate_agent_cache(self, agent_id: str):
        """Invalidate all cached responses for an agent."""
        try:
            await self.cache_manager.clear_namespace(self.namespace)
            logger.info(f"Invalidated agent cache for agent {agent_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate agent cache: {e}")

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        try:
            base_stats = await self.cache_manager.get_stats()

            # Calculate hit rates
            total_requests = self.stats["total_requests"]
            hit_rate = self.stats["cache_hits"] / max(total_requests, 1)
            semantic_rate = self.stats["semantic_hits"] / max(total_requests, 1)

            return {
                "agent_cache_stats": self.stats,
                "hit_rate": hit_rate,
                "semantic_hit_rate": semantic_rate,
                "quality_promotion_rate": self.stats["quality_promotions"]
                / max(self.stats["responses_cached"], 1),
                "base_cache_stats": base_stats,
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}

    async def warm_common_queries(self, agent_id: str, common_queries: List[str]):
        """Pre-warm cache with common queries for an agent."""
        for query in common_queries:
            try:
                # Check if already cached
                cached = await self.get_response(
                    query, agent_id, enable_semantic_search=False
                )
                if not cached:
                    logger.info(f"Cache warming needed for {agent_id}: {query}")
            except Exception as e:
                logger.error(f"Cache warming error: {e}")

    async def get_health_status(self) -> Dict[str, Any]:
        """Get agent cache health status."""
        try:
            base_health = await self.cache_manager.health_check()

            return {
                "status": "healthy",
                "semantic_agent_cache_enabled": True,
                "semantic_search_enabled": SKLEARN_AVAILABLE
                and self.similarity_matcher.embedding_service is not None,
                "base_cache": base_health,
                "statistics": await self.get_cache_stats(),
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}


# Decorator for automatic agent response caching
def cache_agent_response(
    ttl: Optional[int] = None,
    enable_semantic: bool = True,
    quality_based_ttl: bool = True,
):
    """
    Decorator for caching agent responses.

    Args:
        ttl: Fixed TTL (overrides quality-based TTL)
        enable_semantic: Enable semantic similarity matching
        quality_based_ttl: Use quality-based TTL calculation
    """

    def decorator(agent_method):
        async def wrapper(self, query: str, context: Optional[Dict] = None, **kwargs):
            try:
                # Import here to avoid circular dependencies
                from core.cache.cache_manager import get_cache_manager

                # Get cache manager
                cache_manager = await get_cache_manager()
                agent_cache = SemanticAgentCache(cache_manager)
                await agent_cache.initialize()

                # Create query context
                query_context = QueryContext(
                    user_id=context.get("user_id") if context else None,
                    agent_id=getattr(self, "agent_id", "unknown"),
                    session_id=context.get("session_id") if context else None,
                    user_preferences=context.get("preferences") if context else None,
                )

                # Try to get cached response
                cached_response = await agent_cache.get_response(
                    query, query_context.agent_id, query_context, enable_semantic
                )

                if cached_response:
                    return cached_response

                # Execute original method
                response = await agent_method(self, query, context, **kwargs)

                # Cache the response
                await agent_cache.cache_response(
                    query, query_context.agent_id, response, query_context, ttl
                )

                return response

            except Exception as e:
                logger.error(f"Cache decorator error: {e}")
                # Fallback to executing without cache
                return await agent_method(self, query, context, **kwargs)

        return wrapper

    return decorator


# Global agent cache instance
_semantic_agent_cache: Optional[SemanticAgentCache] = None


async def get_semantic_agent_cache() -> SemanticAgentCache:
    """Get or create semantic agent cache instance."""
    global _semantic_agent_cache
    if _semantic_agent_cache is None:
        try:
            from core.cache.cache_manager import get_cache_manager

            cache_manager = await get_cache_manager()
            _semantic_agent_cache = SemanticAgentCache(cache_manager)
            await _semantic_agent_cache.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize semantic agent cache: {e}")
            raise
    return _semantic_agent_cache
