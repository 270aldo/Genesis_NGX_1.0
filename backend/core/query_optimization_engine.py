"""
Query Optimization Engine - FASE 12 POINT 3
==========================================

Motor de optimización de queries que implementa estrategias avanzadas para
maximizar el rendimiento de consultas de datos en NGX Agents.

FUNCIONALIDADES CLAVE:
- Análisis inteligente de patrones de query
- Caching predictivo basado en comportamiento del usuario
- Optimización de joins y consultas complejas
- Query planning dinámico con adaptive execution
- Métricas de rendimiento en tiempo real
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import statistics
from collections import defaultdict, deque

from core.logging_config import get_logger
from core.memory_cache_optimizer import cache_get, cache_set, cache_invalidate, CachePriority

logger = get_logger(__name__)


class QueryType(Enum):
    """Tipos de queries del sistema"""
    USER_DATA = "user_data"              # Consultas de datos del usuario
    ANALYTICS = "analytics"              # Consultas analíticas
    AGGREGATION = "aggregation"          # Consultas de agregación
    REAL_TIME = "real_time"             # Consultas en tiempo real
    HISTORICAL = "historical"            # Consultas históricas
    CROSS_DOMAIN = "cross_domain"        # Consultas multi-dominio
    RECOMMENDATION = "recommendation"    # Consultas para recomendaciones


class OptimizationStrategy(Enum):
    """Estrategias de optimización"""
    CACHE_FIRST = "cache_first"          # Priorizar cache
    INDEX_OPTIMIZED = "index_optimized"  # Optimización por índices
    PARALLEL_EXECUTION = "parallel_execution"  # Ejecución paralela
    BATCH_PROCESSING = "batch_processing"      # Procesamiento por lotes
    STREAMING = "streaming"              # Procesamiento en streaming
    LAZY_LOADING = "lazy_loading"        # Carga perezosa


class QueryComplexity(Enum):
    """Niveles de complejidad de query"""
    SIMPLE = "simple"        # Consultas simples (< 100ms)
    MODERATE = "moderate"    # Consultas moderadas (100-500ms)
    COMPLEX = "complex"      # Consultas complejas (500ms-2s)
    HEAVY = "heavy"         # Consultas pesadas (> 2s)


@dataclass
class QueryPattern:
    """Patrón de query identificado"""
    pattern_id: str
    query_type: QueryType
    frequency: int
    avg_execution_time: float
    cache_hit_rate: float
    optimization_opportunities: List[str]
    user_segments: List[str]
    temporal_patterns: Dict[str, Any]
    complexity: QueryComplexity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        data = asdict(self)
        data['query_type'] = self.query_type.value
        data['complexity'] = self.complexity.value
        return data


@dataclass
class QueryMetrics:
    """Métricas de rendimiento de query"""
    query_id: str
    execution_time: float
    cache_hit: bool
    result_size: int
    optimization_applied: Optional[str]
    timestamp: datetime
    user_id: str
    query_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class OptimizationPlan:
    """Plan de optimización para una query"""
    plan_id: str
    query_hash: str
    strategy: OptimizationStrategy
    estimated_improvement: float  # Porcentaje de mejora esperada
    cache_strategy: Dict[str, Any]
    execution_order: List[str]
    parallelization_plan: Dict[str, Any]
    resource_allocation: Dict[str, Any]
    fallback_strategy: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        data = asdict(self)
        data['strategy'] = self.strategy.value
        return data


class QueryOptimizationEngine:
    """
    Motor de optimización de queries con análisis inteligente y adaptive execution
    
    CAPACIDADES AVANZADAS:
    - Pattern recognition para queries recurrentes
    - Predictive caching basado en comportamiento
    - Dynamic query planning con ajuste automático
    - Performance monitoring en tiempo real
    - Adaptive optimization basada en métricas
    """
    
    def __init__(self):
        self.cache_prefix = "query_optimizer"
        
        # Historiales y métricas
        self.query_history = defaultdict(list)
        self.performance_metrics = {}
        self.optimization_patterns = {}
        
        # Configuración de cache inteligente
        self.cache_strategies = {
            QueryType.USER_DATA: {"ttl": 300, "priority": CachePriority.HIGH},
            QueryType.ANALYTICS: {"ttl": 1800, "priority": CachePriority.MEDIUM},
            QueryType.AGGREGATION: {"ttl": 3600, "priority": CachePriority.LOW},
            QueryType.REAL_TIME: {"ttl": 60, "priority": CachePriority.CRITICAL},
            QueryType.HISTORICAL: {"ttl": 7200, "priority": CachePriority.LOW}
        }
        
        # Umbrales de optimización
        self.optimization_thresholds = {
            "slow_query_threshold": 500,  # ms
            "cache_hit_target": 0.8,     # 80%
            "parallel_threshold": 100,    # ms para considerar paralelización
            "batch_size_threshold": 50    # número de queries para batch
        }
        
        # Pattern detection
        self.query_patterns = {}
        self.pattern_analyzer = QueryPatternAnalyzer()
        
        # Performance baselines
        self.performance_baselines = {
            QueryType.USER_DATA: 50,      # 50ms baseline
            QueryType.ANALYTICS: 200,     # 200ms baseline
            QueryType.AGGREGATION: 500,   # 500ms baseline
            QueryType.REAL_TIME: 25,      # 25ms baseline
            QueryType.HISTORICAL: 1000,   # 1s baseline
        }
    
    async def optimize_query(
        self,
        query_data: Dict[str, Any],
        query_type: QueryType,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Any, QueryMetrics]:
        """
        Optimiza y ejecuta una query con estrategias inteligentes
        
        Args:
            query_data: Datos de la query a ejecutar
            query_type: Tipo de query
            user_id: ID del usuario
            context: Contexto adicional
        
        Returns:
            Tuple[resultado, métricas de la query]
        """
        try:
            start_time = time.time()
            query_id = str(uuid.uuid4())
            
            # Generar hash de la query para identificación
            query_hash = self._generate_query_hash(query_data, query_type)
            
            # Buscar en cache primero
            cached_result = await self._check_cache(query_hash, query_type)
            if cached_result:
                execution_time = (time.time() - start_time) * 1000
                
                metrics = QueryMetrics(
                    query_id=query_id,
                    execution_time=execution_time,
                    cache_hit=True,
                    result_size=len(str(cached_result)),
                    optimization_applied="cache_hit",
                    timestamp=datetime.utcnow(),
                    user_id=user_id,
                    query_hash=query_hash
                )
                
                await self._record_metrics(metrics)
                return cached_result, metrics
            
            # Generar plan de optimización
            optimization_plan = await self._generate_optimization_plan(
                query_data, query_type, query_hash, user_id, context
            )
            
            # Ejecutar query con optimizaciones
            result = await self._execute_optimized_query(
                query_data, query_type, optimization_plan, context
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            # Cachear resultado si es apropiado
            await self._cache_result(query_hash, query_type, result)
            
            # Crear métricas
            metrics = QueryMetrics(
                query_id=query_id,
                execution_time=execution_time,
                cache_hit=False,
                result_size=len(str(result)),
                optimization_applied=optimization_plan.strategy.value,
                timestamp=datetime.utcnow(),
                user_id=user_id,
                query_hash=query_hash
            )
            
            # Registrar métricas y actualizar patrones
            await self._record_metrics(metrics)
            await self._update_query_patterns(query_data, query_type, metrics, user_id)
            
            logger.info(f"Query optimizada ejecutada: {query_id} en {execution_time:.2f}ms")
            
            return result, metrics
            
        except Exception as e:
            logger.error(f"Error optimizando query: {e}")
            raise
    
    async def _generate_optimization_plan(
        self,
        query_data: Dict[str, Any],
        query_type: QueryType,
        query_hash: str,
        user_id: str,
        context: Optional[Dict[str, Any]]
    ) -> OptimizationPlan:
        """Genera plan de optimización inteligente"""
        
        try:
            plan_id = str(uuid.uuid4())
            
            # Analizar histórico de queries similares
            historical_performance = await self._analyze_historical_performance(
                query_hash, query_type, user_id
            )
            
            # Determinar estrategia óptima
            strategy = await self._select_optimization_strategy(
                query_data, query_type, historical_performance, context
            )
            
            # Estimar mejora esperada
            estimated_improvement = self._estimate_performance_improvement(
                strategy, historical_performance, query_type
            )
            
            # Configurar estrategia de cache
            cache_strategy = self._configure_cache_strategy(query_type, query_data)
            
            # Planificar ejecución
            execution_order = self._plan_execution_order(query_data, strategy)
            
            # Configurar paralelización si es apropiada
            parallelization_plan = self._plan_parallelization(
                query_data, strategy, historical_performance
            )
            
            # Configurar asignación de recursos
            resource_allocation = self._allocate_resources(
                query_type, estimated_improvement, strategy
            )
            
            # Estrategia de fallback
            fallback_strategy = self._determine_fallback_strategy(strategy)
            
            optimization_plan = OptimizationPlan(
                plan_id=plan_id,
                query_hash=query_hash,
                strategy=strategy,
                estimated_improvement=estimated_improvement,
                cache_strategy=cache_strategy,
                execution_order=execution_order,
                parallelization_plan=parallelization_plan,
                resource_allocation=resource_allocation,
                fallback_strategy=fallback_strategy
            )
            
            # Cachear plan para reuso
            await self._cache_optimization_plan(optimization_plan)
            
            return optimization_plan
            
        except Exception as e:
            logger.error(f"Error generando plan de optimización: {e}")
            # Plan por defecto
            return OptimizationPlan(
                plan_id=str(uuid.uuid4()),
                query_hash=query_hash,
                strategy=OptimizationStrategy.CACHE_FIRST,
                estimated_improvement=10.0,
                cache_strategy=self.cache_strategies.get(query_type, {}),
                execution_order=["cache_check", "execute", "cache_store"],
                parallelization_plan={},
                resource_allocation={"threads": 1, "memory_limit": "100MB"},
                fallback_strategy="simple_execution"
            )
    
    async def _select_optimization_strategy(
        self,
        query_data: Dict[str, Any],
        query_type: QueryType,
        historical_performance: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> OptimizationStrategy:
        """Selecciona la estrategia de optimización más apropiada"""
        
        # Análisis de complejidad de la query
        complexity = self._analyze_query_complexity(query_data)
        
        # Análisis de frecuencia histórica
        frequency = historical_performance.get('frequency', 0)
        avg_time = historical_performance.get('avg_execution_time', 1000)
        
        # Estrategias basadas en tipo de query
        if query_type == QueryType.REAL_TIME:
            return OptimizationStrategy.CACHE_FIRST
        
        elif query_type == QueryType.ANALYTICS and complexity == QueryComplexity.HEAVY:
            return OptimizationStrategy.PARALLEL_EXECUTION
        
        elif frequency > 10 and avg_time > 200:  # Query frecuente y lenta
            return OptimizationStrategy.INDEX_OPTIMIZED
        
        elif complexity == QueryComplexity.COMPLEX:
            return OptimizationStrategy.STREAMING
        
        elif context and context.get('batch_context'):
            return OptimizationStrategy.BATCH_PROCESSING
        
        elif avg_time < 100:  # Query rápida
            return OptimizationStrategy.LAZY_LOADING
        
        else:
            return OptimizationStrategy.CACHE_FIRST
    
    def _analyze_query_complexity(self, query_data: Dict[str, Any]) -> QueryComplexity:
        """Analiza la complejidad de una query"""
        
        complexity_score = 0
        
        # Factores de complejidad
        if 'joins' in query_data:
            complexity_score += len(query_data['joins']) * 2
        
        if 'aggregations' in query_data:
            complexity_score += len(query_data['aggregations']) * 3
        
        if 'filters' in query_data:
            complexity_score += len(query_data['filters'])
        
        if 'sort_fields' in query_data:
            complexity_score += len(query_data['sort_fields'])
        
        if 'limit' in query_data and query_data['limit'] > 1000:
            complexity_score += 2
        
        # Determinar nivel de complejidad
        if complexity_score <= 3:
            return QueryComplexity.SIMPLE
        elif complexity_score <= 8:
            return QueryComplexity.MODERATE
        elif complexity_score <= 15:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.HEAVY
    
    def _estimate_performance_improvement(
        self,
        strategy: OptimizationStrategy,
        historical_performance: Dict[str, Any],
        query_type: QueryType
    ) -> float:
        """Estima mejora de rendimiento esperada"""
        
        baseline_time = historical_performance.get(
            'avg_execution_time', 
            self.performance_baselines.get(query_type, 500)
        )
        
        # Factores de mejora por estrategia
        improvement_factors = {
            OptimizationStrategy.CACHE_FIRST: 0.9,      # 90% mejora si cache hit
            OptimizationStrategy.INDEX_OPTIMIZED: 0.6,  # 60% mejora
            OptimizationStrategy.PARALLEL_EXECUTION: 0.4, # 40% mejora
            OptimizationStrategy.BATCH_PROCESSING: 0.3,   # 30% mejora
            OptimizationStrategy.STREAMING: 0.5,          # 50% mejora
            OptimizationStrategy.LAZY_LOADING: 0.2        # 20% mejora
        }
        
        improvement_factor = improvement_factors.get(strategy, 0.1)
        estimated_improvement = improvement_factor * 100
        
        return estimated_improvement
    
    def _configure_cache_strategy(
        self, 
        query_type: QueryType, 
        query_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configura estrategia de cache específica"""
        
        base_strategy = self.cache_strategies.get(query_type, {})
        
        # Ajustar TTL basado en tipo de datos
        if 'temporal_range' in query_data:
            range_hours = query_data['temporal_range'].get('hours', 24)
            if range_hours <= 1:
                base_strategy['ttl'] = 300   # 5 minutos para datos muy recientes
            elif range_hours <= 24:
                base_strategy['ttl'] = 1800  # 30 minutos para datos del día
            else:
                base_strategy['ttl'] = 7200  # 2 horas para datos históricos
        
        # Configurar invalidación inteligente
        invalidation_rules = []
        if query_type == QueryType.USER_DATA:
            invalidation_rules.append("user_data_update")
        elif query_type == QueryType.ANALYTICS:
            invalidation_rules.append("analytics_refresh")
        
        base_strategy['invalidation_rules'] = invalidation_rules
        base_strategy['compression'] = True  # Habilitar compresión
        
        return base_strategy
    
    def _plan_execution_order(
        self, 
        query_data: Dict[str, Any], 
        strategy: OptimizationStrategy
    ) -> List[str]:
        """Planifica orden de ejecución optimizado"""
        
        if strategy == OptimizationStrategy.CACHE_FIRST:
            return ["cache_check", "execute_if_miss", "cache_store"]
        
        elif strategy == OptimizationStrategy.PARALLEL_EXECUTION:
            return ["prepare_parallel", "execute_parallel", "merge_results"]
        
        elif strategy == OptimizationStrategy.INDEX_OPTIMIZED:
            return ["optimize_indexes", "execute_with_hints", "cleanup"]
        
        elif strategy == OptimizationStrategy.STREAMING:
            return ["prepare_stream", "stream_execute", "stream_process"]
        
        elif strategy == OptimizationStrategy.BATCH_PROCESSING:
            return ["batch_prepare", "batch_execute", "batch_results"]
        
        else:
            return ["prepare", "execute", "cleanup"]
    
    def _plan_parallelization(
        self,
        query_data: Dict[str, Any],
        strategy: OptimizationStrategy,
        historical_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Planifica paralelización si es apropiada"""
        
        parallelization_plan = {
            "enabled": False,
            "thread_count": 1,
            "split_strategy": "none"
        }
        
        if strategy == OptimizationStrategy.PARALLEL_EXECUTION:
            avg_time = historical_performance.get('avg_execution_time', 0)
            
            if avg_time > self.optimization_thresholds['parallel_threshold']:
                parallelization_plan.update({
                    "enabled": True,
                    "thread_count": min(4, max(2, int(avg_time / 100))),
                    "split_strategy": "data_partitioning"
                })
                
                # Configurar particionamiento
                if 'date_range' in query_data:
                    parallelization_plan["partition_field"] = "date"
                elif 'user_segments' in query_data:
                    parallelization_plan["partition_field"] = "user_id"
                else:
                    parallelization_plan["partition_field"] = "id"
        
        return parallelization_plan
    
    def _allocate_resources(
        self,
        query_type: QueryType,
        estimated_improvement: float,
        strategy: OptimizationStrategy
    ) -> Dict[str, Any]:
        """Asigna recursos basado en tipo y estrategia"""
        
        # Asignación base por tipo
        base_allocation = {
            QueryType.REAL_TIME: {"threads": 2, "memory_limit": "50MB", "priority": "high"},
            QueryType.ANALYTICS: {"threads": 4, "memory_limit": "200MB", "priority": "medium"},
            QueryType.AGGREGATION: {"threads": 3, "memory_limit": "150MB", "priority": "medium"},
            QueryType.HISTORICAL: {"threads": 2, "memory_limit": "100MB", "priority": "low"}
        }
        
        allocation = base_allocation.get(query_type, {
            "threads": 1, "memory_limit": "50MB", "priority": "medium"
        })
        
        # Ajustar basado en estrategia
        if strategy == OptimizationStrategy.PARALLEL_EXECUTION:
            allocation["threads"] = min(8, allocation["threads"] * 2)
            allocation["memory_limit"] = self._increase_memory_limit(allocation["memory_limit"])
        
        elif strategy == OptimizationStrategy.STREAMING:
            allocation["buffer_size"] = "10MB"
            allocation["stream_chunks"] = 1000
        
        return allocation
    
    def _increase_memory_limit(self, current_limit: str) -> str:
        """Incrementa límite de memoria"""
        value = int(current_limit.replace("MB", ""))
        return f"{min(500, value * 2)}MB"
    
    def _determine_fallback_strategy(self, primary_strategy: OptimizationStrategy) -> str:
        """Determina estrategia de fallback"""
        fallback_mapping = {
            OptimizationStrategy.PARALLEL_EXECUTION: "simple_execution",
            OptimizationStrategy.STREAMING: "batch_processing",
            OptimizationStrategy.INDEX_OPTIMIZED: "cache_first",
            OptimizationStrategy.BATCH_PROCESSING: "simple_execution",
            OptimizationStrategy.CACHE_FIRST: "simple_execution",
            OptimizationStrategy.LAZY_LOADING: "simple_execution"
        }
        
        return fallback_mapping.get(primary_strategy, "simple_execution")
    
    async def _execute_optimized_query(
        self,
        query_data: Dict[str, Any],
        query_type: QueryType,
        optimization_plan: OptimizationPlan,
        context: Optional[Dict[str, Any]]
    ) -> Any:
        """Ejecuta query con plan de optimización"""
        
        try:
            strategy = optimization_plan.strategy
            
            if strategy == OptimizationStrategy.PARALLEL_EXECUTION:
                return await self._execute_parallel_query(query_data, optimization_plan)
            
            elif strategy == OptimizationStrategy.STREAMING:
                return await self._execute_streaming_query(query_data, optimization_plan)
            
            elif strategy == OptimizationStrategy.BATCH_PROCESSING:
                return await self._execute_batch_query(query_data, optimization_plan)
            
            elif strategy == OptimizationStrategy.INDEX_OPTIMIZED:
                return await self._execute_index_optimized_query(query_data, optimization_plan)
            
            elif strategy == OptimizationStrategy.LAZY_LOADING:
                return await self._execute_lazy_loading_query(query_data, optimization_plan)
            
            else:  # CACHE_FIRST or default
                return await self._execute_simple_query(query_data, optimization_plan)
        
        except Exception as e:
            logger.warning(f"Optimización falló, usando fallback: {e}")
            return await self._execute_fallback_query(query_data, optimization_plan)
    
    async def _execute_parallel_query(
        self, 
        query_data: Dict[str, Any], 
        plan: OptimizationPlan
    ) -> Any:
        """Ejecuta query con paralelización"""
        
        parallelization = plan.parallelization_plan
        thread_count = parallelization.get('thread_count', 2)
        
        # Simular particionamiento y ejecución paralela
        tasks = []
        for i in range(thread_count):
            partition_data = self._create_partition(query_data, i, thread_count)
            task = self._execute_partition(partition_data)
            tasks.append(task)
        
        # Ejecutar particiones en paralelo
        partition_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Manejar excepciones
        valid_results = [r for r in partition_results if not isinstance(r, Exception)]
        
        if not valid_results:
            raise Exception("Todas las particiones fallaron")
        
        # Merge resultados
        return self._merge_partition_results(valid_results)
    
    async def _execute_streaming_query(
        self, 
        query_data: Dict[str, Any], 
        plan: OptimizationPlan
    ) -> Any:
        """Ejecuta query con streaming"""
        
        # Simular streaming de datos
        buffer_size = plan.resource_allocation.get('buffer_size', '10MB')
        chunk_size = plan.resource_allocation.get('stream_chunks', 1000)
        
        results = []
        async for chunk in self._stream_data_chunks(query_data, chunk_size):
            processed_chunk = await self._process_stream_chunk(chunk)
            results.extend(processed_chunk)
        
        return results
    
    async def _execute_batch_query(
        self, 
        query_data: Dict[str, Any], 
        plan: OptimizationPlan
    ) -> Any:
        """Ejecuta query con procesamiento por lotes"""
        
        # Simular procesamiento por lotes
        batch_size = 100
        all_results = []
        
        batches = self._create_batches(query_data, batch_size)
        for batch in batches:
            batch_result = await self._execute_simple_query(batch, plan)
            all_results.extend(batch_result if isinstance(batch_result, list) else [batch_result])
        
        return all_results
    
    async def _execute_index_optimized_query(
        self, 
        query_data: Dict[str, Any], 
        plan: OptimizationPlan
    ) -> Any:
        """Ejecuta query optimizada por índices"""
        
        # Simular optimización de índices
        optimized_query = self._optimize_with_indexes(query_data)
        return await self._execute_simple_query(optimized_query, plan)
    
    async def _execute_lazy_loading_query(
        self, 
        query_data: Dict[str, Any], 
        plan: OptimizationPlan
    ) -> Any:
        """Ejecuta query con carga perezosa"""
        
        # Simular carga perezosa - solo datos esenciales primero
        essential_data = self._extract_essential_fields(query_data)
        return await self._execute_simple_query(essential_data, plan)
    
    async def _execute_simple_query(
        self, 
        query_data: Dict[str, Any], 
        plan: OptimizationPlan
    ) -> Any:
        """Ejecuta query simple"""
        
        # Simular ejecución de query
        await asyncio.sleep(0.01)  # Simular tiempo de DB
        
        # Generar resultado mock basado en query_data
        return self._generate_mock_result(query_data)
    
    async def _execute_fallback_query(
        self, 
        query_data: Dict[str, Any], 
        plan: OptimizationPlan
    ) -> Any:
        """Ejecuta query con estrategia de fallback"""
        
        fallback_strategy = plan.fallback_strategy
        logger.info(f"Ejecutando fallback strategy: {fallback_strategy}")
        
        return await self._execute_simple_query(query_data, plan)
    
    def _create_partition(self, query_data: Dict[str, Any], partition_id: int, total_partitions: int) -> Dict[str, Any]:
        """Crea partición de datos para ejecución paralela"""
        partition_data = query_data.copy()
        partition_data['partition_id'] = partition_id
        partition_data['total_partitions'] = total_partitions
        return partition_data
    
    async def _execute_partition(self, partition_data: Dict[str, Any]) -> Any:
        """Ejecuta una partición específica"""
        await asyncio.sleep(0.005)  # Simular tiempo de partición
        return self._generate_mock_result(partition_data)
    
    def _merge_partition_results(self, results: List[Any]) -> Any:
        """Combina resultados de particiones"""
        # Simular merge de resultados
        if all(isinstance(r, list) for r in results):
            merged = []
            for result_list in results:
                merged.extend(result_list)
            return merged
        else:
            return results[0] if results else None
    
    async def _stream_data_chunks(self, query_data: Dict[str, Any], chunk_size: int):
        """Genera chunks de datos para streaming"""
        total_chunks = 5  # Simular 5 chunks
        for i in range(total_chunks):
            chunk_data = query_data.copy()
            chunk_data['chunk_id'] = i
            chunk_data['chunk_size'] = chunk_size
            yield chunk_data
            await asyncio.sleep(0.002)  # Simular tiempo entre chunks
    
    async def _process_stream_chunk(self, chunk_data: Dict[str, Any]) -> List[Any]:
        """Procesa un chunk de streaming"""
        await asyncio.sleep(0.001)
        return self._generate_mock_result(chunk_data)
    
    def _create_batches(self, query_data: Dict[str, Any], batch_size: int) -> List[Dict[str, Any]]:
        """Crea lotes para procesamiento batch"""
        # Simular creación de lotes
        num_batches = 3
        batches = []
        for i in range(num_batches):
            batch_data = query_data.copy()
            batch_data['batch_id'] = i
            batch_data['batch_size'] = batch_size
            batches.append(batch_data)
        return batches
    
    def _optimize_with_indexes(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza query con hints de índices"""
        optimized = query_data.copy()
        optimized['use_indexes'] = True
        optimized['index_hints'] = ['idx_user_id', 'idx_timestamp']
        return optimized
    
    def _extract_essential_fields(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae solo campos esenciales para lazy loading"""
        essential = query_data.copy()
        essential['fields'] = ['id', 'name', 'timestamp']  # Solo campos básicos
        essential['lazy_loading'] = True
        return essential
    
    def _generate_mock_result(self, query_data: Dict[str, Any]) -> Any:
        """Genera resultado mock para testing"""
        
        # Simular diferentes tipos de resultados basados en query_data
        if 'aggregation' in query_data:
            return {
                'count': 150,
                'average': 75.5,
                'sum': 11325,
                'metadata': {'query_optimized': True}
            }
        elif 'user_data' in query_data:
            return [
                {'id': i, 'name': f'User {i}', 'value': i * 10}
                for i in range(10)
            ]
        else:
            return {'result': 'success', 'data': 'mock_data', 'optimized': True}
    
    def _generate_query_hash(self, query_data: Dict[str, Any], query_type: QueryType) -> str:
        """Genera hash único para la query"""
        
        # Crear representación determinística
        hash_data = {
            'type': query_type.value,
            'data': json.dumps(query_data, sort_keys=True)
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    async def _check_cache(self, query_hash: str, query_type: QueryType) -> Optional[Any]:
        """Verifica cache para la query"""
        try:
            cache_key = f"{self.cache_prefix}:query:{query_hash}"
            return await cache_get(cache_key)
        except Exception as e:
            logger.warning(f"Error verificando cache: {e}")
            return None
    
    async def _cache_result(self, query_hash: str, query_type: QueryType, result: Any) -> None:
        """Cachea resultado de la query"""
        try:
            cache_strategy = self.cache_strategies.get(query_type, {})
            cache_key = f"{self.cache_prefix}:query:{query_hash}"
            
            await cache_set(
                cache_key,
                result,
                ttl=cache_strategy.get('ttl', 300),
                priority=cache_strategy.get('priority', CachePriority.MEDIUM)
            )
        except Exception as e:
            logger.warning(f"Error cacheando resultado: {e}")
    
    async def _cache_optimization_plan(self, plan: OptimizationPlan) -> None:
        """Cachea plan de optimización"""
        try:
            cache_key = f"{self.cache_prefix}:plan:{plan.query_hash}"
            await cache_set(
                cache_key,
                plan.to_dict(),
                ttl=1800,  # 30 minutos
                priority=CachePriority.LOW
            )
        except Exception as e:
            logger.warning(f"Error cacheando plan: {e}")
    
    async def _record_metrics(self, metrics: QueryMetrics) -> None:
        """Registra métricas de rendimiento"""
        try:
            # Almacenar en historial del usuario
            if metrics.user_id not in self.query_history:
                self.query_history[metrics.user_id] = deque(maxlen=1000)
            
            self.query_history[metrics.user_id].append(metrics.to_dict())
            
            # Actualizar métricas globales
            if metrics.query_hash not in self.performance_metrics:
                self.performance_metrics[metrics.query_hash] = {
                    'total_executions': 0,
                    'total_time': 0,
                    'cache_hits': 0,
                    'avg_execution_time': 0,
                    'cache_hit_rate': 0
                }
            
            query_metrics = self.performance_metrics[metrics.query_hash]
            query_metrics['total_executions'] += 1
            query_metrics['total_time'] += metrics.execution_time
            
            if metrics.cache_hit:
                query_metrics['cache_hits'] += 1
            
            # Recalcular promedios
            query_metrics['avg_execution_time'] = query_metrics['total_time'] / query_metrics['total_executions']
            query_metrics['cache_hit_rate'] = query_metrics['cache_hits'] / query_metrics['total_executions']
            
        except Exception as e:
            logger.error(f"Error registrando métricas: {e}")
    
    async def _analyze_historical_performance(
        self, 
        query_hash: str, 
        query_type: QueryType, 
        user_id: str
    ) -> Dict[str, Any]:
        """Analiza rendimiento histórico de queries similares"""
        
        historical_data = {
            'frequency': 0,
            'avg_execution_time': self.performance_baselines.get(query_type, 500),
            'cache_hit_rate': 0.0,
            'trend': 'stable'
        }
        
        try:
            # Obtener métricas específicas de la query
            if query_hash in self.performance_metrics:
                query_metrics = self.performance_metrics[query_hash]
                historical_data.update({
                    'frequency': query_metrics['total_executions'],
                    'avg_execution_time': query_metrics['avg_execution_time'],
                    'cache_hit_rate': query_metrics['cache_hit_rate']
                })
            
            # Analizar tendencia en historial del usuario
            if user_id in self.query_history:
                user_queries = [
                    q for q in self.query_history[user_id] 
                    if q['query_hash'] == query_hash
                ]
                
                if len(user_queries) >= 3:
                    recent_times = [q['execution_time'] for q in user_queries[-3:]]
                    older_times = [q['execution_time'] for q in user_queries[:-3]]
                    
                    if older_times and recent_times:
                        recent_avg = statistics.mean(recent_times)
                        older_avg = statistics.mean(older_times)
                        
                        if recent_avg < older_avg * 0.9:
                            historical_data['trend'] = 'improving'
                        elif recent_avg > older_avg * 1.1:
                            historical_data['trend'] = 'degrading'
            
            return historical_data
            
        except Exception as e:
            logger.warning(f"Error analizando rendimiento histórico: {e}")
            return historical_data
    
    async def _update_query_patterns(
        self, 
        query_data: Dict[str, Any], 
        query_type: QueryType, 
        metrics: QueryMetrics, 
        user_id: str
    ) -> None:
        """Actualiza patrones de queries detectados"""
        
        try:
            # Detectar patrón de la query
            pattern_signature = self.pattern_analyzer.generate_pattern_signature(
                query_data, query_type
            )
            
            if pattern_signature not in self.query_patterns:
                self.query_patterns[pattern_signature] = QueryPattern(
                    pattern_id=pattern_signature,
                    query_type=query_type,
                    frequency=0,
                    avg_execution_time=0.0,
                    cache_hit_rate=0.0,
                    optimization_opportunities=[],
                    user_segments=[],
                    temporal_patterns={},
                    complexity=self._analyze_query_complexity(query_data)
                )
            
            pattern = self.query_patterns[pattern_signature]
            pattern.frequency += 1
            
            # Actualizar tiempo promedio
            total_time = pattern.avg_execution_time * (pattern.frequency - 1) + metrics.execution_time
            pattern.avg_execution_time = total_time / pattern.frequency
            
            # Actualizar cache hit rate
            cache_hits = pattern.cache_hit_rate * pattern.frequency * (1 if metrics.cache_hit else 0)
            pattern.cache_hit_rate = cache_hits / pattern.frequency
            
            # Identificar oportunidades de optimización
            pattern.optimization_opportunities = self._identify_optimization_opportunities(pattern)
            
        except Exception as e:
            logger.error(f"Error actualizando patrones: {e}")
    
    def _identify_optimization_opportunities(self, pattern: QueryPattern) -> List[str]:
        """Identifica oportunidades de optimización para un patrón"""
        
        opportunities = []
        
        # Oportunidades basadas en tiempo de ejecución
        if pattern.avg_execution_time > self.optimization_thresholds['slow_query_threshold']:
            opportunities.append("slow_query_optimization")
        
        # Oportunidades basadas en cache hit rate
        if pattern.cache_hit_rate < self.optimization_thresholds['cache_hit_target']:
            opportunities.append("cache_strategy_improvement")
        
        # Oportunidades basadas en frecuencia
        if pattern.frequency > 50:
            opportunities.append("high_frequency_optimization")
        
        # Oportunidades basadas en complejidad
        if pattern.complexity == QueryComplexity.HEAVY:
            opportunities.append("complexity_reduction")
            opportunities.append("parallel_execution_candidate")
        
        return opportunities
    
    async def get_optimization_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene analíticas de optimización"""
        
        try:
            analytics = {
                'overall_performance': self._calculate_overall_performance(),
                'optimization_effectiveness': self._calculate_optimization_effectiveness(),
                'query_patterns': self._analyze_query_patterns(),
                'cache_performance': self._analyze_cache_performance(),
                'recommendations': self._generate_optimization_recommendations()
            }
            
            if user_id and user_id in self.query_history:
                analytics['user_specific'] = self._analyze_user_performance(user_id)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error obteniendo analíticas: {e}")
            return {}
    
    def _calculate_overall_performance(self) -> Dict[str, Any]:
        """Calcula rendimiento general del sistema"""
        
        if not self.performance_metrics:
            return {'status': 'no_data'}
        
        all_metrics = self.performance_metrics.values()
        avg_execution_time = statistics.mean([m['avg_execution_time'] for m in all_metrics])
        avg_cache_hit_rate = statistics.mean([m['cache_hit_rate'] for m in all_metrics])
        
        return {
            'average_execution_time': avg_execution_time,
            'average_cache_hit_rate': avg_cache_hit_rate,
            'total_queries_tracked': len(self.performance_metrics),
            'performance_score': self._calculate_performance_score(avg_execution_time, avg_cache_hit_rate)
        }
    
    def _calculate_performance_score(self, avg_time: float, cache_rate: float) -> float:
        """Calcula score de rendimiento general"""
        
        # Score basado en tiempo (mejor = más alto)
        time_score = max(0, 100 - (avg_time / 10))  # 100 para 0ms, decrece
        
        # Score basado en cache hit rate
        cache_score = cache_rate * 100
        
        # Score combinado (ponderado)
        return (time_score * 0.6 + cache_score * 0.4)
    
    def _calculate_optimization_effectiveness(self) -> Dict[str, Any]:
        """Calcula efectividad de las optimizaciones aplicadas"""
        
        strategy_performance = defaultdict(list)
        
        # Analizar rendimiento por estrategia (simulado para desarrollo)
        for metrics in self.performance_metrics.values():
            # En producción, esto vendría de los datos reales
            strategy = "cache_first"  # Simulado
            strategy_performance[strategy].append(metrics['avg_execution_time'])
        
        effectiveness = {}
        for strategy, times in strategy_performance.items():
            effectiveness[strategy] = {
                'avg_time': statistics.mean(times),
                'queries_count': len(times),
                'effectiveness_score': max(0, 100 - statistics.mean(times) / 10)
            }
        
        return effectiveness
    
    def _analyze_query_patterns(self) -> Dict[str, Any]:
        """Analiza patrones de queries detectados"""
        
        if not self.query_patterns:
            return {'total_patterns': 0}
        
        patterns_by_type = defaultdict(int)
        patterns_by_complexity = defaultdict(int)
        
        for pattern in self.query_patterns.values():
            patterns_by_type[pattern.query_type.value] += 1
            patterns_by_complexity[pattern.complexity.value] += 1
        
        return {
            'total_patterns': len(self.query_patterns),
            'patterns_by_type': dict(patterns_by_type),
            'patterns_by_complexity': dict(patterns_by_complexity),
            'most_frequent_patterns': self._get_most_frequent_patterns()
        }
    
    def _get_most_frequent_patterns(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtiene patrones más frecuentes"""
        
        sorted_patterns = sorted(
            self.query_patterns.values(),
            key=lambda p: p.frequency,
            reverse=True
        )
        
        return [
            {
                'pattern_id': p.pattern_id,
                'query_type': p.query_type.value,
                'frequency': p.frequency,
                'avg_execution_time': p.avg_execution_time,
                'optimization_opportunities': p.optimization_opportunities
            }
            for p in sorted_patterns[:limit]
        ]
    
    def _analyze_cache_performance(self) -> Dict[str, Any]:
        """Analiza rendimiento del cache"""
        
        if not self.performance_metrics:
            return {'status': 'no_data'}
        
        total_cache_hits = sum(m['cache_hits'] for m in self.performance_metrics.values())
        total_executions = sum(m['total_executions'] for m in self.performance_metrics.values())
        
        cache_hit_rate = total_cache_hits / total_executions if total_executions > 0 else 0
        
        return {
            'overall_cache_hit_rate': cache_hit_rate,
            'total_cache_hits': total_cache_hits,
            'total_executions': total_executions,
            'cache_effectiveness': 'excellent' if cache_hit_rate > 0.8 else 'good' if cache_hit_rate > 0.6 else 'needs_improvement'
        }
    
    def _generate_optimization_recommendations(self) -> List[str]:
        """Genera recomendaciones de optimización"""
        
        recommendations = []
        
        # Analizar oportunidades de todos los patrones
        all_opportunities = set()
        for pattern in self.query_patterns.values():
            all_opportunities.update(pattern.optimization_opportunities)
        
        # Generar recomendaciones específicas
        if 'slow_query_optimization' in all_opportunities:
            recommendations.append("Implementar optimización de índices para queries lentas")
        
        if 'cache_strategy_improvement' in all_opportunities:
            recommendations.append("Mejorar estrategia de cache para queries frecuentes")
        
        if 'high_frequency_optimization' in all_opportunities:
            recommendations.append("Considerar pre-cálculo para queries de alta frecuencia")
        
        if 'parallel_execution_candidate' in all_opportunities:
            recommendations.append("Implementar ejecución paralela para queries complejas")
        
        # Recomendaciones generales
        overall_perf = self._calculate_overall_performance()
        if overall_perf.get('performance_score', 0) < 70:
            recommendations.append("Revisar configuración general de optimización")
        
        return recommendations
    
    def _analyze_user_performance(self, user_id: str) -> Dict[str, Any]:
        """Analiza rendimiento específico del usuario"""
        
        user_queries = list(self.query_history[user_id])
        
        if not user_queries:
            return {'status': 'no_data'}
        
        execution_times = [q['execution_time'] for q in user_queries]
        cache_hits = [q['cache_hit'] for q in user_queries]
        
        return {
            'total_queries': len(user_queries),
            'avg_execution_time': statistics.mean(execution_times),
            'cache_hit_rate': sum(cache_hits) / len(cache_hits),
            'query_frequency': len(user_queries) / max(1, (datetime.utcnow() - datetime.fromisoformat(user_queries[0]['timestamp'].replace('Z', '+00:00'))).days),
            'performance_trend': self._analyze_user_trend(execution_times)
        }
    
    def _analyze_user_trend(self, execution_times: List[float]) -> str:
        """Analiza tendencia de rendimiento del usuario"""
        
        if len(execution_times) < 5:
            return 'insufficient_data'
        
        recent = execution_times[-5:]
        older = execution_times[:-5]
        
        if not older:
            return 'stable'
        
        recent_avg = statistics.mean(recent)
        older_avg = statistics.mean(older)
        
        if recent_avg < older_avg * 0.9:
            return 'improving'
        elif recent_avg > older_avg * 1.1:
            return 'degrading'
        else:
            return 'stable'


class QueryPatternAnalyzer:
    """Analizador de patrones de queries"""
    
    def generate_pattern_signature(self, query_data: Dict[str, Any], query_type: QueryType) -> str:
        """Genera firma única para el patrón de query"""
        
        # Extraer características clave para el patrón
        pattern_features = {
            'type': query_type.value,
            'has_joins': 'joins' in query_data,
            'has_aggregations': 'aggregations' in query_data,
            'has_filters': 'filters' in query_data,
            'field_count': len(query_data.get('fields', [])),
            'complexity_indicators': self._extract_complexity_indicators(query_data)
        }
        
        # Crear firma hash
        signature_string = json.dumps(pattern_features, sort_keys=True)
        return hashlib.md5(signature_string.encode()).hexdigest()[:16]
    
    def _extract_complexity_indicators(self, query_data: Dict[str, Any]) -> List[str]:
        """Extrae indicadores de complejidad"""
        
        indicators = []
        
        if query_data.get('joins') and len(query_data['joins']) > 2:
            indicators.append('multiple_joins')
        
        if query_data.get('aggregations'):
            indicators.append('has_aggregations')
        
        if query_data.get('subqueries'):
            indicators.append('has_subqueries')
        
        if query_data.get('limit', 0) > 10000:
            indicators.append('large_result_set')
        
        return indicators


# Instancia global del motor de optimización
query_optimizer = QueryOptimizationEngine()


# Funciones helper para uso sencillo
async def optimize_query(
    query_data: Dict[str, Any],
    query_type: QueryType,
    user_id: str,
    context: Optional[Dict[str, Any]] = None
) -> Tuple[Any, QueryMetrics]:
    """Función helper para optimizar queries"""
    return await query_optimizer.optimize_query(query_data, query_type, user_id, context)


async def get_query_analytics(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Función helper para obtener analíticas de queries"""
    return await query_optimizer.get_optimization_analytics(user_id)