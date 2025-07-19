"""
Base class para agentes con capacidades RAG integradas.

Extiende BaseAgent para incluir funcionalidades de Retrieval-Augmented Generation.
"""

from typing import Dict, Any, Optional, List
import asyncio

from agents.base.base_agent import BaseAgent
from rag.pipeline import RAGPipeline
from core.logging_config import get_logger

logger = get_logger(__name__)


class RAGAgent(BaseAgent):
    """
    Agente base con capacidades RAG integradas.

    Proporciona:
    - Búsqueda semántica en knowledge base
    - Generación aumentada con contexto
    - Personalización basada en usuario
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        capabilities: List[str],
        domain: str,
        enable_rag: bool = True,
        rag_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Inicializa un agente con capacidades RAG.

        Args:
            agent_id: ID único del agente
            name: Nombre del agente
            description: Descripción del agente
            capabilities: Lista de capacidades
            domain: Dominio del agente (fitness, nutrition, wellness)
            enable_rag: Habilitar capacidades RAG
            rag_config: Configuración personalizada para RAG
        """
        super().__init__(agent_id, name, description, capabilities)

        self.domain = domain
        self.enable_rag = enable_rag
        self.rag_config = rag_config or {}

        # Inicializar pipeline RAG si está habilitado
        if self.enable_rag:
            self.rag_pipeline = RAGPipeline(
                max_search_results=self.rag_config.get("max_results", 5),
                similarity_threshold=self.rag_config.get("threshold", 0.7),
            )
            logger.info(f"RAG habilitado para agente {name} en dominio {domain}")

    async def _run_async_impl(self, task_input: str, context: Dict[str, Any]) -> Any:
        """
        Implementación del procesamiento con RAG.

        Args:
            task_input: Entrada de la tarea
            context: Contexto de ejecución

        Returns:
            Respuesta del agente
        """
        # Extraer contexto del usuario si existe
        user_context = context.get("user_context", {})

        # Verificar si usar RAG
        use_rag = self.enable_rag and context.get("use_rag", True)

        if use_rag:
            logger.info(f"Procesando con RAG en dominio {self.domain}")

            # Procesar con pipeline RAG
            rag_result = await self.rag_pipeline.process_query(
                query=task_input,
                domain=self.domain,
                user_context=user_context,
                system_prompt=self._get_system_prompt(),
            )

            # Extraer respuesta y metadata
            response = rag_result["response"]
            context["rag_metadata"] = rag_result["metadata"]
            context["context_documents"] = rag_result["context_documents"]

            # Post-procesar si es necesario
            response = await self._post_process_response(response, context)

            return response
        else:
            # Procesamiento sin RAG (fallback al comportamiento original)
            logger.info("Procesando sin RAG")
            return await self._process_without_rag(task_input, context)

    def _get_system_prompt(self) -> str:
        """
        Obtiene el prompt del sistema para este agente.

        Returns:
            Prompt personalizado del sistema
        """
        return f"""Eres {self.name}, un agente especializado de NGX Agents.
{self.description}

Tus capacidades incluyen:
{chr(10).join(f'- {cap}' for cap in self.capabilities)}

Proporciona respuestas precisas, personalizadas y basadas en evidencia científica."""

    async def _post_process_response(
        self, response: str, context: Dict[str, Any]
    ) -> str:
        """
        Post-procesa la respuesta del RAG si es necesario.

        Args:
            response: Respuesta generada
            context: Contexto con metadata

        Returns:
            Respuesta procesada
        """
        # Las clases hijas pueden sobrescribir este método
        return response

    async def _process_without_rag(
        self, task_input: str, context: Dict[str, Any]
    ) -> Any:
        """
        Procesamiento sin RAG - fallback al comportamiento estándar del agente.

        Args:
            task_input: Entrada de la tarea
            context: Contexto de ejecución

        Returns:
            Respuesta del agente
        """
        logger.info(f"Procesamiento sin RAG para agente {self.agent_id}")

        # Extraer información del contexto
        user_id = context.get("user_id")
        session_id = context.get("session_id")

        # Usar el método estándar de procesamiento del agente padre
        result = await super()._run_async_impl(
            task_input, user_id, session_id, **context
        )

        return result

    async def search_knowledge_base(
        self, query: str, max_results: int = 5, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca directamente en la knowledge base.

        Args:
            query: Consulta de búsqueda
            max_results: Número máximo de resultados
            filters: Filtros adicionales

        Returns:
            Lista de documentos encontrados
        """
        if not self.enable_rag:
            logger.warning("RAG no está habilitado para este agente")
            return []

        return await self.rag_pipeline.search_client.search_by_domain(
            query, self.domain, max_results
        )

    async def generate_with_custom_context(
        self,
        query: str,
        custom_documents: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Genera una respuesta con documentos personalizados.

        Args:
            query: Consulta del usuario
            custom_documents: Documentos específicos para usar como contexto
            user_context: Contexto del usuario

        Returns:
            Respuesta generada
        """
        if not self.enable_rag:
            logger.warning("RAG no está habilitado para este agente")
            return "RAG no está disponible para este agente"

        return await self.rag_pipeline.generation_client.generate_with_context(
            query, custom_documents, user_context, self._get_system_prompt()
        )
