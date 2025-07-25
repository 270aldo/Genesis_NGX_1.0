"""
Módulo de gestión de embeddings para contexto.

Este módulo proporciona funcionalidades para generar, almacenar y buscar
embeddings vectoriales, permitiendo búsquedas semánticas y recuperación
de contexto relevante basado en similitud.
"""

import hashlib
import time
import numpy as np
from datetime import datetime
from typing import Any, Dict, List, Optional

from clients.vertex_ai import vertex_ai_client
from clients.gcs_client import gcs_client
from clients.vertex_ai.vector_search_client import vector_search_client
from core.logging_config import get_logger
from core.telemetry import telemetry_manager
import json

# Configurar logger
logger = get_logger(__name__)


class EmbeddingsManager:
    """
    Gestor de embeddings para búsqueda semántica y recuperación de contexto.

    Proporciona métodos para generar, almacenar y buscar embeddings vectoriales,
    permitiendo recuperar contexto relevante basado en similitud semántica.
    """

    def __init__(
        self,
        cache_enabled: bool = True,
        cache_ttl: int = 86400,  # 24 horas
        vector_dimension: int = 3072,  # Actualizado para text-embedding-large-exp-03-07
        similarity_threshold: float = 0.7,
        use_gcs: bool = True,
        gcs_prefix: str = "embeddings/",
        use_vector_search: bool = True,
    ):
        """
        Inicializa el gestor de embeddings.

        Args:
            cache_enabled: Habilitar caché de embeddings
            cache_ttl: Tiempo de vida del caché en segundos
            vector_dimension: Dimensión de los vectores de embedding
            similarity_threshold: Umbral de similitud para considerar relevante
        """
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.vector_dimension = vector_dimension
        self.similarity_threshold = similarity_threshold
        self.use_gcs = use_gcs
        self.gcs_prefix = gcs_prefix
        self.use_vector_search = use_vector_search

        # Almacenamiento de embeddings (en memoria como caché)
        self.embeddings_store = {}

        # Flags de inicialización
        self._gcs_initialized = False
        self._vector_search_initialized = False

        # Caché de textos a embeddings
        self.text_to_embedding_cache = {}

        # Estadísticas
        self.stats = {
            "embedding_requests": 0,
            "batch_embedding_requests": 0,
            "similarity_searches": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
        }

        logger.info("Gestor de embeddings inicializado")

    async def _ensure_gcs_initialized(self) -> None:
        """Asegura que el cliente GCS esté inicializado."""
        if self.use_gcs and not self._gcs_initialized:
            try:
                await gcs_client.initialize()
                self._gcs_initialized = True
                logger.info("Cliente GCS inicializado para embeddings")
                # Opcionalmente, cargar embeddings existentes desde GCS
                # await self._load_embeddings_from_gcs()
            except Exception as e:
                logger.error(f"Error al inicializar GCS: {e}")
                self.use_gcs = False  # Fallback a memoria local

    async def _ensure_vector_search_initialized(self) -> None:
        """Asegura que el cliente Vector Search esté inicializado."""
        if self.use_vector_search and not self._vector_search_initialized:
            try:
                await vector_search_client.initialize()
                self._vector_search_initialized = True
                logger.info("Cliente Vector Search inicializado para embeddings")
            except Exception as e:
                logger.error(f"Error al inicializar Vector Search: {e}")
                self.use_vector_search = False  # Fallback a búsqueda local

    async def _load_embeddings_from_gcs(self, limit: int = 100) -> None:
        """
        Carga embeddings desde GCS a memoria.

        Args:
            limit: Número máximo de embeddings a cargar (para evitar sobrecarga de memoria)
        """
        if not self._gcs_initialized:
            return

        try:
            # Listar archivos de embeddings en GCS
            files = await gcs_client.list_files(prefix=self.gcs_prefix)

            # Cargar hasta 'limit' embeddings
            loaded = 0
            for file_info in files[:limit]:
                if loaded >= limit:
                    break

                try:
                    # Extraer key del nombre del archivo
                    blob_name = file_info["name"]
                    if blob_name.startswith(self.gcs_prefix) and blob_name.endswith(
                        ".json"
                    ):
                        key = blob_name[
                            len(self.gcs_prefix) : -5
                        ]  # Remover prefijo y .json

                        # Descargar y parsear
                        content = await gcs_client.download_file(blob_name)
                        embedding_data = json.loads(content.decode("utf-8"))

                        # Almacenar en memoria
                        self.embeddings_store[key] = embedding_data
                        loaded += 1

                except Exception as e:
                    logger.error(f"Error al cargar embedding {file_info['name']}: {e}")

            logger.info(f"Cargados {loaded} embeddings desde GCS")

        except Exception as e:
            logger.error(f"Error al listar embeddings en GCS: {e}")

    def _get_cache_key(self, text: str) -> str:
        """
        Genera una clave de caché para un texto.

        Args:
            text: Texto para generar la clave

        Returns:
            str: Clave de caché
        """
        return hashlib.md5(text.encode()).hexdigest()

    def _clean_cache_if_needed(self) -> None:
        """Limpia la caché si hay demasiadas entradas."""
        max_cache_size = 10000

        if len(self.text_to_embedding_cache) > max_cache_size:
            # Ordenar por timestamp y eliminar los más antiguos
            sorted_items = sorted(
                self.text_to_embedding_cache.items(), key=lambda x: x[1]["timestamp"]
            )

            # Eliminar el 20% más antiguo
            items_to_remove = int(max_cache_size * 0.2)
            for i in range(items_to_remove):
                if i < len(sorted_items):
                    del self.text_to_embedding_cache[sorted_items[i][0]]

    def _calculate_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        Calcula la similitud coseno entre dos embeddings.

        Args:
            embedding1: Primer vector de embedding
            embedding2: Segundo vector de embedding

        Returns:
            float: Similitud coseno (0-1)
        """
        # Convertir a arrays de numpy
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Calcular similitud coseno
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Genera un embedding para un texto.

        Args:
            text: Texto para generar embedding

        Returns:
            List[float]: Vector de embedding
        """
        # Registrar inicio de telemetría
        span_id = telemetry_manager.start_span(
            name="embeddings_generate", attributes={"text_length": len(text)}
        )

        try:
            # Actualizar estadísticas
            self.stats["embedding_requests"] += 1

            # Verificar caché
            if self.cache_enabled:
                cache_key = self._get_cache_key(text)

                if cache_key in self.text_to_embedding_cache:
                    cache_entry = self.text_to_embedding_cache[cache_key]
                    # Verificar TTL
                    if time.time() - cache_entry["timestamp"] < self.cache_ttl:
                        self.stats["cache_hits"] += 1
                        telemetry_manager.set_span_attribute(span_id, "cache", "hit")
                        return cache_entry["embedding"]

            self.stats["cache_misses"] += 1

            # Generar embedding con Vertex AI
            embedding = await vertex_ai_client.generate_embedding(text)

            # Guardar en caché
            if self.cache_enabled:
                self.text_to_embedding_cache[cache_key] = {
                    "embedding": embedding,
                    "timestamp": time.time(),
                }

                # Limpiar caché si es necesario
                self._clean_cache_if_needed()

            telemetry_manager.set_span_attribute(
                span_id, "embedding_size", len(embedding)
            )
            return embedding

        except Exception as e:
            logger.error(f"Error al generar embedding: {str(e)}", exc_info=True)
            self.stats["errors"] += 1
            telemetry_manager.set_span_attribute(span_id, "error", str(e))

            # Devolver un embedding vacío en caso de error
            return [0.0] * self.vector_dimension

        finally:
            telemetry_manager.end_span(span_id)

    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para múltiples textos.

        Args:
            texts: Lista de textos

        Returns:
            List[List[float]]: Lista de vectores de embedding
        """
        # Registrar inicio de telemetría
        span_id = telemetry_manager.start_span(
            name="embeddings_batch_generate", attributes={"text_count": len(texts)}
        )

        try:
            # Actualizar estadísticas
            self.stats["batch_embedding_requests"] += 1

            # Verificar caché para cada texto
            embeddings = []
            texts_to_embed = []
            indices_to_embed = []

            if self.cache_enabled:
                for i, text in enumerate(texts):
                    cache_key = self._get_cache_key(text)

                    if cache_key in self.text_to_embedding_cache:
                        cache_entry = self.text_to_embedding_cache[cache_key]
                        # Verificar TTL
                        if time.time() - cache_entry["timestamp"] < self.cache_ttl:
                            self.stats["cache_hits"] += 1
                            embeddings.append(cache_entry["embedding"])
                            continue

                    self.stats["cache_misses"] += 1
                    texts_to_embed.append(text)
                    indices_to_embed.append(i)
                    embeddings.append(None)
            else:
                texts_to_embed = texts
                indices_to_embed = list(range(len(texts)))
                embeddings = [None] * len(texts)

            # Si todos los embeddings están en caché, retornar
            if all(e is not None for e in embeddings):
                telemetry_manager.set_span_attribute(span_id, "cache", "all_hit")
                return embeddings

            # Generar embeddings para los textos restantes
            if texts_to_embed:
                new_embeddings = await vertex_ai_client.batch_generate_embeddings(
                    texts_to_embed
                )

                # Actualizar lista de embeddings y caché
                for i, embedding in zip(indices_to_embed, new_embeddings):
                    embeddings[i] = embedding

                    # Guardar en caché
                    if self.cache_enabled:
                        cache_key = self._get_cache_key(texts[i])
                        self.text_to_embedding_cache[cache_key] = {
                            "embedding": embedding,
                            "timestamp": time.time(),
                        }

                # Limpiar caché si es necesario
                if self.cache_enabled:
                    self._clean_cache_if_needed()

            telemetry_manager.set_span_attribute(
                span_id, "embeddings_generated", len(texts_to_embed)
            )
            return embeddings

        except Exception as e:
            logger.error(
                f"Error al generar embeddings en lote: {str(e)}", exc_info=True
            )
            self.stats["errors"] += 1
            telemetry_manager.set_span_attribute(span_id, "error", str(e))

            # Devolver embeddings vacíos en caso de error
            return [[0.0] * self.vector_dimension for _ in range(len(texts))]

        finally:
            telemetry_manager.end_span(span_id)

    async def store_embedding(
        self,
        key: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None,
    ) -> bool:
        """
        Almacena un embedding con su texto y metadatos asociados.

        Args:
            key: Clave única para identificar el embedding
            text: Texto original
            metadata: Metadatos adicionales
            embedding: Vector de embedding (opcional, se genera si no se proporciona)

        Returns:
            bool: True si se almacenó correctamente
        """
        try:
            # Generar embedding si no se proporciona
            if embedding is None:
                embedding = await self.generate_embedding(text)

            # Crear objeto de datos
            embedding_data = {
                "text": text,
                "embedding": embedding,
                "metadata": metadata or {},
                "timestamp": time.time(),
            }

            # Almacenar en memoria siempre (como caché)
            self.embeddings_store[key] = embedding_data

            # Almacenar en GCS si está habilitado
            if self.use_gcs:
                await self._ensure_gcs_initialized()
                if self._gcs_initialized:
                    try:
                        # Convertir a JSON y subir a GCS
                        blob_name = f"{self.gcs_prefix}{key}.json"
                        content = json.dumps(embedding_data)
                        await gcs_client.upload_file(
                            file_path_or_content=content.encode("utf-8"),
                            destination_blob_name=blob_name,
                            content_type="application/json",
                            metadata={"key": key, "type": "embedding"},
                        )
                        logger.debug(f"Embedding almacenado en GCS: {blob_name}")
                    except Exception as e:
                        logger.error(f"Error al almacenar en GCS: {e}")
                        # El embedding ya está en memoria, continuar

            logger.debug(f"Embedding almacenado con clave: {key}")
            return True

        except Exception as e:
            logger.error(f"Error al almacenar embedding: {str(e)}", exc_info=True)
            self.stats["errors"] += 1
            return False

    async def batch_store_embeddings(self, items: List[Dict[str, Any]]) -> List[bool]:
        """
        Almacena múltiples embeddings en lote.

        Args:
            items: Lista de items a almacenar, cada uno con:
                - key: Clave única
                - text: Texto original
                - metadata: Metadatos (opcional)
                - embedding: Vector de embedding (opcional)

        Returns:
            List[bool]: Lista de resultados (True si se almacenó correctamente)
        """
        try:
            # Extraer textos para generar embeddings en lote
            texts = []
            indices_with_missing_embeddings = []

            for i, item in enumerate(items):
                if "embedding" not in item or item["embedding"] is None:
                    texts.append(item["text"])
                    indices_with_missing_embeddings.append(i)

            # Generar embeddings en lote si es necesario
            if texts:
                embeddings = await self.batch_generate_embeddings(texts)

                # Asignar embeddings generados
                for idx, embedding in zip(indices_with_missing_embeddings, embeddings):
                    items[idx]["embedding"] = embedding

            # Almacenar cada item
            results = []
            for item in items:
                result = await self.store_embedding(
                    key=item["key"],
                    text=item["text"],
                    metadata=item.get("metadata"),
                    embedding=item["embedding"],
                )
                results.append(result)

            return results

        except Exception as e:
            logger.error(
                f"Error al almacenar embeddings en lote: {str(e)}", exc_info=True
            )
            self.stats["errors"] += 1
            return [False] * len(items)

    async def find_similar(
        self, query: str, top_k: int = 5, threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Encuentra items similares a una consulta.

        Args:
            query: Texto de consulta
            top_k: Número máximo de resultados
            threshold: Umbral de similitud (opcional, usa el predeterminado si no se proporciona)

        Returns:
            List[Dict[str, Any]]: Lista de items similares con sus puntuaciones
        """
        # Registrar inicio de telemetría
        span_id = telemetry_manager.start_span(
            name="embeddings_find_similar",
            attributes={"query_length": len(query), "top_k": top_k},
        )

        try:
            # Actualizar estadísticas
            self.stats["similarity_searches"] += 1

            # Usar umbral predeterminado si no se proporciona
            if threshold is None:
                threshold = self.similarity_threshold

            # Generar embedding para la consulta
            query_embedding = await self.generate_embedding(query)

            # Intentar usar Vector Search primero si está habilitado
            if self.use_vector_search:
                await self._ensure_vector_search_initialized()
                if self._vector_search_initialized:
                    try:
                        # Buscar en Vector Search
                        vector_results = await vector_search_client.search_similar(
                            query_vector=query_embedding,
                            top_k=top_k
                            * 2,  # Obtener más resultados para filtrar por threshold
                        )

                        # Procesar resultados de Vector Search
                        results = []
                        for result in vector_results:
                            # La distancia coseno en Vector Search es 1 - similitud
                            similarity = 1.0 - result["distance"]

                            if similarity >= threshold:
                                # Intentar obtener los datos completos del embedding
                                embedding_data = await self.get_by_key(result["id"])
                                if embedding_data:
                                    results.append(
                                        {
                                            "key": result["id"],
                                            "text": embedding_data["text"],
                                            "metadata": embedding_data["metadata"],
                                            "similarity": similarity,
                                        }
                                    )

                        # Ordenar y limitar resultados
                        results.sort(key=lambda x: x["similarity"], reverse=True)
                        final_results = results[:top_k]

                        telemetry_manager.set_span_attribute(
                            span_id, "search_method", "vector_search"
                        )
                        telemetry_manager.set_span_attribute(
                            span_id, "results_count", len(final_results)
                        )
                        return final_results

                    except Exception as e:
                        logger.error(
                            f"Error en Vector Search, fallback a búsqueda local: {e}"
                        )
                        # Continuar con búsqueda local

            # Búsqueda local (fallback o si Vector Search no está disponible)
            # Si GCS está habilitado y no tenemos suficientes embeddings en memoria,
            # cargar más desde GCS
            if self.use_gcs and len(self.embeddings_store) < top_k * 2:
                await self._ensure_gcs_initialized()
                if self._gcs_initialized:
                    await self._load_embeddings_from_gcs(limit=min(1000, top_k * 10))

            # Calcular similitud con todos los embeddings almacenados
            similarities = []

            for key, item in self.embeddings_store.items():
                similarity = self._calculate_similarity(
                    query_embedding, item["embedding"]
                )

                if similarity >= threshold:
                    similarities.append(
                        {
                            "key": key,
                            "text": item["text"],
                            "metadata": item["metadata"],
                            "similarity": similarity,
                        }
                    )

            # Ordenar por similitud (descendente) y limitar a top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            results = similarities[:top_k]

            telemetry_manager.set_span_attribute(span_id, "search_method", "local")
            telemetry_manager.set_span_attribute(span_id, "results_count", len(results))
            return results

        except Exception as e:
            logger.error(f"Error al buscar similares: {str(e)}", exc_info=True)
            self.stats["errors"] += 1
            telemetry_manager.set_span_attribute(span_id, "error", str(e))
            return []

        finally:
            telemetry_manager.end_span(span_id)

    async def find_similar_by_embedding(
        self, embedding: List[float], top_k: int = 5, threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Encuentra items similares a un embedding.

        Args:
            embedding: Vector de embedding
            top_k: Número máximo de resultados
            threshold: Umbral de similitud (opcional, usa el predeterminado si no se proporciona)

        Returns:
            List[Dict[str, Any]]: Lista de items similares con sus puntuaciones
        """
        # Registrar inicio de telemetría
        span_id = telemetry_manager.start_span(
            name="embeddings_find_similar_by_embedding", attributes={"top_k": top_k}
        )

        try:
            # Actualizar estadísticas
            self.stats["similarity_searches"] += 1

            # Usar umbral predeterminado si no se proporciona
            if threshold is None:
                threshold = self.similarity_threshold

            # Calcular similitud con todos los embeddings almacenados
            similarities = []

            for key, item in self.embeddings_store.items():
                similarity = self._calculate_similarity(embedding, item["embedding"])

                if similarity >= threshold:
                    similarities.append(
                        {
                            "key": key,
                            "text": item["text"],
                            "metadata": item["metadata"],
                            "similarity": similarity,
                        }
                    )

            # Ordenar por similitud (descendente) y limitar a top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            results = similarities[:top_k]

            telemetry_manager.set_span_attribute(span_id, "results_count", len(results))
            return results

        except Exception as e:
            logger.error(
                f"Error al buscar similares por embedding: {str(e)}", exc_info=True
            )
            self.stats["errors"] += 1
            telemetry_manager.set_span_attribute(span_id, "error", str(e))
            return []

        finally:
            telemetry_manager.end_span(span_id)

    async def get_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un item por su clave.

        Args:
            key: Clave del item

        Returns:
            Optional[Dict[str, Any]]: Item si existe, None en caso contrario
        """
        # Primero buscar en memoria
        if key in self.embeddings_store:
            item = self.embeddings_store[key]
            return {
                "key": key,
                "text": item["text"],
                "embedding": item["embedding"],
                "metadata": item["metadata"],
                "timestamp": item["timestamp"],
            }

        # Si no está en memoria y GCS está habilitado, buscar en GCS
        if self.use_gcs:
            await self._ensure_gcs_initialized()
            if self._gcs_initialized:
                try:
                    blob_name = f"{self.gcs_prefix}{key}.json"
                    content = await gcs_client.download_file(blob_name)
                    embedding_data = json.loads(content.decode("utf-8"))

                    # Almacenar en memoria para futuras consultas
                    self.embeddings_store[key] = embedding_data

                    return {
                        "key": key,
                        "text": embedding_data["text"],
                        "embedding": embedding_data["embedding"],
                        "metadata": embedding_data["metadata"],
                        "timestamp": embedding_data["timestamp"],
                    }
                except FileNotFoundError:
                    logger.debug(f"Embedding no encontrado en GCS: {key}")
                except Exception as e:
                    logger.error(f"Error al obtener embedding de GCS: {e}")

        return None

    async def delete_by_key(self, key: str) -> bool:
        """
        Elimina un item por su clave.

        Args:
            key: Clave del item

        Returns:
            bool: True si se eliminó correctamente
        """
        deleted_from_memory = False
        deleted_from_gcs = False

        # Eliminar de memoria
        if key in self.embeddings_store:
            del self.embeddings_store[key]
            deleted_from_memory = True

        # Eliminar de GCS si está habilitado
        if self.use_gcs:
            await self._ensure_gcs_initialized()
            if self._gcs_initialized:
                try:
                    blob_name = f"{self.gcs_prefix}{key}.json"
                    deleted_from_gcs = await gcs_client.delete_file(blob_name)
                except Exception as e:
                    logger.error(f"Error al eliminar de GCS: {e}")

        return deleted_from_memory or deleted_from_gcs

    def clear_store(self) -> None:
        """Limpia el almacén de embeddings."""
        self.embeddings_store = {}
        logger.info("Almacén de embeddings limpiado")

    def clear_cache(self) -> None:
        """Limpia la caché de embeddings."""
        self.text_to_embedding_cache = {}
        logger.info("Caché de embeddings limpiado")

    async def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del gestor de embeddings.

        Returns:
            Dict[str, Any]: Estadísticas de uso
        """
        stats_data = {
            "stats": self.stats,
            "store_size": len(self.embeddings_store),
            "cache_size": len(self.text_to_embedding_cache),
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "vector_dimension": self.vector_dimension,
            "similarity_threshold": self.similarity_threshold,
            "use_gcs": self.use_gcs,
            "gcs_initialized": self._gcs_initialized,
            "gcs_prefix": self.gcs_prefix,
            "use_vector_search": self.use_vector_search,
            "vector_search_initialized": self._vector_search_initialized,
            "timestamp": datetime.now().isoformat(),
        }

        # Si GCS está habilitado, obtener estadísticas adicionales
        if self.use_gcs and self._gcs_initialized:
            try:
                files = await gcs_client.list_files(prefix=self.gcs_prefix)
                stats_data["gcs_embeddings_count"] = len(files)
            except Exception as e:
                logger.error(f"Error al obtener estadísticas de GCS: {e}")
                stats_data["gcs_embeddings_count"] = "error"

        return stats_data


# Crear instancia única del gestor de embeddings
embeddings_manager = EmbeddingsManager()
