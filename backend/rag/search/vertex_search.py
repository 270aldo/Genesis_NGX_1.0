"""
Cliente de Vertex AI Search para NGX Agents.

Proporciona búsqueda semántica avanzada usando Vertex AI Search
con soporte para filtros, facetas y ranking personalizado.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from google.cloud import discoveryengine_v1alpha as discoveryengine
from google.cloud.discoveryengine_v1alpha import SearchServiceClient, SearchRequest
from google.api_core import retry

from core.logging_config import get_logger
from core.circuit_breaker import circuit_breaker
from infrastructure.adapters.telemetry_adapter import (
    get_telemetry_adapter,
    measure_execution_time,
)

logger = get_logger(__name__)
telemetry_adapter = get_telemetry_adapter()


class VertexSearchClient:
    """
    Cliente para Vertex AI Search con capacidades avanzadas de búsqueda.

    Features:
    - Búsqueda semántica con embeddings
    - Filtros y facetas personalizables
    - Re-ranking basado en relevancia
    - Integración con RAG pipeline
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "global",
        search_app_id: Optional[str] = None,
        datastore_id: Optional[str] = None,
    ):
        """
        Inicializa el cliente de Vertex AI Search.

        Args:
            project_id: ID del proyecto de GCP
            location: Ubicación del servicio (generalmente 'global')
            search_app_id: ID de la aplicación de búsqueda
            datastore_id: ID del datastore
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.location = location
        self.search_app_id = search_app_id or os.getenv("VERTEX_SEARCH_APP_ID")
        self.datastore_id = datastore_id or os.getenv("VERTEX_SEARCH_DATASTORE_ID")

        # Inicializar cliente
        self.client = SearchServiceClient()

        # Construir el serving config path
        self.serving_config = (
            f"projects/{self.project_id}/locations/{self.location}/"
            f"collections/default_collection/engines/{self.search_app_id}/"
            f"servingConfigs/default_config"
        )

        logger.info(
            f"Cliente de Vertex AI Search inicializado - "
            f"App: {self.search_app_id}, Datastore: {self.datastore_id}"
        )

    @measure_execution_time
    @circuit_breaker
    async def search(
        self,
        query: str,
        max_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        boost_specs: Optional[List[Dict[str, Any]]] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda semántica en el datastore.

        Args:
            query: Consulta de búsqueda
            max_results: Número máximo de resultados
            filters: Filtros para aplicar a la búsqueda
            boost_specs: Especificaciones de boost para ranking
            user_context: Contexto del usuario para personalización

        Returns:
            Lista de documentos relevantes con metadata
        """
        with telemetry_adapter.start_span("vertex_ai_search") as span:
            span.set_attribute("query", query)
            span.set_attribute("max_results", max_results)

            try:
                # Construir la request
                request = SearchRequest(
                    serving_config=self.serving_config,
                    query=query,
                    page_size=max_results,
                    query_expansion_spec=SearchRequest.QueryExpansionSpec(
                        condition=SearchRequest.QueryExpansionSpec.Condition.AUTO
                    ),
                    spell_correction_spec=SearchRequest.SpellCorrectionSpec(
                        mode=SearchRequest.SpellCorrectionSpec.Mode.AUTO
                    ),
                )

                # Aplicar filtros si existen
                if filters:
                    request.filter = self._build_filter_expression(filters)

                # Aplicar boost specs si existen
                if boost_specs:
                    request.boost_spec = self._build_boost_spec(boost_specs)

                # Agregar información del usuario si existe
                if user_context:
                    request.user_info = self._build_user_info(user_context)

                # Ejecutar búsqueda
                response = await self._execute_search(request)

                # Procesar resultados
                results = self._process_search_results(response)

                span.set_attribute("results_count", len(results))
                logger.info(
                    f"Búsqueda completada: {len(results)} resultados para '{query}'"
                )

                return results

            except Exception as e:
                span.record_exception(e)
                logger.error(f"Error en búsqueda: {e}")
                raise

    async def search_with_embeddings(
        self,
        query_embedding: List[float],
        query_text: str,
        max_results: int = 5,
        similarity_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda usando embeddings pre-calculados.

        Args:
            query_embedding: Vector de embeddings de la consulta
            query_text: Texto original de la consulta
            max_results: Número máximo de resultados
            similarity_threshold: Umbral de similitud mínima

        Returns:
            Lista de documentos relevantes
        """
        # Por ahora, Vertex AI Search maneja embeddings internamente
        # Esta función es para compatibilidad futura cuando se exponga la API
        logger.info("Búsqueda con embeddings delegada a búsqueda semántica estándar")
        return await self.search(query_text, max_results)

    async def search_by_domain(
        self, query: str, domain: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda filtrada por dominio específico.

        Args:
            query: Consulta de búsqueda
            domain: Dominio (fitness, nutrition, wellness)
            max_results: Número máximo de resultados

        Returns:
            Lista de documentos del dominio especificado
        """
        filters = {"domain": domain}
        return await self.search(query, max_results, filters)

    async def search_personalized(
        self,
        query: str,
        user_id: str,
        user_preferences: Dict[str, Any],
        max_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda personalizada basada en preferencias del usuario.

        Args:
            query: Consulta de búsqueda
            user_id: ID del usuario
            user_preferences: Preferencias y contexto del usuario
            max_results: Número máximo de resultados

        Returns:
            Lista de documentos personalizados
        """
        # Construir boost specs basados en preferencias
        boost_specs = self._build_preference_boosts(user_preferences)

        # Contexto del usuario
        user_context = {"user_id": user_id, "preferences": user_preferences}

        return await self.search(
            query, max_results, boost_specs=boost_specs, user_context=user_context
        )

    def _build_filter_expression(self, filters: Dict[str, Any]) -> str:
        """Construye una expresión de filtro para la búsqueda."""
        expressions = []

        for field, value in filters.items():
            if isinstance(value, list):
                # OR entre valores de la lista
                or_expr = " OR ".join([f'{field}:"{v}"' for v in value])
                expressions.append(f"({or_expr})")
            else:
                expressions.append(f'{field}:"{value}"')

        return " AND ".join(expressions)

    def _build_boost_spec(self, boost_specs: List[Dict[str, Any]]) -> Any:
        """Construye especificaciones de boost para el ranking."""
        # Implementación simplificada - expandir según necesidades
        boost_spec = SearchRequest.BoostSpec()

        for spec in boost_specs:
            condition_boost = SearchRequest.BoostSpec.ConditionBoostSpec(
                condition=spec.get("condition", ""), boost=spec.get("boost", 1.0)
            )
            boost_spec.condition_boost_specs.append(condition_boost)

        return boost_spec

    def _build_user_info(self, user_context: Dict[str, Any]) -> Any:
        """Construye información del usuario para personalización."""
        user_info = SearchRequest.UserInfo(user_id=user_context.get("user_id", ""))

        # Agregar atributos adicionales si están disponibles
        if "user_agent" in user_context:
            user_info.user_agent = user_context["user_agent"]

        return user_info

    def _build_preference_boosts(
        self, preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Construye boosts basados en preferencias del usuario."""
        boost_specs = []

        # Ejemplo: boost para nivel de fitness
        if "fitness_level" in preferences:
            boost_specs.append(
                {
                    "condition": f'fitness_level:"{preferences["fitness_level"]}"',
                    "boost": 1.5,
                }
            )

        # Ejemplo: boost para objetivos
        if "goals" in preferences:
            for goal in preferences["goals"]:
                boost_specs.append({"condition": f'tags:"{goal}"', "boost": 1.3})

        return boost_specs

    async def _execute_search(self, request: SearchRequest) -> Any:
        """Ejecuta la búsqueda con retry automático."""
        retry_config = retry.Retry(
            initial=0.1,
            maximum=10.0,
            multiplier=2.0,
            predicate=retry.if_transient_error,
        )

        return await retry_config.__call__(self.client.search, request=request)

    def _process_search_results(self, response: Any) -> List[Dict[str, Any]]:
        """Procesa y formatea los resultados de búsqueda."""
        results = []

        for result in response.results:
            # Extraer documento
            document = result.document

            # Construir resultado formateado
            formatted_result = {
                "id": document.id,
                "name": document.name,
                "score": (
                    result.relevance_score
                    if hasattr(result, "relevance_score")
                    else 1.0
                ),
                "content": self._extract_content(document),
                "metadata": self._extract_metadata(document),
                "snippets": self._extract_snippets(result),
            }

            results.append(formatted_result)

        return results

    def _extract_content(self, document: Any) -> str:
        """Extrae el contenido principal del documento."""
        # La estructura exacta depende de cómo se indexaron los documentos
        if hasattr(document, "struct_data"):
            struct_data = document.struct_data
            return struct_data.get("content", "") or struct_data.get("text", "")
        return ""

    def _extract_metadata(self, document: Any) -> Dict[str, Any]:
        """Extrae metadata del documento."""
        metadata = {}

        if hasattr(document, "struct_data"):
            struct_data = document.struct_data
            metadata = {
                "title": struct_data.get("title", ""),
                "category": struct_data.get("category", ""),
                "domain": struct_data.get("domain", ""),
                "source": struct_data.get("source", ""),
                "created_at": struct_data.get("created_at", ""),
                "tags": struct_data.get("tags", []),
            }

        return metadata

    def _extract_snippets(self, result: Any) -> List[str]:
        """Extrae snippets relevantes del resultado."""
        snippets = []

        if hasattr(result, "snippets"):
            for snippet in result.snippets:
                if hasattr(snippet, "snippet"):
                    snippets.append(snippet.snippet)

        return snippets
