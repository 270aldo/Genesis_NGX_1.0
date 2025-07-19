"""
Tests para el método batch_generate_embeddings del cliente Vertex AI.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Importar el cliente
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from clients.vertex_ai.client import VertexAIClient


class TestBatchGenerateEmbeddings:
    """Tests para el método batch_generate_embeddings."""

    @pytest.mark.asyncio
    async def test_batch_generate_embeddings_mock_mode(self):
        """Test en modo mock."""
        # Crear cliente
        client = VertexAIClient(
            model_name="gemini-2.5-pro",
            use_redis_cache=False,
            max_cache_size=100
        )
        
        # Simular que el cliente está inicializado
        client._initialized = True
        client.is_initialized = True
        
        # Mock del pool de conexiones
        mock_pool = AsyncMock()
        mock_pool.acquire = AsyncMock(return_value={"mock": True})
        mock_pool.release = AsyncMock()
        client.connection_pool = mock_pool
        
        # Ejecutar el método
        texts = ["Texto 1", "Texto 2"]
        embeddings = await client.batch_generate_embeddings(texts)
        
        # Verificaciones
        assert len(embeddings) == 2
        assert all(len(emb) == 3072 for emb in embeddings)
        assert client.stats["batch_embedding_requests"] == 1
        
        # Verificar que se llamó al pool
        mock_pool.acquire.assert_called_once()
        mock_pool.release.assert_called_once()

    @pytest.mark.asyncio
    async def test_batch_generate_embeddings_empty_list(self):
        """Test para lista vacía."""
        client = VertexAIClient(
            model_name="gemini-2.5-pro",
            use_redis_cache=False
        )
        
        # Simular inicialización
        client._initialized = True
        client.is_initialized = True
        
        # Ejecutar con lista vacía
        embeddings = await client.batch_generate_embeddings([])
        
        # Verificaciones
        assert embeddings == []
        assert client.stats["batch_embedding_requests"] == 1

    @pytest.mark.asyncio
    async def test_batch_generate_embeddings_with_real_model_mock(self):
        """Test simulando el modelo real."""
        client = VertexAIClient(
            model_name="gemini-2.5-pro",
            use_redis_cache=False
        )
        
        # Simular inicialización
        client._initialized = True
        client.is_initialized = True
        
        # Mock del modelo de embeddings
        mock_results = []
        for i in range(3):
            result = Mock()
            result.values = [0.1 * i] * 3072
            mock_results.append(result)
        
        mock_embedding_model = Mock()
        mock_embedding_model.get_embeddings = Mock(return_value=mock_results)
        
        # Mock del pool
        mock_pool = AsyncMock()
        mock_pool.acquire = AsyncMock(return_value={
            "mock": False,
            "embedding_model": mock_embedding_model
        })
        mock_pool.release = AsyncMock()
        client.connection_pool = mock_pool
        
        # Ejecutar
        texts = ["Texto A", "Texto B", "Texto C"]
        embeddings = await client.batch_generate_embeddings(texts)
        
        # Verificaciones
        assert len(embeddings) == 3
        assert all(len(emb) == 3072 for emb in embeddings)
        assert embeddings[0][0] == 0.0  # Primer embedding
        assert embeddings[1][0] == 0.1  # Segundo embedding
        assert embeddings[2][0] == 0.2  # Tercer embedding
        
        # Verificar que se llamó al modelo con los textos correctos
        mock_embedding_model.get_embeddings.assert_called_once_with(texts)

    @pytest.mark.asyncio
    async def test_batch_generate_embeddings_error_handling(self):
        """Test manejo de errores."""
        client = VertexAIClient(
            model_name="gemini-2.5-pro",
            use_redis_cache=False
        )
        
        # Simular inicialización
        client._initialized = True
        client.is_initialized = True
        
        # Mock del modelo que lanza error
        mock_embedding_model = Mock()
        mock_embedding_model.get_embeddings = Mock(
            side_effect=Exception("Error simulado")
        )
        
        # Mock del pool
        mock_pool = AsyncMock()
        mock_pool.acquire = AsyncMock(return_value={
            "mock": False,
            "embedding_model": mock_embedding_model
        })
        mock_pool.release = AsyncMock()
        client.connection_pool = mock_pool
        
        # Ejecutar
        texts = ["Texto que causará error"]
        embeddings = await client.batch_generate_embeddings(texts)
        
        # Verificaciones - debe retornar embeddings vacíos
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 3072
        assert all(val == 0.0 for val in embeddings[0])
        assert "Exception" in client.stats["errors"]