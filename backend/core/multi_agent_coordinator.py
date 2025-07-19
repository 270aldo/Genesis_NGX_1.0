"""
MultiAgentCoordinator: Sistema de comunicación mejorada entre agentes.

Este módulo permite que NEXUS coordine consultas complejas que requieren
la perspectiva de múltiples agentes especializados, creando respuestas
más ricas y coherentes.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from core.logging_config import get_logger
from core.telemetry_loader import telemetry

logger = get_logger(__name__)


class QueryComplexity(Enum):
    """Niveles de complejidad de consultas."""
    SIMPLE = "simple"           # Un solo agente puede responder
    MODERADA = "moderada"       # 2-3 agentes colaboran
    COMPLEJA = "compleja"       # 4+ agentes necesarios
    INTEGRAL = "integral"       # Requiere todo el ecosistema


class CollaborationType(Enum):
    """Tipos de colaboración entre agentes."""
    PARALLEL = "parallel"       # Consultas independientes en paralelo
    SEQUENTIAL = "sequential"   # Un agente consulta a otro secuencialmente
    COLLABORATIVE = "collaborative"  # Síntesis conjunta
    CONSULTATIVE = "consultative"    # Un agente principal con consultas


@dataclass
class AgentPerspective:
    """Perspectiva de un agente sobre una consulta."""
    agent_id: str
    response: str
    confidence_score: float
    supporting_data: Dict[str, Any]
    recommendations: List[str]
    concerns: List[str] = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.concerns is None:
            self.concerns = []


@dataclass
class CollaborationResult:
    """Resultado de una colaboración multi-agente."""
    query: str
    complexity: QueryComplexity
    collaboration_type: CollaborationType
    participating_agents: List[str]
    individual_perspectives: List[AgentPerspective]
    synthesized_response: str
    consensus_level: float  # 0.0 - 1.0
    conflicting_recommendations: List[Dict[str, Any]]
    unified_recommendations: List[str]
    execution_time: float
    metadata: Dict[str, Any]


class MultiAgentCoordinator:
    """
    Coordinador para comunicación avanzada entre múltiples agentes.
    
    Permite a NEXUS orquestar consultas complejas que requieren la perspectiva
    de varios agentes especializados, creando respuestas más coherentes y útiles.
    """

    def __init__(self):
        """Inicializa el coordinador multi-agente."""
        # Mapeo de temas a agentes relevantes
        self.topic_agent_mapping = {
            # Entrenamiento y rendimiento
            "entrenamiento": ["elite_training_strategist", "volt_biometrics", "wave_recovery"],
            "ejercicio": ["elite_training_strategist", "progress_tracker"],
            "fuerza": ["elite_training_strategist", "progress_tracker"],
            "cardio": ["elite_training_strategist", "wave_recovery"],
            "rendimiento": ["elite_training_strategist", "volt_biometrics", "nova_biohacking"],
            
            # Nutrición y metabolismo
            "nutricion": ["precision_nutrition_architect", "code_genetic_specialist"],
            "dieta": ["precision_nutrition_architect", "progress_tracker"],
            "suplementos": ["precision_nutrition_architect", "nova_biohacking"],
            "peso": ["precision_nutrition_architect", "elite_training_strategist", "progress_tracker"],
            
            # Recuperación y bienestar
            "cansancio": ["wave_recovery", "volt_biometrics", "motivation_behavior_coach"],
            "fatiga": ["wave_recovery", "volt_biometrics", "precision_nutrition_architect"],
            "sueño": ["wave_recovery", "nova_biohacking"],
            "estres": ["wave_recovery", "motivation_behavior_coach", "nova_biohacking"],
            "recuperacion": ["wave_recovery", "elite_training_strategist"],
            
            # Salud femenina
            "menstrual": ["female_wellness_coach", "wave_recovery", "precision_nutrition_architect"],
            "hormonal": ["female_wellness_coach", "code_genetic_specialist", "nova_biohacking"],
            "menopausia": ["female_wellness_coach", "precision_nutrition_architect"],
            
            # Motivación y psicología
            "motivacion": ["motivation_behavior_coach", "progress_tracker"],
            "habitos": ["motivation_behavior_coach", "progress_tracker"],
            "adherencia": ["motivation_behavior_coach", "progress_tracker"],
            "meseta": ["motivation_behavior_coach", "progress_tracker", "elite_training_strategist"],
            
            # Datos y progreso
            "progreso": ["progress_tracker", "volt_biometrics", "elite_training_strategist"],
            "metricas": ["volt_biometrics", "progress_tracker"],
            "analisis": ["volt_biometrics", "code_genetic_specialist"],
            
            # Genética y optimización
            "genetica": ["code_genetic_specialist", "precision_nutrition_architect", "elite_training_strategist"],
            "optimizacion": ["nova_biohacking", "code_genetic_specialist", "volt_biometrics"],
            "biohacking": ["nova_biohacking", "wave_recovery", "precision_nutrition_architect"],
        }
        
        # Agentes que requieren colaboración frecuente
        self.collaboration_pairs = {
            "elite_training_strategist": ["wave_recovery", "precision_nutrition_architect", "volt_biometrics"],
            "precision_nutrition_architect": ["code_genetic_specialist", "elite_training_strategist", "nova_biohacking"],
            "wave_recovery": ["elite_training_strategist", "volt_biometrics", "motivation_behavior_coach"],
            "motivation_behavior_coach": ["progress_tracker", "wave_recovery", "female_wellness_coach"],
            "female_wellness_coach": ["wave_recovery", "precision_nutrition_architect", "motivation_behavior_coach"],
            "nova_biohacking": ["code_genetic_specialist", "precision_nutrition_architect", "wave_recovery"],
            "volt_biometrics": ["wave_recovery", "elite_training_strategist", "progress_tracker"],
            "progress_tracker": ["elite_training_strategist", "motivation_behavior_coach", "volt_biometrics"],
            "code_genetic_specialist": ["precision_nutrition_architect", "nova_biohacking", "elite_training_strategist"],
        }

    async def analyze_query_complexity(self, query: str, user_context: Dict[str, Any] = None) -> Tuple[QueryComplexity, List[str]]:
        """
        Analiza la complejidad de una consulta y determina qué agentes deben participar.
        
        Args:
            query: Consulta del usuario
            user_context: Contexto adicional del usuario
            
        Returns:
            Tuple con complejidad detectada y lista de agentes relevantes
        """
        try:
            query_lower = query.lower()
            relevant_agents = set()
            
            # Buscar temas relevantes en la consulta
            for topic, agents in self.topic_agent_mapping.items():
                if topic in query_lower:
                    relevant_agents.update(agents)
            
            # Análisis de patrones complejos que requieren múltiples agentes
            complex_patterns = [
                "estoy cansado", "me siento agotado", "no veo progreso", "se ha estancado",
                "tengo presentación", "viaje de trabajo", "falta de tiempo",
                "dolor", "lesión", "molestia", "incomodo",
                "estrés", "ansiedad", "desmotivado", "frustrado",
                "cambio de rutina", "nuevo objetivo", "plateau"
            ]
            
            # Detectar palabras que indican necesidad de múltiples perspectivas
            complexity_indicators = 0
            for pattern in complex_patterns:
                if pattern in query_lower:
                    complexity_indicators += 1
            
            # Si no hay agentes detectados automáticamente, usar heurísticas
            if not relevant_agents:
                if any(word in query_lower for word in ["general", "overall", "todo", "completo"]):
                    relevant_agents.update(["elite_training_strategist", "precision_nutrition_architect", 
                                          "motivation_behavior_coach", "wave_recovery"])
                else:
                    # Consulta genérica - usar agentes principales
                    relevant_agents.add("motivation_behavior_coach")
            
            # Expandir con agentes colaborativos
            expanded_agents = set(relevant_agents)
            for agent in list(relevant_agents):
                if agent in self.collaboration_pairs:
                    # Añadir hasta 2 colaboradores principales
                    collaborators = self.collaboration_pairs[agent][:2]
                    expanded_agents.update(collaborators)
            
            relevant_agents = list(expanded_agents)
            
            # Determinar complejidad
            if len(relevant_agents) <= 1:
                complexity = QueryComplexity.SIMPLE
            elif len(relevant_agents) <= 3:
                complexity = QueryComplexity.MODERADA
            elif len(relevant_agents) <= 5:
                complexity = QueryComplexity.COMPLEJA
            else:
                complexity = QueryComplexity.INTEGRAL
                # Limitar a los 5 más relevantes para evitar sobrecarga
                relevant_agents = relevant_agents[:5]
            
            # Ajustar por indicadores de complejidad
            if complexity_indicators >= 2:
                if complexity == QueryComplexity.SIMPLE:
                    complexity = QueryComplexity.MODERADA
                elif complexity == QueryComplexity.MODERADA:
                    complexity = QueryComplexity.COMPLEJA
                    
            logger.info(f"Query complexity analysis: {complexity.value}, agents: {relevant_agents}")
            
            return complexity, relevant_agents
            
        except Exception as e:
            logger.error(f"Error analyzing query complexity: {e}", exc_info=True)
            return QueryComplexity.SIMPLE, ["motivation_behavior_coach"]

    async def orchestrate_multi_agent_response(
        self, 
        query: str, 
        user_context: Dict[str, Any] = None,
        a2a_adapter = None
    ) -> CollaborationResult:
        """
        Orquesta una respuesta multi-agente para consultas complejas.
        
        Args:
            query: Consulta del usuario
            user_context: Contexto del usuario
            a2a_adapter: Adaptador A2A para comunicación con agentes
            
        Returns:
            Resultado de la colaboración multi-agente
        """
        start_time = time.time()
        
        try:
            # Analizar complejidad y determinar agentes
            complexity, participating_agents = await self.analyze_query_complexity(query, user_context)
            
            logger.info(f"Orchestrating multi-agent response: {complexity.value} with agents {participating_agents}")
            
            # Determinar tipo de colaboración
            collaboration_type = self._determine_collaboration_type(complexity, participating_agents)
            
            # Recopilar perspectivas individuales
            perspectives = await self._gather_agent_perspectives(
                query, participating_agents, user_context, a2a_adapter
            )
            
            # Sintetizar respuesta unificada
            synthesis_result = await self._synthesize_perspectives(query, perspectives)
            
            execution_time = time.time() - start_time
            
            # Crear resultado de colaboración
            result = CollaborationResult(
                query=query,
                complexity=complexity,
                collaboration_type=collaboration_type,
                participating_agents=participating_agents,
                individual_perspectives=perspectives,
                synthesized_response=synthesis_result["response"],
                consensus_level=synthesis_result["consensus_level"],
                conflicting_recommendations=synthesis_result["conflicts"],
                unified_recommendations=synthesis_result["unified_recommendations"],
                execution_time=execution_time,
                metadata={
                    "user_context": user_context,
                    "analysis_timestamp": time.time(),
                    "orchestrator_version": "1.0.0"
                }
            )
            
            logger.info(f"Multi-agent response completed in {execution_time:.2f}s with consensus {synthesis_result['consensus_level']:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error orchestrating multi-agent response: {e}", exc_info=True)
            # Fallback a respuesta simple
            return await self._create_fallback_result(query, start_time)

    def _determine_collaboration_type(self, complexity: QueryComplexity, agents: List[str]) -> CollaborationType:
        """Determina el tipo de colaboración basado en complejidad y agentes."""
        if complexity == QueryComplexity.SIMPLE:
            return CollaborationType.CONSULTATIVE
        elif complexity == QueryComplexity.MODERADA:
            return CollaborationType.PARALLEL
        elif len(agents) >= 4:
            return CollaborationType.COLLABORATIVE
        else:
            return CollaborationType.SEQUENTIAL

    async def _gather_agent_perspectives(
        self, 
        query: str, 
        agents: List[str], 
        user_context: Dict[str, Any],
        a2a_adapter
    ) -> List[AgentPerspective]:
        """Recopila perspectivas individuales de cada agente."""
        perspectives = []
        
        try:
            # Crear tareas paralelas para consultar agentes
            tasks = []
            for agent_id in agents:
                task = self._query_single_agent(agent_id, query, user_context, a2a_adapter)
                tasks.append(task)
            
            # Ejecutar consultas en paralelo con timeout
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Procesar resultados
            for i, result in enumerate(results):
                agent_id = agents[i]
                if isinstance(result, Exception):
                    logger.warning(f"Agent {agent_id} failed: {result}")
                    # Crear perspectiva de fallback
                    perspective = AgentPerspective(
                        agent_id=agent_id,
                        response=f"El agente {agent_id} no pudo procesar la consulta en este momento.",
                        confidence_score=0.1,
                        supporting_data={},
                        recommendations=[],
                        concerns=["Error en comunicación"]
                    )
                else:
                    perspective = result
                
                perspectives.append(perspective)
            
        except Exception as e:
            logger.error(f"Error gathering agent perspectives: {e}", exc_info=True)
            
        return perspectives

    async def _query_single_agent(
        self, 
        agent_id: str, 
        query: str, 
        user_context: Dict[str, Any],
        a2a_adapter
    ) -> AgentPerspective:
        """Consulta a un agente individual y estructura su respuesta."""
        try:
            # Adaptar query para el agente específico
            adapted_query = self._adapt_query_for_agent(agent_id, query)
            
            # Simular consulta al agente (aquí integrarías con a2a_adapter real)
            if a2a_adapter:
                # Usar el adaptador A2A real
                response = await self._call_agent_via_a2a(agent_id, adapted_query, user_context, a2a_adapter)
            else:
                # Modo simulado para testing
                response = await self._simulate_agent_response(agent_id, adapted_query)
            
            # Estructurar perspectiva
            perspective = AgentPerspective(
                agent_id=agent_id,
                response=response.get("response", "Sin respuesta"),
                confidence_score=response.get("confidence", 0.8),
                supporting_data=response.get("data", {}),
                recommendations=response.get("recommendations", []),
                concerns=response.get("concerns", [])
            )
            
            return perspective
            
        except Exception as e:
            logger.error(f"Error querying agent {agent_id}: {e}", exc_info=True)
            return AgentPerspective(
                agent_id=agent_id,
                response="Error al obtener respuesta",
                confidence_score=0.0,
                supporting_data={},
                recommendations=[]
            )

    def _adapt_query_for_agent(self, agent_id: str, query: str) -> str:
        """Adapta la consulta para que sea más relevante para un agente específico."""
        adaptations = {
            "elite_training_strategist": f"Desde la perspectiva del entrenamiento y ejercicio: {query}",
            "precision_nutrition_architect": f"Considerando aspectos nutricionales: {query}",
            "wave_recovery": f"Evaluando recuperación y bienestar: {query}",
            "motivation_behavior_coach": f"Desde el punto de vista motivacional y psicológico: {query}",
            "volt_biometrics": f"Analizando datos biométricos y métricas: {query}",
            "progress_tracker": f"Evaluando progreso y métricas de avance: {query}",
            "female_wellness_coach": f"Considerando aspectos de salud femenina: {query}",
            "nova_biohacking": f"Desde la perspectiva de optimización avanzada: {query}",
            "code_genetic_specialist": f"Considerando factores genéticos y personalizados: {query}",
        }
        
        return adaptations.get(agent_id, query)

    async def _call_agent_via_a2a(self, agent_id: str, query: str, context: Dict, a2a_adapter) -> Dict[str, Any]:
        """Llama a un agente usando el adaptador A2A real."""
        try:
            # Preparar contexto de tarea A2A
            task_context = {
                "query": query,
                "user_context": context,
                "collaboration_mode": True,
                "requesting_agent": "orchestrator"
            }
            
            # Llamar al agente via A2A
            response = await a2a_adapter.call_agent(agent_id, task_context)
            
            return {
                "response": response.get("response", "Sin respuesta"),
                "confidence": response.get("confidence", 0.7),
                "data": response.get("supporting_data", {}),
                "recommendations": response.get("recommendations", []),
                "concerns": response.get("concerns", [])
            }
            
        except Exception as e:
            logger.error(f"Error calling agent {agent_id} via A2A: {e}")
            return await self._simulate_agent_response(agent_id, query)

    async def _simulate_agent_response(self, agent_id: str, query: str) -> Dict[str, Any]:
        """Simula respuesta de agente para testing."""
        # Respuestas simuladas por agente
        agent_responses = {
            "elite_training_strategist": {
                "response": f"BLAZE recomienda ajustar la intensidad del entrenamiento considerando la consulta: {query[:50]}...",
                "confidence": 0.85,
                "recommendations": ["Ajustar volumen de entrenamiento", "Incluir ejercicios específicos"],
                "concerns": []
            },
            "precision_nutrition_architect": {
                "response": f"SAGE sugiere optimizar la nutrición para abordar: {query[:50]}...",
                "confidence": 0.80,
                "recommendations": ["Ajustar macronutrientes", "Considerar timing de comidas"],
                "concerns": []
            },
            "wave_recovery": {
                "response": f"WAVE identifica necesidades de recuperación relacionadas con: {query[:50]}...",
                "confidence": 0.82,
                "recommendations": ["Priorizar descanso", "Implementar técnicas de recuperación"],
                "concerns": []
            },
            "motivation_behavior_coach": {
                "response": f"SPARK propone estrategias motivacionales para: {query[:50]}...",
                "confidence": 0.78,
                "recommendations": ["Técnicas de mindset", "Estrategias de adherencia"],
                "concerns": []
            }
        }
        
        return agent_responses.get(agent_id, {
            "response": f"Respuesta simulada del agente {agent_id}",
            "confidence": 0.7,
            "recommendations": [f"Recomendación de {agent_id}"],
            "concerns": []
        })

    async def _synthesize_perspectives(self, query: str, perspectives: List[AgentPerspective]) -> Dict[str, Any]:
        """Sintetiza las perspectivas de múltiples agentes en una respuesta unificada."""
        try:
            if not perspectives:
                return {
                    "response": "No se pudieron obtener perspectivas de los agentes.",
                    "consensus_level": 0.0,
                    "conflicts": [],
                    "unified_recommendations": []
                }
            
            # Analizar consenso y conflictos
            all_recommendations = []
            all_concerns = []
            confidence_scores = []
            
            for perspective in perspectives:
                all_recommendations.extend(perspective.recommendations)
                all_concerns.extend(perspective.concerns)
                confidence_scores.append(perspective.confidence_score)
            
            # Calcular nivel de consenso
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            consensus_level = min(avg_confidence, 1.0)
            
            # Detectar conflictos (simplificado)
            conflicts = []
            if len(set(all_recommendations)) < len(all_recommendations) * 0.7:
                conflicts.append({
                    "type": "recommendation_conflict",
                    "description": "Recomendaciones divergentes entre agentes",
                    "agents": [p.agent_id for p in perspectives]
                })
            
            # Crear recomendaciones unificadas
            unified_recommendations = list(set(all_recommendations))[:5]  # Top 5 únicas
            
            # Construir respuesta sintetizada
            response_parts = []
            
            # Introducción
            agent_names = {
                "elite_training_strategist": "BLAZE",
                "precision_nutrition_architect": "SAGE", 
                "wave_recovery": "WAVE",
                "motivation_behavior_coach": "SPARK",
                "volt_biometrics": "VOLT",
                "progress_tracker": "STELLA",
                "female_wellness_coach": "LUNA",
                "nova_biohacking": "NOVA",
                "code_genetic_specialist": "CODE"
            }
            
            participating_names = [agent_names.get(p.agent_id, p.agent_id.upper()) for p in perspectives]
            
            if len(perspectives) == 1:
                response_parts.append(f"He consultado con {participating_names[0]} sobre tu consulta.")
            else:
                response_parts.append(f"He coordinado con mi equipo ({', '.join(participating_names)}) para darte una respuesta integral.")
            
            # Síntesis de perspectivas
            if len(perspectives) > 1:
                response_parts.append("\n**Análisis conjunto:**")
                
                # Combinar insights principales
                key_insights = []
                for perspective in perspectives:
                    if perspective.response and len(perspective.response) > 20:
                        agent_name = agent_names.get(perspective.agent_id, perspective.agent_id.upper())
                        key_insights.append(f"• **{agent_name}**: {perspective.response[:100]}...")
                
                if key_insights:
                    response_parts.extend(key_insights)
            
            # Recomendaciones unificadas
            if unified_recommendations:
                response_parts.append("\n**Plan de acción recomendado:**")
                for i, rec in enumerate(unified_recommendations, 1):
                    response_parts.append(f"{i}. {rec}")
            
            # Consideraciones importantes
            if all_concerns:
                unique_concerns = list(set(all_concerns))[:3]
                response_parts.append("\n**Consideraciones importantes:**")
                for concern in unique_concerns:
                    response_parts.append(f"⚠️ {concern}")
            
            synthesized_response = "\n".join(response_parts)
            
            return {
                "response": synthesized_response,
                "consensus_level": consensus_level,
                "conflicts": conflicts,
                "unified_recommendations": unified_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error synthesizing perspectives: {e}", exc_info=True)
            return {
                "response": "Error al sintetizar las perspectivas de los agentes.",
                "consensus_level": 0.0,
                "conflicts": [],
                "unified_recommendations": []
            }

    async def _create_fallback_result(self, query: str, start_time: float) -> CollaborationResult:
        """Crea un resultado de fallback en caso de error."""
        execution_time = time.time() - start_time
        
        fallback_perspective = AgentPerspective(
            agent_id="motivation_behavior_coach",
            response="Disculpa, hubo un problema técnico al coordinar la respuesta del equipo. Te sugiero intentar de nuevo o reformular tu consulta.",
            confidence_score=0.3,
            supporting_data={},
            recommendations=["Intentar nuevamente", "Reformular la consulta"],
            concerns=["Error técnico en coordinación"]
        )
        
        return CollaborationResult(
            query=query,
            complexity=QueryComplexity.SIMPLE,
            collaboration_type=CollaborationType.CONSULTATIVE,
            participating_agents=["motivation_behavior_coach"],
            individual_perspectives=[fallback_perspective],
            synthesized_response=fallback_perspective.response,
            consensus_level=0.3,
            conflicting_recommendations=[],
            unified_recommendations=fallback_perspective.recommendations,
            execution_time=execution_time,
            metadata={"error": "Fallback response", "timestamp": time.time()}
        )

    def get_collaboration_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de colaboración entre agentes."""
        return {
            "available_agents": len(self.collaboration_pairs),
            "topic_mappings": len(self.topic_agent_mapping),
            "supported_complexity_levels": [c.value for c in QueryComplexity],
            "collaboration_types": [c.value for c in CollaborationType]
        }


# Instancia global del coordinador
multi_agent_coordinator = MultiAgentCoordinator()