"""
Collaboration Skills for NGX Agents
====================================

This module provides advanced collaboration capabilities for NGX agents,
enabling them to participate in debates, workshops, podcasts, teaching sessions,
and other collaborative content creation modes.

These skills are designed to work with NEXUS Conversations platform.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from datetime import datetime
import json

# Import collaboration intelligence
from .collaboration_intelligence import (
    CollaborationIntelligence,
    CollaborationSuggestion,
    CollaborationTrigger,
    CollaborationUrgency
)

logger = logging.getLogger(__name__)


class CollaborationMode(Enum):
    """Tipos de colaboración disponibles"""
    DEBATE = "debate"
    WORKSHOP = "workshop"
    PODCAST = "podcast"
    TEACHING = "teaching"
    CASE_STUDY = "case_study"


class InteractionStyle(Enum):
    """Estilos de interacción para diferentes modos"""
    CONFRONTATIONAL = "confrontational"  # Para debates intensos
    COLLABORATIVE = "collaborative"      # Para workshops
    CONVERSATIONAL = "conversational"  # Para podcasts
    EDUCATIONAL = "educational"        # Para teaching
    ANALYTICAL = "analytical"         # Para case studies


@dataclass
class CollaborationContext:
    """Contexto para una sesión de colaboración"""
    session_id: str
    mode: CollaborationMode
    topic: str
    participants: List[str]
    style: InteractionStyle
    temperature: float = 0.7  # 0-1, controla intensidad
    metadata: Dict[str, Any] = None


@dataclass
class CollaborationTurn:
    """Representa un turno en la colaboración"""
    agent_id: str
    content: str
    timestamp: datetime
    references_previous: Optional[str] = None
    emotion_tone: Optional[str] = None
    confidence: float = 1.0


class CollaborationMixin:
    """
    Mixin que añade capacidades de colaboración a los agentes NGX.
    
    Este mixin permite a los agentes participar en diferentes tipos
    de interacciones colaborativas con otros agentes.
    """
    
    def __init__(self):
        self._collaboration_memory = []
        self._chemistry_scores = {}
        self._collaboration_style = None
        self._current_context = None
        # Initialize collaboration intelligence
        self._collaboration_intelligence = CollaborationIntelligence()
    
    async def enter_debate_mode(
        self, 
        topic: str, 
        stance: str,
        partners: List[Dict[str, Any]],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Prepara al agente para participar en un debate.
        
        Args:
            topic: Tema del debate
            stance: Postura a defender
            partners: Lista de agentes participantes
            temperature: Intensidad del debate (0-1)
            
        Returns:
            Configuración inicial para el debate
        """
        self._current_context = CollaborationContext(
            session_id=f"debate_{datetime.now().timestamp()}",
            mode=CollaborationMode.DEBATE,
            topic=topic,
            participants=[p['id'] for p in partners],
            style=InteractionStyle.CONFRONTATIONAL if temperature > 0.7 else InteractionStyle.CONVERSATIONAL,
            temperature=temperature
        )
        
        # Preparar personalidad para debate
        debate_config = {
            "mode": "debate",
            "stance": stance,
            "topic": topic,
            "style_adjustments": {
                "assertiveness": min(1.0, temperature + 0.2),
                "analytical_depth": 0.8,
                "emotional_expression": temperature * 0.5,
                "use_examples": True,
                "challenge_others": temperature > 0.5
            },
            "ready": True
        }
        
        logger.info(f"Agent {self.agent_id} entering debate mode on topic: {topic}")
        return debate_config
    
    async def collaborate_on_task(
        self,
        deliverable: str,
        role: str,
        team: List[Dict[str, Any]],
        deadline: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modo colaboración para crear contenido conjunto.
        
        Args:
            deliverable: Qué se va a crear
            role: Rol del agente en el equipo
            team: Miembros del equipo
            deadline: Tiempo límite opcional
            
        Returns:
            Configuración para workshop colaborativo
        """
        self._current_context = CollaborationContext(
            session_id=f"workshop_{datetime.now().timestamp()}",
            mode=CollaborationMode.WORKSHOP,
            topic=deliverable,
            participants=[t['id'] for t in team],
            style=InteractionStyle.COLLABORATIVE,
            metadata={"role": role, "deadline": deadline}
        )
        
        workshop_config = {
            "mode": "workshop",
            "deliverable": deliverable,
            "role": role,
            "collaboration_style": {
                "contribution_focus": self._determine_contribution_focus(role),
                "interaction_style": "supportive",
                "build_on_others": True,
                "offer_alternatives": True,
                "seek_consensus": True
            },
            "team_dynamics": self._analyze_team_chemistry(team)
        }
        
        return workshop_config
    
    async def enter_podcast_mode(
        self,
        theme: str,
        episode_format: str,
        co_hosts: List[Dict[str, Any]],
        audience_level: str = "general"
    ) -> Dict[str, Any]:
        """
        Modo podcast para conversaciones naturales.
        
        Args:
            theme: Tema del episodio
            episode_format: Formato (entrevista, mesa redonda, etc.)
            co_hosts: Co-hosts del podcast
            audience_level: Nivel de la audiencia
            
        Returns:
            Configuración para modo podcast
        """
        self._current_context = CollaborationContext(
            session_id=f"podcast_{datetime.now().timestamp()}",
            mode=CollaborationMode.PODCAST,
            topic=theme,
            participants=[h['id'] for h in co_hosts],
            style=InteractionStyle.CONVERSATIONAL,
            temperature=0.6  # Conversacional pero engaging
        )
        
        podcast_config = {
            "mode": "podcast",
            "theme": theme,
            "format": episode_format,
            "personality_adjustments": {
                "humor": 0.7,
                "storytelling": 0.8,
                "relatability": 0.9,
                "use_anecdotes": True,
                "ask_followups": True,
                "natural_flow": True
            },
            "audience_awareness": audience_level,
            "chemistry_mode": "build_rapport"
        }
        
        return podcast_config
    
    async def teach_concept(
        self,
        subject: str,
        learning_objectives: List[str],
        students: List[Dict[str, Any]],
        teaching_style: str = "interactive"
    ) -> Dict[str, Any]:
        """
        Modo enseñanza para explicar conceptos.
        
        Args:
            subject: Materia a enseñar
            learning_objectives: Objetivos de aprendizaje
            students: Agentes estudiantes
            teaching_style: Estilo de enseñanza
            
        Returns:
            Configuración para modo teaching
        """
        self._current_context = CollaborationContext(
            session_id=f"teaching_{datetime.now().timestamp()}",
            mode=CollaborationMode.TEACHING,
            topic=subject,
            participants=[s['id'] for s in students],
            style=InteractionStyle.EDUCATIONAL,
            metadata={"objectives": learning_objectives}
        )
        
        teaching_config = {
            "mode": "teaching",
            "subject": subject,
            "objectives": learning_objectives,
            "teaching_approach": {
                "clarity": 0.9,
                "patience": 0.8,
                "use_examples": True,
                "check_understanding": True,
                "adapt_to_questions": True,
                "encouragement": 0.7
            },
            "interaction_patterns": {
                "explain_then_verify": True,
                "scaffold_concepts": True,
                "relate_to_known": True
            }
        }
        
        return teaching_config
    
    async def analyze_case_study(
        self,
        case: Dict[str, Any],
        analysis_framework: str,
        experts: List[Dict[str, Any]],
        deliverables: List[str]
    ) -> Dict[str, Any]:
        """
        Modo análisis de casos con múltiples perspectivas.
        
        Args:
            case: Detalles del caso
            analysis_framework: Framework de análisis
            experts: Expertos participantes
            deliverables: Qué se debe producir
            
        Returns:
            Configuración para case study
        """
        self._current_context = CollaborationContext(
            session_id=f"case_study_{datetime.now().timestamp()}",
            mode=CollaborationMode.CASE_STUDY,
            topic=case.get('title', 'Case Analysis'),
            participants=[e['id'] for e in experts],
            style=InteractionStyle.ANALYTICAL,
            metadata={"framework": analysis_framework}
        )
        
        case_study_config = {
            "mode": "case_study",
            "case_details": case,
            "analysis_approach": {
                "systematic": True,
                "evidence_based": True,
                "consider_alternatives": True,
                "risk_assessment": True,
                "practical_solutions": True
            },
            "contribution_style": self._determine_expertise_angle(),
            "deliverables": deliverables
        }
        
        return case_study_config
    
    async def analyze_collaboration_opportunity(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> CollaborationSuggestion:
        """
        Intelligent analysis of whether collaboration would benefit the user's query.
        
        This is the main entry point for collaboration intelligence. It analyzes
        the user's input and determines if, when, and how to suggest collaboration.
        
        Args:
            user_input: The user's query or message
            context: Additional context (conversation history, user profile, etc.)
            
        Returns:
            Detailed collaboration suggestion with reasoning and options
        """
        try:
            # Use collaboration intelligence to analyze the query
            suggestion = await self._collaboration_intelligence.analyze_collaboration_need(
                user_input=user_input,
                current_agent_id=getattr(self, 'agent_id', 'unknown'),
                context=context
            )
            
            logger.info(
                f"Collaboration analysis for agent {getattr(self, 'agent_id', 'unknown')}: "
                f"should_collaborate={suggestion.should_collaborate}, "
                f"mode={suggestion.recommended_mode}, "
                f"urgency={suggestion.urgency.value}"
            )
            
            return suggestion
            
        except Exception as e:
            logger.error(f"Error in collaboration analysis: {e}", exc_info=True)
            
            # Fallback: no collaboration suggested
            return CollaborationSuggestion(
                should_collaborate=False,
                trigger_type=CollaborationTrigger.MULTI_DOMAIN,
                urgency=CollaborationUrgency.OPTIONAL,
                recommended_mode="individual",
                suggested_agents=[],
                reasoning="Error in collaboration analysis - proceeding with individual response",
                collaboration_prompt="",
                individual_fallback=True,
                estimated_session_length="N/A",
                expected_outcomes=[],
                user_choice_prompt=""
            )
    
    def should_offer_collaboration(
        self, 
        user_input: str, 
        confidence_threshold: float = 0.7
    ) -> bool:
        """
        Quick check if collaboration should be offered based on input analysis.
        
        Args:
            user_input: User's query
            confidence_threshold: Minimum confidence to suggest collaboration
            
        Returns:
            Whether to offer collaboration
        """
        try:
            # Simple domain detection for quick assessment
            domains = self._collaboration_intelligence._detect_domains(user_input)
            triggers = self._collaboration_intelligence._analyze_triggers(user_input)
            
            # Quick decision logic
            if len(domains) >= 2:  # Multiple domains
                return True
            
            if any(trigger["urgency"] == CollaborationUrgency.ESSENTIAL for trigger in triggers):
                return True
                
            if any(trigger["urgency"] == CollaborationUrgency.RECOMMENDED for trigger in triggers):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in quick collaboration check: {e}")
            return False
    
    async def generate_smart_response_with_collaboration_option(
        self,
        user_input: str,
        individual_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an enhanced response that includes collaboration options when appropriate.
        
        This method takes an individual agent response and enhances it with
        collaboration suggestions when beneficial.
        
        Args:
            user_input: Original user query
            individual_response: The agent's individual response
            context: Additional context
            
        Returns:
            Enhanced response with collaboration options
        """
        try:
            # Analyze collaboration opportunity
            suggestion = await self.analyze_collaboration_opportunity(user_input, context)
            
            if not suggestion.should_collaborate:
                # No collaboration needed - return individual response
                return {
                    "response": individual_response,
                    "collaboration_offered": False,
                    "response_type": "individual"
                }
            
            # Generate enhanced response with collaboration option
            enhanced_response = self._format_response_with_collaboration_option(
                individual_response, suggestion
            )
            
            return {
                "response": enhanced_response,
                "collaboration_offered": True,
                "response_type": "enhanced_with_collaboration",
                "collaboration_suggestion": suggestion,
                "individual_fallback": individual_response
            }
            
        except Exception as e:
            logger.error(f"Error generating smart response: {e}", exc_info=True)
            
            # Fallback to individual response
            return {
                "response": individual_response,
                "collaboration_offered": False,
                "response_type": "individual",
                "error": "Collaboration analysis failed"
            }
    
    def _format_response_with_collaboration_option(
        self,
        individual_response: str,
        suggestion: CollaborationSuggestion
    ) -> str:
        """Format response to include collaboration option naturally"""
        
        urgency_indicators = {
            CollaborationUrgency.ESSENTIAL: "⚠️ **Recomendación importante:**",
            CollaborationUrgency.RECOMMENDED: "💡 **Sugerencia:**",
            CollaborationUrgency.OPTIONAL: "🤝 **Opción adicional:**"
        }
        
        urgency_prefix = urgency_indicators.get(suggestion.urgency, "💡")
        
        # Create enhanced response
        enhanced_response = f"""{individual_response}

---

{urgency_prefix} {suggestion.reasoning}

{suggestion.user_choice_prompt}

**Beneficios esperados de la colaboración:**
{chr(10).join([f"• {outcome}" for outcome in suggestion.expected_outcomes])}

**Tiempo estimado:** {suggestion.estimated_session_length}

*Para iniciar la colaboración, responde "colaborar" o "sí". Para continuar solo conmigo, responde "individual" o continúa con otra pregunta.*"""

        return enhanced_response
    
    async def generate_collaboration_turn(
        self,
        previous_turns: List[CollaborationTurn],
        intervention: Optional[Dict[str, Any]] = None
    ) -> CollaborationTurn:
        """
        Genera un turno de participación en la colaboración actual.
        
        Args:
            previous_turns: Turnos anteriores en la conversación
            intervention: Intervención opcional del director
            
        Returns:
            Nuevo turno de colaboración
        """
        if not self._current_context:
            raise ValueError("No collaboration context set")
        
        # Analizar turnos previos
        context_analysis = self._analyze_conversation_flow(previous_turns)
        
        # Aplicar intervención si existe
        if intervention:
            context_analysis = self._apply_intervention(context_analysis, intervention)
        
        # Generar respuesta basada en modo y contexto
        response_content = await self._generate_contextual_response(
            context_analysis,
            self._current_context
        )
        
        # Crear turno
        turn = CollaborationTurn(
            agent_id=self.agent_id,
            content=response_content['text'],
            timestamp=datetime.now(),
            references_previous=response_content.get('references'),
            emotion_tone=response_content.get('emotion'),
            confidence=response_content.get('confidence', 0.8)
        )
        
        # Actualizar memoria de colaboración
        self._collaboration_memory.append(turn)
        
        return turn
    
    def update_chemistry_score(self, partner_id: str, interaction_quality: float):
        """
        Actualiza el score de química con otro agente.
        
        Args:
            partner_id: ID del agente partner
            interaction_quality: Calidad de la interacción (0-1)
        """
        if partner_id not in self._chemistry_scores:
            self._chemistry_scores[partner_id] = {
                "score": 0.5,
                "interactions": 0,
                "last_interaction": None
            }
        
        # Actualizar con promedio ponderado
        current = self._chemistry_scores[partner_id]
        new_score = (current["score"] * current["interactions"] + interaction_quality) / (current["interactions"] + 1)
        
        self._chemistry_scores[partner_id] = {
            "score": new_score,
            "interactions": current["interactions"] + 1,
            "last_interaction": datetime.now()
        }
    
    def get_collaboration_personality_adjustments(self) -> Dict[str, float]:
        """
        Obtiene ajustes de personalidad para el modo actual.
        
        Returns:
            Diccionario con ajustes de personalidad
        """
        if not self._current_context:
            return {}
        
        base_adjustments = {
            CollaborationMode.DEBATE: {
                "assertiveness": 0.8,
                "analytical": 0.9,
                "competitive": 0.7
            },
            CollaborationMode.WORKSHOP: {
                "cooperative": 0.9,
                "creative": 0.8,
                "supportive": 0.8
            },
            CollaborationMode.PODCAST: {
                "conversational": 0.9,
                "humor": 0.7,
                "engaging": 0.8
            },
            CollaborationMode.TEACHING: {
                "patient": 0.9,
                "clear": 0.9,
                "encouraging": 0.8
            },
            CollaborationMode.CASE_STUDY: {
                "analytical": 0.9,
                "objective": 0.9,
                "thorough": 0.8
            }
        }
        
        return base_adjustments.get(self._current_context.mode, {})
    
    # Métodos privados de utilidad
    
    def _determine_contribution_focus(self, role: str) -> str:
        """Determina el foco de contribución basado en el rol"""
        role_focus_map = {
            "leader": "coordination",
            "expert": "deep_insights", 
            "creative": "innovative_ideas",
            "analyst": "data_interpretation",
            "facilitator": "synthesis"
        }
        return role_focus_map.get(role.lower(), "general_support")
    
    def _analyze_team_chemistry(self, team: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analiza la química del equipo"""
        chemistry_analysis = {
            "overall_score": 0.0,
            "best_partner": None,
            "collaboration_style": "adaptive"
        }
        
        scores = []
        for member in team:
            if member['id'] in self._chemistry_scores:
                scores.append(self._chemistry_scores[member['id']]['score'])
        
        if scores:
            chemistry_analysis['overall_score'] = sum(scores) / len(scores)
            
        return chemistry_analysis
    
    def _determine_expertise_angle(self) -> str:
        """Determina el ángulo de expertise para case studies"""
        # Esto se personalizaría según el agente específico
        return "holistic_analysis"
    
    def _analyze_conversation_flow(self, turns: List[CollaborationTurn]) -> Dict[str, Any]:
        """Analiza el flujo de la conversación"""
        if not turns:
            return {"phase": "opening", "energy": "neutral", "direction": "exploratory"}
        
        recent_turns = turns[-5:] if len(turns) > 5 else turns
        
        # Análisis simple del flujo
        return {
            "phase": "development" if len(turns) > 3 else "opening",
            "energy": self._assess_conversation_energy(recent_turns),
            "direction": self._assess_conversation_direction(recent_turns),
            "my_last_contribution": next((t for t in reversed(turns) if t.agent_id == self.agent_id), None)
        }
    
    def _assess_conversation_energy(self, turns: List[CollaborationTurn]) -> str:
        """Evalúa la energía de la conversación"""
        # Implementación simplificada
        if any(t.emotion_tone in ['passionate', 'intense'] for t in turns):
            return "high"
        elif any(t.emotion_tone in ['calm', 'thoughtful'] for t in turns):
            return "moderate"
        return "low"
    
    def _assess_conversation_direction(self, turns: List[CollaborationTurn]) -> str:
        """Evalúa la dirección de la conversación"""
        # Implementación simplificada
        return "convergent"  # o "divergent", "circular"
    
    def _apply_intervention(self, context: Dict[str, Any], intervention: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica una intervención del director al contexto"""
        if intervention.get('temperature_change'):
            self._current_context.temperature = intervention['temperature_change']
        
        if intervention.get('topic_pivot'):
            context['direction'] = 'pivoting'
            context['new_focus'] = intervention['topic_pivot']
        
        if intervention.get('energy_boost'):
            context['energy'] = 'high'
        
        return context
    
    async def _generate_contextual_response(
        self,
        context_analysis: Dict[str, Any],
        collaboration_context: CollaborationContext
    ) -> Dict[str, Any]:
        """
        Genera una respuesta contextual basada en el análisis.
        
        Este método sería sobrescrito por cada agente específico
        para generar respuestas según su personalidad.
        """
        # Placeholder - cada agente implementaría su lógica específica
        return {
            "text": f"[{self.agent_id}] Participando en {collaboration_context.mode.value} sobre {collaboration_context.topic}",
            "emotion": "engaged",
            "confidence": 0.8,
            "references": None
        }
    
    def get_collaboration_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de colaboración del agente.
        
        Returns:
            Estadísticas de participación y química
        """
        return {
            "total_collaborations": len(self._collaboration_memory),
            "chemistry_scores": self._chemistry_scores,
            "preferred_modes": self._analyze_preferred_modes(),
            "collaboration_style": self._collaboration_style,
            "average_confidence": self._calculate_average_confidence()
        }
    
    def _analyze_preferred_modes(self) -> List[str]:
        """Analiza los modos preferidos basado en el historial"""
        # Implementación simplificada
        return ["debate", "workshop"]
    
    def _calculate_average_confidence(self) -> float:
        """Calcula la confianza promedio en colaboraciones"""
        if not self._collaboration_memory:
            return 0.0
        
        confidences = [turn.confidence for turn in self._collaboration_memory]
        return sum(confidences) / len(confidences)


class CollaborationOrchestrator:
    """
    Orquestador de colaboraciones entre agentes.
    Maneja el flujo de turnos y la coordinación.
    """
    
    def __init__(self):
        self.active_sessions = {}
        self.session_history = []
    
    async def start_collaboration(
        self,
        mode: CollaborationMode,
        topic: str,
        participants: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Inicia una nueva sesión de colaboración.
        
        Returns:
            ID de la sesión
        """
        session_id = f"{mode.value}_{datetime.now().timestamp()}"
        
        session = {
            "id": session_id,
            "mode": mode,
            "topic": topic,
            "participants": participants,
            "config": config or {},
            "turns": [],
            "start_time": datetime.now(),
            "status": "active"
        }
        
        self.active_sessions[session_id] = session
        logger.info(f"Started collaboration session {session_id}")
        
        return session_id
    
    async def process_turn(
        self,
        session_id: str,
        agent_id: str,
        turn_content: CollaborationTurn
    ) -> Dict[str, Any]:
        """
        Procesa un turno en la colaboración.
        
        Returns:
            Estado actualizado de la sesión
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session["turns"].append(turn_content)
        
        # Determinar siguiente turno
        next_agent = self._determine_next_speaker(session)
        
        return {
            "session_id": session_id,
            "turn_number": len(session["turns"]),
            "next_speaker": next_agent,
            "session_status": session["status"]
        }
    
    def _determine_next_speaker(self, session: Dict[str, Any]) -> Optional[str]:
        """Determina quién habla a continuación"""
        # Lógica simplificada - round robin
        participants = session["participants"]
        turns = session["turns"]
        
        if not turns:
            return participants[0]["id"]
        
        last_speaker = turns[-1].agent_id
        current_idx = next((i for i, p in enumerate(participants) if p["id"] == last_speaker), 0)
        next_idx = (current_idx + 1) % len(participants)
        
        return participants[next_idx]["id"]
    
    async def end_collaboration(self, session_id: str) -> Dict[str, Any]:
        """
        Finaliza una sesión de colaboración.
        
        Returns:
            Resumen de la sesión
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session["status"] = "completed"
        session["end_time"] = datetime.now()
        
        # Generar resumen
        summary = {
            "session_id": session_id,
            "duration": (session["end_time"] - session["start_time"]).total_seconds(),
            "total_turns": len(session["turns"]),
            "participants": [p["id"] for p in session["participants"]],
            "mode": session["mode"].value,
            "topic": session["topic"]
        }
        
        # Archivar sesión
        self.session_history.append(session)
        del self.active_sessions[session_id]
        
        return summary