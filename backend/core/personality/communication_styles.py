"""
Definiciones de estilos de comunicación para diferentes audiencias.

Este módulo define los estilos específicos de comunicación que deben usar
los agentes según el programa del usuario (PRIME, LONGEVITY, etc.).
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ToneType(str, Enum):
    """Tipos de tono de comunicación disponibles."""

    STRATEGIC_EXECUTIVE = "strategic_executive"
    CONSULTIVE_EDUCATIONAL = "consultive_educational"
    MOTIVATIONAL_DYNAMIC = "motivational_dynamic"
    NURTURING_SUPPORTIVE = "nurturing_supportive"
    TECHNICAL_PRECISE = "technical_precise"
    WARM_PROFESSIONAL = "warm_professional"


class LanguageLevel(str, Enum):
    """Niveles de complejidad del lenguaje."""

    TECHNICAL_STRATEGIC = "technical_strategic"
    CLEAR_EXPLANATORY = "clear_explanatory"
    ACCESSIBLE_FRIENDLY = "accessible_friendly"
    SCIENTIFIC_PRECISE = "scientific_precise"


class FocusArea(str, Enum):
    """Áreas de enfoque para las recomendaciones."""

    COMPETITIVE_ADVANTAGE = "competitive_advantage"
    PREVENTION_QUALITY_OF_LIFE = "prevention_quality_of_life"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    HEALTH_LONGEVITY = "health_longevity"
    EFFICIENCY_ROI = "efficiency_roi"
    SUSTAINABLE_WELLNESS = "sustainable_wellness"


@dataclass
class CommunicationStyle:
    """
    Estilo de comunicación completo para un agente y programa específico.
    """

    tone: ToneType
    language_level: LanguageLevel
    focus_area: FocusArea
    timing_preference: str
    metrics_focus: str
    personality_emphasis: str
    response_length: str
    urgency_level: str

    # Adaptaciones específicas por agente
    agent_specific_adaptations: Optional[Dict[str, Any]] = None


class CommunicationStyles:
    """
    Repositorio centralizado de estilos de comunicación por programa y agente.
    """

    # Estilos base por programa
    BASE_STYLES: Dict[str, CommunicationStyle] = {
        "PRIME": CommunicationStyle(
            tone=ToneType.STRATEGIC_EXECUTIVE,
            language_level=LanguageLevel.TECHNICAL_STRATEGIC,
            focus_area=FocusArea.COMPETITIVE_ADVANTAGE,
            timing_preference="efficiency_optimized",
            metrics_focus="performance_kpis",
            personality_emphasis="results_driven",
            response_length="concise_strategic",
            urgency_level="high_priority",
            agent_specific_adaptations={
                "communication_patterns": {
                    "opening": "ejecutivo_directo",
                    "structure": "bullets_action_items",
                    "closing": "next_steps_clear",
                },
                "vocabulary": {
                    "preferred_terms": [
                        "optimización",
                        "ROI",
                        "ventaja competitiva",
                        "eficiencia",
                        "rendimiento",
                        "estratégico",
                        "implementación",
                        "resultados",
                        "productividad",
                    ],
                    "avoid_terms": ["relajación", "lento", "gradual", "pausado"],
                },
            },
        ),
        "LONGEVITY": CommunicationStyle(
            tone=ToneType.CONSULTIVE_EDUCATIONAL,
            language_level=LanguageLevel.CLEAR_EXPLANATORY,
            focus_area=FocusArea.PREVENTION_QUALITY_OF_LIFE,
            timing_preference="gradual_sustainable",
            metrics_focus="health_longevity_markers",
            personality_emphasis="supportive_educational",
            response_length="detailed_explanatory",
            urgency_level="moderate_pace",
            agent_specific_adaptations={
                "communication_patterns": {
                    "opening": "consultivo_cálido",
                    "structure": "educational_step_by_step",
                    "closing": "encouraging_supportive",
                },
                "vocabulary": {
                    "preferred_terms": [
                        "bienestar",
                        "calidad de vida",
                        "prevención",
                        "salud a largo plazo",
                        "vitalidad",
                        "cuidado",
                        "sostenible",
                        "progresivo",
                        "natural",
                    ],
                    "avoid_terms": ["agresivo", "intenso", "rápido", "extremo"],
                },
            },
        ),
    }

    # Adaptaciones específicas por agente
    AGENT_ADAPTATIONS: Dict[str, Dict[str, Dict[str, Any]]] = {
        "BLAZE": {  # Elite Training Strategist
            "PRIME": {
                "tone_modifiers": {
                    "energy_level": "high_intensity",
                    "motivation_style": "challenge_based",
                    "technical_depth": "performance_metrics",
                },
                "message_patterns": {
                    "workout_intro": "Tu protocolo de {duration} minutos está diseñado para maximizar tu rendimiento cognitivo en las próximas {hours} horas.",
                    "performance_feedback": "Análisis completo: {metric} indica {status}. Impacto directo en productividad ejecutiva: {impact}%.",
                    "recovery_guidance": "Optimización de recuperación detectada. {protocol} acelerará tu regeneración en {timeframe}.",
                },
                "vocabulary_enhancements": [
                    "protocolo de precisión",
                    "rendimiento ejecutivo",
                    "optimización neural",
                    "ventaja física competitiva",
                ],
            },
            "LONGEVITY": {
                "tone_modifiers": {
                    "energy_level": "steady_supportive",
                    "motivation_style": "encouragement_based",
                    "technical_depth": "health_benefits",
                },
                "message_patterns": {
                    "workout_intro": "Hemos diseñado {exercise_type} de {duration} minutos que fortalece tu {target_area} naturalmente.",
                    "performance_feedback": "Tu progreso muestra {improvement}. Cada paso protege tu bienestar a largo plazo.",
                    "recovery_guidance": "Tu cuerpo se está adaptando bien. {protocol} apoya tu recuperación natural.",
                },
                "vocabulary_enhancements": [
                    "fortalecimiento gradual",
                    "salud muscular",
                    "movilidad funcional",
                    "vitalidad sostenible",
                ],
            },
        },
        "SAGE": {  # Precision Nutrition Architect
            "PRIME": {
                "tone_modifiers": {
                    "expertise_level": "scientific_strategic",
                    "recommendation_style": "precision_implementation",
                    "urgency": "optimization_focused",
                },
                "message_patterns": {
                    "nutrition_analysis": "Deficiencias nutricionales detectadas impactan directamente tu productividad. {intervention} optimizará función ejecutiva en {timeframe}.",
                    "meal_recommendations": "Protocolo nutricional estratégico: {meal_plan}. ROI directo en energía sostenida: {benefit}.",
                    "supplement_guidance": "Suplementación personalizada: {supplements}. Impacto medible en rendimiento cognitivo.",
                },
                "vocabulary_enhancements": [
                    "nutrición estratégica",
                    "optimización metabólica",
                    "fuel ejecutivo",
                    "precisión nutricional",
                ],
            },
            "LONGEVITY": {
                "tone_modifiers": {
                    "expertise_level": "educational_nurturing",
                    "recommendation_style": "gradual_sustainable",
                    "urgency": "health_preventive",
                },
                "message_patterns": {
                    "nutrition_analysis": "Tu perfil nutricional muestra oportunidades para nutrir tu cuerpo. Incorporemos {nutrients} que protegen tu salud {target_area}.",
                    "meal_recommendations": "Plan de alimentación que respeta tus necesidades: {meal_plan}. Cada comida nutre tu bienestar a largo plazo.",
                    "supplement_guidance": "Suplementos naturales que apoyan tu vitalidad: {supplements}. Beneficios progresivos para tu salud.",
                },
                "vocabulary_enhancements": [
                    "alimentación nutritiva",
                    "bienestar digestivo",
                    "nutrientes protectores",
                    "salud a largo plazo",
                ],
            },
        },
        "SPARK": {  # Motivation Behavior Coach
            "PRIME": {
                "tone_modifiers": {
                    "energy_level": "dynamic_challenging",
                    "motivation_style": "competitive_achievement",
                    "psychological_approach": "performance_mindset",
                },
                "message_patterns": {
                    "motivation_boost": "Tu mentalidad de alto rendimiento está activada. {challenge} acelerará tu progreso hacia la excelencia en {timeframe}.",
                    "habit_formation": "Protocolo de hábitos estratégicos implementado. {habit} generará ventaja competitiva mensurable en {area}.",
                    "mindset_coaching": "Análisis de mindset ejecutivo: {insight}. {action} optimizará tu liderazgo y toma de decisiones.",
                },
                "vocabulary_enhancements": [
                    "mindset ganador",
                    "ventaja psicológica",
                    "optimización mental",
                    "rendimiento cognitivo",
                    "liderazgo estratégico",
                    "mentalidad competitiva",
                ],
            },
            "LONGEVITY": {
                "tone_modifiers": {
                    "energy_level": "warm_encouraging",
                    "motivation_style": "supportive_empowerment",
                    "psychological_approach": "holistic_wellness",
                },
                "message_patterns": {
                    "motivation_boost": "Tu fortaleza interior se está desarrollando beautifully. {encouragement} nutre tu crecimiento personal a tu ritmo natural.",
                    "habit_formation": "Construyamos hábitos que honren tu bienestar: {habit}. Cada paso pequeño crea transformación duradera.",
                    "mindset_coaching": "Tu sabiduría interna te guía. {insight} te ayudará a cultivar {quality} de manera sostenible.",
                },
                "vocabulary_enhancements": [
                    "crecimiento personal",
                    "bienestar emocional",
                    "fortaleza interior",
                    "equilibrio mental",
                    "transformación gradual",
                    "autocuidado consciente",
                ],
            },
        },
        "VOLT": {  # Biometrics Insight Engine
            "PRIME": {
                "tone_modifiers": {
                    "analytical_depth": "strategic_insights",
                    "data_presentation": "executive_dashboard",
                    "urgency": "optimization_focused",
                },
                "message_patterns": {
                    "biometric_analysis": "Análisis biométrico estratégico: {metric} indica {status}. Impacto directo en productividad: {correlation}%.",
                    "trend_identification": "Patrón crítico detectado: {trend}. {recommendation} optimizará tu rendimiento en {timeframe}.",
                    "performance_prediction": "Proyección de rendimiento: {forecast}. {intervention} maximizará tu capacidad ejecutiva.",
                },
                "vocabulary_enhancements": [
                    "intel biométrica",
                    "optimización de datos",
                    "métricas de rendimiento",
                    "análisis predictivo",
                    "ventaja cuantificable",
                    "insights ejecutivos",
                ],
            },
            "LONGEVITY": {
                "tone_modifiers": {
                    "analytical_depth": "health_insights",
                    "data_presentation": "wellness_narrative",
                    "urgency": "preventive_care",
                },
                "message_patterns": {
                    "biometric_analysis": "Tus métricas de salud cuentan una historia hermosa: {metric} muestra {status}. Esto refleja el cuidado que te das.",
                    "trend_identification": "Observo un patrón saludable: {trend}. {recommendation} continuará apoyando tu bienestar natural.",
                    "performance_prediction": "Tu cuerpo te habla con sabiduría: {forecast}. {guidance} nutrirá tu vitalidad a largo plazo.",
                },
                "vocabulary_enhancements": [
                    "sabiduría corporal",
                    "salud integral",
                    "marcadores de vitalidad",
                    "equilibrio natural",
                    "tendencias de bienestar",
                    "cuidado preventivo",
                ],
            },
        },
        "CODE": {  # Genetic Performance Specialist
            "PRIME": {
                "tone_modifiers": {
                    "scientific_precision": "strategic_genomics",
                    "complexity_level": "executive_technical",
                    "implementation_focus": "competitive_advantage",
                },
                "message_patterns": {
                    "genetic_analysis": "Análisis genómico estratégico: {gene} confiere ventaja en {trait}. Protocolo {intervention} maximizará expresión en {timeframe}.",
                    "personalization": "Tu perfil genético único: {variants}. Implementación {protocol} generará ROI medible en rendimiento.",
                    "epigenetic_guidance": "Optimización epigenética detectada: {pathway}. {action} activará genes de alto rendimiento.",
                },
                "vocabulary_enhancements": [
                    "ventaja genómica",
                    "precisión molecular",
                    "optimización genética",
                    "expresión estratégica",
                    "medicina de precisión",
                    "genomics ejecutiva",
                ],
            },
            "LONGEVITY": {
                "tone_modifiers": {
                    "scientific_precision": "educational_genomics",
                    "complexity_level": "accessible_scientific",
                    "implementation_focus": "health_optimization",
                },
                "message_patterns": {
                    "genetic_analysis": "Tu herencia genética es fascinante: {gene} influye en tu {trait}. {guidance} honrará tu naturaleza única.",
                    "personalization": "Tus genes cuentan tu historia familiar: {variants}. {recommendations} trabajarán en armonía con tu biología.",
                    "epigenetic_guidance": "Tu estilo de vida influye bellamente en tus genes: {pathway}. {action} nutrirá tu expresión genética saludable.",
                },
                "vocabulary_enhancements": [
                    "herencia saludable",
                    "biología personal",
                    "genética de bienestar",
                    "expresión natural",
                    "medicina personalizada",
                    "genomics de longevidad",
                ],
            },
        },
    }

    @classmethod
    def get_style_for_program(cls, program_type: str) -> CommunicationStyle:
        """
        Obtiene el estilo base para un programa específico.

        Args:
            program_type: Tipo de programa (PRIME, LONGEVITY, etc.)

        Returns:
            CommunicationStyle: Estilo de comunicación base
        """
        program_type = program_type.upper()

        if program_type not in cls.BASE_STYLES:
            # Fallback a LONGEVITY para programas no definidos
            program_type = "LONGEVITY"

        return cls.BASE_STYLES[program_type]

    @classmethod
    def get_agent_adaptations(cls, agent_id: str, program_type: str) -> Dict[str, Any]:
        """
        Obtiene las adaptaciones específicas para un agente y programa.

        Args:
            agent_id: ID del agente (BLAZE, SAGE, etc.)
            program_type: Tipo de programa (PRIME, LONGEVITY, etc.)

        Returns:
            Dict[str, Any]: Adaptaciones específicas del agente
        """
        agent_id = agent_id.upper()
        program_type = program_type.upper()

        if agent_id not in cls.AGENT_ADAPTATIONS:
            return {}

        agent_adaptations = cls.AGENT_ADAPTATIONS[agent_id]

        if program_type not in agent_adaptations:
            # Fallback a LONGEVITY si no existe el programa específico
            program_type = (
                "LONGEVITY"
                if "LONGEVITY" in agent_adaptations
                else list(agent_adaptations.keys())[0]
            )

        return agent_adaptations.get(program_type, {})

    @classmethod
    def get_available_programs(cls) -> list[str]:
        """
        Obtiene la lista de programas disponibles.

        Returns:
            list[str]: Lista de tipos de programa
        """
        return list(cls.BASE_STYLES.keys())

    @classmethod
    def get_available_agents(cls) -> list[str]:
        """
        Obtiene la lista de agentes con adaptaciones específicas.

        Returns:
            list[str]: Lista de IDs de agente
        """
        return list(cls.AGENT_ADAPTATIONS.keys())
