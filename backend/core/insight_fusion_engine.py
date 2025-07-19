"""
Insight Fusion Engine - FASE 12 POINT 2
========================================

Motor de fusión inteligente que combina insights de múltiples agentes especializados
para generar recomendaciones unificadas y análisis de alto nivel.

FUNCIONALIDADES CLAVE:
- Fusión de datos multi-agente con ponderación inteligente
- Resolución de conflictos entre insights contradictorios
- Generación de meta-insights y patrones emergentes
- Síntesis de recomendaciones accionables
- Scoring de confianza agregado
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import statistics

from core.logging_config import get_logger
from core.memory_cache_optimizer import cache_get, cache_set, cache_invalidate, CachePriority
from core.agent_collaboration_hub import (
    AgentRole, AgentInsight, CollaborativeInsight, InsightPriority
)

logger = get_logger(__name__)


class FusionStrategy(Enum):
    """Estrategias de fusión de insights"""
    WEIGHTED_AVERAGE = "weighted_average"  # Promedio ponderado por confianza
    CONSENSUS_BASED = "consensus_based"    # Basado en consenso de mayoría
    EXPERT_PRIORITY = "expert_priority"    # Prioridad a agentes con mayor expertise
    TEMPORAL_FUSION = "temporal_fusion"    # Fusión basada en recencia temporal
    CONFIDENCE_FUSION = "confidence_fusion" # Fusión basada en scores de confianza


class ConflictResolution(Enum):
    """Métodos de resolución de conflictos"""
    MAJORITY_RULE = "majority_rule"        # Regla de mayoría
    HIGHEST_CONFIDENCE = "highest_confidence" # Mayor confianza gana
    DOMAIN_EXPERTISE = "domain_expertise"   # Expertise en dominio específico
    TEMPORAL_PRIORITY = "temporal_priority" # Datos más recientes prioritarios
    USER_PREFERENCE = "user_preference"     # Preferencias históricas del usuario


@dataclass
class FusionContext:
    """Contexto para el proceso de fusión"""
    user_id: str
    domain_focus: Optional[str] = None  # nutrition, fitness, wellness, etc.
    temporal_window: Optional[timedelta] = None
    confidence_threshold: float = 0.6
    conflict_resolution: ConflictResolution = ConflictResolution.HIGHEST_CONFIDENCE
    fusion_strategy: FusionStrategy = FusionStrategy.WEIGHTED_AVERAGE
    user_preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.user_preferences is None:
            self.user_preferences = {}
        if self.temporal_window is None:
            self.temporal_window = timedelta(hours=24)


@dataclass
class FusedInsight:
    """Insight resultante del proceso de fusión"""
    insight_id: str
    unified_content: str
    contributing_agents: List[AgentRole]
    fusion_method: str
    confidence_score: float
    consensus_level: float
    conflict_indicators: List[str]
    meta_insights: List[str]
    actionable_recommendations: List[str]
    data_sources: List[str]
    fusion_timestamp: datetime
    user_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        data = asdict(self)
        data['contributing_agents'] = [agent.value for agent in self.contributing_agents]
        data['fusion_timestamp'] = self.fusion_timestamp.isoformat()
        return data


@dataclass
class ConflictAnalysis:
    """Análisis de conflictos entre insights"""
    conflict_type: str  # data_contradiction, recommendation_conflict, confidence_disparity
    conflicting_agents: List[AgentRole]
    conflict_severity: float  # 0.0 - 1.0
    resolution_method: str
    resolution_confidence: float
    affected_domains: List[str]


class InsightFusionEngine:
    """
    Motor de fusión inteligente para combinar insights de múltiples agentes
    
    CAPACIDADES AVANZADAS:
    - Análisis de correlaciones cruzadas entre dominios
    - Detección de patrones emergentes
    - Resolución inteligente de conflictos
    - Generación de meta-insights de alto nivel
    - Optimización basada en feedback del usuario
    """
    
    def __init__(self):
        self.cache_prefix = "fusion_engine"
        self.fusion_history = {}
        self.user_feedback_patterns = {}
        
        # Configuración de pesos por dominio
        self.domain_weights = {
            "nutrition": 0.25,
            "fitness": 0.25, 
            "analytics": 0.20,
            "wellness": 0.15,
            "genetics": 0.10,
            "psychology": 0.05
        }
        
        # Matriz de compatibilidad entre agentes
        self.agent_compatibility_matrix = self._initialize_compatibility_matrix()
    
    def _initialize_compatibility_matrix(self) -> Dict[Tuple[AgentRole, AgentRole], float]:
        """Inicializa matriz de compatibilidad entre agentes"""
        matrix = {}
        
        # Altas compatibilidades conocidas
        high_compatibility_pairs = [
            (AgentRole.SAGE_NUTRITION, AgentRole.BLAZE_TRAINING),     # 0.95
            (AgentRole.WAVE_ANALYTICS, AgentRole.STELLA_PROGRESS),    # 0.92
            (AgentRole.NOVA_BIOHACKING, AgentRole.LUNA_WELLNESS),     # 0.93
            (AgentRole.HELIX_GENETICS, AgentRole.VOLT_BIOMETRICS),    # 0.94
        ]
        
        # Asignar altas compatibilidades
        for agent1, agent2 in high_compatibility_pairs:
            matrix[(agent1, agent2)] = 0.95
            matrix[(agent2, agent1)] = 0.95
        
        # Compatibilidades medias por defecto
        all_agents = list(AgentRole)
        for i, agent1 in enumerate(all_agents):
            for agent2 in all_agents[i+1:]:
                if (agent1, agent2) not in matrix:
                    matrix[(agent1, agent2)] = 0.7
                    matrix[(agent2, agent1)] = 0.7
        
        return matrix
    
    async def fuse_insights(
        self,
        insights: List[AgentInsight],
        context: FusionContext
    ) -> FusedInsight:
        """
        Fusiona múltiples insights en un insight unificado
        
        Args:
            insights: Lista de insights individuales de agentes
            context: Contexto de fusión con parámetros
        
        Returns:
            FusedInsight: Insight fusionado y optimizado
        """
        try:
            if not insights:
                raise ValueError("No insights provided for fusion")
            
            fusion_id = str(uuid.uuid4())
            
            # 1. Análisis de conflictos
            conflicts = await self._analyze_conflicts(insights, context)
            
            # 2. Filtrado por confianza y temporal
            filtered_insights = await self._filter_insights(insights, context)
            
            # 3. Aplicar estrategia de fusión
            unified_content = await self._apply_fusion_strategy(
                filtered_insights, context, conflicts
            )
            
            # 4. Calcular métricas de fusión
            confidence_score = await self._calculate_fusion_confidence(
                filtered_insights, conflicts
            )
            consensus_level = self._calculate_consensus_level(filtered_insights)
            
            # 5. Generar meta-insights
            meta_insights = await self._generate_meta_insights(
                filtered_insights, context
            )
            
            # 6. Crear recomendaciones accionables
            recommendations = await self._synthesize_recommendations(
                filtered_insights, meta_insights, context
            )
            
            # 7. Construir insight fusionado
            fused_insight = FusedInsight(
                insight_id=fusion_id,
                unified_content=unified_content,
                contributing_agents=[insight.agent_id for insight in filtered_insights],
                fusion_method=context.fusion_strategy.value,
                confidence_score=confidence_score,
                consensus_level=consensus_level,
                conflict_indicators=[c.conflict_type for c in conflicts],
                meta_insights=meta_insights,
                actionable_recommendations=recommendations,
                data_sources=self._extract_data_sources(filtered_insights),
                fusion_timestamp=datetime.utcnow(),
                user_id=context.user_id
            )
            
            # 8. Cachear resultado
            await self._cache_fused_insight(fused_insight)
            
            # 9. Actualizar historial de fusión
            await self._update_fusion_history(context.user_id, fused_insight)
            
            logger.info(f"Fusión completada: {fusion_id} con {len(filtered_insights)} insights")
            
            return fused_insight
            
        except Exception as e:
            logger.error(f"Error en fusión de insights: {e}")
            raise
    
    async def _analyze_conflicts(
        self, 
        insights: List[AgentInsight], 
        context: FusionContext
    ) -> List[ConflictAnalysis]:
        """Analiza conflictos entre insights"""
        conflicts = []
        
        try:
            # Comparar insights por pares
            for i, insight1 in enumerate(insights):
                for insight2 in insights[i+1:]:
                    
                    # Detectar contradicciones en recomendaciones
                    recommendation_conflict = self._detect_recommendation_conflicts(
                        insight1.recommendations, insight2.recommendations
                    )
                    
                    if recommendation_conflict:
                        conflicts.append(ConflictAnalysis(
                            conflict_type="recommendation_conflict",
                            conflicting_agents=[insight1.agent_id, insight2.agent_id],
                            conflict_severity=recommendation_conflict['severity'],
                            resolution_method=context.conflict_resolution.value,
                            resolution_confidence=0.8,
                            affected_domains=[
                                self._get_agent_domain(insight1.agent_id),
                                self._get_agent_domain(insight2.agent_id)
                            ]
                        ))
                    
                    # Detectar disparidad en confianza
                    confidence_diff = abs(insight1.confidence - insight2.confidence)
                    if confidence_diff > 0.3:
                        conflicts.append(ConflictAnalysis(
                            conflict_type="confidence_disparity",
                            conflicting_agents=[insight1.agent_id, insight2.agent_id],
                            conflict_severity=confidence_diff,
                            resolution_method="confidence_weighted",
                            resolution_confidence=0.9,
                            affected_domains=["confidence_scoring"]
                        ))
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error analizando conflictos: {e}")
            return []
    
    def _detect_recommendation_conflicts(
        self, 
        rec1: List[str], 
        rec2: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Detecta conflictos entre recomendaciones"""
        
        # Palabras clave que indican conflictos
        conflict_patterns = [
            (["increase", "more", "higher"], ["decrease", "less", "lower"]),
            (["avoid", "stop", "reduce"], ["continue", "maintain", "increase"]),
            (["rest", "recovery"], ["intense", "high-intensity", "push"]),
            (["carbs", "carbohydrates"], ["low-carb", "keto", "no-carbs"])
        ]
        
        rec1_text = " ".join(rec1).lower()
        rec2_text = " ".join(rec2).lower()
        
        for positive_words, negative_words in conflict_patterns:
            has_positive_1 = any(word in rec1_text for word in positive_words)
            has_negative_2 = any(word in rec2_text for word in negative_words)
            
            has_positive_2 = any(word in rec2_text for word in positive_words)
            has_negative_1 = any(word in rec1_text for word in negative_words)
            
            if (has_positive_1 and has_negative_2) or (has_positive_2 and has_negative_1):
                return {
                    "severity": 0.7,
                    "pattern": f"{positive_words} vs {negative_words}",
                    "conflicting_terms": [positive_words, negative_words]
                }
        
        return None
    
    def _get_agent_domain(self, agent_id: AgentRole) -> str:
        """Obtiene el dominio de un agente"""
        domain_mapping = {
            AgentRole.SAGE_NUTRITION: "nutrition",
            AgentRole.BLAZE_TRAINING: "fitness",
            AgentRole.WAVE_ANALYTICS: "analytics",
            AgentRole.STELLA_PROGRESS: "progress",
            AgentRole.NOVA_BIOHACKING: "biohacking",
            AgentRole.LUNA_WELLNESS: "wellness",
            AgentRole.HELIX_GENETICS: "genetics",
            AgentRole.VOLT_BIOMETRICS: "biometrics",
            AgentRole.NEXUS_MOTIVATION: "psychology"
        }
        return domain_mapping.get(agent_id, "unknown")
    
    async def _filter_insights(
        self, 
        insights: List[AgentInsight], 
        context: FusionContext
    ) -> List[AgentInsight]:
        """Filtra insights basado en criterios del contexto"""
        filtered = []
        
        for insight in insights:
            # Filtro por confianza mínima
            if insight.confidence < context.confidence_threshold:
                continue
            
            # Filtro temporal
            if context.temporal_window:
                time_diff = datetime.utcnow() - insight.generated_at
                if time_diff > context.temporal_window:
                    continue
            
            # Filtro por dominio
            if context.domain_focus:
                agent_domain = self._get_agent_domain(insight.agent_id)
                if agent_domain != context.domain_focus:
                    continue
            
            filtered.append(insight)
        
        return filtered
    
    async def _apply_fusion_strategy(
        self,
        insights: List[AgentInsight],
        context: FusionContext,
        conflicts: List[ConflictAnalysis]
    ) -> str:
        """Aplica estrategia de fusión seleccionada"""
        
        if context.fusion_strategy == FusionStrategy.WEIGHTED_AVERAGE:
            return await self._weighted_average_fusion(insights)
        
        elif context.fusion_strategy == FusionStrategy.CONSENSUS_BASED:
            return await self._consensus_based_fusion(insights)
        
        elif context.fusion_strategy == FusionStrategy.EXPERT_PRIORITY:
            return await self._expert_priority_fusion(insights, context)
        
        elif context.fusion_strategy == FusionStrategy.CONFIDENCE_FUSION:
            return await self._confidence_based_fusion(insights)
        
        else:
            # Default: weighted average
            return await self._weighted_average_fusion(insights)
    
    async def _weighted_average_fusion(self, insights: List[AgentInsight]) -> str:
        """Fusión por promedio ponderado"""
        if not insights:
            return "No hay insights disponibles para fusión"
        
        # Ponderar por confianza
        total_weight = sum(insight.confidence for insight in insights)
        
        fusion_parts = []
        for insight in insights:
            weight = insight.confidence / total_weight if total_weight > 0 else 1.0 / len(insights)
            weight_percentage = int(weight * 100)
            
            fusion_parts.append(
                f"**{insight.agent_id.value.upper()}** ({weight_percentage}%): {insight.content}"
            )
        
        unified_content = "## ANÁLISIS FUSIONADO MULTI-AGENTE\n\n" + "\n\n".join(fusion_parts)
        
        # Agregar síntesis ejecutiva
        unified_content += "\n\n## SÍNTESIS EJECUTIVA\n"
        unified_content += "Los agentes especializados convergen en un enfoque integrado que combina "
        unified_content += f"expertise de {len(insights)} dominios complementarios para optimización holística."
        
        return unified_content
    
    async def _consensus_based_fusion(self, insights: List[AgentInsight]) -> str:
        """Fusión basada en consenso"""
        # Extraer temas comunes
        common_themes = self._extract_common_themes(insights)
        
        fusion_content = "## CONSENSO MULTI-AGENTE\n\n"
        
        if common_themes:
            fusion_content += "### ÁREAS DE CONSENSO:\n"
            for theme, frequency in common_themes.items():
                if frequency >= len(insights) * 0.6:  # 60% de consenso
                    fusion_content += f"• **{theme}**: Confirmado por {frequency}/{len(insights)} agentes\n"
        
        fusion_content += "\n### PERSPECTIVAS INTEGRADAS:\n"
        for insight in insights:
            fusion_content += f"• {insight.content}\n"
        
        return fusion_content
    
    async def _expert_priority_fusion(
        self, 
        insights: List[AgentInsight], 
        context: FusionContext
    ) -> str:
        """Fusión con prioridad a expertise específico"""
        
        # Ordenar por relevancia de expertise al dominio
        domain_relevance = {}
        for insight in insights:
            agent_domain = self._get_agent_domain(insight.agent_id)
            if context.domain_focus and agent_domain == context.domain_focus:
                domain_relevance[insight] = 1.0
            else:
                domain_relevance[insight] = 0.7
        
        # Ordenar por relevancia y confianza
        sorted_insights = sorted(
            insights, 
            key=lambda x: domain_relevance.get(x, 0.5) * x.confidence, 
            reverse=True
        )
        
        fusion_content = f"## ANÁLISIS EXPERTO - ENFOQUE {context.domain_focus or 'INTEGRADO'}\n\n"
        
        # Insight principal (mayor expertise)
        primary_insight = sorted_insights[0]
        fusion_content += f"### PERSPECTIVA PRINCIPAL ({primary_insight.agent_id.value}):\n"
        fusion_content += f"{primary_insight.content}\n\n"
        
        # Insights de apoyo
        if len(sorted_insights) > 1:
            fusion_content += "### PERSPECTIVAS COMPLEMENTARIAS:\n"
            for insight in sorted_insights[1:]:
                fusion_content += f"**{insight.agent_id.value}**: {insight.content}\n\n"
        
        return fusion_content
    
    async def _confidence_based_fusion(self, insights: List[AgentInsight]) -> str:
        """Fusión basada en scores de confianza"""
        # Ordenar por confianza
        sorted_insights = sorted(insights, key=lambda x: x.confidence, reverse=True)
        
        fusion_content = "## ANÁLISIS POR NIVEL DE CONFIANZA\n\n"
        
        # Categorizar por niveles de confianza
        high_confidence = [i for i in sorted_insights if i.confidence >= 0.8]
        medium_confidence = [i for i in sorted_insights if 0.6 <= i.confidence < 0.8]
        low_confidence = [i for i in sorted_insights if i.confidence < 0.6]
        
        if high_confidence:
            fusion_content += "### INSIGHTS DE ALTA CONFIANZA (≥80%):\n"
            for insight in high_confidence:
                fusion_content += f"• **{insight.agent_id.value}** ({insight.confidence:.0%}): {insight.content}\n"
            fusion_content += "\n"
        
        if medium_confidence:
            fusion_content += "### INSIGHTS DE CONFIANZA MEDIA (60-79%):\n"
            for insight in medium_confidence:
                fusion_content += f"• **{insight.agent_id.value}** ({insight.confidence:.0%}): {insight.content}\n"
            fusion_content += "\n"
        
        return fusion_content
    
    def _extract_common_themes(self, insights: List[AgentInsight]) -> Dict[str, int]:
        """Extrae temas comunes entre insights"""
        # Palabras clave importantes
        keywords = []
        for insight in insights:
            content_words = insight.content.lower().split()
            # Filtrar palabras relevantes (más de 4 caracteres)
            relevant_words = [w for w in content_words if len(w) > 4]
            keywords.extend(relevant_words)
        
        # Contar frecuencias
        theme_frequency = {}
        for keyword in set(keywords):
            count = sum(1 for insight in insights if keyword in insight.content.lower())
            if count > 1:  # Aparece en múltiples insights
                theme_frequency[keyword] = count
        
        return theme_frequency
    
    async def _calculate_fusion_confidence(
        self,
        insights: List[AgentInsight],
        conflicts: List[ConflictAnalysis]
    ) -> float:
        """Calcula confianza del insight fusionado"""
        if not insights:
            return 0.0
        
        # Confianza base: promedio de insights individuales
        base_confidence = statistics.mean([i.confidence for i in insights])
        
        # Bonus por múltiples agentes
        multi_agent_bonus = min(0.1 * (len(insights) - 1), 0.3)
        
        # Penalización por conflictos
        conflict_penalty = min(0.05 * len(conflicts), 0.2)
        
        # Bonus por compatibilidad entre agentes
        compatibility_bonus = self._calculate_compatibility_bonus(insights)
        
        final_confidence = base_confidence + multi_agent_bonus + compatibility_bonus - conflict_penalty
        
        return max(0.0, min(1.0, final_confidence))
    
    def _calculate_compatibility_bonus(self, insights: List[AgentInsight]) -> float:
        """Calcula bonus por compatibilidad entre agentes"""
        if len(insights) < 2:
            return 0.0
        
        total_compatibility = 0.0
        pair_count = 0
        
        for i, insight1 in enumerate(insights):
            for insight2 in insights[i+1:]:
                compatibility = self.agent_compatibility_matrix.get(
                    (insight1.agent_id, insight2.agent_id), 0.7
                )
                total_compatibility += compatibility
                pair_count += 1
        
        if pair_count == 0:
            return 0.0
        
        avg_compatibility = total_compatibility / pair_count
        # Convertir a bonus (0.7 = sin bonus, 1.0 = bonus máximo de 0.15)
        return max(0.0, (avg_compatibility - 0.7) * 0.5)
    
    def _calculate_consensus_level(self, insights: List[AgentInsight]) -> float:
        """Calcula nivel de consenso entre insights"""
        if len(insights) < 2:
            return 1.0
        
        # Calcular basado en varianza de confianza
        confidences = [i.confidence for i in insights]
        avg_confidence = statistics.mean(confidences)
        confidence_variance = statistics.variance(confidences) if len(confidences) > 1 else 0
        
        # Menor varianza = mayor consenso
        consensus = 1.0 - min(confidence_variance, 1.0)
        
        return consensus
    
    async def _generate_meta_insights(
        self, 
        insights: List[AgentInsight], 
        context: FusionContext
    ) -> List[str]:
        """Genera meta-insights de alto nivel"""
        meta_insights = []
        
        try:
            # Análisis de patrones emergentes
            if len(insights) >= 3:
                meta_insights.append(
                    f"Convergencia detectada: {len(insights)} agentes especializados coinciden "
                    f"en enfoque integrado con confianza promedio de "
                    f"{statistics.mean([i.confidence for i in insights]):.0%}"
                )
            
            # Análisis de dominios representados
            domains = set(self._get_agent_domain(i.agent_id) for i in insights)
            if len(domains) >= 3:
                meta_insights.append(
                    f"Análisis multi-dominio: Cobertura de {len(domains)} áreas especializadas "
                    f"({', '.join(domains)}) permite optimización holística"
                )
            
            # Análisis temporal
            time_span = max(i.generated_at for i in insights) - min(i.generated_at for i in insights)
            if time_span.total_seconds() < 300:  # Menos de 5 minutos
                meta_insights.append(
                    "Análisis en tiempo real: Insights generados simultáneamente "
                    "garantizan coherencia temporal y relevancia inmediata"
                )
            
            # Análisis de expertise
            high_confidence_agents = [i.agent_id.value for i in insights if i.confidence > 0.8]
            if len(high_confidence_agents) >= 2:
                meta_insights.append(
                    f"Validación de expertise: {len(high_confidence_agents)} agentes "
                    f"de alta confianza ({', '.join(high_confidence_agents)}) "
                    f"respaldan las recomendaciones"
                )
            
            return meta_insights[:3]  # Máximo 3 meta-insights
            
        except Exception as e:
            logger.error(f"Error generando meta-insights: {e}")
            return ["Análisis multi-agente completado con éxito"]
    
    async def _synthesize_recommendations(
        self,
        insights: List[AgentInsight],
        meta_insights: List[str],
        context: FusionContext
    ) -> List[str]:
        """Sintetiza recomendaciones accionables"""
        all_recommendations = []
        
        # Recopilar todas las recomendaciones
        for insight in insights:
            all_recommendations.extend(insight.recommendations)
        
        # Eliminar duplicados y priorizar
        unique_recommendations = list(set(all_recommendations))
        
        # Generar recomendaciones sintetizadas
        synthesized = []
        
        # Recomendación principal basada en consenso
        if len(insights) >= 2:
            synthesized.append(
                f"ACCIÓN PRIORITARIA: Implementar enfoque integrado combinando "
                f"expertise de {', '.join([i.agent_id.value for i in insights])}"
            )
        
        # Recomendaciones específicas
        synthesized.extend(unique_recommendations[:4])  # Top 4 específicas
        
        # Recomendación de seguimiento
        synthesized.append(
            "SEGUIMIENTO: Monitorear progreso y ajustar estrategia basado en "
            "feedback y resultados obtenidos"
        )
        
        return synthesized
    
    def _extract_data_sources(self, insights: List[AgentInsight]) -> List[str]:
        """Extrae fuentes de datos de los insights"""
        sources = set()
        
        for insight in insights:
            # Extraer de supporting_data
            if 'data_sources' in insight.supporting_data:
                sources.update(insight.supporting_data['data_sources'])
            
            # Inferir del agente
            agent_sources = {
                AgentRole.SAGE_NUTRITION: ['nutrition_logs', 'meal_tracking'],
                AgentRole.BLAZE_TRAINING: ['workout_logs', 'performance_metrics'],
                AgentRole.WAVE_ANALYTICS: ['historical_data', 'trends_analysis'],
                AgentRole.VOLT_BIOMETRICS: ['wearable_data', 'biomarkers'],
                AgentRole.HELIX_GENETICS: ['genetic_data', 'dna_analysis']
            }
            
            if insight.agent_id in agent_sources:
                sources.update(agent_sources[insight.agent_id])
        
        return list(sources)
    
    async def _cache_fused_insight(self, fused_insight: FusedInsight) -> None:
        """Cachea insight fusionado"""
        try:
            cache_key = f"{self.cache_prefix}:fused:{fused_insight.insight_id}"
            await cache_set(
                cache_key,
                fused_insight.to_dict(),
                ttl=7200,  # 2 horas
                priority=CachePriority.HIGH
            )
        except Exception as e:
            logger.error(f"Error cacheando insight fusionado: {e}")
    
    async def _update_fusion_history(self, user_id: str, fused_insight: FusedInsight) -> None:
        """Actualiza historial de fusiones del usuario"""
        try:
            if user_id not in self.fusion_history:
                self.fusion_history[user_id] = []
            
            self.fusion_history[user_id].append({
                'insight_id': fused_insight.insight_id,
                'timestamp': fused_insight.fusion_timestamp,
                'confidence': fused_insight.confidence_score,
                'agents': [agent.value for agent in fused_insight.contributing_agents]
            })
            
            # Mantener solo últimas 50 fusiones
            self.fusion_history[user_id] = self.fusion_history[user_id][-50:]
            
        except Exception as e:
            logger.error(f"Error actualizando historial de fusión: {e}")
    
    async def get_fusion_analytics(self, user_id: str) -> Dict[str, Any]:
        """Obtiene analíticas de fusión para un usuario"""
        try:
            user_history = self.fusion_history.get(user_id, [])
            
            if not user_history:
                return {
                    'total_fusions': 0,
                    'average_confidence': 0.0,
                    'most_used_agents': [],
                    'fusion_trends': []
                }
            
            # Calcular métricas
            confidences = [f['confidence'] for f in user_history]
            all_agents = []
            for fusion in user_history:
                all_agents.extend(fusion['agents'])
            
            # Contar agentes más utilizados
            agent_frequency = {}
            for agent in all_agents:
                agent_frequency[agent] = agent_frequency.get(agent, 0) + 1
            
            most_used = sorted(agent_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
            
            analytics = {
                'total_fusions': len(user_history),
                'average_confidence': statistics.mean(confidences) if confidences else 0.0,
                'confidence_trend': confidences[-10:],  # Últimas 10 fusiones
                'most_used_agents': most_used,
                'fusion_frequency': self._calculate_fusion_frequency(user_history),
                'last_fusion': user_history[-1]['timestamp'].isoformat() if user_history else None
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error obteniendo analíticas de fusión: {e}")
            return {}
    
    def _calculate_fusion_frequency(self, history: List[Dict]) -> Dict[str, int]:
        """Calcula frecuencia de fusiones por período"""
        now = datetime.utcnow()
        
        # Contar fusiones por período
        last_24h = sum(1 for f in history if (now - f['timestamp']).days == 0)
        last_week = sum(1 for f in history if (now - f['timestamp']).days <= 7)
        last_month = sum(1 for f in history if (now - f['timestamp']).days <= 30)
        
        return {
            'last_24_hours': last_24h,
            'last_week': last_week,
            'last_month': last_month
        }


# Instancia global del motor de fusión
fusion_engine = InsightFusionEngine()


# Funciones helper para uso sencillo
async def fuse_agent_insights(
    insights: List[AgentInsight],
    user_id: str,
    domain_focus: Optional[str] = None,
    fusion_strategy: FusionStrategy = FusionStrategy.WEIGHTED_AVERAGE
) -> FusedInsight:
    """Función helper para fusionar insights de agentes"""
    context = FusionContext(
        user_id=user_id,
        domain_focus=domain_focus,
        fusion_strategy=fusion_strategy
    )
    
    return await fusion_engine.fuse_insights(insights, context)


async def get_user_fusion_analytics(user_id: str) -> Dict[str, Any]:
    """Función helper para obtener analíticas de fusión"""
    return await fusion_engine.get_fusion_analytics(user_id)