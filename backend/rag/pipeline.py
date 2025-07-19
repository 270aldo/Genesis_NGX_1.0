"""
Pipeline RAG principal para NGX Agents.

Integra embeddings, búsqueda y generación en un flujo cohesivo
optimizado para respuestas de fitness y nutrición.
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

from .embeddings.vertex_embeddings import VertexEmbeddingsClient
from .search.vertex_search import VertexSearchClient
from .generation.flash_client import VertexFlashClient

from core.logging_config import get_logger
from infrastructure.adapters.telemetry_adapter import (
    get_telemetry_adapter,
    measure_execution_time,
)

logger = get_logger(__name__)
telemetry_adapter = get_telemetry_adapter()


class RAGPipeline:
    """
    Pipeline completo de Retrieval-Augmented Generation para NGX Agents.

    Features:
    - Búsqueda semántica con embeddings
    - Filtrado por dominio y contexto
    - Generación contextualizada
    - Personalización por usuario
    - Métricas y telemetría
    """

    def __init__(
        self,
        embeddings_client: Optional[VertexEmbeddingsClient] = None,
        search_client: Optional[VertexSearchClient] = None,
        generation_client: Optional[VertexFlashClient] = None,
        max_search_results: int = 5,
        similarity_threshold: float = 0.7,
    ):
        """
        Inicializa el pipeline RAG.

        Args:
            embeddings_client: Cliente de embeddings (se crea uno si no se proporciona)
            search_client: Cliente de búsqueda (se crea uno si no se proporciona)
            generation_client: Cliente de generación (se crea uno si no se proporciona)
            max_search_results: Número máximo de documentos a recuperar
            similarity_threshold: Umbral mínimo de similitud
        """
        self.embeddings_client = embeddings_client or VertexEmbeddingsClient()
        self.search_client = search_client or VertexSearchClient()
        self.generation_client = generation_client or VertexFlashClient()

        self.max_search_results = max_search_results
        self.similarity_threshold = similarity_threshold

        logger.info("Pipeline RAG inicializado")

    @measure_execution_time
    async def process_query(
        self,
        query: str,
        domain: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Procesa una consulta completa a través del pipeline RAG.

        Args:
            query: Consulta del usuario
            domain: Dominio específico (fitness, nutrition, wellness)
            user_context: Contexto y preferencias del usuario
            filters: Filtros adicionales para la búsqueda
            system_prompt: Prompt personalizado del sistema
            stream: Si generar respuesta en streaming

        Returns:
            Diccionario con respuesta y metadata
        """
        with telemetry_adapter.start_span("rag_pipeline_process") as span:
            span.set_attribute("query_length", len(query))
            span.set_attribute("domain", domain or "general")

            try:
                # 1. Generar embeddings de la consulta
                logger.info(f"Generando embeddings para: {query[:50]}...")
                query_embedding = await self.embeddings_client.embed_for_search(query)

                # 2. Buscar documentos relevantes
                logger.info("Realizando búsqueda semántica...")
                search_results = await self._search_documents(
                    query, query_embedding, domain, filters, user_context
                )

                span.set_attribute("documents_found", len(search_results))

                # 3. Filtrar por relevancia
                relevant_docs = self._filter_by_relevance(search_results)
                span.set_attribute("relevant_documents", len(relevant_docs))

                # 4. Generar respuesta
                logger.info("Generando respuesta con contexto...")

                if stream:
                    # Retornar generador para streaming
                    return {
                        "response_generator": self.generation_client.generate_stream(
                            query, relevant_docs, user_context, system_prompt
                        ),
                        "context_documents": relevant_docs,
                        "metadata": {
                            "total_documents": len(search_results),
                            "relevant_documents": len(relevant_docs),
                            "query_embedding_dims": len(query_embedding),
                            "timestamp": datetime.now().isoformat(),
                        },
                    }
                else:
                    response = await self.generation_client.generate_with_context(
                        query, relevant_docs, user_context, system_prompt
                    )

                    # 5. Preparar resultado completo
                    result = {
                        "response": response,
                        "context_documents": relevant_docs,
                        "metadata": {
                            "total_documents": len(search_results),
                            "relevant_documents": len(relevant_docs),
                            "query_embedding_dims": len(query_embedding),
                            "response_length": len(response),
                            "timestamp": datetime.now().isoformat(),
                        },
                    }

                    span.set_attribute("response_length", len(response))
                    logger.info("Pipeline RAG completado exitosamente")

                    return result

            except Exception as e:
                span.record_exception(e)
                logger.error(f"Error en pipeline RAG: {e}")
                raise

    async def process_multi_turn(
        self,
        messages: List[Dict[str, str]],
        domain: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Procesa una conversación multi-turno con contexto acumulativo.

        Args:
            messages: Lista de mensajes [{"role": "user/assistant", "content": "..."}]
            domain: Dominio de la conversación
            user_context: Contexto del usuario

        Returns:
            Respuesta con contexto de toda la conversación
        """
        # Construir contexto de conversación
        conversation_context = self._build_conversation_context(messages)

        # Última pregunta del usuario
        last_query = messages[-1]["content"]

        # Buscar información relevante para toda la conversación
        all_relevant_docs = []

        # Buscar para la pregunta actual
        current_results = await self.process_query(last_query, domain, user_context)
        all_relevant_docs.extend(current_results["context_documents"])

        # Buscar para preguntas anteriores importantes
        for msg in messages[-3:]:  # Últimas 3 interacciones
            if msg["role"] == "user":
                try:
                    results = await self._search_documents(
                        msg["content"], None, domain, None, user_context
                    )
                    all_relevant_docs.extend(results[:2])  # Top 2 de cada
                except Exception:
                    pass

        # Deduplicar documentos
        unique_docs = self._deduplicate_documents(all_relevant_docs)

        # Generar respuesta con contexto completo
        system_prompt = f"""Eres un asistente experto de NGX Agents.
Esta es una conversación en curso. Ten en cuenta el contexto completo de la conversación.

HISTORIAL DE CONVERSACIÓN:
{conversation_context}

Responde de manera coherente con la conversación previa."""

        response = await self.generation_client.generate_with_context(
            last_query, unique_docs, user_context, system_prompt
        )

        return {
            "response": response,
            "context_documents": unique_docs,
            "conversation_context": conversation_context,
            "metadata": {
                "turn_count": len(messages),
                "total_context_docs": len(unique_docs),
                "timestamp": datetime.now().isoformat(),
            },
        }

    async def process_by_agent(
        self, query: str, agent_type: str, user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesa una consulta optimizada para un agente específico.

        Args:
            query: Consulta del usuario
            agent_type: Tipo de agente (nutrition, training, etc.)
            user_context: Contexto del usuario

        Returns:
            Respuesta optimizada para el agente
        """
        # Mapeo de agentes a dominios y configuraciones
        agent_configs = {
            "nutrition": {
                "domain": "nutrition",
                "system_prompt": "Eres el Precision Nutrition Architect de NGX. Proporciona consejos nutricionales basados en evidencia científica.",
                "filters": {"category": ["diet", "supplements", "recipes"]},
            },
            "training": {
                "domain": "fitness",
                "system_prompt": "Eres el Elite Training Strategist de NGX. Diseña programas de entrenamiento personalizados y efectivos.",
                "filters": {"category": ["exercises", "programs", "techniques"]},
            },
            "recovery": {
                "domain": "wellness",
                "system_prompt": "Eres el Recovery Corrective de NGX. Especialízate en recuperación y prevención de lesiones.",
                "filters": {"category": ["recovery", "injury_prevention", "mobility"]},
            },
            "biohacking": {
                "domain": "wellness",
                "system_prompt": "Eres el Biohacking Innovator de NGX. Explora técnicas avanzadas de optimización del rendimiento.",
                "filters": {"category": ["biohacking", "optimization", "technology"]},
            },
        }

        config = agent_configs.get(agent_type, {})

        return await self.process_query(
            query,
            domain=config.get("domain"),
            user_context=user_context,
            filters=config.get("filters"),
            system_prompt=config.get("system_prompt"),
        )

    async def _search_documents(
        self,
        query: str,
        query_embedding: Optional[List[float]],
        domain: Optional[str],
        filters: Optional[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Realiza la búsqueda de documentos."""
        # Si hay dominio específico, usar búsqueda por dominio
        if domain:
            return await self.search_client.search_by_domain(
                query, domain, self.max_search_results
            )

        # Si hay contexto de usuario, usar búsqueda personalizada
        if user_context and "user_id" in user_context:
            return await self.search_client.search_personalized(
                query,
                user_context["user_id"],
                user_context.get("preferences", {}),
                self.max_search_results,
            )

        # Búsqueda general con filtros
        return await self.search_client.search(query, self.max_search_results, filters)

    def _filter_by_relevance(
        self, documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filtra documentos por score de relevancia."""
        return [
            doc for doc in documents if doc.get("score", 0) >= self.similarity_threshold
        ]

    def _build_conversation_context(self, messages: List[Dict[str, str]]) -> str:
        """Construye el contexto de conversación."""
        context_parts = []

        for msg in messages[:-1]:  # Excluir el último mensaje
            role = "Usuario" if msg["role"] == "user" else "Asistente"
            context_parts.append(f"{role}: {msg['content']}")

        return "\n".join(context_parts)

    def _deduplicate_documents(
        self, documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Elimina documentos duplicados manteniendo los de mayor score."""
        seen_ids = {}

        for doc in documents:
            doc_id = doc.get("id")
            if doc_id:
                if doc_id not in seen_ids or doc.get("score", 0) > seen_ids[doc_id].get(
                    "score", 0
                ):
                    seen_ids[doc_id] = doc

        return list(seen_ids.values())

    async def index_document(
        self, content: str, metadata: Dict[str, Any], document_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Indexa un nuevo documento en el sistema RAG.

        Args:
            content: Contenido del documento
            metadata: Metadata del documento (título, categoría, etc.)
            document_id: ID único del documento

        Returns:
            Información sobre el documento indexado
        """
        # Generar embeddings para el documento
        embedding = await self.embeddings_client.embed_for_storage(content)

        # Preparar documento para indexación
        document = {
            "id": document_id or f"doc_{datetime.now().timestamp()}",
            "content": content,
            "metadata": metadata,
            "embedding": embedding,
            "indexed_at": datetime.now().isoformat(),
        }

        # Aquí se integraría con Vertex AI Search para indexación
        # Por ahora retornamos la información del documento
        logger.info(f"Documento preparado para indexación: {document['id']}")

        return {
            "document_id": document["id"],
            "embedding_dims": len(embedding),
            "content_length": len(content),
            "metadata": metadata,
        }
