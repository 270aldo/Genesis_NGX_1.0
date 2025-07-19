"""
Response Optimizer - FASE 12 POINT 3
====================================

Sistema de optimización de respuestas API que implementa carga selectiva,
streaming de datos, compresión inteligente y progressive enhancement para
maximizar el rendimiento y minimizar el ancho de banda.

FUNCIONALIDADES CLAVE:
- Selective data loading con field projection
- Progressive enhancement para respuestas grandes
- Streaming de datos para operaciones pesadas
- Compresión inteligente integrada
- Edge case optimization
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Callable, TypeVar
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
from collections import defaultdict

from core.logging_config import get_logger
from core.memory_cache_optimizer import cache_get, cache_set, cache_invalidate, CachePriority
from core.response_compression import CompressionAlgorithm, ResponseCompressor

logger = get_logger(__name__)

T = TypeVar('T')


class LoadingStrategy(Enum):
    """Estrategias de carga de datos"""
    FULL = "full"                    # Carga completa tradicional
    SELECTIVE = "selective"          # Solo campos solicitados
    PROGRESSIVE = "progressive"      # Carga inicial mínima + expansión
    STREAMING = "streaming"          # Streaming para datos grandes
    PAGINATED = "paginated"          # Paginación con cursores
    LAZY = "lazy"                    # Carga bajo demanda


class ResponseType(Enum):
    """Tipos de respuesta optimizables"""
    USER_PROFILE = "user_profile"
    AGENT_LIST = "agent_list"
    WORKOUT_DATA = "workout_data"
    NUTRITION_DATA = "nutrition_data"
    ANALYTICS = "analytics"
    CONVERSATION = "conversation"
    HEALTH_METRICS = "health_metrics"
    RECOMMENDATIONS = "recommendations"


class OptimizationLevel(Enum):
    """Niveles de optimización"""
    NONE = "none"                    # Sin optimización
    BASIC = "basic"                  # Compresión básica
    STANDARD = "standard"            # Selective loading + compresión
    ADVANCED = "advanced"            # Todo + streaming + progressive
    EXTREME = "extreme"              # Optimización máxima con trade-offs


@dataclass
class FieldProjection:
    """Proyección de campos para carga selectiva"""
    include_fields: Set[str] = field(default_factory=set)
    exclude_fields: Set[str] = field(default_factory=set)
    depth_limit: int = 3
    include_nested: bool = True
    include_computed: bool = False
    
    def should_include_field(self, field_name: str, depth: int = 0) -> bool:
        """Determina si un campo debe incluirse"""
        if depth > self.depth_limit:
            return False
            
        if self.exclude_fields and field_name in self.exclude_fields:
            return False
            
        if self.include_fields:
            return field_name in self.include_fields
            
        return True


@dataclass
class ResponseMetadata:
    """Metadatos de la respuesta optimizada"""
    response_id: str
    original_size: int
    optimized_size: int
    compression_ratio: float
    loading_strategy: LoadingStrategy
    optimization_level: OptimizationLevel
    fields_included: int
    fields_excluded: int
    processing_time: float
    cache_hit: bool
    streaming_enabled: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        data = asdict(self)
        data['loading_strategy'] = self.loading_strategy.value
        data['optimization_level'] = self.optimization_level.value
        return data


@dataclass
class StreamingChunk:
    """Chunk de datos para streaming"""
    chunk_id: str
    sequence: int
    data: Any
    is_final: bool
    metadata: Dict[str, Any]
    
    def to_json(self) -> str:
        """Serializa a JSON"""
        return json.dumps({
            'chunk_id': self.chunk_id,
            'sequence': self.sequence,
            'data': self.data,
            'is_final': self.is_final,
            'metadata': self.metadata
        })


class SelectiveLoader:
    """Cargador selectivo de campos"""
    
    def __init__(self):
        self.field_mappings = self._initialize_field_mappings()
        self.computed_fields = self._initialize_computed_fields()
    
    def _initialize_field_mappings(self) -> Dict[ResponseType, Dict[str, Any]]:
        """Inicializa mappings de campos por tipo de respuesta"""
        return {
            ResponseType.USER_PROFILE: {
                'essential': ['id', 'name', 'email', 'created_at'],
                'basic': ['age', 'gender', 'fitness_level', 'goals'],
                'detailed': ['preferences', 'medical_history', 'program_data'],
                'computed': ['progress_summary', 'achievement_count', 'current_streak']
            },
            ResponseType.WORKOUT_DATA: {
                'essential': ['id', 'date', 'type', 'duration'],
                'basic': ['calories', 'intensity', 'completed'],
                'detailed': ['exercises', 'heart_rate_data', 'performance_metrics'],
                'computed': ['effectiveness_score', 'progress_delta', 'recommendations']
            },
            ResponseType.NUTRITION_DATA: {
                'essential': ['id', 'date', 'total_calories'],
                'basic': ['macros', 'meal_count', 'water_intake'],
                'detailed': ['meals', 'supplements', 'nutritional_breakdown'],
                'computed': ['nutritional_score', 'deficit_surplus', 'recommendations']
            },
            ResponseType.ANALYTICS: {
                'essential': ['period', 'key_metrics'],
                'basic': ['trends', 'comparisons', 'summaries'],
                'detailed': ['raw_data', 'correlations', 'predictions'],
                'computed': ['insights', 'action_items', 'forecasts']
            }
        }
    
    def _initialize_computed_fields(self) -> Dict[str, Callable]:
        """Inicializa funciones para campos computados"""
        return {
            'progress_summary': self._compute_progress_summary,
            'achievement_count': self._compute_achievement_count,
            'current_streak': self._compute_current_streak,
            'effectiveness_score': self._compute_effectiveness_score,
            'nutritional_score': self._compute_nutritional_score
        }
    
    def apply_projection(self, 
                        data: Dict[str, Any], 
                        projection: FieldProjection,
                        response_type: ResponseType) -> Dict[str, Any]:
        """Aplica proyección de campos a los datos"""
        try:
            result = {}
            field_mapping = self.field_mappings.get(response_type, {})
            
            # Si no hay campos específicos, incluir esenciales
            if not projection.include_fields:
                projection.include_fields = set(field_mapping.get('essential', []))
            
            # Aplicar proyección recursivamente
            result = self._apply_projection_recursive(data, projection, 0)
            
            # Agregar campos computados si están habilitados
            if projection.include_computed and response_type in self.field_mappings:
                computed_fields = field_mapping.get('computed', [])
                for field_name in computed_fields:
                    if projection.should_include_field(field_name):
                        compute_func = self.computed_fields.get(field_name)
                        if compute_func:
                            result[field_name] = compute_func(data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error aplicando proyección: {e}")
            return data  # Retornar datos originales en caso de error
    
    def _apply_projection_recursive(self, 
                                   data: Any, 
                                   projection: FieldProjection, 
                                   depth: int) -> Any:
        """Aplica proyección recursivamente"""
        if depth > projection.depth_limit:
            return None
        
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if projection.should_include_field(key, depth):
                    if isinstance(value, (dict, list)) and projection.include_nested:
                        result[key] = self._apply_projection_recursive(value, projection, depth + 1)
                    else:
                        result[key] = value
            return result
            
        elif isinstance(data, list):
            return [self._apply_projection_recursive(item, projection, depth) for item in data]
            
        else:
            return data
    
    def _compute_progress_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Computa resumen de progreso"""
        return {
            'total_workouts': data.get('workout_count', 0),
            'weekly_average': data.get('weekly_avg', 0),
            'improvement_rate': data.get('improvement', 0),
            'last_activity': data.get('last_activity_date')
        }
    
    def _compute_achievement_count(self, data: Dict[str, Any]) -> int:
        """Computa conteo de logros"""
        achievements = data.get('achievements', [])
        return len(achievements)
    
    def _compute_current_streak(self, data: Dict[str, Any]) -> int:
        """Computa racha actual"""
        return data.get('current_streak', 0)
    
    def _compute_effectiveness_score(self, data: Dict[str, Any]) -> float:
        """Computa score de efectividad"""
        # Lógica simplificada para ejemplo
        completed = data.get('completed', False)
        intensity = data.get('intensity', 0)
        duration = data.get('duration', 0)
        
        if not completed:
            return 0.0
        
        score = min(100, (intensity * 0.6 + min(duration / 60, 1) * 40))
        return round(score, 2)
    
    def _compute_nutritional_score(self, data: Dict[str, Any]) -> float:
        """Computa score nutricional"""
        # Lógica simplificada para ejemplo
        calories = data.get('total_calories', 0)
        target = data.get('target_calories', 2000)
        
        if target == 0:
            return 0.0
        
        deviation = abs(calories - target) / target
        score = max(0, 100 - (deviation * 100))
        return round(score, 2)


class ProgressiveEnhancer:
    """Mejora progresiva de respuestas"""
    
    def __init__(self):
        self.enhancement_levels = {
            'minimal': self._get_minimal_fields,
            'basic': self._get_basic_fields,
            'standard': self._get_standard_fields,
            'full': self._get_full_fields
        }
    
    def create_progressive_response(self,
                                   data: Dict[str, Any],
                                   response_type: ResponseType,
                                   initial_level: str = 'minimal') -> Dict[str, Any]:
        """Crea respuesta con mejora progresiva"""
        try:
            # Obtener campos para nivel inicial
            level_func = self.enhancement_levels.get(initial_level, self._get_minimal_fields)
            initial_fields = level_func(response_type)
            
            # Crear respuesta inicial
            initial_response = {
                field: data.get(field) 
                for field in initial_fields 
                if field in data
            }
            
            # Agregar metadatos de mejora progresiva
            initial_response['_progressive'] = {
                'current_level': initial_level,
                'available_levels': list(self.enhancement_levels.keys()),
                'next_level_url': f"/api/v1/enhance/{response_type.value}",
                'estimated_sizes': self._estimate_level_sizes(data, response_type)
            }
            
            return initial_response
            
        except Exception as e:
            logger.error(f"Error creando respuesta progresiva: {e}")
            return data
    
    def enhance_to_level(self,
                        data: Dict[str, Any],
                        response_type: ResponseType,
                        target_level: str) -> Dict[str, Any]:
        """Mejora respuesta a un nivel específico"""
        level_func = self.enhancement_levels.get(target_level, self._get_full_fields)
        target_fields = level_func(response_type)
        
        enhanced_response = {
            field: data.get(field) 
            for field in target_fields 
            if field in data
        }
        
        return enhanced_response
    
    def _get_minimal_fields(self, response_type: ResponseType) -> List[str]:
        """Campos mínimos por tipo"""
        minimal_fields = {
            ResponseType.USER_PROFILE: ['id', 'name', 'avatar_url'],
            ResponseType.WORKOUT_DATA: ['id', 'date', 'type', 'duration'],
            ResponseType.NUTRITION_DATA: ['id', 'date', 'total_calories'],
            ResponseType.ANALYTICS: ['period', 'summary']
        }
        return minimal_fields.get(response_type, ['id'])
    
    def _get_basic_fields(self, response_type: ResponseType) -> List[str]:
        """Campos básicos por tipo"""
        basic_fields = {
            ResponseType.USER_PROFILE: ['id', 'name', 'email', 'age', 'fitness_level'],
            ResponseType.WORKOUT_DATA: ['id', 'date', 'type', 'duration', 'calories', 'intensity'],
            ResponseType.NUTRITION_DATA: ['id', 'date', 'total_calories', 'macros'],
            ResponseType.ANALYTICS: ['period', 'summary', 'key_metrics', 'trends']
        }
        return basic_fields.get(response_type, ['id', 'name'])
    
    def _get_standard_fields(self, response_type: ResponseType) -> List[str]:
        """Campos estándar por tipo"""
        # En producción, esto sería más extenso
        return self._get_basic_fields(response_type) + ['created_at', 'updated_at']
    
    def _get_full_fields(self, response_type: ResponseType) -> List[str]:
        """Todos los campos disponibles"""
        # En producción, retornaría lista completa de campos
        return []  # Indica que se incluyen todos los campos
    
    def _estimate_level_sizes(self, data: Dict[str, Any], response_type: ResponseType) -> Dict[str, int]:
        """Estima tamaños por nivel de mejora"""
        full_size = len(json.dumps(data))
        
        return {
            'minimal': int(full_size * 0.1),
            'basic': int(full_size * 0.3),
            'standard': int(full_size * 0.6),
            'full': full_size
        }


class StreamingOptimizer:
    """Optimizador para streaming de respuestas grandes"""
    
    def __init__(self, chunk_size: int = 1024):
        self.chunk_size = chunk_size
        self.active_streams = {}
        self.stream_metadata = {}
    
    async def create_stream(self,
                           data: Union[List, Dict],
                           stream_id: str = None) -> str:
        """Crea un stream para datos grandes"""
        stream_id = stream_id or str(hash(str(data)))
        
        # Guardar referencia al stream
        self.active_streams[stream_id] = {
            'data': data,
            'position': 0,
            'created_at': datetime.utcnow(),
            'chunk_count': 0
        }
        
        # Calcular metadatos
        self.stream_metadata[stream_id] = {
            'total_size': len(json.dumps(data)),
            'estimated_chunks': self._estimate_chunks(data),
            'data_type': type(data).__name__
        }
        
        return stream_id
    
    async def get_next_chunk(self, stream_id: str) -> Optional[StreamingChunk]:
        """Obtiene el siguiente chunk del stream"""
        if stream_id not in self.active_streams:
            return None
        
        stream = self.active_streams[stream_id]
        data = stream['data']
        
        if isinstance(data, list):
            chunk = await self._get_list_chunk(stream_id, data)
        elif isinstance(data, dict):
            chunk = await self._get_dict_chunk(stream_id, data)
        else:
            chunk = None
        
        if chunk and chunk.is_final:
            # Limpiar stream completado
            await self._cleanup_stream(stream_id)
        
        return chunk
    
    async def _get_list_chunk(self, stream_id: str, data: List) -> Optional[StreamingChunk]:
        """Obtiene chunk de una lista"""
        stream = self.active_streams[stream_id]
        position = stream['position']
        
        if position >= len(data):
            return None
        
        # Calcular elementos en este chunk
        chunk_items = []
        chunk_size_bytes = 0
        
        while position < len(data) and chunk_size_bytes < self.chunk_size:
            item = data[position]
            item_size = len(json.dumps(item))
            
            if chunk_size_bytes + item_size > self.chunk_size and chunk_items:
                break
            
            chunk_items.append(item)
            chunk_size_bytes += item_size
            position += 1
        
        stream['position'] = position
        stream['chunk_count'] += 1
        
        is_final = position >= len(data)
        
        return StreamingChunk(
            chunk_id=f"{stream_id}_{stream['chunk_count']}",
            sequence=stream['chunk_count'],
            data=chunk_items,
            is_final=is_final,
            metadata={
                'items_count': len(chunk_items),
                'bytes_size': chunk_size_bytes,
                'progress': position / len(data)
            }
        )
    
    async def _get_dict_chunk(self, stream_id: str, data: Dict) -> Optional[StreamingChunk]:
        """Obtiene chunk de un diccionario"""
        stream = self.active_streams[stream_id]
        
        # Para diccionarios, enviamos por secciones lógicas
        if stream['chunk_count'] == 0:
            # Primer chunk: metadata y campos esenciales
            essential_fields = ['id', 'type', 'created_at', 'version']
            chunk_data = {k: v for k, v in data.items() if k in essential_fields}
            is_final = len(chunk_data) == len(data)
        else:
            # Chunks subsiguientes: resto de campos
            sent_fields = stream.get('sent_fields', set(essential_fields))
            remaining_fields = set(data.keys()) - sent_fields
            
            if not remaining_fields:
                return None
            
            # Tomar campos hasta llenar chunk
            chunk_data = {}
            chunk_size_bytes = 0
            
            for field in remaining_fields:
                field_data = data[field]
                field_size = len(json.dumps({field: field_data}))
                
                if chunk_size_bytes + field_size > self.chunk_size and chunk_data:
                    break
                
                chunk_data[field] = field_data
                chunk_size_bytes += field_size
                sent_fields.add(field)
            
            stream['sent_fields'] = sent_fields
            is_final = len(sent_fields) == len(data)
        
        stream['chunk_count'] += 1
        
        return StreamingChunk(
            chunk_id=f"{stream_id}_{stream['chunk_count']}",
            sequence=stream['chunk_count'],
            data=chunk_data,
            is_final=is_final,
            metadata={
                'fields_count': len(chunk_data),
                'total_fields': len(data),
                'progress': len(stream.get('sent_fields', [])) / len(data)
            }
        )
    
    async def _cleanup_stream(self, stream_id: str):
        """Limpia stream completado"""
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]
        if stream_id in self.stream_metadata:
            del self.stream_metadata[stream_id]
    
    def _estimate_chunks(self, data: Any) -> int:
        """Estima número de chunks necesarios"""
        data_size = len(json.dumps(data))
        return max(1, (data_size // self.chunk_size) + 1)


class ResponseOptimizer:
    """
    Optimizador principal de respuestas con todas las estrategias
    
    CAPACIDADES:
    - Selective field loading con proyecciones
    - Progressive enhancement para UX mejorada
    - Streaming para respuestas grandes
    - Integración con compresión existente
    - Edge case optimization
    """
    
    def __init__(self):
        self.cache_prefix = "response_optimizer"
        self.selective_loader = SelectiveLoader()
        self.progressive_enhancer = ProgressiveEnhancer()
        self.streaming_optimizer = StreamingOptimizer()
        self.response_compressor = ResponseCompressor()
        
        # Configuración de umbrales
        self.size_thresholds = {
            'compression': 1024,      # 1KB para comprimir
            'streaming': 100 * 1024,  # 100KB para streaming
            'progressive': 10 * 1024  # 10KB para progressive
        }
        
        # Métricas
        self.optimization_metrics = defaultdict(lambda: {
            'total_responses': 0,
            'bytes_saved': 0,
            'avg_compression_ratio': 0.0,
            'cache_hits': 0,
            'streaming_used': 0
        })
    
    async def optimize_response(self,
                               data: Any,
                               response_type: ResponseType,
                               optimization_level: OptimizationLevel = OptimizationLevel.STANDARD,
                               projection: FieldProjection = None,
                               request_headers: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Optimiza una respuesta aplicando todas las estrategias apropiadas
        
        Args:
            data: Datos de la respuesta
            response_type: Tipo de respuesta
            optimization_level: Nivel de optimización deseado
            projection: Proyección de campos (opcional)
            request_headers: Headers de la solicitud
        
        Returns:
            Respuesta optimizada con metadatos
        """
        try:
            start_time = time.time()
            original_size = len(json.dumps(data))
            
            # Verificar cache primero
            cache_key = await self._generate_cache_key(data, response_type, projection)
            cached_response = await self._check_cache(cache_key)
            if cached_response:
                self.optimization_metrics[response_type]['cache_hits'] += 1
                return cached_response
            
            # Aplicar optimizaciones según nivel
            optimized_data = data
            loading_strategy = LoadingStrategy.FULL
            
            if optimization_level == OptimizationLevel.NONE:
                pass  # Sin optimización
                
            elif optimization_level == OptimizationLevel.BASIC:
                # Solo compresión
                optimized_data = data
                
            elif optimization_level in [OptimizationLevel.STANDARD, OptimizationLevel.ADVANCED]:
                # Aplicar carga selectiva
                if projection:
                    optimized_data = self.selective_loader.apply_projection(
                        data, projection, response_type
                    )
                    loading_strategy = LoadingStrategy.SELECTIVE
                
                # Para ADVANCED, considerar progressive enhancement
                if optimization_level == OptimizationLevel.ADVANCED and original_size > self.size_thresholds['progressive']:
                    optimized_data = self.progressive_enhancer.create_progressive_response(
                        optimized_data, response_type
                    )
                    loading_strategy = LoadingStrategy.PROGRESSIVE
                    
            elif optimization_level == OptimizationLevel.EXTREME:
                # Optimización máxima
                if original_size > self.size_thresholds['streaming']:
                    # Usar streaming para datos muy grandes
                    stream_id = await self.streaming_optimizer.create_stream(data)
                    optimized_data = {
                        'stream_id': stream_id,
                        'stream_metadata': self.streaming_optimizer.stream_metadata[stream_id],
                        'first_chunk': await self.streaming_optimizer.get_next_chunk(stream_id)
                    }
                    loading_strategy = LoadingStrategy.STREAMING
                    self.optimization_metrics[response_type]['streaming_used'] += 1
                else:
                    # Progressive enhancement extremo
                    optimized_data = self.progressive_enhancer.create_progressive_response(
                        data, response_type, 'minimal'
                    )
                    loading_strategy = LoadingStrategy.PROGRESSIVE
            
            # Serializar datos optimizados
            optimized_json = json.dumps(optimized_data)
            optimized_size = len(optimized_json)
            
            # Comprimir si es apropiado
            compressed_data = optimized_json
            compression_algorithm = None
            
            if optimized_size > self.size_thresholds['compression'] and request_headers:
                accept_encoding = request_headers.get('accept-encoding', '')
                compressed_result = self.response_compressor.compress_response(
                    optimized_json.encode(),
                    accept_encoding
                )
                if compressed_result:
                    compressed_data = compressed_result['data']
                    compression_algorithm = compressed_result['algorithm']
            
            # Calcular métricas
            final_size = len(compressed_data) if isinstance(compressed_data, bytes) else len(compressed_data)
            compression_ratio = 1 - (final_size / original_size) if original_size > 0 else 0
            processing_time = time.time() - start_time
            
            # Crear metadatos de respuesta
            metadata = ResponseMetadata(
                response_id=str(hash(cache_key)),
                original_size=original_size,
                optimized_size=final_size,
                compression_ratio=compression_ratio,
                loading_strategy=loading_strategy,
                optimization_level=optimization_level,
                fields_included=len(optimized_data) if isinstance(optimized_data, dict) else 0,
                fields_excluded=len(data) - len(optimized_data) if isinstance(data, dict) and isinstance(optimized_data, dict) else 0,
                processing_time=processing_time,
                cache_hit=False,
                streaming_enabled=loading_strategy == LoadingStrategy.STREAMING
            )
            
            # Actualizar métricas
            await self._update_metrics(response_type, metadata)
            
            # Construir respuesta final
            response = {
                'data': optimized_data,
                'metadata': metadata.to_dict(),
                'headers': {}
            }
            
            # Agregar headers de compresión si aplica
            if compression_algorithm:
                response['headers']['Content-Encoding'] = compression_algorithm
                response['data'] = compressed_data  # Datos comprimidos
            
            # Cachear respuesta optimizada
            await self._cache_response(cache_key, response)
            
            logger.info(f"Respuesta optimizada: {compression_ratio:.2%} reducción, {processing_time:.3f}s procesamiento")
            
            return response
            
        except Exception as e:
            logger.error(f"Error optimizando respuesta: {e}")
            # En caso de error, retornar datos originales
            return {
                'data': data,
                'metadata': {
                    'optimization_failed': True,
                    'error': str(e)
                },
                'headers': {}
            }
    
    async def get_streamed_response(self, stream_id: str) -> Optional[StreamingChunk]:
        """Obtiene siguiente chunk de una respuesta streamed"""
        return await self.streaming_optimizer.get_next_chunk(stream_id)
    
    async def enhance_response(self,
                              data: Dict[str, Any],
                              response_type: ResponseType,
                              target_level: str) -> Dict[str, Any]:
        """Mejora una respuesta progresiva a un nivel específico"""
        enhanced = self.progressive_enhancer.enhance_to_level(
            data, response_type, target_level
        )
        return {
            'data': enhanced,
            'metadata': {
                'enhancement_level': target_level,
                'enhanced_at': datetime.utcnow().isoformat()
            }
        }
    
    async def _generate_cache_key(self,
                                 data: Any,
                                 response_type: ResponseType,
                                 projection: FieldProjection = None) -> str:
        """Genera clave de cache única"""
        key_parts = [
            response_type.value,
            str(hash(json.dumps(data, sort_keys=True)))
        ]
        
        if projection:
            key_parts.append(str(hash(frozenset(projection.include_fields))))
            key_parts.append(str(hash(frozenset(projection.exclude_fields))))
        
        return f"{self.cache_prefix}:{':'.join(key_parts)}"
    
    async def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Verifica cache de respuestas optimizadas"""
        try:
            return await cache_get(cache_key)
        except Exception as e:
            logger.debug(f"Cache miss: {e}")
            return None
    
    async def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cachea respuesta optimizada"""
        try:
            # No cachear respuestas con streaming
            if response.get('metadata', {}).get('streaming_enabled'):
                return
            
            await cache_set(
                cache_key,
                response,
                ttl=300,  # 5 minutos
                priority=CachePriority.MEDIUM
            )
        except Exception as e:
            logger.debug(f"Error cacheando respuesta: {e}")
    
    async def _update_metrics(self, response_type: ResponseType, metadata: ResponseMetadata):
        """Actualiza métricas de optimización"""
        metrics = self.optimization_metrics[response_type]
        
        metrics['total_responses'] += 1
        metrics['bytes_saved'] += (metadata.original_size - metadata.optimized_size)
        
        # Actualizar promedio de compresión
        old_avg = metrics['avg_compression_ratio']
        new_avg = (old_avg * (metrics['total_responses'] - 1) + metadata.compression_ratio) / metrics['total_responses']
        metrics['avg_compression_ratio'] = new_avg
    
    async def get_optimization_analytics(self) -> Dict[str, Any]:
        """Obtiene analíticas de optimización"""
        total_metrics = {
            'total_responses': 0,
            'total_bytes_saved': 0,
            'total_cache_hits': 0,
            'total_streaming_used': 0
        }
        
        type_metrics = {}
        
        for response_type, metrics in self.optimization_metrics.items():
            type_metrics[response_type] = metrics.copy()
            
            total_metrics['total_responses'] += metrics['total_responses']
            total_metrics['total_bytes_saved'] += metrics['bytes_saved']
            total_metrics['total_cache_hits'] += metrics['cache_hits']
            total_metrics['total_streaming_used'] += metrics['streaming_used']
        
        # Calcular ahorros en MB
        total_metrics['mb_saved'] = round(total_metrics['total_bytes_saved'] / 1024 / 1024, 2)
        
        return {
            'summary': total_metrics,
            'by_type': type_metrics,
            'optimization_effectiveness': self._calculate_effectiveness(total_metrics),
            'recommendations': self._generate_recommendations(type_metrics),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _calculate_effectiveness(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula efectividad de la optimización"""
        if metrics['total_responses'] == 0:
            return {'status': 'no_data'}
        
        cache_hit_rate = metrics['total_cache_hits'] / metrics['total_responses']
        avg_savings_per_response = metrics['total_bytes_saved'] / metrics['total_responses']
        
        return {
            'cache_hit_rate': round(cache_hit_rate, 3),
            'avg_bytes_saved_per_response': round(avg_savings_per_response, 0),
            'streaming_usage_rate': metrics['total_streaming_used'] / metrics['total_responses'],
            'effectiveness_score': min(100, (cache_hit_rate * 50 + min(avg_savings_per_response / 1000, 50)))
        }
    
    def _generate_recommendations(self, type_metrics: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones de optimización"""
        recommendations = []
        
        for response_type, metrics in type_metrics.items():
            if metrics['total_responses'] > 10:
                if metrics['avg_compression_ratio'] < 0.3:
                    recommendations.append(
                        f"Consider using higher optimization levels for {response_type} "
                        f"(current compression: {metrics['avg_compression_ratio']:.1%})"
                    )
                
                if metrics['cache_hits'] / max(metrics['total_responses'], 1) < 0.5:
                    recommendations.append(
                        f"Low cache hit rate for {response_type}. "
                        "Consider increasing cache TTL or improving cache keys"
                    )
        
        if not recommendations:
            recommendations.append("Optimization performing well. Continue monitoring.")
        
        return recommendations


# Instancia global del optimizador
response_optimizer = ResponseOptimizer()


# Funciones helper para uso sencillo
async def optimize_api_response(data: Any,
                               response_type: ResponseType,
                               fields: List[str] = None,
                               exclude_fields: List[str] = None,
                               optimization_level: OptimizationLevel = OptimizationLevel.STANDARD,
                               request_headers: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Función helper para optimizar respuestas API
    
    Args:
        data: Datos a optimizar
        response_type: Tipo de respuesta
        fields: Campos a incluir (opcional)
        exclude_fields: Campos a excluir (opcional)
        optimization_level: Nivel de optimización
        request_headers: Headers de la request
    
    Returns:
        Respuesta optimizada con metadatos
    """
    projection = None
    if fields or exclude_fields:
        projection = FieldProjection(
            include_fields=set(fields) if fields else set(),
            exclude_fields=set(exclude_fields) if exclude_fields else set()
        )
    
    return await response_optimizer.optimize_response(
        data=data,
        response_type=response_type,
        optimization_level=optimization_level,
        projection=projection,
        request_headers=request_headers
    )


async def get_stream_chunk(stream_id: str) -> Optional[StreamingChunk]:
    """Función helper para obtener chunks de streaming"""
    return await response_optimizer.get_streamed_response(stream_id)


async def enhance_progressive_response(data: Dict[str, Any],
                                     response_type: ResponseType,
                                     target_level: str) -> Dict[str, Any]:
    """Función helper para mejorar respuestas progresivas"""
    return await response_optimizer.enhance_response(data, response_type, target_level)


async def get_optimization_analytics() -> Dict[str, Any]:
    """Función helper para obtener analíticas de optimización"""
    return await response_optimizer.get_optimization_analytics()


# Ejemplo de uso
async def example_usage():
    """Ejemplo de uso del optimizador de respuestas"""
    
    # Datos de ejemplo (usuario completo)
    user_data = {
        'id': '123',
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 30,
        'created_at': '2024-01-01',
        'fitness_level': 'intermediate',
        'goals': ['weight_loss', 'muscle_gain'],
        'preferences': {
            'workout_time': 'morning',
            'dietary_restrictions': ['vegetarian']
        },
        'medical_history': {
            'conditions': [],
            'medications': []
        },
        'program_data': {
            'current_program': 'strength_building',
            'week': 4,
            'compliance': 0.85
        },
        'achievements': [
            {'id': 1, 'name': 'First Workout'},
            {'id': 2, 'name': '7 Day Streak'}
        ]
    }
    
    # Ejemplo 1: Optimización estándar con campos selectivos
    print("=== Ejemplo 1: Carga Selectiva ===")
    response1 = await optimize_api_response(
        data=user_data,
        response_type=ResponseType.USER_PROFILE,
        fields=['id', 'name', 'email', 'fitness_level'],
        optimization_level=OptimizationLevel.STANDARD
    )
    print(f"Original: {len(json.dumps(user_data))} bytes")
    print(f"Optimizado: {response1['metadata']['optimized_size']} bytes")
    print(f"Campos incluidos: {response1['metadata']['fields_included']}")
    
    # Ejemplo 2: Progressive enhancement
    print("\n=== Ejemplo 2: Progressive Enhancement ===")
    response2 = await optimize_api_response(
        data=user_data,
        response_type=ResponseType.USER_PROFILE,
        optimization_level=OptimizationLevel.ADVANCED
    )
    print(f"Nivel inicial: {response2['data'].get('_progressive', {}).get('current_level')}")
    print(f"Niveles disponibles: {response2['data'].get('_progressive', {}).get('available_levels')}")
    
    # Ejemplo 3: Streaming para datos grandes
    large_data = [{'id': i, 'data': f'Item {i}' * 100} for i in range(1000)]
    print("\n=== Ejemplo 3: Streaming ===")
    response3 = await optimize_api_response(
        data=large_data,
        response_type=ResponseType.ANALYTICS,
        optimization_level=OptimizationLevel.EXTREME
    )
    if response3['metadata'].get('streaming_enabled'):
        print(f"Streaming habilitado - Stream ID: {response3['data']['stream_id']}")
        print(f"Chunks estimados: {response3['data']['stream_metadata']['estimated_chunks']}")
    
    # Obtener analíticas
    print("\n=== Analíticas de Optimización ===")
    analytics = await get_optimization_analytics()
    print(f"Total respuestas optimizadas: {analytics['summary']['total_responses']}")
    print(f"MB ahorrados: {analytics['summary']['mb_saved']}")
    print(f"Efectividad: {analytics['optimization_effectiveness']}")


if __name__ == "__main__":
    asyncio.run(example_usage())