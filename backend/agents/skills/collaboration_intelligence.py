"""
Collaboration Intelligence Layer for NGX Agents
==============================================

This module provides advanced AI-powered intelligence for detecting when agents should
collaborate, what type of collaboration is optimal, and how to seamlessly integrate
collaborative suggestions into natural agent responses.

This is the brain that makes collaboration feel natural and intelligent.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CollaborationTrigger(Enum):
    """Types of triggers that suggest collaboration"""
    MULTI_DOMAIN = "multi_domain"           # Multiple expertise areas
    COMPLEX_CASE = "complex_case"           # Complex medical/personal cases  
    CONFLICTING_GOALS = "conflicting_goals" # Contradictory objectives
    DEBATE_REQUEST = "debate_request"       # User wants different perspectives
    COMPREHENSIVE_PLAN = "comprehensive_plan" # User wants complete solution
    EDUCATIONAL_DEPTH = "educational_depth" # Deep learning request
    UNCERTAINTY_HIGH = "uncertainty_high"   # Agent not confident alone


class CollaborationUrgency(Enum):
    """How urgently collaboration is recommended"""
    OPTIONAL = "optional"       # Nice to have
    RECOMMENDED = "recommended" # Should collaborate  
    ESSENTIAL = "essential"     # Must collaborate for safety/quality


@dataclass
class DomainProfile:
    """Profile of expertise domains"""
    name: str
    keywords: List[str]
    agent_specialists: List[str]
    complexity_indicators: List[str]
    collaboration_synergies: List[str]  # Which domains work well together


@dataclass
class CollaborationSuggestion:
    """Structured suggestion for collaboration"""
    should_collaborate: bool
    trigger_type: CollaborationTrigger
    urgency: CollaborationUrgency
    recommended_mode: str  # debate, workshop, teaching, etc.
    suggested_agents: List[Dict[str, str]]
    reasoning: str
    collaboration_prompt: str
    individual_fallback: bool
    estimated_session_length: str
    expected_outcomes: List[str]
    user_choice_prompt: str


class CollaborationIntelligence:
    """
    Advanced AI system for intelligent collaboration detection and suggestion.
    
    This class analyzes user queries and agent contexts to determine:
    1. When collaboration would be beneficial
    2. What type of collaboration is optimal  
    3. Which agents should participate
    4. How to present options to users naturally
    """
    
    def __init__(self):
        self.domain_profiles = self._initialize_domain_profiles()
        self.collaboration_patterns = self._initialize_collaboration_patterns()
        self.agent_specialties = self._initialize_agent_specialties()
        self.conversation_memory = []
        
    def _initialize_domain_profiles(self) -> Dict[str, DomainProfile]:
        """Initialize comprehensive domain knowledge profiles"""
        return {
            "nutrition": DomainProfile(
                name="Nutrición y Alimentación",
                keywords=[
                    # Basic nutrition
                    "comida", "alimento", "nutrición", "dieta", "comer", "alimentación",
                    "vitamina", "mineral", "proteína", "carbohidrato", "grasa",
                    # Specific diets
                    "keto", "cetogénica", "vegana", "vegetariana", "paleo", "intermitente", "ayuno",
                    "mediterránea", "dash", "flexitariana", "carnívora",
                    # Medical nutrition
                    "diabetes", "colesterol", "presión", "hipertensión", "intestino", "digestión",
                    "alergia", "intolerancia", "celíaco", "lactosa", "inflamación",
                    # Goals
                    "perder peso", "ganar peso", "masa muscular", "quemar grasa", "definir",
                    "volumen", "cutting", "bulking", "recomposición", "metabolismo"
                ],
                agent_specialists=["sage"],
                complexity_indicators=[
                    "múltiples alergias", "diabetes tipo", "enfermedad", "medicamento",
                    "condición médica", "historial", "problema digestivo", "síndrome"
                ],
                collaboration_synergies=[
                    "exercise", "mental_health", "medical", "biometrics"
                ]
            ),
            
            "exercise": DomainProfile(
                name="Ejercicio y Entrenamiento",
                keywords=[
                    # Exercise types
                    "ejercicio", "entrenamiento", "gimnasio", "pesas", "cardio", "correr",
                    "natación", "ciclismo", "yoga", "pilates", "crossfit", "funcional",
                    "hiit", "aeróbico", "anaeróbico", "fuerza", "resistencia", "flexibilidad",
                    # Body parts
                    "piernas", "brazos", "espalda", "pecho", "abdomen", "glúteos", "hombros",
                    "bíceps", "tríceps", "core", "cuádriceps", "isquiotibiales",
                    # Training concepts  
                    "rutina", "plan", "programa", "rep", "serie", "descanso", "progresión",
                    "periodización", "volumen", "intensidad", "frecuencia", "técnica",
                    # Injuries/issues
                    "lesión", "dolor", "rehabilitación", "fisioterapia", "recuperación"
                ],
                agent_specialists=["blaze"],
                complexity_indicators=[
                    "lesión previa", "limitación física", "cirugía", "artritis", "hernia",
                    "problema articular", "edad avanzada", "principiante absoluto"
                ],
                collaboration_synergies=[
                    "nutrition", "mental_health", "biometrics", "recovery"
                ]
            ),
            
            "mental_health": DomainProfile(
                name="Salud Mental y Motivación",
                keywords=[
                    # Mental states
                    "motivación", "disciplina", "ansiedad", "estrés", "depresión",
                    "autoestima", "confianza", "miedo", "frustración", "burnout",
                    "cansancio mental", "agobio", "presión", "inseguridad",
                    # Behavioral
                    "hábito", "rutina", "consistencia", "adherencia", "rendirse",
                    "procrastinar", "excusa", "falta de tiempo", "desmotivación",
                    "atracón", "antojos", "compulsión", "control", "willpower",
                    # Goals & mindset
                    "objetivo", "meta", "sueño", "transformación", "cambio",
                    "mentalidad", "actitud", "perseverancia", "paciencia"
                ],
                agent_specialists=["spark"],
                complexity_indicators=[
                    "depresión severa", "trastorno", "trauma", "terapia", "medicación",
                    "historial de trastornos", "recaída frecuente", "problema grave"
                ],
                collaboration_synergies=[
                    "nutrition", "exercise", "lifestyle", "medical"
                ]
            ),
            
            "biometrics": DomainProfile(
                name="Análisis Biométrico y Datos",
                keywords=[
                    # Measurements
                    "peso", "altura", "imc", "grasa corporal", "músculo", "medidas",
                    "circunferencias", "pliegues", "bioimpedancia", "dexa", "bod pod",
                    # Vital signs
                    "presión arterial", "frecuencia cardíaca", "saturación", "glucosa",
                    "colesterol", "triglicéridos", "hemoglobina", "ferritina",
                    # Tracking
                    "progreso", "seguimiento", "datos", "análisis", "tendencia",
                    "comparación", "evolución", "baseline", "objetivo numérico",
                    # Devices
                    "báscula", "cinta métrica", "pulsómetro", "smartwatch", "aplicación"
                ],
                agent_specialists=["flux"],
                complexity_indicators=[
                    "múltiples métricas", "datos contradictorios", "meseta prolongada",
                    "fluctuaciones extrañas", "resultados médicos", "análisis complejo"
                ],
                collaboration_synergies=[
                    "nutrition", "exercise", "medical", "goal_setting"
                ]
            ),
            
            "medical": DomainProfile(
                name="Condiciones Médicas y Salud",
                keywords=[
                    # Conditions
                    "diabetes", "hipertensión", "colesterol", "tiroides", "pcos", "sop",
                    "síndrome metabólico", "resistencia insulina", "prediabetes",
                    "hipotiroidismo", "hipertiroidismo", "apnea", "fibromialgia",
                    # Medications
                    "medicamento", "pastilla", "insulina", "metformina", "estatina",
                    "anticonceptivo", "hormona", "suplemento", "tratamiento",
                    # Symptoms
                    "síntoma", "dolor", "fatiga", "mareo", "náusea", "inflamación",
                    "retención", "hinchazón", "irregular", "problema"
                ],
                agent_specialists=["sage", "flux"],
                complexity_indicators=[
                    "múltiples condiciones", "medicamentos múltiples", "cirugía reciente",
                    "embarazo", "lactancia", "edad avanzada", "condición rara"
                ],
                collaboration_synergies=[
                    "nutrition", "exercise", "mental_health", "biometrics"
                ]
            ),
            
            "lifestyle": DomainProfile(
                name="Estilo de Vida y Hábitos", 
                keywords=[
                    # Time/schedule
                    "tiempo", "horario", "ocupado", "trabajo", "viaje", "turno",
                    "disponibilidad", "calendario", "rutina diaria", "agenda",
                    # Social/family
                    "familia", "niños", "pareja", "social", "amigos", "compromiso",
                    "evento", "celebración", "vacaciones", "fin de semana",
                    # Habits
                    "hábito", "costumbre", "rutina", "estructura", "organización",
                    "planificación", "preparación", "batch cooking"
                ],
                agent_specialists=["nexus", "spark"],
                complexity_indicators=[
                    "horario muy irregular", "viajes frecuentes", "múltiples responsabilidades",
                    "familia numerosa", "trabajo demandante", "poco tiempo"
                ],
                collaboration_synergies=[
                    "nutrition", "exercise", "mental_health", "goal_setting"
                ]
            )
        }
    
    def _initialize_collaboration_patterns(self) -> Dict[str, Dict]:
        """Initialize patterns that indicate need for collaboration"""
        return {
            # Multi-domain indicators
            "comprehensive_request": {
                "patterns": [
                    r"plan\s+(completo|integral|total)",
                    r"todo\s+lo\s+que\s+necesito",
                    r"(ayuda|guía)\s+(completa|total)",
                    r"desde\s+cero\s+hasta",
                    r"paso\s+a\s+paso\s+completo"
                ],
                "trigger": CollaborationTrigger.COMPREHENSIVE_PLAN,
                "urgency": CollaborationUrgency.RECOMMENDED
            },
            
            "uncertainty_indicators": {
                "patterns": [
                    r"no\s+(sé|se)\s+(qué|que|como|cómo)",
                    r"(confundido|perdido|abrumado)",
                    r"muchas\s+opciones",
                    r"no\s+estoy\s+seguro",
                    r"(dudas|incertidumbre)"
                ],
                "trigger": CollaborationTrigger.UNCERTAINTY_HIGH,
                "urgency": CollaborationUrgency.RECOMMENDED
            },
            
            "debate_request": {
                "patterns": [
                    r"(pros\s+y\s+contras|ventajas\s+y\s+desventajas)",
                    r"(opiniones\s+diferentes|perspectivas\s+diferentes)",
                    r"(qué\s+es\s+mejor|cuál\s+es\s+mejor)",
                    r"(debate|discusión|comparar)",
                    r"(diferentes\s+enfoques|múltiples\s+opciones)"
                ],
                "trigger": CollaborationTrigger.DEBATE_REQUEST,
                "urgency": CollaborationUrgency.RECOMMENDED
            },
            
            "conflicting_goals": {
                "patterns": [
                    r"(perder\s+grasa\s+y\s+ganar\s+músculo|ganar\s+músculo\s+y\s+perder\s+grasa)",
                    r"(rápido\s+pero\s+sostenible|sostenible\s+pero\s+rápido)",
                    r"(poco\s+tiempo\s+pero\s+resultados)",
                    r"(económico\s+pero\s+efectivo|efectivo\s+pero\s+económico)",
                    r"(sin\s+ejercicio\s+pero\s+en\s+forma)"
                ],
                "trigger": CollaborationTrigger.CONFLICTING_GOALS,
                "urgency": CollaborationUrgency.ESSENTIAL
            },
            
            "complex_medical": {
                "patterns": [
                    r"(diabetes\s+y\s+\w+|hipertensión\s+y\s+\w+)",
                    r"(medicamento\s+y\s+\w+|tratamiento\s+y\s+\w+)",
                    r"(condición\s+médica|problema\s+de\s+salud)",
                    r"(múltiples\s+síntomas|varios\s+problemas)",
                    r"(doctor\s+dijo|médico\s+recomendó)"
                ],
                "trigger": CollaborationTrigger.COMPLEX_CASE,
                "urgency": CollaborationUrgency.ESSENTIAL
            },
            
            "educational_depth": {
                "patterns": [
                    r"(explica\s+(detalladamente|en\s+profundidad))",
                    r"(quiero\s+(entender|aprender)\s+sobre)",
                    r"(cómo\s+funciona\s+exactamente)",
                    r"(ciencia\s+detrás|base\s+científica)",
                    r"(curso\s+completo|masterclass)"
                ],
                "trigger": CollaborationTrigger.EDUCATIONAL_DEPTH,
                "urgency": CollaborationUrgency.RECOMMENDED
            }
        }
    
    def _initialize_agent_specialties(self) -> Dict[str, Dict]:
        """Map of agent specialties and their collaboration strengths"""
        return {
            "nexus": {
                "specialty": "Coordinación y síntesis",
                "strengths": ["orchestration", "synthesis", "project_management"],
                "best_collaborations": ["any_multi_agent_session"],
                "collaboration_role": "coordinator"
            },
            "sage": {
                "specialty": "Nutrición y alimentación",
                "strengths": ["nutrition", "medical_nutrition", "meal_planning"],
                "best_collaborations": ["blaze", "flux", "spark"],
                "collaboration_role": "nutrition_expert"
            },
            "blaze": {
                "specialty": "Entrenamiento y ejercicio",
                "strengths": ["exercise", "training_plans", "injury_prevention"],
                "best_collaborations": ["sage", "flux", "spark"],
                "collaboration_role": "fitness_expert"
            },
            "flux": {
                "specialty": "Análisis biométrico y datos",
                "strengths": ["data_analysis", "progress_tracking", "biometrics"],
                "best_collaborations": ["sage", "blaze", "nexus"],
                "collaboration_role": "data_analyst"
            },
            "spark": {
                "specialty": "Motivación y salud mental",
                "strengths": ["motivation", "behavior_change", "mental_health"],
                "best_collaborations": ["sage", "blaze", "nexus"],
                "collaboration_role": "mindset_coach"
            },
            "luna": {
                "specialty": "Descanso y recuperación",
                "strengths": ["sleep", "recovery", "stress_management"],
                "best_collaborations": ["spark", "blaze", "sage"],
                "collaboration_role": "recovery_specialist"
            },
            "echo": {
                "specialty": "Comunicación y adherencia",
                "strengths": ["communication", "habit_formation", "accountability"],
                "best_collaborations": ["spark", "nexus", "any"],
                "collaboration_role": "communication_specialist"
            }
        }
    
    async def analyze_collaboration_need(
        self, 
        user_input: str, 
        current_agent_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> CollaborationSuggestion:
        """
        Comprehensive analysis to determine if and how collaboration should be suggested.
        
        Args:
            user_input: User's query/message
            current_agent_id: The agent currently handling the query
            context: Additional context (conversation history, user profile, etc.)
            
        Returns:
            Detailed collaboration suggestion with reasoning
        """
        logger.info(f"Analyzing collaboration need for agent {current_agent_id}")
        
        # Step 1: Detect domains involved
        involved_domains = self._detect_domains(user_input)
        logger.debug(f"Detected domains: {involved_domains}")
        
        # Step 2: Analyze complexity and triggers
        triggers = self._analyze_triggers(user_input)
        logger.debug(f"Detected triggers: {triggers}")
        
        # Step 3: Assess collaboration necessity
        necessity = self._assess_collaboration_necessity(
            involved_domains, triggers, current_agent_id, context
        )
        
        # Step 4: If collaboration recommended, determine optimal setup
        if necessity["should_collaborate"]:
            collaboration_plan = self._design_collaboration_plan(
                user_input, involved_domains, triggers, current_agent_id, necessity
            )
            return collaboration_plan
        else:
            return CollaborationSuggestion(
                should_collaborate=False,
                trigger_type=CollaborationTrigger.MULTI_DOMAIN,
                urgency=CollaborationUrgency.OPTIONAL,
                recommended_mode="individual",
                suggested_agents=[],
                reasoning="Query can be handled effectively by individual agent",
                collaboration_prompt="",
                individual_fallback=True,
                estimated_session_length="N/A",
                expected_outcomes=[],
                user_choice_prompt=""
            )
    
    def _detect_domains(self, user_input: str) -> List[str]:
        """Detect which expertise domains are involved in the query"""
        detected_domains = []
        input_lower = user_input.lower()
        
        for domain_name, profile in self.domain_profiles.items():
            domain_score = 0
            
            # Check for keyword matches
            for keyword in profile.keywords:
                if keyword.lower() in input_lower:
                    domain_score += 1
            
            # Check for complexity indicators (higher weight)
            for complexity_indicator in profile.complexity_indicators:
                if complexity_indicator.lower() in input_lower:
                    domain_score += 3
            
            # Threshold for domain detection
            if domain_score >= 1:
                detected_domains.append(domain_name)
                logger.debug(f"Domain '{domain_name}' detected with score: {domain_score}")
        
        return detected_domains
    
    def _analyze_triggers(self, user_input: str) -> List[Dict[str, Any]]:
        """Analyze patterns that trigger collaboration recommendations"""
        detected_triggers = []
        
        for pattern_name, pattern_info in self.collaboration_patterns.items():
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, user_input, re.IGNORECASE):
                    detected_triggers.append({
                        "pattern_name": pattern_name,
                        "trigger": pattern_info["trigger"],
                        "urgency": pattern_info["urgency"],
                        "matched_pattern": pattern
                    })
                    logger.debug(f"Trigger detected: {pattern_name}")
                    break
        
        return detected_triggers
    
    def _assess_collaboration_necessity(
        self, 
        domains: List[str], 
        triggers: List[Dict[str, Any]], 
        current_agent_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Assess whether collaboration is necessary and at what urgency level"""
        
        # Check if current agent can handle all detected domains
        current_agent_domains = self._get_agent_domains(current_agent_id)
        unhandled_domains = [d for d in domains if d not in current_agent_domains]
        
        # Calculate collaboration score
        collaboration_score = 0
        urgency_level = CollaborationUrgency.OPTIONAL
        reasoning_factors = []
        
        # Factor 1: Multiple domains beyond current agent's expertise
        if len(unhandled_domains) > 0:
            collaboration_score += len(unhandled_domains) * 2
            reasoning_factors.append(f"Domains outside expertise: {unhandled_domains}")
            if len(unhandled_domains) >= 2:
                urgency_level = CollaborationUrgency.RECOMMENDED
        
        # Factor 2: Detected collaboration triggers
        for trigger_info in triggers:
            if trigger_info["urgency"] == CollaborationUrgency.ESSENTIAL:
                collaboration_score += 5
                urgency_level = CollaborationUrgency.ESSENTIAL
                reasoning_factors.append(f"Essential trigger: {trigger_info['pattern_name']}")
            elif trigger_info["urgency"] == CollaborationUrgency.RECOMMENDED:
                collaboration_score += 3
                if urgency_level == CollaborationUrgency.OPTIONAL:
                    urgency_level = CollaborationUrgency.RECOMMENDED
                reasoning_factors.append(f"Recommended trigger: {trigger_info['pattern_name']}")
        
        # Factor 3: Query complexity (word count, question complexity)
        query_complexity = self._assess_query_complexity(domains, triggers)
        collaboration_score += query_complexity
        if query_complexity >= 3:
            reasoning_factors.append("High query complexity detected")
        
        # Decision threshold
        should_collaborate = collaboration_score >= 3
        
        return {
            "should_collaborate": should_collaborate,
            "collaboration_score": collaboration_score,
            "urgency": urgency_level,
            "reasoning_factors": reasoning_factors,
            "unhandled_domains": unhandled_domains
        }
    
    def _design_collaboration_plan(
        self,
        user_input: str,
        domains: List[str],
        triggers: List[Dict[str, Any]],
        current_agent_id: str,
        necessity: Dict[str, Any]
    ) -> CollaborationSuggestion:
        """Design the optimal collaboration plan"""
        
        # Determine collaboration mode
        collab_mode = self._determine_collaboration_mode(triggers, domains, user_input)
        
        # Select optimal agent team
        suggested_agents = self._select_agent_team(domains, current_agent_id, collab_mode)
        
        # Generate human-friendly explanations
        reasoning = self._generate_reasoning(necessity, domains, triggers)
        collaboration_prompt = self._generate_collaboration_prompt(
            collab_mode, suggested_agents, domains, user_input
        )
        user_choice_prompt = self._generate_user_choice_prompt(
            suggested_agents, collab_mode, reasoning
        )
        
        # Estimate session details
        estimated_length = self._estimate_session_length(collab_mode, len(suggested_agents))
        expected_outcomes = self._predict_collaboration_outcomes(
            collab_mode, domains, suggested_agents
        )
        
        return CollaborationSuggestion(
            should_collaborate=True,
            trigger_type=triggers[0]["trigger"] if triggers else CollaborationTrigger.MULTI_DOMAIN,
            urgency=necessity["urgency"],
            recommended_mode=collab_mode,
            suggested_agents=suggested_agents,
            reasoning=reasoning,
            collaboration_prompt=collaboration_prompt,
            individual_fallback=True,
            estimated_session_length=estimated_length,
            expected_outcomes=expected_outcomes,
            user_choice_prompt=user_choice_prompt
        )
    
    def _determine_collaboration_mode(
        self, 
        triggers: List[Dict[str, Any]], 
        domains: List[str], 
        user_input: str
    ) -> str:
        """Determine the best collaboration mode based on context"""
        
        # Priority order based on triggers
        for trigger_info in triggers:
            if trigger_info["trigger"] == CollaborationTrigger.DEBATE_REQUEST:
                return "debate"
            elif trigger_info["trigger"] == CollaborationTrigger.EDUCATIONAL_DEPTH:
                return "teaching"
            elif trigger_info["trigger"] == CollaborationTrigger.COMPREHENSIVE_PLAN:
                return "workshop"
            elif trigger_info["trigger"] == CollaborationTrigger.COMPLEX_CASE:
                return "case_study"
        
        # Default based on domain count
        if len(domains) >= 3:
            return "workshop"  # Complex multi-domain requires structured collaboration
        elif len(domains) == 2:
            return "workshop"  # Two domains usually benefit from workshop approach
        else:
            return "workshop"  # Default to workshop for most scenarios
    
    def _select_agent_team(
        self, 
        domains: List[str], 
        current_agent_id: str, 
        collab_mode: str
    ) -> List[Dict[str, str]]:
        """Select the optimal team of agents for collaboration"""
        
        suggested_agents = []
        
        # Always include current agent unless they're not suited for collaboration
        current_agent_info = self.agent_specialties.get(current_agent_id, {})
        suggested_agents.append({
            "id": current_agent_id,
            "name": current_agent_info.get("specialty", "Current Agent"),
            "role": current_agent_info.get("collaboration_role", "specialist")
        })
        
        # Add specialists for each domain
        for domain in domains:
            domain_profile = self.domain_profiles.get(domain, {})
            for specialist_id in domain_profile.get("agent_specialists", []):
                if specialist_id != current_agent_id:
                    specialist_info = self.agent_specialties.get(specialist_id, {})
                    if not any(agent["id"] == specialist_id for agent in suggested_agents):
                        suggested_agents.append({
                            "id": specialist_id,
                            "name": specialist_info.get("specialty", specialist_id.title()),
                            "role": specialist_info.get("collaboration_role", "specialist")
                        })
        
        # Add coordinator if needed (complex sessions)
        if len(suggested_agents) >= 3 and not any(agent["id"] == "nexus" for agent in suggested_agents):
            suggested_agents.append({
                "id": "nexus",
                "name": "Coordinación y síntesis",
                "role": "coordinator"
            })
        
        # Limit team size for practical reasons
        return suggested_agents[:4]  # Max 4 agents for manageable collaboration
    
    def _generate_reasoning(
        self, 
        necessity: Dict[str, Any], 
        domains: List[str], 
        triggers: List[Dict[str, Any]]
    ) -> str:
        """Generate human-friendly reasoning for collaboration suggestion"""
        
        reasoning_parts = []
        
        # Domain-based reasoning
        if len(domains) > 1:
            domain_names = [self.domain_profiles[d].name for d in domains if d in self.domain_profiles]
            reasoning_parts.append(
                f"Tu consulta involucra múltiples áreas de expertise: {', '.join(domain_names)}"
            )
        
        # Trigger-based reasoning
        for trigger_info in triggers:
            trigger_type = trigger_info["trigger"]
            if trigger_type == CollaborationTrigger.COMPLEX_CASE:
                reasoning_parts.append("Detecté que es un caso complejo que se beneficia de múltiples perspectivas")
            elif trigger_type == CollaborationTrigger.DEBATE_REQUEST:
                reasoning_parts.append("Solicitas diferentes perspectivas o comparaciones")
            elif trigger_type == CollaborationTrigger.COMPREHENSIVE_PLAN:
                reasoning_parts.append("Buscas una solución completa e integral")
            elif trigger_type == CollaborationTrigger.UNCERTAINTY_HIGH:
                reasoning_parts.append("Noto incertidumbre que múltiples expertos pueden resolver mejor")
        
        # Add collaboration benefits
        reasoning_parts.append(
            "La colaboración entre especialistas te dará una perspectiva más completa y soluciones más efectivas"
        )
        
        return ". ".join(reasoning_parts) + "."
    
    def _generate_collaboration_prompt(
        self,
        mode: str,
        agents: List[Dict[str, str]],
        domains: List[str],
        user_input: str
    ) -> str:
        """Generate a natural prompt for collaboration"""
        
        agent_names = [agent["name"] for agent in agents]
        
        mode_descriptions = {
            "debate": f"un debate estructurado entre {' y '.join(agent_names)} para explorar diferentes perspectivas",
            "workshop": f"una sesión colaborativa donde {', '.join(agent_names)} trabajen juntos en tu solución",
            "teaching": f"una sesión educativa donde {agent_names[0]} enseñe con apoyo de {', '.join(agent_names[1:])}",
            "case_study": f"un análisis profundo de tu caso con {', '.join(agent_names)} como expertos",
            "podcast": f"una conversación natural estilo podcast entre {' y '.join(agent_names)}"
        }
        
        return mode_descriptions.get(mode, f"una colaboración entre {', '.join(agent_names)}")
    
    def _generate_user_choice_prompt(
        self,
        agents: List[Dict[str, str]],
        mode: str,
        reasoning: str
    ) -> str:
        """Generate user-friendly choice prompt"""
        
        agent_list = "\n".join([f"  • {agent['name']}" for agent in agents])
        
        return f"""
{reasoning}

Te ofrezco dos opciones:

🤝 **Colaboración Recomendada** ({mode})
{agent_list}

👤 **Respuesta Individual**
Solo yo te respondo desde mi especialidad

¿Qué prefieres? La colaboración te dará una perspectiva más completa, pero si tienes prisa, puedo responderte individualmente primero.
"""
    
    def _estimate_session_length(self, mode: str, agent_count: int) -> str:
        """Estimate collaboration session length"""
        base_times = {
            "debate": 10,
            "workshop": 15,
            "teaching": 12,
            "case_study": 20,
            "podcast": 8
        }
        
        base_time = base_times.get(mode, 12)
        total_time = base_time + (agent_count - 1) * 3  # 3 min per additional agent
        
        return f"{total_time}-{total_time + 5} minutos"
    
    def _predict_collaboration_outcomes(
        self,
        mode: str,
        domains: List[str],
        agents: List[Dict[str, str]]
    ) -> List[str]:
        """Predict expected outcomes from collaboration"""
        
        outcomes = []
        
        if mode == "debate":
            outcomes.extend([
                "Perspectivas balanceadas pros/contras",
                "Argumentos fundamentados de cada lado",
                "Recomendación final consensuada"
            ])
        elif mode == "workshop":
            outcomes.extend([
                "Plan integral personalizado",
                "Estrategias coordinadas entre especialidades",
                "Roadmap paso a paso"
            ])
        elif mode == "teaching":
            outcomes.extend([
                "Comprensión profunda del tema",
                "Ejemplos prácticos aplicables",
                "Material de referencia adicional"
            ])
        elif mode == "case_study":
            outcomes.extend([
                "Análisis exhaustivo de tu situación",
                "Múltiples opciones de solución",
                "Plan de implementación detallado"
            ])
        
        # Add domain-specific outcomes
        if "nutrition" in domains:
            outcomes.append("Plan nutricional específico")
        if "exercise" in domains:
            outcomes.append("Rutina de ejercicio personalizada")
        if "mental_health" in domains:
            outcomes.append("Estrategias de motivación y adherencia")
        
        return outcomes[:5]  # Limit to top 5 outcomes
    
    def _assess_query_complexity(self, domains: List[str], triggers: List[Dict[str, Any]]) -> int:
        """Assess complexity score of the query"""
        complexity = 0
        
        # Domain complexity
        complexity += len(domains)
        
        # Trigger complexity
        for trigger_info in triggers:
            if trigger_info["urgency"] == CollaborationUrgency.ESSENTIAL:
                complexity += 2
            elif trigger_info["urgency"] == CollaborationUrgency.RECOMMENDED:
                complexity += 1
        
        return complexity
    
    def _get_agent_domains(self, agent_id: str) -> List[str]:
        """Get domains that an agent can handle effectively"""
        domain_map = {
            "sage": ["nutrition", "medical"],
            "blaze": ["exercise"],
            "flux": ["biometrics", "medical"],
            "spark": ["mental_health", "lifestyle"],
            "luna": ["lifestyle", "mental_health"],
            "echo": ["lifestyle"],
            "nexus": ["lifestyle"]  # Coordinator can handle general lifestyle queries
        }
        
        return domain_map.get(agent_id, [])
    
    def get_collaboration_stats(self) -> Dict[str, Any]:
        """Get statistics about collaboration suggestions and patterns"""
        return {
            "total_domains": len(self.domain_profiles),
            "total_patterns": len(self.collaboration_patterns),
            "total_agents": len(self.agent_specialties),
            "domain_synergies": sum(
                len(profile.collaboration_synergies) 
                for profile in self.domain_profiles.values()
            )
        }