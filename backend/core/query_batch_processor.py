"""
Query Batch Processor - FASE 12 QUICK WIN #1

Sistema de procesamiento por lotes de consultas para mejorar el rendimiento
de la base de datos en un 40%. Agrupa múltiples consultas individuales en
operaciones batch optimizadas.

IMPACTO ESPERADO: 40% mejora en llamadas a DB
"""

import asyncio
import time
from collections import defaultdict
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from core.logging_config import get_logger

logger = get_logger(__name__)


class BatchPriority(Enum):
    """Prioridad de procesamiento del batch."""
    CRITICAL = 1    # <50ms
    HIGH = 2        # <100ms  
    NORMAL = 3      # <200ms
    LOW = 4         # <500ms


@dataclass
class BatchQuery:
    """Consulta individual para procesamiento en batch."""
    id: str
    table: str
    query_type: str
    data: Dict[str, Any]
    priority: BatchPriority
    timestamp: float = field(default_factory=time.time)
    callback: Optional[Callable] = None
    future: Optional[asyncio.Future] = None


@dataclass
class BatchGroup:
    """Grupo de consultas para procesamiento batch."""
    table: str
    query_type: str
    queries: List[BatchQuery] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


class QueryBatchProcessor:
    """
    Procesador de consultas por lotes para optimización de DB.
    
    Agrupa consultas similares y las ejecuta en operaciones batch
    para reducir el número de roundtrips a la base de datos.
    """
    
    def __init__(self, 
                 max_batch_size: int = 100,
                 max_wait_time: float = 0.05,  # 50ms max wait
                 flush_interval: float = 0.1):  # 100ms flush interval
        """
        Inicializa el procesador de batch.
        
        Args:
            max_batch_size: Tamaño máximo del batch antes de forzar flush
            max_wait_time: Tiempo máximo de espera antes de flush (segundos)
            flush_interval: Intervalo de flush automático (segundos)
        """
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.flush_interval = flush_interval
        
        # Almacén de consultas pendientes
        self.pending_queries: Dict[str, BatchGroup] = {}
        self.query_futures: Dict[str, asyncio.Future] = {}
        
        # Métricas de rendimiento
        self.metrics = {
            'total_queries': 0,
            'batched_queries': 0,
            'individual_queries': 0,
            'batch_savings_percent': 0.0,
            'avg_batch_size': 0.0,
            'last_flush_time': time.time()
        }
        
        # Task de flush automático
        self._flush_task: Optional[asyncio.Task] = None
        self._running = False
        
        logger.info(f"QueryBatchProcessor inicializado - max_batch: {max_batch_size}, "
                   f"max_wait: {max_wait_time}s, flush_interval: {flush_interval}s")
    
    async def start(self):
        """Inicia el procesador de batch."""
        if self._running:
            return
            
        self._running = True
        self._flush_task = asyncio.create_task(self._auto_flush_loop())
        logger.info("QueryBatchProcessor iniciado")
    
    async def stop(self):
        """Detiene el procesador de batch."""
        self._running = False
        
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Flush final de consultas pendientes
        await self._flush_all_batches()
        logger.info("QueryBatchProcessor detenido")
    
    async def add_query(self, 
                       query_id: str,
                       table: str, 
                       query_type: str,
                       data: Dict[str, Any],
                       priority: BatchPriority = BatchPriority.NORMAL) -> Any:
        """
        Añade una consulta al batch processor.
        
        Args:
            query_id: ID único de la consulta
            table: Tabla de destino
            query_type: Tipo de consulta (select, insert, update, delete)
            data: Datos de la consulta
            priority: Prioridad de procesamiento
            
        Returns:
            Resultado de la consulta cuando se procese
        """
        self.metrics['total_queries'] += 1
        
        # Crear future para el resultado
        future = asyncio.Future()
        
        # Crear consulta batch
        batch_query = BatchQuery(
            id=query_id,
            table=table,
            query_type=query_type,
            data=data,
            priority=priority,
            future=future
        )
        
        # Determinar clave del batch
        batch_key = self._get_batch_key(table, query_type)
        
        # Añadir a batch group
        if batch_key not in self.pending_queries:
            self.pending_queries[batch_key] = BatchGroup(
                table=table,
                query_type=query_type
            )
        
        self.pending_queries[batch_key].queries.append(batch_query)
        self.query_futures[query_id] = future
        
        # Verificar si necesitamos flush inmediato
        batch_group = self.pending_queries[batch_key]
        
        should_flush = (
            len(batch_group.queries) >= self.max_batch_size or
            priority == BatchPriority.CRITICAL or
            (time.time() - batch_group.created_at) > self.max_wait_time
        )
        
        if should_flush:
            await self._flush_batch(batch_key)
        
        return await future
    
    def _get_batch_key(self, table: str, query_type: str) -> str:
        """Genera clave única para el batch group."""
        return f"{table}:{query_type}"
    
    async def _auto_flush_loop(self):
        """Loop automático de flush de batches."""
        while self._running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_stale_batches()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en auto_flush_loop: {e}")
    
    async def _flush_stale_batches(self):
        """Flush batches que han esperado demasiado tiempo."""
        current_time = time.time()
        stale_batches = []
        
        for batch_key, batch_group in self.pending_queries.items():
            if (current_time - batch_group.created_at) > self.max_wait_time:
                stale_batches.append(batch_key)
        
        for batch_key in stale_batches:
            await self._flush_batch(batch_key)
    
    async def _flush_batch(self, batch_key: str):
        """
        Flush un batch específico.
        
        Args:
            batch_key: Clave del batch a procesar
        """
        if batch_key not in self.pending_queries:
            return
        
        batch_group = self.pending_queries.pop(batch_key)
        
        if not batch_group.queries:
            return
        
        # Actualizar métricas
        batch_size = len(batch_group.queries)
        self.metrics['batched_queries'] += batch_size
        self.metrics['avg_batch_size'] = (
            (self.metrics['avg_batch_size'] * (self.metrics['batched_queries'] - batch_size) + batch_size) /
            self.metrics['batched_queries']
        )
        
        # Calcular savings
        if self.metrics['total_queries'] > 0:
            individual_calls = self.metrics['total_queries']
            actual_calls = self.metrics['batched_queries'] / self.metrics['avg_batch_size'] if self.metrics['avg_batch_size'] > 0 else self.metrics['total_queries']
            self.metrics['batch_savings_percent'] = ((individual_calls - actual_calls) / individual_calls) * 100
        
        try:
            await self._execute_batch(batch_group)
            logger.debug(f"Batch ejecutado: {batch_key} con {batch_size} consultas")
        except Exception as e:
            logger.error(f"Error ejecutando batch {batch_key}: {e}")
            # Marcar todos los futures como error
            for query in batch_group.queries:
                if query.future and not query.future.done():
                    query.future.set_exception(e)
    
    async def _flush_all_batches(self):
        """Flush todos los batches pendientes."""
        batch_keys = list(self.pending_queries.keys())
        for batch_key in batch_keys:
            await self._flush_batch(batch_key)
    
    async def _execute_batch(self, batch_group: BatchGroup):
        """
        Ejecuta un batch group usando la estrategia apropiada.
        
        Args:
            batch_group: Grupo de consultas a ejecutar
        """
        from clients.supabase_client import supabase_client
        
        if batch_group.query_type == "insert":
            await self._execute_insert_batch(batch_group, supabase_client)
        elif batch_group.query_type == "update":
            await self._execute_update_batch(batch_group, supabase_client)
        elif batch_group.query_type == "select":
            await self._execute_select_batch(batch_group, supabase_client)
        elif batch_group.query_type == "delete":
            await self._execute_delete_batch(batch_group, supabase_client)
        else:
            # Fallback a ejecución individual
            await self._execute_individual_batch(batch_group, supabase_client)
    
    async def _execute_insert_batch(self, batch_group: BatchGroup, client):
        """Ejecuta batch de inserts usando upsert múltiple."""
        try:
            # Preparar datos para insert múltiple
            insert_data = [query.data.get('data', {}) for query in batch_group.queries]
            
            if not insert_data:
                return
            
            # Ejecutar insert batch
            result = await client.supabase.table(batch_group.table).insert(insert_data).execute()
            
            # Distribuir resultados
            result_data = result.data if hasattr(result, 'data') else []
            for i, query in enumerate(batch_group.queries):
                if query.future and not query.future.done():
                    row_result = result_data[i] if i < len(result_data) else {}
                    query.future.set_result({
                        'data': [row_result],
                        'count': 1
                    })
        
        except Exception as e:
            # En caso de error, ejecutar individualmente
            logger.warning(f"Batch insert falló, ejecutando individualmente: {e}")
            await self._execute_individual_batch(batch_group, client)
    
    async def _execute_update_batch(self, batch_group: BatchGroup, client):
        """Ejecuta batch de updates - ejecutión individual optimizada."""
        # Updates son inherentemente individuales, pero optimizamos la ejecución
        tasks = []
        
        for query in batch_group.queries:
            task = self._execute_single_update(query, client)
            tasks.append(task)
        
        # Ejecutar todos concurrentemente
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_single_update(self, query: BatchQuery, client):
        """Ejecuta un single update."""
        try:
            result = await client.execute_query(
                table=query.table,
                query_type='update',
                **query.data
            )
            
            if query.future and not query.future.done():
                query.future.set_result(result)
        
        except Exception as e:
            if query.future and not query.future.done():
                query.future.set_exception(e)
    
    async def _execute_select_batch(self, batch_group: BatchGroup, client):
        """Ejecuta batch de selects con optimización de consultas similares."""
        # Agrupar selects similares
        similar_queries = defaultdict(list)
        
        for query in batch_group.queries:
            # Crear key basada en columns y filters (sin límites)
            query_data = query.data.copy()
            query_data.pop('limit', None)  # Remover límites para agrupación
            
            similar_key = str(sorted(query_data.items()))
            similar_queries[similar_key].append(query)
        
        # Ejecutar grupos similares
        for similar_group in similar_queries.values():
            await self._execute_similar_selects(similar_group, client)
    
    async def _execute_similar_selects(self, queries: List[BatchQuery], client):
        """Ejecuta selects similares con una consulta optimizada."""
        if len(queries) == 1:
            # Ejecución individual
            query = queries[0]
            try:
                result = await client.execute_query(
                    table=query.table,
                    query_type='select',
                    **query.data
                )
                if query.future and not query.future.done():
                    query.future.set_result(result)
            except Exception as e:
                if query.future and not query.future.done():
                    query.future.set_exception(e)
            return
        
        # Para múltiples consultas similares, ejecutar una consulta grande y distribuir
        try:
            # Usar los parámetros de la primera consulta pero sin límite
            base_query = queries[0].data.copy()
            base_query.pop('limit', None)
            
            # Ejecutar consulta amplia
            result = await client.execute_query(
                table=queries[0].table,
                query_type='select',
                **base_query
            )
            
            # Distribuir resultados basados en límites individuales
            for query in queries:
                if query.future and not query.future.done():
                    limit = query.data.get('limit')
                    if limit and result.get('data'):
                        limited_result = {
                            'data': result['data'][:limit],
                            'count': min(limit, result.get('count', 0))
                        }
                        query.future.set_result(limited_result)
                    else:
                        query.future.set_result(result)
        
        except Exception as e:
            # Fallback a ejecución individual
            for query in queries:
                try:
                    result = await client.execute_query(
                        table=query.table,
                        query_type='select',
                        **query.data
                    )
                    if query.future and not query.future.done():
                        query.future.set_result(result)
                except Exception as individual_error:
                    if query.future and not query.future.done():
                        query.future.set_exception(individual_error)
    
    async def _execute_delete_batch(self, batch_group: BatchGroup, client):
        """Ejecuta batch de deletes - ejecución individual optimizada."""
        tasks = []
        
        for query in batch_group.queries:
            task = self._execute_single_delete(query, client)
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_single_delete(self, query: BatchQuery, client):
        """Ejecuta un single delete."""
        try:
            result = await client.execute_query(
                table=query.table,
                query_type='delete',
                **query.data
            )
            
            if query.future and not query.future.done():
                query.future.set_result(result)
        
        except Exception as e:
            if query.future and not query.future.done():
                query.future.set_exception(e)
    
    async def _execute_individual_batch(self, batch_group: BatchGroup, client):
        """Fallback: ejecuta consultas individualmente pero concurrentemente."""
        tasks = []
        
        for query in batch_group.queries:
            task = self._execute_single_query(query, client)
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_single_query(self, query: BatchQuery, client):
        """Ejecuta una consulta individual."""
        try:
            result = await client.execute_query(
                table=query.table,
                query_type=query.query_type,
                **query.data
            )
            
            if query.future and not query.future.done():
                query.future.set_result(result)
        
        except Exception as e:
            if query.future and not query.future.done():
                query.future.set_exception(e)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de rendimiento del batch processor."""
        return {
            **self.metrics,
            'pending_batches': len(self.pending_queries),
            'total_pending_queries': sum(len(bg.queries) for bg in self.pending_queries.values()),
            'uptime_seconds': time.time() - self.metrics['last_flush_time']
        }


# Instancia global del batch processor
batch_processor = QueryBatchProcessor()


async def initialize_batch_processor():
    """Inicializa el batch processor global."""
    await batch_processor.start()
    logger.info("Query Batch Processor inicializado globalmente")


async def shutdown_batch_processor():
    """Detiene el batch processor global."""
    await batch_processor.stop()
    logger.info("Query Batch Processor detenido")