"""
Memory Cache Optimizer - FASE 12 QUICK WIN #3

Sistema de optimización de caché en memoria para mejorar el tiempo de respuesta en un 25%.
Implementa estrategias avanzadas de caché con TTL adaptativo y precalentamiento inteligente.

IMPACTO ESPERADO: 25% mejora en tiempo de respuesta
"""

import asyncio
import time
import json
import hashlib
from typing import Dict, Any, Optional, Callable, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import heapq
from collections import OrderedDict, defaultdict

from core.logging_config import get_logger
from core.settings_lazy import settings

logger = get_logger(__name__)


class CacheStrategy(Enum):
    """Estrategias de caché disponibles."""
    LRU = "lru"           # Least Recently Used
    LFU = "lfu"           # Least Frequently Used
    TTL = "ttl"           # Time To Live
    ADAPTIVE = "adaptive" # Adaptativo basado en patrones


class CachePriority(Enum):
    """Prioridades de caché."""
    CRITICAL = 1    # Datos críticos, mantener siempre
    HIGH = 2        # Alta prioridad
    NORMAL = 3      # Prioridad normal
    LOW = 4         # Baja prioridad


@dataclass
class CacheEntry:
    """Entrada individual en el caché."""
    key: str
    value: Any
    size_bytes: int
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    ttl: Optional[float] = None
    priority: CachePriority = CachePriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado."""
        if self.ttl is None:
            return False
        return time.time() > (self.created_at + self.ttl)
    
    def access(self):
        """Registra un acceso a la entrada."""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class CacheStats:
    """Estadísticas del caché."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    entry_count: int = 0
    avg_hit_time_ms: float = 0.0
    avg_miss_time_ms: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Calcula la tasa de aciertos."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0


class MemoryCacheOptimizer:
    """
    Optimizador de caché en memoria con estrategias avanzadas.
    
    Características:
    - Múltiples estrategias de evicción
    - TTL adaptativo basado en patrones de acceso
    - Precalentamiento inteligente
    - Límites de memoria configurables
    - Métricas detalladas de rendimiento
    """
    
    def __init__(self,
                 max_size_mb: int = 100,
                 strategy: CacheStrategy = CacheStrategy.ADAPTIVE,
                 default_ttl: float = 300,  # 5 minutos
                 enable_prewarming: bool = True):
        """
        Inicializa el optimizador de caché.
        
        Args:
            max_size_mb: Tamaño máximo del caché en MB
            strategy: Estrategia de caché a usar
            default_ttl: TTL por defecto en segundos
            enable_prewarming: Si habilitar precalentamiento
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.strategy = strategy
        self.default_ttl = default_ttl
        self.enable_prewarming = enable_prewarming
        
        # Almacén principal del caché
        self._cache: Dict[str, CacheEntry] = {}
        self._lru_order = OrderedDict()  # Para estrategia LRU
        self._access_patterns = defaultdict(list)  # Para estrategia adaptativa
        
        # Estadísticas
        self.stats = CacheStats()
        self._hit_times: List[float] = []
        self._miss_times: List[float] = []
        
        # Precalentamiento
        self._prewarm_queue: List[Tuple[float, str, Callable]] = []  # heap de (prioridad, key, loader)
        self._prewarm_task: Optional[asyncio.Task] = None
        self._running = False
        
        logger.info(
            f"MemoryCacheOptimizer inicializado - "
            f"max_size: {max_size_mb}MB, strategy: {strategy.value}, "
            f"default_ttl: {default_ttl}s"
        )
    
    async def start(self):
        """Inicia el optimizador de caché."""
        if self._running:
            return
        
        self._running = True
        
        if self.enable_prewarming:
            self._prewarm_task = asyncio.create_task(self._prewarm_loop())
        
        # Iniciar limpieza periódica
        asyncio.create_task(self._cleanup_loop())
        
        logger.info("MemoryCacheOptimizer iniciado")
    
    async def stop(self):
        """Detiene el optimizador de caché."""
        self._running = False
        
        if self._prewarm_task:
            self._prewarm_task.cancel()
            try:
                await self._prewarm_task
            except asyncio.CancelledError:
                pass
        
        logger.info("MemoryCacheOptimizer detenido")
    
    async def get(self, key: str, loader: Optional[Callable] = None) -> Optional[Any]:
        """
        Obtiene un valor del caché.
        
        Args:
            key: Clave a buscar
            loader: Función para cargar el valor si no está en caché
            
        Returns:
            Valor del caché o None
        """
        start_time = time.time()
        
        # Verificar si existe en caché
        entry = self._cache.get(key)
        
        if entry and not entry.is_expired():
            # Cache hit
            entry.access()
            self._update_lru(key)
            self._record_access_pattern(key, True)
            
            self.stats.hits += 1
            hit_time = time.time() - start_time
            self._hit_times.append(hit_time)
            self._update_avg_times()
            
            return entry.value
        
        # Cache miss
        self.stats.misses += 1
        self._record_access_pattern(key, False)
        
        if loader:
            # Cargar valor
            try:
                value = await loader() if asyncio.iscoroutinefunction(loader) else loader()
                
                # Almacenar en caché
                await self.set(key, value)
                
                miss_time = time.time() - start_time
                self._miss_times.append(miss_time)
                self._update_avg_times()
                
                return value
            except Exception as e:
                logger.error(f"Error cargando valor para key {key}: {e}")
                return None
        
        miss_time = time.time() - start_time
        self._miss_times.append(miss_time)
        self._update_avg_times()
        
        return None
    
    async def set(self, 
                  key: str, 
                  value: Any, 
                  ttl: Optional[float] = None,
                  priority: CachePriority = CachePriority.NORMAL) -> bool:
        """
        Almacena un valor en el caché.
        
        Args:
            key: Clave para almacenar
            value: Valor a almacenar
            ttl: TTL personalizado (None usa el default)
            priority: Prioridad del caché
            
        Returns:
            True si se almacenó correctamente
        """
        try:
            # Calcular tamaño
            size_bytes = self._estimate_size(value)
            
            # Verificar espacio disponible
            if size_bytes > self.max_size_bytes:
                logger.warning(f"Valor demasiado grande para caché: {size_bytes} bytes")
                return False
            
            # Hacer espacio si es necesario
            await self._ensure_space(size_bytes)
            
            # Determinar TTL
            if ttl is None:
                ttl = self._calculate_adaptive_ttl(key) if self.strategy == CacheStrategy.ADAPTIVE else self.default_ttl
            
            # Crear entrada
            entry = CacheEntry(
                key=key,
                value=value,
                size_bytes=size_bytes,
                ttl=ttl,
                priority=priority
            )
            
            # Almacenar
            self._cache[key] = entry
            self._update_lru(key)
            
            # Actualizar estadísticas
            self.stats.total_size_bytes += size_bytes
            self.stats.entry_count = len(self._cache)
            
            logger.debug(f"Valor almacenado en caché: key={key}, size={size_bytes}, ttl={ttl}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error almacenando en caché: {e}")
            return False
    
    def invalidate(self, key: str) -> bool:
        """
        Invalida una entrada del caché.
        
        Args:
            key: Clave a invalidar
            
        Returns:
            True si se invalidó correctamente
        """
        if key in self._cache:
            entry = self._cache.pop(key)
            self.stats.total_size_bytes -= entry.size_bytes
            self.stats.entry_count = len(self._cache)
            
            if key in self._lru_order:
                del self._lru_order[key]
            
            logger.debug(f"Entrada invalidada: {key}")
            return True
        
        return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalida todas las entradas que coincidan con un patrón.
        
        Args:
            pattern: Patrón a buscar en las claves
            
        Returns:
            Número de entradas invalidadas
        """
        import re
        
        count = 0
        pattern_re = re.compile(pattern)
        
        keys_to_remove = [
            key for key in self._cache.keys()
            if pattern_re.search(key)
        ]
        
        for key in keys_to_remove:
            if self.invalidate(key):
                count += 1
        
        logger.info(f"Invalidadas {count} entradas con patrón: {pattern}")
        return count
    
    def clear(self):
        """Limpia todo el caché."""
        self._cache.clear()
        self._lru_order.clear()
        self._access_patterns.clear()
        
        self.stats.total_size_bytes = 0
        self.stats.entry_count = 0
        self.stats.evictions += len(self._cache)
        
        logger.info("Caché limpiado completamente")
    
    async def prewarm(self, 
                     key: str, 
                     loader: Callable, 
                     priority: float = 0.5,
                     ttl: Optional[float] = None):
        """
        Programa el precalentamiento de una entrada.
        
        Args:
            key: Clave a precalentar
            loader: Función para cargar el valor
            priority: Prioridad (0-1, menor = más prioritario)
            ttl: TTL personalizado
        """
        if not self.enable_prewarming:
            return
        
        # Agregar a la cola de precalentamiento
        heapq.heappush(self._prewarm_queue, (priority, key, loader))
        
        logger.debug(f"Precalentamiento programado: {key} (prioridad: {priority})")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché."""
        return {
            "hit_rate": f"{self.stats.hit_rate:.1f}%",
            "hits": self.stats.hits,
            "misses": self.stats.misses,
            "evictions": self.stats.evictions,
            "entry_count": self.stats.entry_count,
            "total_size_mb": self.stats.total_size_bytes / (1024 * 1024),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "utilization": f"{(self.stats.total_size_bytes / self.max_size_bytes * 100):.1f}%",
            "avg_hit_time_ms": self.stats.avg_hit_time_ms,
            "avg_miss_time_ms": self.stats.avg_miss_time_ms,
            "strategy": self.strategy.value,
            "prewarm_queue_size": len(self._prewarm_queue)
        }
    
    def _estimate_size(self, value: Any) -> int:
        """Estima el tamaño en bytes de un valor."""
        if isinstance(value, (str, bytes)):
            return len(value.encode('utf-8') if isinstance(value, str) else value)
        elif isinstance(value, (dict, list)):
            return len(json.dumps(value).encode('utf-8'))
        else:
            # Estimación aproximada
            return 256
    
    def _update_lru(self, key: str):
        """Actualiza el orden LRU."""
        if key in self._lru_order:
            self._lru_order.move_to_end(key)
        else:
            self._lru_order[key] = True
    
    def _record_access_pattern(self, key: str, hit: bool):
        """Registra patrón de acceso para estrategia adaptativa."""
        self._access_patterns[key].append({
            'timestamp': time.time(),
            'hit': hit
        })
        
        # Mantener solo los últimos 100 accesos
        if len(self._access_patterns[key]) > 100:
            self._access_patterns[key] = self._access_patterns[key][-100:]
    
    def _calculate_adaptive_ttl(self, key: str) -> float:
        """Calcula TTL adaptativo basado en patrones de acceso."""
        pattern = self._access_patterns.get(key, [])
        
        if len(pattern) < 2:
            return self.default_ttl
        
        # Calcular intervalos entre accesos
        intervals = []
        for i in range(1, len(pattern)):
            intervals.append(pattern[i]['timestamp'] - pattern[i-1]['timestamp'])
        
        if intervals:
            # TTL = promedio de intervalos * factor de seguridad
            avg_interval = sum(intervals) / len(intervals)
            return min(avg_interval * 1.5, self.default_ttl * 2)  # Max 2x default TTL
        
        return self.default_ttl
    
    async def _ensure_space(self, required_bytes: int):
        """Asegura que hay espacio suficiente en el caché."""
        while self.stats.total_size_bytes + required_bytes > self.max_size_bytes:
            # Necesitamos evictar algo
            if not self._cache:
                break
            
            # Seleccionar víctima según estrategia
            victim_key = self._select_eviction_victim()
            
            if victim_key:
                self.invalidate(victim_key)
                self.stats.evictions += 1
            else:
                break
    
    def _select_eviction_victim(self) -> Optional[str]:
        """Selecciona una entrada para evictar según la estrategia."""
        if not self._cache:
            return None
        
        # Primero eliminar entradas expiradas
        for key, entry in list(self._cache.items()):
            if entry.is_expired():
                return key
        
        # Luego aplicar estrategia
        if self.strategy == CacheStrategy.LRU:
            # Evictar el menos recientemente usado
            if self._lru_order:
                return next(iter(self._lru_order))
        
        elif self.strategy == CacheStrategy.LFU:
            # Evictar el menos frecuentemente usado
            min_key = min(self._cache.keys(), key=lambda k: self._cache[k].access_count)
            return min_key
        
        elif self.strategy == CacheStrategy.TTL:
            # Evictar el más antiguo
            min_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
            return min_key
        
        elif self.strategy == CacheStrategy.ADAPTIVE:
            # Estrategia adaptativa: combinar factores
            scores = {}
            current_time = time.time()
            
            for key, entry in self._cache.items():
                # No evictar entradas críticas
                if entry.priority == CachePriority.CRITICAL:
                    continue
                
                # Score = (tiempo_sin_acceso * peso_prioridad) / (accesos + 1)
                time_since_access = current_time - entry.last_accessed
                priority_weight = entry.priority.value
                score = (time_since_access * priority_weight) / (entry.access_count + 1)
                scores[key] = score
            
            if scores:
                return max(scores, key=scores.get)
        
        # Fallback: evictar cualquiera
        return next(iter(self._cache))
    
    def _update_avg_times(self):
        """Actualiza tiempos promedio de hit/miss."""
        if self._hit_times:
            self.stats.avg_hit_time_ms = sum(self._hit_times[-100:]) / len(self._hit_times[-100:]) * 1000
        
        if self._miss_times:
            self.stats.avg_miss_time_ms = sum(self._miss_times[-100:]) / len(self._miss_times[-100:]) * 1000
    
    async def _prewarm_loop(self):
        """Loop de precalentamiento del caché."""
        while self._running:
            try:
                if self._prewarm_queue:
                    # Obtener siguiente item a precalentar
                    priority, key, loader = heapq.heappop(self._prewarm_queue)
                    
                    # Verificar si ya está en caché
                    if key not in self._cache:
                        logger.debug(f"Precalentando: {key}")
                        await self.get(key, loader)
                    
                    # Pequeña pausa para no saturar
                    await asyncio.sleep(0.1)
                else:
                    # No hay items, esperar más
                    await asyncio.sleep(1)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en loop de precalentamiento: {e}")
                await asyncio.sleep(1)
    
    async def _cleanup_loop(self):
        """Loop de limpieza periódica."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Cada minuto
                
                # Limpiar entradas expiradas
                expired_count = 0
                for key in list(self._cache.keys()):
                    if key in self._cache and self._cache[key].is_expired():
                        self.invalidate(key)
                        expired_count += 1
                
                if expired_count > 0:
                    logger.info(f"Limpiadas {expired_count} entradas expiradas del caché")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en loop de limpieza: {e}")


# Instancia global del optimizador
memory_cache = MemoryCacheOptimizer()


# Funciones de conveniencia
async def cache_get(key: str, loader: Optional[Callable] = None) -> Optional[Any]:
    """
    Obtiene un valor del caché optimizado.
    
    Args:
        key: Clave a buscar
        loader: Función para cargar si no está en caché
        
    Returns:
        Valor del caché o None
    """
    return await memory_cache.get(key, loader)


async def cache_set(key: str, 
                   value: Any, 
                   ttl: Optional[float] = None,
                   priority: str = "normal") -> bool:
    """
    Almacena un valor en el caché optimizado.
    
    Args:
        key: Clave para almacenar
        value: Valor a almacenar
        ttl: TTL en segundos (None = default)
        priority: Prioridad ('critical', 'high', 'normal', 'low')
        
    Returns:
        True si se almacenó correctamente
    """
    priority_map = {
        'critical': CachePriority.CRITICAL,
        'high': CachePriority.HIGH,
        'normal': CachePriority.NORMAL,
        'low': CachePriority.LOW
    }
    
    cache_priority = priority_map.get(priority, CachePriority.NORMAL)
    return await memory_cache.set(key, value, ttl, cache_priority)


def cache_invalidate(key: str) -> bool:
    """Invalida una entrada del caché."""
    return memory_cache.invalidate(key)


def cache_stats() -> Dict[str, Any]:
    """Obtiene estadísticas del caché."""
    return memory_cache.get_stats()


async def initialize_memory_cache():
    """Inicializa el sistema de caché optimizado."""
    await memory_cache.start()
    logger.info("✅ FASE 12 QUICK WIN #3: Memory Cache Optimizer inicializado - Esperada mejora 25% en response time")


async def shutdown_memory_cache():
    """Cierra el sistema de caché optimizado."""
    await memory_cache.stop()
    logger.info("Memory Cache Optimizer cerrado correctamente")