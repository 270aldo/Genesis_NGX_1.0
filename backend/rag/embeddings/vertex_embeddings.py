"""
Vertex AI Embeddings Client optimizado para text-embedding-large-exp-03-07.

Este cliente proporciona una interfaz eficiente para generar embeddings
usando el modelo experimental más reciente de Google con 1536 dimensiones.
"""

import asyncio
import hashlib
import json
import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta

from vertexai.language_models import TextEmbeddingModel
import vertexai
from google.cloud import aiplatform

from core.logging_config import get_logger
from core.circuit_breaker import circuit_breaker
from infrastructure.adapters.telemetry_adapter import (
    get_telemetry_adapter,
    measure_execution_time,
)

logger = get_logger(__name__)
telemetry_adapter = get_telemetry_adapter()


class VertexEmbeddingsClient:
    """
    Cliente optimizado para generar embeddings con text-embedding-large-exp-03-07.

    Features:
    - Modelo experimental con 1536 dimensiones
    - Batch processing para eficiencia
    - Caché inteligente para reducir costos
    - Circuit breaker para resiliencia
    - Telemetría detallada
    """

    # Configuración del modelo experimental
    MODEL_NAME = "text-embedding-large-exp-03-07"
    EMBEDDING_DIMENSIONS = 3072
    MAX_BATCH_SIZE = 250  # Límite recomendado para batch
    MAX_TEXT_LENGTH = 3072  # Límite de caracteres por texto

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        cache_ttl: int = 86400,  # 24 horas por defecto
        enable_cache: bool = True,
    ):
        """
        Inicializa el cliente de embeddings.

        Args:
            project_id: ID del proyecto de GCP
            location: Ubicación de Vertex AI
            cache_ttl: Tiempo de vida del caché en segundos
            enable_cache: Habilitar caché de embeddings
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.location = location
        self.cache_ttl = cache_ttl
        self.enable_cache = enable_cache
        self._cache: Dict[str, Dict[str, Any]] = {}

        # Inicializar Vertex AI
        vertexai.init(project=self.project_id, location=self.location)

        # Cargar el modelo
        self._initialize_model()

        logger.info(
            f"Cliente de embeddings inicializado con modelo {self.MODEL_NAME} "
            f"({self.EMBEDDING_DIMENSIONS} dimensiones)"
        )

    def _initialize_model(self):
        """Inicializa el modelo de embeddings."""
        try:
            self.model = TextEmbeddingModel.from_pretrained(self.MODEL_NAME)
            logger.info(f"Modelo {self.MODEL_NAME} cargado exitosamente")
        except Exception as e:
            logger.error(f"Error al cargar el modelo: {e}")
            raise

    def _get_cache_key(self, text: str) -> str:
        """Genera una clave de caché única para el texto."""
        return hashlib.sha256(f"{self.MODEL_NAME}:{text}".encode()).hexdigest()

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Verifica si una entrada de caché sigue siendo válida."""
        if not self.enable_cache:
            return False

        expiry_time = datetime.fromisoformat(cache_entry["timestamp"]) + timedelta(
            seconds=self.cache_ttl
        )
        return datetime.now() < expiry_time

    @measure_execution_time
    @circuit_breaker
    async def embed_text(
        self, text: str, task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> List[float]:
        """
        Genera embeddings para un texto individual.

        Args:
            text: Texto a procesar
            task_type: Tipo de tarea (RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY, etc.)

        Returns:
            Vector de embeddings de 1536 dimensiones
        """
        # Verificar caché
        cache_key = self._get_cache_key(text)
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.debug(
                    f"Embedding recuperado del caché para texto de {len(text)} caracteres"
                )
                return cache_entry["embedding"]

        # Validar longitud del texto
        if len(text) > self.MAX_TEXT_LENGTH:
            logger.warning(
                f"Texto truncado de {len(text)} a {self.MAX_TEXT_LENGTH} caracteres"
            )
            text = text[: self.MAX_TEXT_LENGTH]

        # Generar embedding
        with telemetry_adapter.start_span("vertex_ai_embed_text") as span:
            span.set_attribute("model", self.MODEL_NAME)
            span.set_attribute("text_length", len(text))
            span.set_attribute("task_type", task_type)

            try:
                embeddings = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.model.get_embeddings([text], task_type=task_type)
                )

                embedding = embeddings[0].values

                # Guardar en caché
                if self.enable_cache:
                    self._cache[cache_key] = {
                        "embedding": embedding,
                        "timestamp": datetime.now().isoformat(),
                    }

                span.set_attribute("embedding_dimensions", len(embedding))
                logger.info(
                    f"Embedding generado exitosamente: {len(embedding)} dimensiones"
                )

                return embedding

            except Exception as e:
                span.record_exception(e)
                logger.error(f"Error al generar embedding: {e}")
                raise

    @measure_execution_time
    @circuit_breaker
    async def embed_batch(
        self,
        texts: List[str],
        task_type: str = "RETRIEVAL_DOCUMENT",
        show_progress: bool = True,
    ) -> List[List[float]]:
        """
        Genera embeddings para un batch de textos.

        Args:
            texts: Lista de textos a procesar
            task_type: Tipo de tarea
            show_progress: Mostrar progreso del procesamiento

        Returns:
            Lista de vectores de embeddings
        """
        if not texts:
            return []

        # Dividir en sub-batches si es necesario
        embeddings = []

        for i in range(0, len(texts), self.MAX_BATCH_SIZE):
            batch = texts[i : i + self.MAX_BATCH_SIZE]

            if show_progress:
                logger.info(
                    f"Procesando batch {i//self.MAX_BATCH_SIZE + 1}/{(len(texts)-1)//self.MAX_BATCH_SIZE + 1}"
                )

            # Verificar caché para cada texto
            batch_embeddings = []
            texts_to_process = []
            cache_indices = []

            for idx, text in enumerate(batch):
                cache_key = self._get_cache_key(text)
                if cache_key in self._cache and self._is_cache_valid(
                    self._cache[cache_key]
                ):
                    batch_embeddings.append(self._cache[cache_key]["embedding"])
                else:
                    texts_to_process.append(text[: self.MAX_TEXT_LENGTH])
                    cache_indices.append(idx)

            # Procesar textos no cacheados
            if texts_to_process:
                with telemetry_adapter.start_span("vertex_ai_embed_batch") as span:
                    span.set_attribute("model", self.MODEL_NAME)
                    span.set_attribute("batch_size", len(texts_to_process))
                    span.set_attribute("task_type", task_type)

                    try:
                        new_embeddings = await asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda: self.model.get_embeddings(
                                texts_to_process, task_type=task_type
                            ),
                        )

                        # Insertar embeddings nuevos en las posiciones correctas
                        new_idx = 0
                        for idx in range(len(batch)):
                            if idx in cache_indices:
                                embedding = new_embeddings[new_idx].values
                                batch_embeddings.insert(idx, embedding)

                                # Guardar en caché
                                if self.enable_cache:
                                    cache_key = self._get_cache_key(batch[idx])
                                    self._cache[cache_key] = {
                                        "embedding": embedding,
                                        "timestamp": datetime.now().isoformat(),
                                    }

                                new_idx += 1

                        span.set_attribute("embeddings_generated", len(new_embeddings))

                    except Exception as e:
                        span.record_exception(e)
                        logger.error(f"Error al generar embeddings del batch: {e}")
                        raise

            embeddings.extend(batch_embeddings)

        logger.info(f"Batch procesado: {len(embeddings)} embeddings generados")
        return embeddings

    async def embed_for_search(self, query: str) -> List[float]:
        """
        Genera embeddings optimizados para búsqueda.

        Args:
            query: Consulta de búsqueda

        Returns:
            Vector de embeddings optimizado para búsqueda
        """
        return await self.embed_text(query, task_type="RETRIEVAL_QUERY")

    async def embed_for_storage(self, document: str) -> List[float]:
        """
        Genera embeddings optimizados para almacenamiento.

        Args:
            document: Documento a almacenar

        Returns:
            Vector de embeddings optimizado para almacenamiento
        """
        return await self.embed_text(document, task_type="RETRIEVAL_DOCUMENT")

    def clear_cache(self):
        """Limpia el caché de embeddings."""
        self._cache.clear()
        logger.info("Caché de embeddings limpiado")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché."""
        valid_entries = sum(
            1 for entry in self._cache.values() if self._is_cache_valid(entry)
        )

        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self._cache) - valid_entries,
            "cache_size_mb": sum(len(str(entry)) for entry in self._cache.values())
            / (1024 * 1024),
        }
