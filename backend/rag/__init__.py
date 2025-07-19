"""
RAG (Retrieval-Augmented Generation) implementation for NGX Agents.

This module provides advanced RAG capabilities using Vertex AI Search
and the latest text-embedding-large-exp-03-07 model for enhanced agent responses.
"""

from .embeddings.vertex_embeddings import VertexEmbeddingsClient
from .search.vertex_search import VertexSearchClient
from .generation.flash_client import VertexFlashClient
from .pipeline import RAGPipeline

__all__ = [
    "VertexEmbeddingsClient",
    "VertexSearchClient",
    "VertexFlashClient",
    "RAGPipeline",
]
