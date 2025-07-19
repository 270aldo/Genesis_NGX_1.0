"""
Cliente de Vertex AI Gemini 2.0 Flash para generación en RAG.

Proporciona generación de respuestas optimizada usando Gemini 2.0 Flash
con soporte para contexto enriquecido y streaming.
"""

import os
from typing import List, Dict, Any, Optional, AsyncGenerator
import json

from vertexai.generative_models import GenerativeModel, GenerationConfig, Part
import vertexai

from core.logging_config import get_logger
from core.circuit_breaker import circuit_breaker
from infrastructure.adapters.telemetry_adapter import (
    get_telemetry_adapter,
    measure_execution_time,
)

logger = get_logger(__name__)
telemetry_adapter = get_telemetry_adapter()


class VertexFlashClient:
    """
    Cliente optimizado para Gemini 2.0 Flash con capacidades RAG.

    Features:
    - Generación contextual con documentos recuperados
    - Streaming de respuestas
    - Prompt engineering avanzado
    - Control fino de parámetros
    """

    MODEL_NAME = "gemini-2.0-flash-exp"

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        temperature: float = 0.3,
        max_output_tokens: int = 8192,
        top_p: float = 0.8,
        top_k: int = 40,
    ):
        """
        Inicializa el cliente de Gemini 2.0 Flash.

        Args:
            project_id: ID del proyecto de GCP
            location: Ubicación de Vertex AI
            temperature: Control de creatividad (0-1)
            max_output_tokens: Máximo de tokens en la respuesta
            top_p: Nucleus sampling
            top_k: Top-k sampling
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.location = location

        # Configuración de generación
        self.generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
            top_k=top_k,
            candidate_count=1,
        )

        # Inicializar Vertex AI
        vertexai.init(project=self.project_id, location=self.location)

        # Cargar el modelo
        self._initialize_model()

        logger.info(f"Cliente Flash inicializado con modelo {self.MODEL_NAME}")

    def _initialize_model(self):
        """Inicializa el modelo generativo."""
        try:
            self.model = GenerativeModel(self.MODEL_NAME)
            logger.info(f"Modelo {self.MODEL_NAME} cargado exitosamente")
        except Exception as e:
            logger.error(f"Error al cargar el modelo: {e}")
            raise

    @measure_execution_time
    @circuit_breaker
    async def generate_with_context(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Genera una respuesta usando documentos de contexto recuperados.

        Args:
            query: Consulta del usuario
            context_documents: Documentos recuperados por búsqueda
            user_context: Contexto adicional del usuario
            system_prompt: Prompt del sistema personalizado

        Returns:
            Respuesta generada
        """
        with telemetry_adapter.start_span("vertex_ai_generate_rag") as span:
            span.set_attribute("model", self.MODEL_NAME)
            span.set_attribute("context_docs_count", len(context_documents))

            try:
                # Construir el prompt con contexto
                prompt = self._build_rag_prompt(
                    query, context_documents, user_context, system_prompt
                )

                # Generar respuesta
                response = await self._generate(prompt)

                span.set_attribute("response_length", len(response))
                logger.info(f"Respuesta generada: {len(response)} caracteres")

                return response

            except Exception as e:
                span.record_exception(e)
                logger.error(f"Error en generación RAG: {e}")
                raise

    @measure_execution_time
    @circuit_breaker
    async def generate_stream(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Genera una respuesta en streaming.

        Args:
            query: Consulta del usuario
            context_documents: Documentos recuperados
            user_context: Contexto del usuario
            system_prompt: Prompt del sistema

        Yields:
            Chunks de la respuesta
        """
        with telemetry_adapter.start_span("vertex_ai_generate_stream") as span:
            span.set_attribute("model", self.MODEL_NAME)

            try:
                # Construir el prompt
                prompt = self._build_rag_prompt(
                    query, context_documents, user_context, system_prompt
                )

                # Generar respuesta en streaming
                response_stream = self.model.generate_content(
                    prompt, generation_config=self.generation_config, stream=True
                )

                total_chars = 0
                for chunk in response_stream:
                    if chunk.text:
                        total_chars += len(chunk.text)
                        yield chunk.text

                span.set_attribute("total_chars_streamed", total_chars)

            except Exception as e:
                span.record_exception(e)
                logger.error(f"Error en streaming: {e}")
                raise

    def _build_rag_prompt(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Construye un prompt optimizado para RAG.

        Args:
            query: Consulta del usuario
            context_documents: Documentos de contexto
            user_context: Información del usuario
            system_prompt: Instrucciones del sistema

        Returns:
            Prompt completo para el modelo
        """
        # System prompt por defecto para NGX
        if not system_prompt:
            system_prompt = """Eres un experto asistente de fitness y nutrición de NGX Agents. 
Tu objetivo es proporcionar respuestas precisas, personalizadas y basadas en evidencia científica.

Utiliza la información proporcionada en el contexto para fundamentar tus respuestas.
Si la información no está en el contexto, indícalo claramente.
Mantén un tono profesional pero amigable."""

        # Formatear documentos de contexto
        context_text = self._format_context_documents(context_documents)

        # Información del usuario si está disponible
        user_info = ""
        if user_context:
            user_info = self._format_user_context(user_context)

        # Construir prompt completo
        prompt = f"""{system_prompt}

{user_info}

CONTEXTO RELEVANTE:
{context_text}

PREGUNTA DEL USUARIO:
{query}

RESPUESTA:"""

        return prompt

    def _format_context_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Formatea los documentos de contexto para el prompt."""
        if not documents:
            return "No se encontró información relevante en la base de conocimiento."

        formatted_docs = []
        for i, doc in enumerate(documents, 1):
            formatted_doc = f"[Documento {i}]"

            # Título/metadata
            metadata = doc.get("metadata", {})
            if metadata.get("title"):
                formatted_doc += f"\nTítulo: {metadata['title']}"
            if metadata.get("domain"):
                formatted_doc += f"\nDominio: {metadata['domain']}"
            if metadata.get("category"):
                formatted_doc += f"\nCategoría: {metadata['category']}"

            # Contenido
            content = doc.get("content", "")
            formatted_doc += f"\nContenido: {content}"

            # Score de relevancia
            if "score" in doc:
                formatted_doc += f"\nRelevancia: {doc['score']:.2f}"

            formatted_docs.append(formatted_doc)

        return "\n\n".join(formatted_docs)

    def _format_user_context(self, user_context: Dict[str, Any]) -> str:
        """Formatea el contexto del usuario para el prompt."""
        user_info_parts = ["INFORMACIÓN DEL USUARIO:"]

        if "fitness_level" in user_context:
            user_info_parts.append(
                f"- Nivel de fitness: {user_context['fitness_level']}"
            )

        if "goals" in user_context:
            goals = ", ".join(user_context["goals"])
            user_info_parts.append(f"- Objetivos: {goals}")

        if "restrictions" in user_context:
            restrictions = ", ".join(user_context["restrictions"])
            user_info_parts.append(f"- Restricciones: {restrictions}")

        if "preferences" in user_context:
            user_info_parts.append(
                f"- Preferencias: {json.dumps(user_context['preferences'], ensure_ascii=False)}"
            )

        return "\n".join(user_info_parts)

    async def _generate(self, prompt: str) -> str:
        """Genera una respuesta completa."""
        response = self.model.generate_content(
            prompt, generation_config=self.generation_config
        )

        return response.text

    async def generate_structured(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        output_schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Genera una respuesta estructurada siguiendo un esquema.

        Args:
            query: Consulta del usuario
            context_documents: Documentos de contexto
            output_schema: Esquema de salida esperado

        Returns:
            Respuesta estructurada como diccionario
        """
        # Añadir instrucciones para output estructurado
        system_prompt = f"""Eres un asistente experto de NGX Agents.
Debes responder en formato JSON siguiendo exactamente este esquema:
{json.dumps(output_schema, indent=2, ensure_ascii=False)}

Asegúrate de que tu respuesta sea válida JSON."""

        response = await self.generate_with_context(
            query, context_documents, system_prompt=system_prompt
        )

        # Parsear la respuesta JSON
        try:
            # Extraer JSON de la respuesta
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_str = response[json_start:json_end]

            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error parseando respuesta estructurada: {e}")
            # Retornar respuesta como texto si falla el parsing
            return {"response": response, "error": "Failed to parse structured output"}

    def update_generation_config(self, **kwargs):
        """Actualiza la configuración de generación."""
        for key, value in kwargs.items():
            if hasattr(self.generation_config, key):
                setattr(self.generation_config, key, value)

        logger.info(f"Configuración de generación actualizada: {kwargs}")
