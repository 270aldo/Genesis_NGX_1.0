"""
Response Compression System - FASE 12 QUICK WIN #2

Sistema de compresión de respuestas para reducir el ancho de banda en un 60%.
Implementa compresión inteligente con soporte para gzip, brotli y zstd.

IMPACTO ESPERADO: 60% mejora en ancho de banda
"""

import gzip
import json
import time
from io import BytesIO
from typing import Dict, Any, Optional, Union, Tuple
from enum import Enum
import logging

try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False
    
try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

from core.logging_config import get_logger

logger = get_logger(__name__)


class CompressionType(Enum):
    """Tipos de compresión soportados."""
    NONE = "none"
    GZIP = "gzip"
    BROTLI = "br"
    ZSTD = "zstd"


class CompressionLevel:
    """Niveles de compresión por algoritmo."""
    GZIP_FAST = 1      # Más rápido, menos compresión
    GZIP_BALANCED = 6  # Balance entre velocidad y compresión
    GZIP_BEST = 9      # Mejor compresión, más lento
    
    BROTLI_FAST = 1
    BROTLI_BALANCED = 6
    BROTLI_BEST = 11
    
    ZSTD_FAST = 1
    ZSTD_BALANCED = 3
    ZSTD_BEST = 22


class ResponseCompressor:
    """
    Sistema de compresión de respuestas optimizado para APIs.
    
    Características:
    - Detección automática del mejor algoritmo
    - Compresión adaptativa basada en tamaño
    - Caché de respuestas comprimidas
    - Métricas de rendimiento
    """
    
    def __init__(self,
                 min_size_bytes: int = 1024,  # 1KB mínimo para comprimir
                 default_algorithm: CompressionType = CompressionType.GZIP,
                 cache_enabled: bool = True,
                 cache_max_size: int = 100):
        """
        Inicializa el compresor de respuestas.
        
        Args:
            min_size_bytes: Tamaño mínimo para aplicar compresión
            default_algorithm: Algoritmo por defecto
            cache_enabled: Si usar caché de respuestas comprimidas
            cache_max_size: Tamaño máximo del caché
        """
        self.min_size_bytes = min_size_bytes
        self.default_algorithm = default_algorithm
        self.cache_enabled = cache_enabled
        self.cache_max_size = cache_max_size
        
        # Caché de respuestas comprimidas
        self._cache: Dict[str, Tuple[bytes, CompressionType]] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Métricas
        self.metrics = {
            'total_compressions': 0,
            'total_bytes_original': 0,
            'total_bytes_compressed': 0,
            'average_compression_ratio': 0.0,
            'compression_time_total': 0.0,
            'algorithms_used': {alg.value: 0 for alg in CompressionType}
        }
        
        # Verificar algoritmos disponibles
        self._available_algorithms = self._check_available_algorithms()
        logger.info(f"ResponseCompressor inicializado - Algoritmos disponibles: {self._available_algorithms}")
    
    def _check_available_algorithms(self) -> Dict[CompressionType, bool]:
        """Verifica qué algoritmos de compresión están disponibles."""
        return {
            CompressionType.NONE: True,
            CompressionType.GZIP: True,  # Siempre disponible
            CompressionType.BROTLI: BROTLI_AVAILABLE,
            CompressionType.ZSTD: ZSTD_AVAILABLE
        }
    
    def compress_response(self,
                         data: Union[Dict, str, bytes],
                         accept_encoding: str = "",
                         force_algorithm: Optional[CompressionType] = None) -> Tuple[bytes, CompressionType]:
        """
        Comprime una respuesta usando el mejor algoritmo disponible.
        
        Args:
            data: Datos a comprimir (dict, string o bytes)
            accept_encoding: Header Accept-Encoding del cliente
            force_algorithm: Forzar un algoritmo específico
            
        Returns:
            Tupla de (datos_comprimidos, tipo_compresión)
        """
        start_time = time.time()
        
        # Convertir datos a bytes si es necesario
        if isinstance(data, dict):
            original_data = json.dumps(data, separators=(',', ':')).encode('utf-8')
        elif isinstance(data, str):
            original_data = data.encode('utf-8')
        else:
            original_data = data
        
        original_size = len(original_data)
        
        # Verificar si vale la pena comprimir
        if original_size < self.min_size_bytes:
            return original_data, CompressionType.NONE
        
        # Verificar caché
        if self.cache_enabled:
            cache_key = self._generate_cache_key(original_data)
            if cache_key in self._cache:
                self._cache_hits += 1
                return self._cache[cache_key]
            self._cache_misses += 1
        
        # Determinar algoritmo a usar
        if force_algorithm:
            algorithm = force_algorithm
        else:
            algorithm = self._select_best_algorithm(accept_encoding, original_size)
        
        # Comprimir
        compressed_data = self._compress_with_algorithm(original_data, algorithm)
        
        # Actualizar métricas
        compression_time = time.time() - start_time
        self._update_metrics(original_size, len(compressed_data), algorithm, compression_time)
        
        # Guardar en caché si está habilitado
        if self.cache_enabled and len(self._cache) < self.cache_max_size:
            self._cache[cache_key] = (compressed_data, algorithm)
        
        return compressed_data, algorithm
    
    def _select_best_algorithm(self, accept_encoding: str, data_size: int) -> CompressionType:
        """
        Selecciona el mejor algoritmo basado en Accept-Encoding y tamaño.
        
        Args:
            accept_encoding: Header Accept-Encoding del cliente
            data_size: Tamaño de los datos originales
            
        Returns:
            Tipo de compresión seleccionado
        """
        # Parse Accept-Encoding header
        accepted = set(enc.strip().lower() for enc in accept_encoding.split(','))
        
        # Prioridad de algoritmos por eficiencia
        if data_size > 100000:  # > 100KB
            # Para datos grandes, priorizar ratio de compresión
            priority = [
                (CompressionType.ZSTD, "zstd"),
                (CompressionType.BROTLI, "br"),
                (CompressionType.GZIP, "gzip")
            ]
        else:
            # Para datos pequeños, priorizar velocidad
            priority = [
                (CompressionType.GZIP, "gzip"),
                (CompressionType.ZSTD, "zstd"),
                (CompressionType.BROTLI, "br")
            ]
        
        # Seleccionar primer algoritmo soportado
        for algo, encoding in priority:
            if (encoding in accepted or '*' in accepted) and self._available_algorithms.get(algo, False):
                return algo
        
        # Si ninguno es aceptado pero el cliente acepta cualquiera
        if '*' in accepted:
            return self.default_algorithm
        
        # No comprimir si el cliente no acepta ningún algoritmo
        return CompressionType.NONE
    
    def _compress_with_algorithm(self, data: bytes, algorithm: CompressionType) -> bytes:
        """
        Comprime datos con el algoritmo especificado.
        
        Args:
            data: Datos a comprimir
            algorithm: Algoritmo a usar
            
        Returns:
            Datos comprimidos
        """
        if algorithm == CompressionType.GZIP:
            return self._compress_gzip(data)
        elif algorithm == CompressionType.BROTLI:
            return self._compress_brotli(data)
        elif algorithm == CompressionType.ZSTD:
            return self._compress_zstd(data)
        else:
            return data
    
    def _compress_gzip(self, data: bytes, level: int = CompressionLevel.GZIP_BALANCED) -> bytes:
        """Comprime usando gzip."""
        buffer = BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb', compresslevel=level) as gz:
            gz.write(data)
        return buffer.getvalue()
    
    def _compress_brotli(self, data: bytes, level: int = CompressionLevel.BROTLI_BALANCED) -> bytes:
        """Comprime usando brotli."""
        if not BROTLI_AVAILABLE:
            logger.warning("Brotli no disponible, usando gzip como fallback")
            return self._compress_gzip(data)
        
        return brotli.compress(data, quality=level)
    
    def _compress_zstd(self, data: bytes, level: int = CompressionLevel.ZSTD_BALANCED) -> bytes:
        """Comprime usando zstandard."""
        if not ZSTD_AVAILABLE:
            logger.warning("Zstandard no disponible, usando gzip como fallback")
            return self._compress_gzip(data)
        
        cctx = zstd.ZstdCompressor(level=level)
        return cctx.compress(data)
    
    def _generate_cache_key(self, data: bytes) -> str:
        """Genera clave de caché para datos."""
        import hashlib
        return hashlib.md5(data).hexdigest()
    
    def _update_metrics(self, original_size: int, compressed_size: int, 
                       algorithm: CompressionType, compression_time: float):
        """Actualiza métricas de compresión."""
        self.metrics['total_compressions'] += 1
        self.metrics['total_bytes_original'] += original_size
        self.metrics['total_bytes_compressed'] += compressed_size
        self.metrics['compression_time_total'] += compression_time
        self.metrics['algorithms_used'][algorithm.value] += 1
        
        # Calcular ratio promedio
        if self.metrics['total_bytes_original'] > 0:
            self.metrics['average_compression_ratio'] = (
                1 - (self.metrics['total_bytes_compressed'] / self.metrics['total_bytes_original'])
            ) * 100
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de compresión."""
        cache_hit_rate = 0
        if (self._cache_hits + self._cache_misses) > 0:
            cache_hit_rate = (self._cache_hits / (self._cache_hits + self._cache_misses)) * 100
        
        return {
            **self.metrics,
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self._cache),
            'average_compression_time': (
                self.metrics['compression_time_total'] / self.metrics['total_compressions']
                if self.metrics['total_compressions'] > 0 else 0
            ),
            'bandwidth_saved_percent': self.metrics['average_compression_ratio']
        }
    
    def clear_cache(self):
        """Limpia el caché de respuestas comprimidas."""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("Caché de compresión limpiado")
    
    def get_content_encoding_header(self, algorithm: CompressionType) -> Optional[str]:
        """
        Obtiene el header Content-Encoding para el algoritmo.
        
        Args:
            algorithm: Tipo de compresión usado
            
        Returns:
            Valor del header Content-Encoding o None
        """
        if algorithm == CompressionType.NONE:
            return None
        return algorithm.value


# Instancia global del compresor
response_compressor = ResponseCompressor()


# Funciones de conveniencia
async def compress_api_response(response_data: Union[Dict, str], 
                               accept_encoding: str = "") -> Tuple[bytes, Optional[str]]:
    """
    Comprime una respuesta de API.
    
    Args:
        response_data: Datos de la respuesta
        accept_encoding: Header Accept-Encoding del cliente
        
    Returns:
        Tupla de (datos_comprimidos, content_encoding_header)
    """
    compressed_data, algorithm = response_compressor.compress_response(
        response_data, 
        accept_encoding
    )
    
    content_encoding = response_compressor.get_content_encoding_header(algorithm)
    
    return compressed_data, content_encoding


def get_compression_metrics() -> Dict[str, Any]:
    """
    Obtiene métricas del sistema de compresión.
    
    Returns:
        Dict con métricas de compresión
    """
    return response_compressor.get_metrics()


def estimate_bandwidth_savings(original_size: int, compressed_size: int) -> Dict[str, Any]:
    """
    Estima el ahorro de ancho de banda.
    
    Args:
        original_size: Tamaño original en bytes
        compressed_size: Tamaño comprimido en bytes
        
    Returns:
        Dict con estimaciones de ahorro
    """
    if original_size == 0:
        return {
            "savings_bytes": 0,
            "savings_percent": 0,
            "compression_ratio": 1.0
        }
    
    savings_bytes = original_size - compressed_size
    savings_percent = (savings_bytes / original_size) * 100
    compression_ratio = original_size / compressed_size if compressed_size > 0 else float('inf')
    
    return {
        "original_size_bytes": original_size,
        "compressed_size_bytes": compressed_size,
        "savings_bytes": savings_bytes,
        "savings_percent": round(savings_percent, 2),
        "compression_ratio": round(compression_ratio, 2),
        "bandwidth_impact": f"{savings_percent:.1f}% reduction"
    }