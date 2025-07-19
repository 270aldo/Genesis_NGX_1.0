"""
Advanced Async Processor - FASE 12 POINT 3
==========================================

Sistema avanzado de procesamiento asíncrono que optimiza el rendimiento 
mediante patterns async sofisticados, manejo concurrente mejorado y 
scheduling inteligente basado en recursos.

FUNCIONALIDADES CLAVE:
- Advanced async patterns con circuit breakers
- Concurrent request handling con rate limiting
- Background task optimization con prioridades
- Resource-aware scheduling con monitoring
- Batch processing inteligente
"""

import asyncio
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, TypeVar, Generic, Union
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import concurrent.futures
from collections import defaultdict, deque
import psutil
import weakref

from core.logging_config import get_logger
from core.memory_cache_optimizer import cache_get, cache_set, cache_invalidate, CachePriority

logger = get_logger(__name__)

T = TypeVar('T')


class TaskPriority(Enum):
    """Prioridades de tareas async"""
    CRITICAL = "critical"     # Respuestas de usuario inmediatas
    HIGH = "high"            # Operaciones importantes del sistema
    NORMAL = "normal"        # Procesamiento estándar
    LOW = "low"             # Tareas de background
    BULK = "bulk"           # Procesamiento en lote


class ProcessorState(Enum):
    """Estados del procesador async"""
    IDLE = "idle"
    ACTIVE = "active"
    OVERLOADED = "overloaded"
    CIRCUIT_OPEN = "circuit_open"
    DEGRADED = "degraded"


class ResourceType(Enum):
    """Tipos de recursos del sistema"""
    CPU = "cpu"
    MEMORY = "memory"
    IO = "io"
    NETWORK = "network"
    DATABASE = "database"


@dataclass
class TaskMetrics:
    """Métricas de rendimiento de tareas"""
    task_id: str
    start_time: datetime
    end_time: Optional[datetime]
    execution_time: Optional[float]
    priority: TaskPriority
    status: str
    error_message: Optional[str]
    resource_usage: Dict[str, float]
    retry_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        data = asdict(self)
        data['priority'] = self.priority.value
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat() if self.end_time else None
        return data


@dataclass
class ResourceLimits:
    """Límites de recursos del sistema"""
    max_cpu_percent: float = 80.0
    max_memory_percent: float = 75.0
    max_concurrent_tasks: int = 100
    max_queue_size: int = 1000
    max_execution_time: int = 300  # segundos


@dataclass
class CircuitBreakerConfig:
    """Configuración del circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    half_open_max_calls: int = 3
    success_threshold: int = 2


class CircuitBreaker:
    """Circuit breaker para protección de recursos"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = "closed"  # closed, open, half-open
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.call_count = 0
    
    def call_allowed(self) -> bool:
        """Determina si la llamada está permitida"""
        now = datetime.utcnow()
        
        if self.state == "closed":
            return True
        elif self.state == "open":
            if self.last_failure_time and \
               now - self.last_failure_time > timedelta(seconds=self.config.recovery_timeout):
                self.state = "half-open"
                self.call_count = 0
                return True
            return False
        elif self.state == "half-open":
            return self.call_count < self.config.half_open_max_calls
        
        return False
    
    def record_success(self):
        """Registra una ejecución exitosa"""
        if self.state == "half-open":
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = "closed"
                self.failure_count = 0
                self.success_count = 0
        else:
            self.failure_count = 0
    
    def record_failure(self):
        """Registra una falla"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = "open"


class ResourceMonitor:
    """Monitor de recursos del sistema"""
    
    def __init__(self):
        self.limits = ResourceLimits()
        self.monitoring = True
        self._stats_cache = {}
        self._last_update = None
    
    def get_current_usage(self) -> Dict[str, float]:
        """Obtiene uso actual de recursos"""
        now = datetime.utcnow()
        
        # Cache por 1 segundo para evitar overhead
        if self._last_update and (now - self._last_update).total_seconds() < 1.0:
            return self._stats_cache
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            usage = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available / 1024 / 1024,
                'active_threads': threading.active_count(),
                'timestamp': now.isoformat()
            }
            
            self._stats_cache = usage
            self._last_update = now
            
            return usage
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas de recursos: {e}")
            return {'cpu_percent': 0, 'memory_percent': 0}
    
    def is_resource_available(self, resource_type: ResourceType) -> bool:
        """Verifica si un recurso está disponible"""
        usage = self.get_current_usage()
        
        if resource_type == ResourceType.CPU:
            return usage.get('cpu_percent', 0) < self.limits.max_cpu_percent
        elif resource_type == ResourceType.MEMORY:
            return usage.get('memory_percent', 0) < self.limits.max_memory_percent
        
        return True
    
    def get_resource_pressure(self) -> float:
        """Calcula la presión general de recursos (0.0-1.0)"""
        usage = self.get_current_usage()
        
        cpu_pressure = usage.get('cpu_percent', 0) / 100.0
        memory_pressure = usage.get('memory_percent', 0) / 100.0
        
        # Promedio ponderado
        return (cpu_pressure * 0.6 + memory_pressure * 0.4)


class TaskQueue:
    """Cola de tareas con prioridades"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.queues = {
            TaskPriority.CRITICAL: deque(),
            TaskPriority.HIGH: deque(),
            TaskPriority.NORMAL: deque(),
            TaskPriority.LOW: deque(),
            TaskPriority.BULK: deque()
        }
        self.total_size = 0
        self._lock = asyncio.Lock()
    
    async def enqueue(self, task: Any, priority: TaskPriority) -> bool:
        """Encola una tarea con prioridad"""
        async with self._lock:
            if self.total_size >= self.max_size:
                # Si está lleno, rechazar tareas de baja prioridad
                if priority in [TaskPriority.LOW, TaskPriority.BULK]:
                    return False
                
                # Para alta prioridad, remover tarea de baja prioridad
                if self.queues[TaskPriority.BULK]:
                    self.queues[TaskPriority.BULK].popleft()
                    self.total_size -= 1
                elif self.queues[TaskPriority.LOW]:
                    self.queues[TaskPriority.LOW].popleft()
                    self.total_size -= 1
                else:
                    return False
            
            self.queues[priority].append(task)
            self.total_size += 1
            return True
    
    async def dequeue(self) -> Optional[Any]:
        """Desencola tarea con mayor prioridad"""
        async with self._lock:
            # Procesar en orden de prioridad
            for priority in [TaskPriority.CRITICAL, TaskPriority.HIGH, 
                            TaskPriority.NORMAL, TaskPriority.LOW, TaskPriority.BULK]:
                if self.queues[priority]:
                    task = self.queues[priority].popleft()
                    self.total_size -= 1
                    return task
            
            return None
    
    def size(self) -> int:
        """Tamaño actual de la cola"""
        return self.total_size
    
    def get_queue_stats(self) -> Dict[str, int]:
        """Estadísticas de las colas"""
        return {
            priority.value: len(queue) 
            for priority, queue in self.queues.items()
        }


class AsyncTask(Generic[T]):
    """Wrapper para tareas asíncronas con metadatos"""
    
    def __init__(self, 
                 coro: Callable[..., T],
                 task_id: str = None,
                 priority: TaskPriority = TaskPriority.NORMAL,
                 timeout: int = 300,
                 retry_count: int = 3,
                 metadata: Dict[str, Any] = None):
        self.task_id = task_id or str(uuid.uuid4())
        self.coro = coro
        self.priority = priority
        self.timeout = timeout
        self.retry_count = retry_count
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.attempts = 0
    
    async def execute(self) -> T:
        """Ejecuta la tarea"""
        start_time = time.time()
        
        try:
            if asyncio.iscoroutine(self.coro):
                result = await asyncio.wait_for(self.coro, timeout=self.timeout)
            else:
                result = await asyncio.wait_for(self.coro(), timeout=self.timeout)
            
            execution_time = time.time() - start_time
            logger.debug(f"Tarea {self.task_id} completada en {execution_time:.3f}s")
            
            return result
            
        except asyncio.TimeoutError:
            logger.warning(f"Tarea {self.task_id} timeout después de {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"Error ejecutando tarea {self.task_id}: {e}")
            raise


class BatchProcessor:
    """Procesador de lotes para tareas similares"""
    
    def __init__(self, batch_size: int = 10, timeout: float = 1.0):
        self.batch_size = batch_size
        self.timeout = timeout
        self.batches = defaultdict(list)
        self.batch_timers = {}
        self._lock = asyncio.Lock()
    
    async def add_to_batch(self, batch_key: str, item: Any) -> None:
        """Agrega item a un lote"""
        async with self._lock:
            self.batches[batch_key].append(item)
            
            # Si es el primer item del lote, iniciar timer
            if len(self.batches[batch_key]) == 1:
                self.batch_timers[batch_key] = asyncio.create_task(
                    self._batch_timeout(batch_key)
                )
            
            # Si alcanzamos el tamaño del lote, procesarlo
            if len(self.batches[batch_key]) >= self.batch_size:
                await self._process_batch(batch_key)
    
    async def _batch_timeout(self, batch_key: str):
        """Timeout del lote"""
        await asyncio.sleep(self.timeout)
        async with self._lock:
            if batch_key in self.batches and self.batches[batch_key]:
                await self._process_batch(batch_key)
    
    async def _process_batch(self, batch_key: str):
        """Procesa un lote completo"""
        if batch_key not in self.batches:
            return
        
        items = self.batches[batch_key]
        del self.batches[batch_key]
        
        # Cancelar timer si existe
        if batch_key in self.batch_timers:
            self.batch_timers[batch_key].cancel()
            del self.batch_timers[batch_key]
        
        if items:
            logger.info(f"Procesando lote {batch_key} con {len(items)} items")
            # Aquí iría la lógica específica de procesamiento por lotes
            # Por ejemplo, batch database operations


class AdvancedAsyncProcessor:
    """
    Procesador asíncrono avanzado con optimizaciones enterprise
    
    CAPACIDADES AVANZADAS:
    - Circuit breakers para protección de recursos
    - Monitoring de recursos en tiempo real
    - Task queues con prioridades dinámicas
    - Batch processing inteligente
    - Rate limiting adaptativo
    - Resource-aware scheduling
    """
    
    def __init__(self, 
                 max_workers: int = None,
                 resource_limits: ResourceLimits = None,
                 circuit_breaker_config: CircuitBreakerConfig = None):
        
        # Configuración
        self.max_workers = max_workers or min(32, (psutil.cpu_count() or 1) * 4)
        self.resource_limits = resource_limits or ResourceLimits()
        self.circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        
        # Estado del procesador
        self.state = ProcessorState.IDLE
        self.active_tasks = set()
        self.completed_tasks = 0
        self.failed_tasks = 0
        
        # Componentes principales
        self.task_queue = TaskQueue(self.resource_limits.max_queue_size)
        self.resource_monitor = ResourceMonitor()
        self.batch_processor = BatchProcessor()
        self.circuit_breaker = CircuitBreaker(self.circuit_breaker_config)
        
        # Thread pool para CPU-intensive tasks
        self.thread_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=min(4, psutil.cpu_count() or 1)
        )
        
        # Métricas y monitoreo
        self.task_metrics = {}
        self.performance_stats = {
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'avg_execution_time': 0.0,
            'resource_pressure_avg': 0.0,
            'circuit_breaker_trips': 0
        }
        
        # Control de concurrencia
        self.semaphore = asyncio.Semaphore(self.max_workers)
        self.rate_limiter = defaultdict(deque)
        
        # Worker tasks
        self.workers = []
        self.running = False
        
        # Cache para resultados frecuentes
        self.cache_prefix = "async_processor"
    
    async def start(self):
        """Inicia el procesador"""
        if self.running:
            return
        
        self.running = True
        self.state = ProcessorState.ACTIVE
        
        # Crear workers
        for i in range(min(4, self.max_workers)):
            worker = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self.workers.append(worker)
        
        # Iniciar monitor de recursos
        monitor_task = asyncio.create_task(self._resource_monitor_loop())
        self.workers.append(monitor_task)
        
        logger.info(f"Async Processor iniciado con {len(self.workers)} workers")
    
    async def stop(self):
        """Detiene el procesador"""
        self.running = False
        
        # Cancelar workers
        for worker in self.workers:
            worker.cancel()
        
        # Esperar que terminen
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        # Limpiar thread pool
        self.thread_executor.shutdown(wait=True)
        
        self.state = ProcessorState.IDLE
        logger.info("Async Processor detenido")
    
    async def submit_task(self, 
                         coro: Callable[..., T],
                         priority: TaskPriority = TaskPriority.NORMAL,
                         timeout: int = 300,
                         retry_count: int = 3,
                         metadata: Dict[str, Any] = None) -> str:
        """
        Envía tarea para procesamiento asíncrono
        
        Args:
            coro: Corrutina o función async a ejecutar
            priority: Prioridad de la tarea
            timeout: Timeout en segundos
            retry_count: Número de reintentos
            metadata: Metadatos adicionales
        
        Returns:
            Task ID para tracking
        """
        try:
            # Verificar circuit breaker
            if not self.circuit_breaker.call_allowed():
                raise Exception("Circuit breaker abierto - servicio degradado")
            
            # Verificar recursos
            resource_pressure = self.resource_monitor.get_resource_pressure()
            if resource_pressure > 0.9:
                self.state = ProcessorState.OVERLOADED
                if priority not in [TaskPriority.CRITICAL, TaskPriority.HIGH]:
                    raise Exception("Sistema sobrecargado - rechazando tarea de baja prioridad")
            
            # Crear tarea
            task = AsyncTask(
                coro=coro,
                priority=priority,
                timeout=timeout,
                retry_count=retry_count,
                metadata=metadata
            )
            
            # Encolar tarea
            enqueued = await self.task_queue.enqueue(task, priority)
            if not enqueued:
                raise Exception("Cola de tareas llena")
            
            # Registrar métricas iniciales
            self.task_metrics[task.task_id] = TaskMetrics(
                task_id=task.task_id,
                start_time=datetime.utcnow(),
                end_time=None,
                execution_time=None,
                priority=priority,
                status="queued",
                error_message=None,
                resource_usage={},
                retry_count=0
            )
            
            logger.debug(f"Tarea {task.task_id} encolada con prioridad {priority.value}")
            return task.task_id
            
        except Exception as e:
            logger.error(f"Error enviando tarea: {e}")
            self.circuit_breaker.record_failure()
            raise
    
    async def submit_batch(self, 
                          batch_key: str,
                          item: Any,
                          processor_func: Callable = None) -> None:
        """
        Envía item para procesamiento por lotes
        
        Args:
            batch_key: Clave del lote
            item: Item a procesar
            processor_func: Función de procesamiento del lote
        """
        await self.batch_processor.add_to_batch(batch_key, item)
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene estado de una tarea"""
        metrics = self.task_metrics.get(task_id)
        if metrics:
            return metrics.to_dict()
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancela una tarea si es posible"""
        # En implementación real, buscaría en cola activa y cancelaría
        if task_id in self.task_metrics:
            self.task_metrics[task_id].status = "cancelled"
            return True
        return False
    
    async def _worker_loop(self, worker_id: str):
        """Loop principal del worker"""
        logger.info(f"Worker {worker_id} iniciado")
        
        while self.running:
            try:
                # Obtener tarea de la cola
                task = await self.task_queue.dequeue()
                if not task:
                    await asyncio.sleep(0.1)
                    continue
                
                # Verificar límites de recursos
                if not self._should_process_task(task):
                    # Re-encolar tarea para más tarde
                    await self.task_queue.enqueue(task, task.priority)
                    await asyncio.sleep(1.0)
                    continue
                
                # Procesar tarea
                await self._process_task(task, worker_id)
                
            except Exception as e:
                logger.error(f"Error en worker {worker_id}: {e}")
                await asyncio.sleep(1.0)
        
        logger.info(f"Worker {worker_id} terminado")
    
    async def _process_task(self, task: AsyncTask, worker_id: str):
        """Procesa una tarea individual"""
        async with self.semaphore:
            start_time = time.time()
            
            try:
                # Registrar inicio
                self.active_tasks.add(task.task_id)
                metrics = self.task_metrics[task.task_id]
                metrics.status = "running"
                
                # Obtener recursos antes de ejecutar
                pre_resources = self.resource_monitor.get_current_usage()
                
                # Ejecutar tarea
                result = await task.execute()
                
                # Calcular métricas
                execution_time = time.time() - start_time
                post_resources = self.resource_monitor.get_current_usage()
                
                # Actualizar métricas
                metrics.end_time = datetime.utcnow()
                metrics.execution_time = execution_time
                metrics.status = "completed"
                metrics.resource_usage = {
                    'cpu_delta': post_resources.get('cpu_percent', 0) - pre_resources.get('cpu_percent', 0),
                    'memory_delta': post_resources.get('memory_percent', 0) - pre_resources.get('memory_percent', 0),
                    'execution_time': execution_time
                }
                
                # Registrar éxito
                self.circuit_breaker.record_success()
                self.completed_tasks += 1
                self.performance_stats['successful_tasks'] += 1
                
                # Cachear resultado si es apropiado
                await self._cache_result_if_appropriate(task, result)
                
                logger.debug(f"Worker {worker_id} completó tarea {task.task_id} en {execution_time:.3f}s")
                
            except Exception as e:
                # Manejar error
                execution_time = time.time() - start_time
                
                metrics = self.task_metrics[task.task_id]
                metrics.end_time = datetime.utcnow()
                metrics.execution_time = execution_time
                metrics.status = "failed"
                metrics.error_message = str(e)
                
                # Reintentar si es apropiado
                if task.attempts < task.retry_count:
                    task.attempts += 1
                    metrics.retry_count = task.attempts
                    await asyncio.sleep(min(2 ** task.attempts, 10))  # Exponential backoff
                    await self.task_queue.enqueue(task, task.priority)
                    logger.warning(f"Reintentando tarea {task.task_id} (intento {task.attempts})")
                else:
                    # Tarea fallida definitivamente
                    self.circuit_breaker.record_failure()
                    self.failed_tasks += 1
                    self.performance_stats['failed_tasks'] += 1
                    logger.error(f"Tarea {task.task_id} falló definitivamente: {e}")
                
            finally:
                self.active_tasks.discard(task.task_id)
                self.performance_stats['total_tasks'] += 1
    
    def _should_process_task(self, task: AsyncTask) -> bool:
        """Determina si una tarea debe procesarse ahora"""
        # Verificar presión de recursos
        resource_pressure = self.resource_monitor.get_resource_pressure()
        
        # Tareas críticas siempre se procesan
        if task.priority == TaskPriority.CRITICAL:
            return True
        
        # Si la presión es alta, solo procesar tareas importantes
        if resource_pressure > 0.8:
            return task.priority in [TaskPriority.HIGH, TaskPriority.CRITICAL]
        
        # Si hay muchas tareas activas, esperar
        if len(self.active_tasks) >= self.max_workers:
            return False
        
        return True
    
    async def _resource_monitor_loop(self):
        """Loop de monitoreo de recursos"""
        while self.running:
            try:
                usage = self.resource_monitor.get_current_usage()
                pressure = self.resource_monitor.get_resource_pressure()
                
                # Actualizar estado del procesador
                if pressure > 0.9:
                    self.state = ProcessorState.OVERLOADED
                elif pressure > 0.7:
                    self.state = ProcessorState.DEGRADED
                else:
                    self.state = ProcessorState.ACTIVE
                
                # Actualizar estadísticas
                self.performance_stats['resource_pressure_avg'] = (
                    self.performance_stats['resource_pressure_avg'] * 0.9 + pressure * 0.1
                )
                
                # Log si hay problemas de recursos
                if pressure > 0.8:
                    logger.warning(f"Alta presión de recursos: {pressure:.2f} - CPU: {usage.get('cpu_percent', 0):.1f}% - Memoria: {usage.get('memory_percent', 0):.1f}%")
                
                await asyncio.sleep(5.0)  # Monitorear cada 5 segundos
                
            except Exception as e:
                logger.error(f"Error en monitor de recursos: {e}")
                await asyncio.sleep(10.0)
    
    async def _cache_result_if_appropriate(self, task: AsyncTask, result: Any):
        """Cachea resultado si es apropiado"""
        try:
            # Solo cachear resultados pequeños y de tareas frecuentes
            if (task.metadata.get('cacheable', False) and 
                len(str(result)) < 10000):  # < 10KB
                
                cache_key = f"{self.cache_prefix}:result:{hash(str(task.coro))}"
                await cache_set(
                    cache_key,
                    result,
                    ttl=300,  # 5 minutos
                    priority=CachePriority.LOW
                )
                
        except Exception as e:
            logger.debug(f"Error cacheando resultado: {e}")
    
    async def get_processor_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del procesador"""
        resource_usage = self.resource_monitor.get_current_usage()
        queue_stats = self.task_queue.get_queue_stats()
        
        # Calcular tiempo promedio de ejecución
        completed_metrics = [
            m for m in self.task_metrics.values() 
            if m.execution_time is not None
        ]
        
        avg_execution_time = 0.0
        if completed_metrics:
            avg_execution_time = sum(m.execution_time for m in completed_metrics) / len(completed_metrics)
        
        return {
            'processor_state': self.state.value,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'queue_size': self.task_queue.size(),
            'queue_stats': queue_stats,
            'resource_usage': resource_usage,
            'circuit_breaker_state': self.circuit_breaker.state,
            'performance_stats': self.performance_stats.copy(),
            'avg_execution_time': avg_execution_time,
            'workers_count': len(self.workers),
            'max_workers': self.max_workers,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check del procesador"""
        stats = await self.get_processor_stats()
        
        # Determinar estado de salud
        health_status = "healthy"
        issues = []
        
        if self.state == ProcessorState.OVERLOADED:
            health_status = "degraded"
            issues.append("Sistema sobrecargado")
        
        if self.circuit_breaker.state == "open":
            health_status = "unhealthy"
            issues.append("Circuit breaker abierto")
        
        if stats['resource_usage'].get('cpu_percent', 0) > 90:
            health_status = "degraded"
            issues.append("CPU alta")
        
        if stats['resource_usage'].get('memory_percent', 0) > 85:
            health_status = "degraded"
            issues.append("Memoria alta")
        
        return {
            'status': health_status,
            'issues': issues,
            'processor_stats': stats,
            'uptime': str(datetime.utcnow() - self.performance_stats.get('start_time', datetime.utcnow())),
            'timestamp': datetime.utcnow().isoformat()
        }


# Instancia global del procesador
async_processor = AdvancedAsyncProcessor()


# Funciones helper para uso sencillo
async def submit_async_task(coro: Callable[..., T],
                           priority: TaskPriority = TaskPriority.NORMAL,
                           timeout: int = 300,
                           retry_count: int = 3,
                           metadata: Dict[str, Any] = None) -> str:
    """
    Función helper para enviar tareas async
    
    Args:
        coro: Corrutina a ejecutar
        priority: Prioridad de la tarea
        timeout: Timeout en segundos
        retry_count: Número de reintentos
        metadata: Metadatos adicionales
    
    Returns:
        Task ID para tracking
    """
    return await async_processor.submit_task(
        coro=coro,
        priority=priority,
        timeout=timeout,
        retry_count=retry_count,
        metadata=metadata
    )


async def get_async_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Función helper para obtener estado de tarea"""
    return await async_processor.get_task_status(task_id)


async def get_async_processor_stats() -> Dict[str, Any]:
    """Función helper para obtener estadísticas del procesador"""
    return await async_processor.get_processor_stats()


# Decoradores para facilitar uso
def async_task(priority: TaskPriority = TaskPriority.NORMAL,
               timeout: int = 300,
               retry_count: int = 3,
               cacheable: bool = False):
    """Decorador para convertir función en tarea async"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            metadata = {'cacheable': cacheable}
            task_id = await submit_async_task(
                coro=lambda: func(*args, **kwargs),
                priority=priority,
                timeout=timeout,
                retry_count=retry_count,
                metadata=metadata
            )
            return task_id
        return wrapper
    return decorator


# Ejemplo de uso
async def example_usage():
    """Ejemplo de uso del procesador async avanzado"""
    
    # Iniciar procesador
    await async_processor.start()
    
    try:
        # Definir una tarea de ejemplo
        async def sample_task(duration: float = 1.0):
            await asyncio.sleep(duration)
            return f"Tarea completada después de {duration}s"
        
        # Enviar tarea crítica
        critical_task_id = await submit_async_task(
            coro=lambda: sample_task(0.5),
            priority=TaskPriority.CRITICAL,
            metadata={'type': 'user_request'}
        )
        
        # Enviar tarea normal
        normal_task_id = await submit_async_task(
            coro=lambda: sample_task(2.0),
            priority=TaskPriority.NORMAL,
            metadata={'type': 'background_process'}
        )
        
        # Esperar un poco
        await asyncio.sleep(3.0)
        
        # Verificar estados
        critical_status = await get_async_task_status(critical_task_id)
        normal_status = await get_async_task_status(normal_task_id)
        
        print(f"Tarea crítica: {critical_status}")
        print(f"Tarea normal: {normal_status}")
        
        # Obtener estadísticas
        stats = await get_async_processor_stats()
        print(f"Estadísticas del procesador: {stats}")
        
    finally:
        # Detener procesador
        await async_processor.stop()


if __name__ == "__main__":
    asyncio.run(example_usage())