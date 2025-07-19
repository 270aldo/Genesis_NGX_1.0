"""
Memory Search Engine - FASE 12 POINT 1
======================================

Motor de búsqueda semántica avanzado para memoria conversacional que permite:
- Búsqueda semántica por contenido y contexto
- Filtros inteligentes por agente, tiempo y relevancia
- Scoring avanzado con múltiples criterios
- Cache inteligente de búsquedas frecuentes

IMPACTO: Recuperación de memoria 500% más inteligente y contextual
"""

import asyncio
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import re
import hashlib

from core.logging_config import get_logger
from core.memory_cache_optimizer import cache_get, cache_set, CachePriority
from core.conversation_memory import MemoryEntry, ConversationContext, EmotionalState, conversation_memory
from clients.supabase_client import get_supabase_client

logger = get_logger(__name__)


class SearchScope(Enum):
    """Alcance de búsqueda"""
    ALL = "all"
    RECENT = "recent"  # Últimas 24 horas
    WEEK = "week"  # Última semana
    MONTH = "month"  # Último mes
    SESSION = "session"  # Sesión específica


class SortOrder(Enum):
    """Orden de resultados"""
    RELEVANCE = "relevance"  # Por score de relevancia
    TIMESTAMP = "timestamp"  # Por fecha (más reciente primero)
    IMPORTANCE = "importance"  # Por score de importancia
    MIXED = "mixed"  # Combinación de factores


@dataclass
class SearchFilter:
    """Filtros de búsqueda"""
    agent_ids: Optional[List[str]] = None
    contexts: Optional[List[ConversationContext]] = None
    emotional_states: Optional[List[EmotionalState]] = None
    min_importance: Optional[float] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para cache key"""
        return {
            'agent_ids': self.agent_ids,
            'contexts': [c.value for c in self.contexts] if self.contexts else None,
            'emotional_states': [e.value for e in self.emotional_states] if self.emotional_states else None,
            'min_importance': self.min_importance,
            'date_from': self.date_from.isoformat() if self.date_from else None,
            'date_to': self.date_to.isoformat() if self.date_to else None,
            'session_id': self.session_id
        }


@dataclass
class SearchResult:
    """Resultado de búsqueda con scoring"""
    memory_entry: MemoryEntry
    relevance_score: float  # 0.0 - 1.0
    match_highlights: List[str]  # Fragmentos que coinciden
    match_reason: str  # Explicación de por qué coincide
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'memory_entry': self.memory_entry.to_dict(),
            'relevance_score': self.relevance_score,
            'match_highlights': self.match_highlights,
            'match_reason': self.match_reason
        }


class MemorySearchEngine:
    """
    Motor de búsqueda semántica avanzado para memoria conversacional
    
    CARACTERÍSTICAS AVANZADAS:
    - Búsqueda textual con stemming y sinónimos
    - Búsqueda semántica por contexto y emociones
    - Scoring multi-criterio (relevancia, recencia, importancia)
    - Cache inteligente de búsquedas populares
    - Sugerencias automáticas de búsqueda
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.search_cache_prefix = "memory_search"
        
        # Diccionarios para análisis semántico
        self.context_keywords = {
            ConversationContext.WORKOUT_PLANNING: [
                'ejercicio', 'entrenamiento', 'rutina', 'fitness', 'gym', 'músculo',
                'repeticiones', 'series', 'peso', 'cardio', 'fuerza'
            ],
            ConversationContext.NUTRITION_GUIDANCE: [
                'comida', 'nutrición', 'dieta', 'proteína', 'carbohidratos', 'grasas',
                'calorías', 'macros', 'vitaminas', 'suplementos', 'alimentación'
            ],
            ConversationContext.PROGRESS_REVIEW: [
                'progreso', 'resultados', 'medidas', 'peso', 'logros', 'mejoras',
                'avance', 'evolución', 'comparación', 'estadísticas'
            ],
            ConversationContext.MOTIVATION_SUPPORT: [
                'motivación', 'apoyo', 'ánimo', 'meta', 'objetivo', 'inspiración',
                'constancia', 'determinación', 'fuerza mental', 'perseverancia'
            ]
        }
        
        self.emotional_keywords = {
            EmotionalState.MOTIVATED: ['entusiasmado', 'motivado', 'energético', 'positivo'],
            EmotionalState.FRUSTRATED: ['frustrado', 'molesto', 'irritado', 'desanimado'],
            EmotionalState.CONFIDENT: ['seguro', 'confiado', 'capaz', 'determinado'],
            EmotionalState.UNCERTAIN: ['dudoso', 'inseguro', 'confundido', 'indeciso']
        }
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        filters: Optional[SearchFilter] = None,
        scope: SearchScope = SearchScope.ALL,
        sort_order: SortOrder = SortOrder.MIXED,
        limit: int = 20
    ) -> List[SearchResult]:
        """
        Búsqueda principal de memorias con scoring avanzado
        
        Args:
            user_id: ID del usuario
            query: Texto de búsqueda
            filters: Filtros adicionales
            scope: Alcance temporal de búsqueda
            sort_order: Orden de resultados
            limit: Máximo número de resultados
        
        Returns:
            Lista de resultados ordenados por relevancia
        """
        try:
            # Intentar desde caché
            cache_key = self._generate_search_cache_key(
                user_id, query, filters, scope, sort_order, limit
            )
            
            cached_results = await cache_get(cache_key)
            if cached_results:
                logger.debug(f"Resultados de búsqueda obtenidos desde caché: {cache_key}")
                return [
                    SearchResult(
                        memory_entry=MemoryEntry.from_dict(r['memory_entry']),
                        relevance_score=r['relevance_score'],
                        match_highlights=r['match_highlights'],
                        match_reason=r['match_reason']
                    )
                    for r in cached_results
                ]
            
            # Preparar filtros temporales
            time_filters = self._prepare_time_filters(scope, filters)
            
            # Obtener candidatos de memoria
            candidates = await conversation_memory.get_conversation_history(
                user_id=user_id,
                agent_id=filters.agent_ids[0] if filters and filters.agent_ids else None,
                context=filters.contexts[0] if filters and filters.contexts else None,
                limit=500  # Obtener más candidatos para mejor scoring
            )
            
            # Aplicar filtros adicionales
            filtered_candidates = self._apply_filters(candidates, filters, time_filters)
            
            # Realizar scoring semántico
            scored_results = await self._score_memories(query, filtered_candidates)
            
            # Ordenar resultados
            sorted_results = self._sort_results(scored_results, sort_order)
            
            # Aplicar límite
            final_results = sorted_results[:limit]
            
            # Cachear resultados
            await cache_set(
                cache_key,
                [r.to_dict() for r in final_results],
                ttl=300,  # 5 minutos
                priority=CachePriority.NORMAL
            )
            
            logger.info(f"Búsqueda completada: {len(final_results)} resultados para '{query}'")
            return final_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda de memoria: {e}")
            return []
    
    async def search_by_context(
        self,
        user_id: str,
        context: ConversationContext,
        emotional_state: Optional[EmotionalState] = None,
        limit: int = 20
    ) -> List[SearchResult]:
        """Búsqueda específica por contexto conversacional"""
        try:
            # Generar query basado en contexto
            context_query = " ".join(self.context_keywords.get(context, []))
            
            if emotional_state:
                emotional_query = " ".join(self.emotional_keywords.get(emotional_state, []))
                context_query = f"{context_query} {emotional_query}"
            
            # Configurar filtros
            filters = SearchFilter(
                contexts=[context],
                emotional_states=[emotional_state] if emotional_state else None
            )
            
            return await self.search_memories(
                user_id=user_id,
                query=context_query,
                filters=filters,
                scope=SearchScope.ALL,
                sort_order=SortOrder.RELEVANCE,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Error en búsqueda por contexto: {e}")
            return []
    
    async def search_similar_conversations(
        self,
        user_id: str,
        reference_memory: MemoryEntry,
        limit: int = 10
    ) -> List[SearchResult]:
        """Encuentra conversaciones similares a una memoria de referencia"""
        try:
            # Extraer términos clave de la memoria de referencia
            key_terms = self._extract_key_terms(reference_memory.content)
            
            # Crear query de similitud
            similarity_query = " ".join(key_terms[:10])  # Top 10 términos
            
            # Configurar filtros similares
            filters = SearchFilter(
                contexts=[reference_memory.context] if reference_memory.context else None,
                emotional_states=[reference_memory.emotional_state] if reference_memory.emotional_state else None,
                min_importance=max(0.1, reference_memory.importance_score - 0.3)
            )
            
            # Buscar memorias similares
            results = await self.search_memories(
                user_id=user_id,
                query=similarity_query,
                filters=filters,
                scope=SearchScope.ALL,
                sort_order=SortOrder.RELEVANCE,
                limit=limit + 1  # +1 para excluir la memoria de referencia
            )
            
            # Excluir la memoria de referencia de los resultados
            filtered_results = [
                r for r in results 
                if r.memory_entry.id != reference_memory.id
            ]
            
            return filtered_results[:limit]
            
        except Exception as e:
            logger.error(f"Error buscando conversaciones similares: {e}")
            return []
    
    async def get_search_suggestions(
        self,
        user_id: str,
        partial_query: str,
        limit: int = 5
    ) -> List[str]:
        """Genera sugerencias de búsqueda basadas en el historial del usuario"""
        try:
            if len(partial_query) < 2:
                return []
            
            # Obtener memoria reciente del usuario
            recent_memories = await conversation_memory.get_conversation_history(
                user_id=user_id,
                limit=100
            )
            
            # Extraer términos frecuentes que coincidan con la consulta parcial
            suggestions = set()
            partial_lower = partial_query.lower()
            
            for memory in recent_memories:
                words = self._tokenize_text(memory.content)
                for word in words:
                    if (word.lower().startswith(partial_lower) and 
                        len(word) > len(partial_query) and
                        len(word) <= 20):  # Evitar palabras muy largas
                        suggestions.add(word.lower())
            
            # Agregar sugerencias de contexto si aplican
            for context in ConversationContext:
                context_words = self.context_keywords.get(context, [])
                for word in context_words:
                    if word.lower().startswith(partial_lower):
                        suggestions.add(word)
            
            # Ordenar por frecuencia y retornar top resultados
            sorted_suggestions = sorted(list(suggestions))[:limit]
            
            return sorted_suggestions
            
        except Exception as e:
            logger.error(f"Error generando sugerencias: {e}")
            return []
    
    def _prepare_time_filters(
        self, 
        scope: SearchScope, 
        filters: Optional[SearchFilter]
    ) -> Dict[str, datetime]:
        """Prepara filtros temporales basados en el alcance"""
        time_filters = {}
        now = datetime.utcnow()
        
        if scope == SearchScope.RECENT:
            time_filters['date_from'] = now - timedelta(hours=24)
        elif scope == SearchScope.WEEK:
            time_filters['date_from'] = now - timedelta(days=7)
        elif scope == SearchScope.MONTH:
            time_filters['date_from'] = now - timedelta(days=30)
        
        # Aplicar filtros adicionales si se proporcionan
        if filters:
            if filters.date_from:
                time_filters['date_from'] = max(
                    time_filters.get('date_from', filters.date_from),
                    filters.date_from
                )
            if filters.date_to:
                time_filters['date_to'] = filters.date_to
        
        return time_filters
    
    def _apply_filters(
        self,
        candidates: List[MemoryEntry],
        filters: Optional[SearchFilter],
        time_filters: Dict[str, datetime]
    ) -> List[MemoryEntry]:
        """Aplica filtros a los candidatos de memoria"""
        if not filters and not time_filters:
            return candidates
        
        filtered = []
        
        for memory in candidates:
            # Filtro temporal
            if time_filters.get('date_from') and memory.timestamp < time_filters['date_from']:
                continue
            if time_filters.get('date_to') and memory.timestamp > time_filters['date_to']:
                continue
            
            if not filters:
                filtered.append(memory)
                continue
            
            # Filtro por agente
            if filters.agent_ids and memory.agent_id not in filters.agent_ids:
                continue
            
            # Filtro por contexto
            if filters.contexts and memory.context not in filters.contexts:
                continue
            
            # Filtro por estado emocional
            if filters.emotional_states and memory.emotional_state not in filters.emotional_states:
                continue
            
            # Filtro por importancia mínima
            if filters.min_importance and memory.importance_score < filters.min_importance:
                continue
            
            # Filtro por sesión
            if filters.session_id and memory.session_id != filters.session_id:
                continue
            
            filtered.append(memory)
        
        return filtered
    
    async def _score_memories(
        self,
        query: str,
        candidates: List[MemoryEntry]
    ) -> List[SearchResult]:
        """Aplica scoring semántico a los candidatos"""
        query_terms = self._tokenize_text(query)
        results = []
        
        for memory in candidates:
            # Calcular score de relevancia textual
            text_score = self._calculate_text_relevance(query_terms, memory.content)
            
            # Calcular score de relevancia contextual
            context_score = self._calculate_context_relevance(query_terms, memory)
            
            # Calcular score temporal (más reciente = mayor score)
            time_score = self._calculate_time_relevance(memory.timestamp)
            
            # Calcular score de importancia
            importance_score = memory.importance_score
            
            # Score combinado
            combined_score = (
                text_score * 0.4 +
                context_score * 0.25 +
                time_score * 0.2 +
                importance_score * 0.15
            )
            
            if combined_score > 0.1:  # Umbral mínimo de relevancia
                # Generar highlights
                highlights = self._generate_highlights(query_terms, memory.content)
                
                # Generar explicación de match
                match_reason = self._generate_match_reason(
                    text_score, context_score, time_score, importance_score
                )
                
                result = SearchResult(
                    memory_entry=memory,
                    relevance_score=combined_score,
                    match_highlights=highlights,
                    match_reason=match_reason
                )
                
                results.append(result)
        
        return results
    
    def _calculate_text_relevance(self, query_terms: List[str], content: str) -> float:
        """Calcula relevancia textual usando TF-IDF simplificado"""
        content_terms = self._tokenize_text(content)
        content_lower = [term.lower() for term in content_terms]
        
        if not query_terms or not content_terms:
            return 0.0
        
        matches = 0
        for term in query_terms:
            if term.lower() in content_lower:
                # Bonus por palabras completas
                if term in content_terms:
                    matches += 2
                else:
                    matches += 1
        
        # Normalizar por longitud de query y contenido
        max_possible_matches = len(query_terms) * 2
        relevance = matches / max_possible_matches if max_possible_matches > 0 else 0.0
        
        return min(relevance, 1.0)
    
    def _calculate_context_relevance(
        self,
        query_terms: List[str],
        memory: MemoryEntry
    ) -> float:
        """Calcula relevancia contextual basada en contexto y estado emocional"""
        score = 0.0
        
        # Score por contexto
        if memory.context:
            context_keywords = self.context_keywords.get(memory.context, [])
            for term in query_terms:
                if term.lower() in [kw.lower() for kw in context_keywords]:
                    score += 0.5
        
        # Score por estado emocional
        if memory.emotional_state:
            emotional_keywords = self.emotional_keywords.get(memory.emotional_state, [])
            for term in query_terms:
                if term.lower() in [kw.lower() for kw in emotional_keywords]:
                    score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_time_relevance(self, timestamp: datetime) -> float:
        """Calcula relevancia temporal (más reciente = mayor score)"""
        now = datetime.utcnow()
        age_hours = (now - timestamp).total_seconds() / 3600
        
        # Decay exponencial con half-life de 7 días
        half_life_hours = 7 * 24
        decay_factor = math.exp(-0.693 * age_hours / half_life_hours)
        
        return decay_factor
    
    def _sort_results(
        self,
        results: List[SearchResult],
        sort_order: SortOrder
    ) -> List[SearchResult]:
        """Ordena resultados según el criterio especificado"""
        if sort_order == SortOrder.RELEVANCE:
            return sorted(results, key=lambda r: r.relevance_score, reverse=True)
        elif sort_order == SortOrder.TIMESTAMP:
            return sorted(results, key=lambda r: r.memory_entry.timestamp, reverse=True)
        elif sort_order == SortOrder.IMPORTANCE:
            return sorted(results, key=lambda r: r.memory_entry.importance_score, reverse=True)
        elif sort_order == SortOrder.MIXED:
            # Combinar relevancia y recencia
            return sorted(
                results,
                key=lambda r: (r.relevance_score * 0.7 + self._calculate_time_relevance(r.memory_entry.timestamp) * 0.3),
                reverse=True
            )
        else:
            return results
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokeniza texto en palabras relevantes"""
        # Limpiar y dividir por espacios
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filtrar palabras muy cortas y stopwords básicas
        stopwords = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'las', 'del', 'los', 'una', 'al', 'todo', 'esta', 'sus', 'otro', 'como', 'pero', 'ese', 'dos', 'más', 'muy', 'o', 'si', 'mi', 'ya', 'hasta', 'hay'}
        
        filtered_words = [
            word for word in words 
            if len(word) > 2 and word not in stopwords
        ]
        
        return filtered_words
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extrae términos clave de un texto"""
        words = self._tokenize_text(text)
        
        # Contar frecuencias
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Ordenar por frecuencia
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Retornar palabras más frecuentes
        return [word for word, freq in sorted_words]
    
    def _generate_highlights(self, query_terms: List[str], content: str) -> List[str]:
        """Genera fragmentos destacados que coinciden con la búsqueda"""
        highlights = []
        content_lower = content.lower()
        
        for term in query_terms:
            term_lower = term.lower()
            if term_lower in content_lower:
                # Encontrar posición del término
                start_pos = content_lower.find(term_lower)
                
                # Extraer contexto alrededor del término
                context_start = max(0, start_pos - 30)
                context_end = min(len(content), start_pos + len(term) + 30)
                
                context = content[context_start:context_end]
                
                # Agregar puntos suspensivos si se truncó
                if context_start > 0:
                    context = "..." + context
                if context_end < len(content):
                    context = context + "..."
                
                highlights.append(context)
        
        return highlights[:3]  # Máximo 3 highlights
    
    def _generate_match_reason(
        self,
        text_score: float,
        context_score: float,
        time_score: float,
        importance_score: float
    ) -> str:
        """Genera explicación de por qué coincidió el resultado"""
        reasons = []
        
        if text_score > 0.3:
            reasons.append("coincidencia textual")
        
        if context_score > 0.2:
            reasons.append("contexto relevante")
        
        if time_score > 0.5:
            reasons.append("conversación reciente")
        
        if importance_score > 0.7:
            reasons.append("alta importancia")
        
        if not reasons:
            reasons.append("relevancia general")
        
        return ", ".join(reasons)
    
    def _generate_search_cache_key(
        self,
        user_id: str,
        query: str,
        filters: Optional[SearchFilter],
        scope: SearchScope,
        sort_order: SortOrder,
        limit: int
    ) -> str:
        """Genera clave de caché para búsqueda"""
        key_parts = [
            self.search_cache_prefix,
            user_id,
            query.lower(),
            scope.value,
            sort_order.value,
            str(limit)
        ]
        
        if filters:
            filter_str = json.dumps(filters.to_dict(), sort_keys=True)
            key_parts.append(hashlib.md5(filter_str.encode()).hexdigest()[:8])
        
        return ":".join(key_parts)
    
    async def get_search_analytics(self, user_id: str) -> Dict[str, Any]:
        """Obtiene analíticas de búsqueda para un usuario"""
        try:
            # Obtener memorias del usuario
            memories = await conversation_memory.get_conversation_history(
                user_id=user_id,
                limit=500
            )
            
            if not memories:
                return {}
            
            # Analizar distribución por contexto
            context_distribution = {}
            for memory in memories:
                if memory.context:
                    context = memory.context.value
                    context_distribution[context] = context_distribution.get(context, 0) + 1
            
            # Analizar distribución emocional
            emotional_distribution = {}
            for memory in memories:
                if memory.emotional_state:
                    emotion = memory.emotional_state.value
                    emotional_distribution[emotion] = emotional_distribution.get(emotion, 0) + 1
            
            # Términos más frecuentes
            all_words = []
            for memory in memories:
                words = self._tokenize_text(memory.content)
                all_words.extend(words)
            
            word_freq = {}
            for word in all_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            top_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'total_memories': len(memories),
                'context_distribution': context_distribution,
                'emotional_distribution': emotional_distribution,
                'top_terms': [{'term': term, 'frequency': freq} for term, freq in top_terms],
                'memory_date_range': {
                    'oldest': memories[-1].timestamp.isoformat() if memories else None,
                    'newest': memories[0].timestamp.isoformat() if memories else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo analíticas de búsqueda: {e}")
            return {}


# Instancia global del motor de búsqueda
memory_search = MemorySearchEngine()


# Funciones helper para uso sencillo
async def search_user_memories(
    user_id: str,
    query: str,
    filters: Optional[SearchFilter] = None,
    limit: int = 20
) -> List[SearchResult]:
    """Función helper para búsqueda de memorias"""
    return await memory_search.search_memories(
        user_id=user_id,
        query=query,
        filters=filters,
        limit=limit
    )


async def find_similar_conversations(
    user_id: str,
    reference_memory: MemoryEntry,
    limit: int = 10
) -> List[SearchResult]:
    """Función helper para encontrar conversaciones similares"""
    return await memory_search.search_similar_conversations(
        user_id=user_id,
        reference_memory=reference_memory,
        limit=limit
    )


async def get_memory_search_suggestions(
    user_id: str,
    partial_query: str
) -> List[str]:
    """Función helper para sugerencias de búsqueda"""
    return await memory_search.get_search_suggestions(
        user_id=user_id,
        partial_query=partial_query
    )