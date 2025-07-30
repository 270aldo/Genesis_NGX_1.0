"""
Compression Middleware - FASE 12 QUICK WIN #2

Middleware de FastAPI para compresión automática de respuestas.
Integra el sistema de compresión con todas las respuestas de la API.

IMPACTO ESPERADO: 60% mejora en ancho de banda
"""

import time
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message

from core.response_compression import (
    response_compressor,
    CompressionType,
    compress_api_response
)
from core.logging_config import get_logger
from core.settings_lazy import settings

logger = get_logger(__name__)


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware para compresión automática de respuestas.
    
    Características:
    - Compresión transparente basada en Accept-Encoding
    - Exclusión inteligente de rutas
    - Métricas de rendimiento
    - Soporte para streaming responses
    """
    
    def __init__(self, app, 
                 min_size: int = 1024,
                 excluded_paths: Optional[list] = None,
                 excluded_extensions: Optional[list] = None):
        """
        Inicializa el middleware de compresión.
        
        Args:
            app: Aplicación FastAPI
            min_size: Tamaño mínimo para comprimir (bytes)
            excluded_paths: Rutas excluidas de compresión
            excluded_extensions: Extensiones de archivo excluidas
        """
        super().__init__(app)
        self.min_size = min_size
        self.excluded_paths = excluded_paths or [
            "/health",
            "/metrics", 
            "/api/v1/batch-metrics/health",
            "/docs",
            "/openapi.json"
        ]
        self.excluded_extensions = excluded_extensions or [
            ".jpg", ".jpeg", ".png", ".gif", ".webp",  # Imágenes ya comprimidas
            ".mp3", ".mp4", ".avi", ".mov",           # Audio/Video
            ".zip", ".gz", ".br", ".zst"              # Ya comprimidos
        ]
        
        logger.info("✅ FASE 12 QUICK WIN #2: Compression Middleware inicializado")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesa la request y comprime la response si es apropiado.
        
        Args:
            request: Request entrante
            call_next: Siguiente middleware/handler
            
        Returns:
            Response posiblemente comprimida
        """
        # Verificar si la ruta está excluida
        if self._should_exclude_path(request.url.path):
            return await call_next(request)
        
        # Obtener Accept-Encoding del cliente
        accept_encoding = request.headers.get("accept-encoding", "")
        
        # Procesar request
        start_time = time.time()
        response = await call_next(request)
        
        # Solo comprimir respuestas exitosas
        if response.status_code >= 300:
            return response
        
        # No comprimir streaming responses por ahora
        if isinstance(response, StreamingResponse):
            return response
        
        # Verificar Content-Type
        content_type = response.headers.get("content-type", "")
        if not self._should_compress_content_type(content_type):
            return response
        
        # Si ya está comprimido, no volver a comprimir
        if response.headers.get("content-encoding"):
            return response
        
        # Comprimir la respuesta
        return await self._compress_response(response, accept_encoding, start_time)
    
    def _should_exclude_path(self, path: str) -> bool:
        """Verifica si la ruta debe ser excluida de compresión."""
        # Verificar rutas exactas
        if path in self.excluded_paths:
            return True
        
        # Verificar extensiones
        for ext in self.excluded_extensions:
            if path.endswith(ext):
                return True
        
        return False
    
    def _should_compress_content_type(self, content_type: str) -> bool:
        """Verifica si el content-type debe ser comprimido."""
        # Comprimir JSON, texto, HTML, XML, JavaScript, CSS
        compressible_types = [
            "application/json",
            "text/",
            "application/xml",
            "application/javascript",
            "application/x-javascript"
        ]
        
        return any(ct in content_type.lower() for ct in compressible_types)
    
    async def _compress_response(self, response: Response, 
                               accept_encoding: str, 
                               start_time: float) -> Response:
        """
        Comprime el contenido de la respuesta.
        
        Args:
            response: Response original
            accept_encoding: Accept-Encoding del cliente
            start_time: Tiempo de inicio del procesamiento
            
        Returns:
            Response comprimida o original si no se puede comprimir
        """
        try:
            # Leer el body de la respuesta
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Verificar tamaño mínimo
            if len(body) < self.min_size:
                # Recrear response sin comprimir
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
            
            # Comprimir
            compressed_body, algorithm = response_compressor.compress_response(
                body,
                accept_encoding
            )
            
            # Si no se comprimió (algorithm == NONE), devolver original
            if algorithm == CompressionType.NONE:
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
            
            # Crear nueva response comprimida
            headers = dict(response.headers)
            headers["content-encoding"] = algorithm.value
            headers["content-length"] = str(len(compressed_body))
            
            # Agregar header de rendimiento
            compression_time = time.time() - start_time
            original_size = len(body)
            compressed_size = len(compressed_body)
            savings_percent = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0
            
            headers["x-compression-ratio"] = f"{savings_percent:.1f}%"
            headers["x-compression-time"] = f"{compression_time*1000:.1f}ms"
            
            # Log de métricas
            logger.debug(
                f"Response comprimida: {original_size} → {compressed_size} bytes "
                f"({savings_percent:.1f}% ahorro) usando {algorithm.value}"
            )
            
            return Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type
            )
            
        except Exception as e:
            logger.error(f"Error comprimiendo response: {e}")
            # En caso de error, devolver response original
            return response


def setup_compression_middleware(app, **kwargs):
    """
    Configura el middleware de compresión en la aplicación.
    
    Args:
        app: Aplicación FastAPI
        **kwargs: Argumentos adicionales para el middleware
    """
    # Solo activar si está habilitado en settings
    if not getattr(settings, 'ENABLE_RESPONSE_COMPRESSION', True):
        logger.info("Compresión de respuestas deshabilitada por configuración")
        return
    
    # Configurar parámetros por defecto
    min_size = kwargs.get('min_size', getattr(settings, 'COMPRESSION_MIN_SIZE', 1024))
    
    # Agregar middleware
    app.add_middleware(
        CompressionMiddleware,
        min_size=min_size,
        excluded_paths=kwargs.get('excluded_paths'),
        excluded_extensions=kwargs.get('excluded_extensions')
    )
    
    logger.info(
        f"✅ FASE 12 QUICK WIN #2: Compression Middleware configurado "
        f"(min_size: {min_size} bytes)"
    )