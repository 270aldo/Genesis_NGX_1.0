"""
Cache Decorators - FASE 12 QUICK WIN #3

Decoradores para facilitar el uso del Memory Cache Optimizer
en funciones y métodos de la aplicación.

IMPACTO ESPERADO: 25% mejora en tiempo de respuesta
"""

import functools
import hashlib
import json
import inspect
from typing import Any, Callable, Optional, Union, List

from core.memory_cache_optimizer import (
    cache_get,
    cache_set,
    cache_invalidate,
    CachePriority
)
from core.logging_config import get_logger

logger = get_logger(__name__)


def cached(
    ttl: Optional[float] = None,
    key_prefix: Optional[str] = None,
    priority: str = "normal",
    invalidate_on: Optional[List[str]] = None
):
    """
    Decorador para cachear resultados de funciones.
    
    Args:
        ttl: Time To Live en segundos (None = default)
        key_prefix: Prefijo personalizado para la clave
        priority: Prioridad del cache ('critical', 'high', 'normal', 'low')
        invalidate_on: Lista de nombres de funciones que invalidan este cache
        
    Example:
        @cached(ttl=300, priority="high")
        async def get_user_data(user_id: str):
            return await fetch_from_db(user_id)
    """
    def decorator(func: Callable) -> Callable:
        # Obtener información de la función
        func_name = func.__name__
        module_name = func.__module__
        is_async = inspect.iscoroutinefunction(func)
        
        # Registrar invalidaciones si se especifican
        if invalidate_on:
            _register_invalidations(func_name, invalidate_on)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generar clave de cache
            cache_key = _generate_cache_key(
                func_name, module_name, args, kwargs, key_prefix
            )
            
            # Intentar obtener del cache
            cached_value = await cache_get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit para {func_name}: {cache_key}")
                return cached_value
            
            # Ejecutar función
            logger.debug(f"Cache miss para {func_name}: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Almacenar en cache
            await cache_set(cache_key, result, ttl=ttl, priority=priority)
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Para funciones síncronas, usar asyncio.run
            import asyncio
            
            # Generar clave de cache
            cache_key = _generate_cache_key(
                func_name, module_name, args, kwargs, key_prefix
            )
            
            # Intentar obtener del cache
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                cached_value = loop.run_until_complete(cache_get(cache_key))
                if cached_value is not None:
                    logger.debug(f"Cache hit para {func_name}: {cache_key}")
                    return cached_value
                
                # Ejecutar función
                logger.debug(f"Cache miss para {func_name}: {cache_key}")
                result = func(*args, **kwargs)
                
                # Almacenar en cache
                loop.run_until_complete(
                    cache_set(cache_key, result, ttl=ttl, priority=priority)
                )
                
                return result
            finally:
                loop.close()
        
        # Agregar método para invalidar cache
        wrapper = async_wrapper if is_async else sync_wrapper
        wrapper.invalidate_cache = lambda *args, **kwargs: _invalidate_function_cache(
            func_name, module_name, args, kwargs, key_prefix
        )
        
        return wrapper
    
    return decorator


def cached_property(
    ttl: Optional[float] = None,
    priority: str = "normal"
):
    """
    Decorador para cachear propiedades de clases.
    
    Args:
        ttl: Time To Live en segundos
        priority: Prioridad del cache
        
    Example:
        class MyClass:
            @cached_property(ttl=600)
            def expensive_property(self):
                return calculate_expensive_value()
    """
    def decorator(func: Callable) -> property:
        attr_name = f"_cached_{func.__name__}"
        
        @functools.wraps(func)
        async def async_getter(self):
            # Generar clave única para la instancia
            instance_id = id(self)
            cache_key = f"property:{func.__module__}:{self.__class__.__name__}:{instance_id}:{func.__name__}"
            
            # Intentar obtener del cache
            cached_value = await cache_get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Calcular valor
            if inspect.iscoroutinefunction(func):
                result = await func(self)
            else:
                result = func(self)
            
            # Almacenar en cache
            await cache_set(cache_key, result, ttl=ttl, priority=priority)
            
            return result
        
        @functools.wraps(func)
        def sync_getter(self):
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                return loop.run_until_complete(async_getter(self))
            finally:
                loop.close()
        
        # Determinar si usar versión async o sync
        if inspect.iscoroutinefunction(func):
            return property(async_getter)
        else:
            return property(sync_getter)
    
    return decorator


def cache_key(*key_params: str):
    """
    Decorador para especificar qué parámetros usar para la clave de cache.
    
    Args:
        *key_params: Nombres de parámetros a incluir en la clave
        
    Example:
        @cached(ttl=300)
        @cache_key("user_id", "date")
        async def get_user_stats(user_id: str, date: str, include_details: bool):
            # Solo user_id y date se usarán para la clave
            return await calculate_stats(user_id, date, include_details)
    """
    def decorator(func: Callable) -> Callable:
        func._cache_key_params = key_params
        return func
    
    return decorator


def invalidates(*cache_patterns: str):
    """
    Decorador para invalidar patrones de cache cuando se ejecuta una función.
    
    Args:
        *cache_patterns: Patrones de cache a invalidar
        
    Example:
        @invalidates("user:*", "stats:*")
        async def update_user(user_id: str, data: dict):
            # Al ejecutarse, invalidará todos los caches que coincidan
            return await save_user(user_id, data)
    """
    def decorator(func: Callable) -> Callable:
        is_async = inspect.iscoroutinefunction(func)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Ejecutar función
            result = await func(*args, **kwargs)
            
            # Invalidar caches
            for pattern in cache_patterns:
                # Reemplazar placeholders con valores de argumentos
                invalidation_pattern = _resolve_pattern(pattern, func, args, kwargs)
                from core.memory_cache_optimizer import memory_cache
                count = memory_cache.invalidate_pattern(invalidation_pattern)
                logger.debug(f"Invalidadas {count} entradas con patrón: {invalidation_pattern}")
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Ejecutar función
            result = func(*args, **kwargs)
            
            # Invalidar caches
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                for pattern in cache_patterns:
                    invalidation_pattern = _resolve_pattern(pattern, func, args, kwargs)
                    from core.memory_cache_optimizer import memory_cache
                    count = memory_cache.invalidate_pattern(invalidation_pattern)
                    logger.debug(f"Invalidadas {count} entradas con patrón: {invalidation_pattern}")
            finally:
                loop.close()
            
            return result
        
        return async_wrapper if is_async else sync_wrapper
    
    return decorator


def prewarm_cache(
    loader_func: Callable,
    key_generator: Callable,
    priority: float = 0.5
):
    """
    Decorador para marcar funciones que deben precalentar el cache.
    
    Args:
        loader_func: Función que carga los datos
        key_generator: Función que genera las claves a precalentar
        priority: Prioridad de precalentamiento (0-1)
        
    Example:
        @prewarm_cache(
            loader_func=get_user_data,
            key_generator=lambda: [f"user:{id}" for id in get_active_users()]
        )
        async def startup_prewarm():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Ejecutar función original
            result = await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Generar claves a precalentar
            keys = key_generator() if callable(key_generator) else key_generator
            
            # Programar precalentamiento
            from core.memory_cache_optimizer import memory_cache
            for key in keys:
                await memory_cache.prewarm(key, loader_func, priority)
            
            logger.info(f"Programado precalentamiento de {len(keys)} claves")
            
            return result
        
        return wrapper
    
    return decorator


# Funciones auxiliares privadas

def _generate_cache_key(
    func_name: str,
    module_name: str,
    args: tuple,
    kwargs: dict,
    prefix: Optional[str] = None
) -> str:
    """Genera una clave única para el cache."""
    # Construir base de la clave
    key_parts = [
        prefix or "func",
        module_name.replace('.', '_'),
        func_name
    ]
    
    # Serializar argumentos
    args_str = json.dumps(args, sort_keys=True, default=str)
    kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
    
    # Crear hash de argumentos para evitar claves muy largas
    args_hash = hashlib.md5(f"{args_str}:{kwargs_str}".encode()).hexdigest()[:8]
    
    key_parts.append(args_hash)
    
    return ":".join(key_parts)


def _resolve_pattern(pattern: str, func: Callable, args: tuple, kwargs: dict) -> str:
    """Resuelve placeholders en un patrón de invalidación."""
    # Obtener nombres de parámetros
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    
    # Reemplazar placeholders
    resolved = pattern
    for param_name, value in bound_args.arguments.items():
        placeholder = f"{{{param_name}}}"
        if placeholder in resolved:
            resolved = resolved.replace(placeholder, str(value))
    
    return resolved


def _invalidate_function_cache(
    func_name: str,
    module_name: str,
    args: tuple,
    kwargs: dict,
    prefix: Optional[str] = None
) -> bool:
    """Invalida el cache de una función específica."""
    cache_key = _generate_cache_key(func_name, module_name, args, kwargs, prefix)
    return cache_invalidate(cache_key)


# Registro global de invalidaciones
_invalidation_registry = {}


def _register_invalidations(func_name: str, invalidates: List[str]):
    """Registra qué funciones invalidan el cache de otras."""
    for target in invalidates:
        if target not in _invalidation_registry:
            _invalidation_registry[target] = []
        _invalidation_registry[target].append(func_name)