"""
Gestor de búsqueda de texto completo para NGX Agents.

Utiliza las capacidades de búsqueda de texto completo de PostgreSQL/Supabase
para proporcionar búsqueda rápida y eficiente en diferentes tipos de contenido.
"""

from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
import asyncio

from clients.supabase_client import supabase_client
from core.logging_config import get_logger
from core.telemetry import telemetry_manager

logger = get_logger(__name__)

# Tipos de contenido que se pueden buscar
SearchType = Literal[
    "conversations",
    "training_plans",
    "nutrition_logs",
    "progress_metrics",
    "user_notes",
    "all",
]


class SearchManager:
    """
    Gestor centralizado para búsquedas de texto completo en NGX Agents.

    Proporciona búsqueda unificada en diferentes tipos de contenido
    almacenados en Supabase.
    """

    def __init__(self):
        """Inicializa el gestor de búsqueda."""
        self.client = supabase_client
        self._initialized = False

        # Configuración de búsqueda por tipo
        self.search_configs = {
            "conversations": {
                "table": "conversations",
                "search_columns": ["user_message", "agent_response"],
                "return_columns": [
                    "id",
                    "user_message",
                    "agent_response",
                    "agent_name",
                    "created_at",
                ],
                "order_by": "created_at",
                "order_desc": True,
            },
            "training_plans": {
                "table": "training_plans",
                "search_columns": ["name", "description", "exercises"],
                "return_columns": [
                    "id",
                    "name",
                    "description",
                    "difficulty",
                    "duration_weeks",
                    "created_at",
                ],
                "order_by": "created_at",
                "order_desc": True,
            },
            "nutrition_logs": {
                "table": "nutrition_logs",
                "search_columns": ["meal_name", "foods", "notes"],
                "return_columns": [
                    "id",
                    "meal_name",
                    "meal_type",
                    "calories",
                    "protein",
                    "carbs",
                    "fats",
                    "logged_at",
                ],
                "order_by": "logged_at",
                "order_desc": True,
            },
            "progress_metrics": {
                "table": "progress_metrics",
                "search_columns": ["metric_name", "notes"],
                "return_columns": [
                    "id",
                    "metric_name",
                    "value",
                    "unit",
                    "category",
                    "recorded_at",
                ],
                "order_by": "recorded_at",
                "order_desc": True,
            },
            "user_notes": {
                "table": "user_notes",
                "search_columns": ["title", "content", "tags"],
                "return_columns": [
                    "id",
                    "title",
                    "content",
                    "category",
                    "tags",
                    "created_at",
                ],
                "order_by": "created_at",
                "order_desc": True,
            },
        }

        # Estadísticas
        self.stats = {
            "searches_performed": 0,
            "results_returned": 0,
            "errors": 0,
            "search_types": {},
        }

    async def initialize(self):
        """
        Inicializa el gestor de búsqueda y verifica las tablas.

        Este método debe ser llamado antes de realizar búsquedas.
        """
        if self._initialized:
            return

        try:
            # Verificar conexión con Supabase
            await self.client.initialize()

            # Aquí podrías verificar que las tablas existen y tienen
            # los índices de búsqueda apropiados

            self._initialized = True
            logger.info("SearchManager inicializado correctamente")

        except Exception as e:
            logger.error(f"Error al inicializar SearchManager: {e}")
            raise

    async def search(
        self,
        query: str,
        search_type: SearchType = "all",
        user_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Realiza una búsqueda de texto completo.

        Args:
            query: Texto a buscar
            search_type: Tipo de contenido a buscar
            user_id: ID del usuario (para filtrar resultados)
            limit: Número máximo de resultados
            offset: Desplazamiento para paginación
            filters: Filtros adicionales

        Returns:
            Diccionario con resultados y metadatos
        """
        # Iniciar telemetría
        span_id = telemetry_manager.start_span(
            name="search_text",
            attributes={
                "query_length": len(query),
                "search_type": search_type,
                "limit": limit,
            },
        )

        try:
            # Asegurar inicialización
            if not self._initialized:
                await self.initialize()

            # Actualizar estadísticas
            self.stats["searches_performed"] += 1
            if search_type not in self.stats["search_types"]:
                self.stats["search_types"][search_type] = 0
            self.stats["search_types"][search_type] += 1

            # Sanitizar query
            sanitized_query = self._sanitize_query(query)

            # Realizar búsqueda según el tipo
            if search_type == "all":
                results = await self._search_all_types(
                    sanitized_query, user_id, limit, offset, filters
                )
            else:
                results = await self._search_single_type(
                    sanitized_query, search_type, user_id, limit, offset, filters
                )

            # Actualizar estadísticas
            total_results = sum(len(r["results"]) for r in results)
            self.stats["results_returned"] += total_results

            # Preparar respuesta
            response = {
                "query": query,
                "search_type": search_type,
                "results": results,
                "total_results": total_results,
                "limit": limit,
                "offset": offset,
                "timestamp": datetime.now().isoformat(),
            }

            telemetry_manager.set_span_attribute(
                span_id, "total_results", total_results
            )
            return response

        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            self.stats["errors"] += 1
            telemetry_manager.set_span_attribute(span_id, "error", str(e))
            raise

        finally:
            telemetry_manager.end_span(span_id)

    async def _search_single_type(
        self,
        query: str,
        search_type: SearchType,
        user_id: Optional[str],
        limit: int,
        offset: int,
        filters: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Busca en un tipo específico de contenido."""
        config = self.search_configs.get(search_type)
        if not config:
            raise ValueError(f"Tipo de búsqueda no válido: {search_type}")

        try:
            # Construir consulta base
            query_builder = self.client.client.table(config["table"]).select(
                ", ".join(config["return_columns"])
            )

            # Aplicar búsqueda de texto
            # Usando el operador 'ilike' para búsqueda insensible a mayúsculas
            # En producción, podrías configurar búsqueda de texto completo con to_tsquery
            search_conditions = []
            for column in config["search_columns"]:
                search_conditions.append(f"{column}.ilike.%{query}%")

            # Combinar condiciones con OR
            if search_conditions:
                query_builder = query_builder.or_(",".join(search_conditions))

            # Filtrar por usuario si se proporciona
            if user_id:
                query_builder = query_builder.eq("user_id", user_id)

            # Aplicar filtros adicionales
            if filters:
                for key, value in filters.items():
                    query_builder = query_builder.eq(key, value)

            # Aplicar orden
            query_builder = query_builder.order(
                config["order_by"], desc=config.get("order_desc", True)
            )

            # Aplicar límite y offset
            query_builder = query_builder.limit(limit).offset(offset)

            # Ejecutar consulta
            response = await asyncio.get_event_loop().run_in_executor(
                None, query_builder.execute
            )

            return [{"type": search_type, "results": response.data or []}]

        except Exception as e:
            logger.error(f"Error buscando en {search_type}: {e}")
            return [{"type": search_type, "results": [], "error": str(e)}]

    async def _search_all_types(
        self,
        query: str,
        user_id: Optional[str],
        limit: int,
        offset: int,
        filters: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Busca en todos los tipos de contenido."""
        # Limitar resultados por tipo cuando se busca en todos
        limit_per_type = max(5, limit // len(self.search_configs))

        # Crear tareas de búsqueda paralelas
        tasks = []
        for search_type in self.search_configs.keys():
            task = self._search_single_type(
                query, search_type, user_id, limit_per_type, 0, filters
            )
            tasks.append(task)

        # Ejecutar búsquedas en paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filtrar errores y aplanar resultados
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error en búsqueda paralela: {result}")
            else:
                valid_results.extend(result)

        return valid_results

    def _sanitize_query(self, query: str) -> str:
        """
        Sanitiza la consulta de búsqueda.

        Args:
            query: Consulta original

        Returns:
            Consulta sanitizada
        """
        # Eliminar caracteres especiales que podrían causar problemas
        # En PostgreSQL, algunos caracteres tienen significado especial
        special_chars = ["'", '"', "\\", "%", "_", "[", "]", "^", "$"]

        sanitized = query
        for char in special_chars:
            sanitized = sanitized.replace(char, f"\\{char}")

        # Limitar longitud
        max_length = 200
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized.strip()

    async def create_search_indexes(self):
        """
        Crea índices de búsqueda en las tablas de Supabase.

        Este método debe ejecutarse una vez durante la configuración inicial.
        """
        # SQL para crear índices de búsqueda de texto completo
        index_queries = [
            """
            -- Índice para búsqueda en conversaciones
            CREATE INDEX IF NOT EXISTS idx_conversations_search 
            ON conversations 
            USING gin(to_tsvector('english', user_message || ' ' || agent_response));
            """,
            """
            -- Índice para búsqueda en planes de entrenamiento
            CREATE INDEX IF NOT EXISTS idx_training_plans_search 
            ON training_plans 
            USING gin(to_tsvector('english', name || ' ' || description || ' ' || exercises));
            """,
            """
            -- Índice para búsqueda en registros de nutrición
            CREATE INDEX IF NOT EXISTS idx_nutrition_logs_search 
            ON nutrition_logs 
            USING gin(to_tsvector('english', meal_name || ' ' || foods || ' ' || notes));
            """,
            """
            -- Índice para búsqueda en métricas de progreso
            CREATE INDEX IF NOT EXISTS idx_progress_metrics_search 
            ON progress_metrics 
            USING gin(to_tsvector('english', metric_name || ' ' || notes));
            """,
            """
            -- Índice para búsqueda en notas de usuario
            CREATE INDEX IF NOT EXISTS idx_user_notes_search 
            ON user_notes 
            USING gin(to_tsvector('english', title || ' ' || content || ' ' || tags));
            """,
        ]

        # Nota: Estos índices deberían crearse mediante migraciones de base de datos
        # o directamente en Supabase Dashboard
        logger.info("Índices de búsqueda SQL generados. Ejecutar en Supabase.")

        return index_queries

    async def get_search_suggestions(
        self,
        partial_query: str,
        search_type: SearchType = "all",
        user_id: Optional[str] = None,
        limit: int = 5,
    ) -> List[str]:
        """
        Obtiene sugerencias de búsqueda basadas en una consulta parcial.

        Args:
            partial_query: Texto parcial
            search_type: Tipo de contenido
            user_id: ID del usuario
            limit: Número máximo de sugerencias

        Returns:
            Lista de sugerencias
        """
        # Implementación simplificada
        # En producción, podrías usar un índice especializado para autocompletado

        results = await self.search(
            query=partial_query,
            search_type=search_type,
            user_id=user_id,
            limit=limit * 2,  # Obtener más resultados para extraer sugerencias
        )

        suggestions = set()

        # Extraer términos relevantes de los resultados
        for result_group in results["results"]:
            for item in result_group.get("results", []):
                # Extraer texto según el tipo
                if result_group["type"] == "conversations":
                    text = f"{item.get('user_message', '')} {item.get('agent_response', '')}"
                elif result_group["type"] == "training_plans":
                    text = f"{item.get('name', '')} {item.get('description', '')}"
                else:
                    # Genérico para otros tipos
                    text = " ".join(str(v) for v in item.values() if isinstance(v, str))

                # Extraer palabras que coincidan con la consulta parcial
                words = text.lower().split()
                for word in words:
                    if word.startswith(partial_query.lower()) and len(word) > len(
                        partial_query
                    ):
                        suggestions.add(word)

                if len(suggestions) >= limit:
                    break

        return list(suggestions)[:limit]

    async def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del gestor de búsqueda.

        Returns:
            Diccionario con estadísticas
        """
        return {
            "stats": self.stats.copy(),
            "search_types_available": list(self.search_configs.keys()),
            "initialized": self._initialized,
            "timestamp": datetime.now().isoformat(),
        }


# Instancia global del gestor de búsqueda
search_manager = SearchManager()
