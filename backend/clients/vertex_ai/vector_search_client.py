"""
Cliente para Vertex AI Vector Search.

Proporciona métodos para buscar vectores similares usando el índice desplegado.
"""

import asyncio
from typing import List, Dict, Any, Optional
from google.cloud import aiplatform
from google.cloud.aiplatform import MatchingEngineIndex, MatchingEngineIndexEndpoint

from core.logging_config import get_logger
from config.secrets import settings

logger = get_logger(__name__)


class VectorSearchClient:
    """Cliente para interactuar con Vertex AI Vector Search."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        index_id: Optional[str] = None,
        index_endpoint_id: Optional[str] = None,
    ):
        """
        Inicializa el cliente de Vector Search.

        Args:
            project_id: ID del proyecto de GCP
            location: Región donde está el índice
            index_id: ID del índice de Vector Search
            index_endpoint_id: ID del endpoint desplegado
        """
        self.project_id = project_id or settings.GCP_PROJECT_ID
        self.location = location
        self.index_id = index_id or settings.VERTEX_AI_INDEX_ID
        self.index_endpoint_id = (
            index_endpoint_id or settings.VERTEX_AI_INDEX_ENDPOINT_ID
        )

        self.index_endpoint = None
        self._initialized = False

    async def initialize(self):
        """Inicializa la conexión con el Vector Search endpoint."""
        if self._initialized:
            return

        try:
            # Inicializar AI Platform
            aiplatform.init(project=self.project_id, location=self.location)

            # Obtener referencia al index endpoint
            self.index_endpoint = MatchingEngineIndexEndpoint(
                index_endpoint_name=self.index_endpoint_id
            )

            self._initialized = True
            logger.info(
                f"Vector Search Client inicializado para endpoint: {self.index_endpoint_id}"
            )

        except Exception as e:
            logger.error(f"Error al inicializar Vector Search Client: {e}")
            raise

    async def search_similar(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_expression: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca vectores similares en el índice.

        Args:
            query_vector: Vector de consulta (3072 dimensiones)
            top_k: Número de resultados a retornar
            filter_expression: Expresión de filtro opcional

        Returns:
            Lista de resultados con IDs y distancias
        """
        if not self._initialized:
            await self.initialize()

        try:
            loop = asyncio.get_event_loop()

            # Realizar búsqueda
            response = await loop.run_in_executor(
                None,
                lambda: self.index_endpoint.find_neighbors(
                    deployed_index_id=self.index_id,
                    queries=[query_vector],
                    num_neighbors=top_k,
                ),
            )

            # Procesar resultados
            results = []
            for neighbor_list in response:
                for neighbor in neighbor_list.neighbors:
                    results.append(
                        {
                            "id": neighbor.datapoint_id,
                            "distance": neighbor.distance,
                            "crowding_tag": (
                                neighbor.crowding_tag
                                if hasattr(neighbor, "crowding_tag")
                                else None
                            ),
                        }
                    )

            return results[:top_k]

        except Exception as e:
            logger.error(f"Error al buscar vectores similares: {e}")
            return []

    async def batch_search_similar(
        self,
        query_vectors: List[List[float]],
        top_k: int = 10,
        filter_expression: Optional[str] = None,
    ) -> List[List[Dict[str, Any]]]:
        """
        Busca múltiples vectores similares en lote.

        Args:
            query_vectors: Lista de vectores de consulta
            top_k: Número de resultados por consulta
            filter_expression: Expresión de filtro opcional

        Returns:
            Lista de listas de resultados
        """
        if not self._initialized:
            await self.initialize()

        try:
            loop = asyncio.get_event_loop()

            # Realizar búsqueda en lote
            response = await loop.run_in_executor(
                None,
                lambda: self.index_endpoint.find_neighbors(
                    deployed_index_id=self.index_id,
                    queries=query_vectors,
                    num_neighbors=top_k,
                ),
            )

            # Procesar resultados por cada consulta
            all_results = []
            for neighbor_list in response:
                query_results = []
                for neighbor in neighbor_list.neighbors:
                    query_results.append(
                        {
                            "id": neighbor.datapoint_id,
                            "distance": neighbor.distance,
                            "crowding_tag": (
                                neighbor.crowding_tag
                                if hasattr(neighbor, "crowding_tag")
                                else None
                            ),
                        }
                    )
                all_results.append(query_results[:top_k])

            return all_results

        except Exception as e:
            logger.error(f"Error en búsqueda batch: {e}")
            return [[] for _ in query_vectors]


# Instancia global
# Use lazy initialization to prevent hanging during import
from core.lazy_init import LazyInstance
vector_search_client = LazyInstance(VectorSearchClient, "VectorSearchClient")
