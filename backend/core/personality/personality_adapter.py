"""
Adaptador de personalidad principal para comunicación ultra-personalizada.

Este módulo implementa la clase principal PersonalityAdapter que orquesta
toda la transformación de personalidad basada en el programa del usuario.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from .communication_styles import CommunicationStyles
from .response_transformer import ResponseTransformer, TransformationContext
from ..telemetry import get_tracer

logger = logging.getLogger(__name__)


@dataclass
class PersonalityProfile:
    """
    Perfil de personalidad completo para un usuario.
    """

    program_type: str
    age: Optional[int] = None
    preferences: Optional[Dict[str, Any]] = None
    communication_history: Optional[List[Dict[str, Any]]] = None
    emotional_patterns: Optional[Dict[str, Any]] = None
    engagement_metrics: Optional[Dict[str, Any]] = None


@dataclass
class AdaptationMetrics:
    """
    Métricas de la adaptación realizada.
    """

    original_length: int
    transformed_length: int
    transformation_type: str
    adaptations_applied: List[str]
    confidence_score: float
    processing_time_ms: float


class PersonalityAdapter:
    """
    Adaptador principal que transforma respuestas de agentes según la personalidad
    y programa del usuario para crear comunicación ultra-personalizada.
    """

    def __init__(self):
        self.communication_styles = CommunicationStyles()
        self.response_transformer = ResponseTransformer()
        self._adaptation_cache: Dict[str, Dict[str, Any]] = {}
        self._metrics_history: List[AdaptationMetrics] = []
        self.tracer = get_tracer("personality_adapter")

    def adapt_response(
        self,
        agent_id: str,
        original_message: str,
        user_profile: PersonalityProfile,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Adapta una respuesta de agente según el perfil de personalidad del usuario.

        Args:
            agent_id: ID del agente que genera la respuesta
            original_message: Mensaje original del agente
            user_profile: Perfil de personalidad del usuario
            context: Contexto adicional de la conversación

        Returns:
            Dict con el mensaje adaptado y métricas de transformación
        """
        import time

        start_time = time.time()

        try:
            # Crear contexto de transformación
            transformation_context = TransformationContext(
                program_type=user_profile.program_type,
                agent_id=agent_id,
                user_context=asdict(user_profile),
                session_context=context,
                emotional_state=self._detect_emotional_state(user_profile),
                interaction_history=user_profile.communication_history,
            )

            # Validar inputs
            self._validate_inputs(agent_id, original_message, user_profile)

            # Verificar caché
            cache_key = self._generate_cache_key(
                agent_id, original_message, user_profile.program_type
            )

            if cache_key in self._adaptation_cache:
                logger.info(f"Using cached adaptation for {agent_id}")
                cached_result = self._adaptation_cache[cache_key]
                cached_result["from_cache"] = True
                return cached_result

            # Aplicar transformación
            adapted_message = self.response_transformer.transform_response(
                original_message, transformation_context
            )

            # Calcular métricas
            processing_time = (time.time() - start_time) * 1000
            adaptations_applied = self._identify_adaptations_applied(
                original_message, adapted_message, transformation_context
            )

            metrics = AdaptationMetrics(
                original_length=len(original_message),
                transformed_length=len(adapted_message),
                transformation_type=f"{agent_id}_{user_profile.program_type}",
                adaptations_applied=adaptations_applied,
                confidence_score=self._calculate_confidence_score(
                    original_message, adapted_message
                ),
                processing_time_ms=processing_time,
            )

            # Almacenar métricas
            self._metrics_history.append(metrics)

            # Resultado completo
            result = {
                "adapted_message": adapted_message,
                "original_message": original_message,
                "program_type": user_profile.program_type,
                "agent_id": agent_id,
                "adaptation_metrics": asdict(metrics),
                "style_applied": self._get_style_summary(transformation_context),
                "from_cache": False,
            }

            # Guardar en caché
            self._adaptation_cache[cache_key] = result

            logger.info(
                f"Personality adaptation completed for {agent_id} - {user_profile.program_type}. "
                f"Confidence: {metrics.confidence_score:.2f}, Time: {processing_time:.2f}ms"
            )

            return result

        except Exception as e:
            logger.error(f"Error in personality adaptation: {e}")
            # Fallback: retornar mensaje original con métricas de error
            return {
                "adapted_message": original_message,
                "original_message": original_message,
                "program_type": user_profile.program_type,
                "agent_id": agent_id,
                "adaptation_metrics": {"error": str(e), "fallback_used": True},
                "style_applied": "fallback",
                "from_cache": False,
            }

    def get_personality_preview(
        self,
        agent_id: str,
        program_type: str,
        sample_message: str = "Este es un ejemplo de respuesta del agente.",
    ) -> Dict[str, Any]:
        """
        Genera una vista previa de cómo se adapta la personalidad para un agente y programa.

        Args:
            agent_id: ID del agente
            program_type: Tipo de programa (PRIME, LONGEVITY, etc.)
            sample_message: Mensaje de ejemplo para transformar

        Returns:
            Dict con la vista previa de adaptación
        """
        try:
            # Crear perfil de ejemplo
            sample_profile = PersonalityProfile(program_type=program_type)

            # Adaptar mensaje de ejemplo
            result = self.adapt_response(
                agent_id=agent_id,
                original_message=sample_message,
                user_profile=sample_profile,
            )

            # Obtener detalles del estilo
            style = self.communication_styles.get_style_for_program(program_type)
            adaptations = self.communication_styles.get_agent_adaptations(
                agent_id, program_type
            )

            return {
                "agent_id": agent_id,
                "program_type": program_type,
                "original_sample": sample_message,
                "adapted_sample": result["adapted_message"],
                "style_details": {
                    "tone": style.tone.value,
                    "language_level": style.language_level.value,
                    "focus_area": style.focus_area.value,
                    "response_length": style.response_length,
                    "urgency_level": style.urgency_level,
                },
                "agent_adaptations": adaptations,
                "transformation_summary": result["adaptation_metrics"],
            }

        except Exception as e:
            logger.error(f"Error generating personality preview: {e}")
            return {"error": str(e)}

    def analyze_adaptation_performance(self) -> Dict[str, Any]:
        """
        Analiza el rendimiento de las adaptaciones realizadas.

        Returns:
            Dict con estadísticas de rendimiento
        """
        if not self._metrics_history:
            return {"message": "No hay métricas disponibles"}

        # Calcular estadísticas
        total_adaptations = len(self._metrics_history)
        avg_confidence = (
            sum(m.confidence_score for m in self._metrics_history) / total_adaptations
        )
        avg_processing_time = (
            sum(m.processing_time_ms for m in self._metrics_history) / total_adaptations
        )

        # Adaptaciones por tipo
        transformation_types = {}
        for metric in self._metrics_history:
            t_type = metric.transformation_type
            if t_type not in transformation_types:
                transformation_types[t_type] = 0
            transformation_types[t_type] += 1

        # Adaptaciones más comunes
        all_adaptations = []
        for metric in self._metrics_history:
            all_adaptations.extend(metric.adaptations_applied)

        adaptation_frequency = {}
        for adaptation in all_adaptations:
            if adaptation not in adaptation_frequency:
                adaptation_frequency[adaptation] = 0
            adaptation_frequency[adaptation] += 1

        return {
            "total_adaptations": total_adaptations,
            "average_confidence": round(avg_confidence, 3),
            "average_processing_time_ms": round(avg_processing_time, 2),
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "transformation_types": transformation_types,
            "most_common_adaptations": sorted(
                adaptation_frequency.items(), key=lambda x: x[1], reverse=True
            )[:10],
            "performance_grade": self._calculate_performance_grade(
                avg_confidence, avg_processing_time
            ),
        }

    def clear_cache(self) -> None:
        """Limpia el caché de adaptaciones."""
        self._adaptation_cache.clear()
        logger.info("Personality adaptation cache cleared")

    def get_supported_combinations(self) -> Dict[str, List[str]]:
        """
        Obtiene las combinaciones soportadas de agente-programa.

        Returns:
            Dict con agentes y sus programas soportados
        """
        programs = self.communication_styles.get_available_programs()
        agents = self.communication_styles.get_available_agents()

        combinations = {}
        for agent in agents:
            combinations[agent] = programs

        # Todos los agentes soportan todos los programas con fallback
        all_agents = [
            "NEXUS",
            "BLAZE",
            "SAGE",
            "SPARK",
            "VOLT",
            "STELLA",
            "WAVE",
            "CODE",
            "NOVA",
            "GUARDIAN",
            "NODE",
            "AURA",
            "LUNA",
        ]

        for agent in all_agents:
            if agent not in combinations:
                combinations[agent] = programs

        return combinations

    # Métodos auxiliares privados

    def _validate_inputs(
        self, agent_id: str, message: str, profile: PersonalityProfile
    ) -> None:
        """Valida los inputs de entrada."""
        if not agent_id or not agent_id.strip():
            raise ValueError("agent_id no puede estar vacío")

        if not message or not message.strip():
            raise ValueError("mensaje no puede estar vacío")

        if not profile.program_type:
            raise ValueError("program_type es requerido en el perfil")

    def _generate_cache_key(
        self, agent_id: str, message: str, program_type: str
    ) -> str:
        """Genera una clave de caché para la adaptación."""
        import hashlib

        content = f"{agent_id}_{program_type}_{message[:100]}"
        return hashlib.md5(content.encode()).hexdigest()

    def _detect_emotional_state(self, profile: PersonalityProfile) -> Optional[str]:
        """Detecta el estado emocional del usuario basado en su perfil."""
        if not profile.emotional_patterns:
            return None

        # Lógica simple de detección emocional
        patterns = profile.emotional_patterns

        if patterns.get("stress_level", 0) > 7:
            return "stressed"
        elif patterns.get("motivation_level", 0) > 8:
            return "motivated"
        elif patterns.get("frustration_level", 0) > 6:
            return "frustrated"
        else:
            return "neutral"

    def _identify_adaptations_applied(
        self, original: str, adapted: str, context: TransformationContext
    ) -> List[str]:
        """Identifica qué adaptaciones se aplicaron."""
        adaptations = []

        # Detectar cambios en longitud
        if len(adapted) < len(original) * 0.8:
            adaptations.append("length_reduction")
        elif len(adapted) > len(original) * 1.2:
            adaptations.append("length_expansion")

        # Detectar cambios de vocabulario
        if "ROI" in adapted and "ROI" not in original:
            adaptations.append("executive_vocabulary")
        if "bienestar" in adapted and "bienestar" not in original:
            adaptations.append("wellness_vocabulary")

        # Detectar cambios estructurales
        if "**" in adapted and "**" not in original:
            adaptations.append("formatting_enhancement")
        if "•" in adapted and "•" not in original:
            adaptations.append("bullet_formatting")

        # Detectar adaptaciones de tono
        if context.program_type == "PRIME":
            if any(
                word in adapted.lower()
                for word in ["estratégico", "optimización", "protocolo"]
            ):
                adaptations.append("executive_tone")
        elif context.program_type == "LONGEVITY":
            if any(
                word in adapted.lower()
                for word in ["gradual", "sostenible", "bienestar"]
            ):
                adaptations.append("wellness_tone")

        return adaptations

    def _calculate_confidence_score(self, original: str, adapted: str) -> float:
        """Calcula un score de confianza para la adaptación."""
        # Score basado en diferencias significativas pero no extremas
        length_ratio = len(adapted) / len(original) if original else 0

        # Score óptimo si la longitud está entre 80% y 150% del original
        if 0.8 <= length_ratio <= 1.5:
            base_score = 0.8
        else:
            base_score = 0.6

        # Bonus por estructura mejorada
        if "**" in adapted or "•" in adapted:
            base_score += 0.1

        # Bonus por adaptación de vocabulario
        specialized_terms = ["ROI", "protocolo", "bienestar", "optimización"]
        if any(term in adapted for term in specialized_terms):
            base_score += 0.1

        return min(1.0, base_score)

    def _get_style_summary(self, context: TransformationContext) -> Dict[str, str]:
        """Obtiene un resumen del estilo aplicado."""
        style = self.communication_styles.get_style_for_program(context.program_type)

        return {
            "tone": style.tone.value,
            "focus": style.focus_area.value,
            "urgency": style.urgency_level,
            "length": style.response_length,
        }

    def _calculate_cache_hit_rate(self) -> float:
        """Calcula la tasa de aciertos del caché."""
        if not self._metrics_history:
            return 0.0

        # Esta es una implementación simplificada
        # En producción, se trackearía por separado
        return 0.15  # Estimación conservadora del 15%

    def _calculate_performance_grade(
        self, avg_confidence: float, avg_processing_time: float
    ) -> str:
        """Calcula una calificación de rendimiento."""
        # Criterios: confianza > 0.8 y tiempo < 50ms = A
        if avg_confidence > 0.8 and avg_processing_time < 50:
            return "A"
        elif avg_confidence > 0.7 and avg_processing_time < 100:
            return "B"
        elif avg_confidence > 0.6 and avg_processing_time < 200:
            return "C"
        else:
            return "D"
    
    def get_error_response(self, error_type: str, personality_type: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a personality-appropriate error response.
        
        Args:
            error_type: Type of error that occurred
            personality_type: User's personality type (PRIME/LONGEVITY)
            context: Additional context about the error
            
        Returns:
            str: Personality-adapted error message
        """
        base_messages = {
            "connection": "Estamos experimentando problemas de conexión.",
            "timeout": "La operación tardó más de lo esperado.",
            "validation": "Los datos proporcionados necesitan ajustes.",
            "server": "Encontramos un problema técnico.",
            "default": "Algo no salió como esperábamos."
        }
        
        base_message = base_messages.get(error_type, base_messages["default"])
        
        if personality_type == "PRIME":
            # Direct, solution-focused error messages
            solutions = {
                "connection": "Verificando sistemas alternativos para procesar tu solicitud.",
                "timeout": "Optimizando el proceso para una respuesta más rápida.",
                "validation": "Por favor, verifica los datos para continuar con eficiencia.",
                "server": "Activando protocolo de recuperación. Tiempo estimado: 30 segundos.",
                "default": "Implementando solución alternativa inmediatamente."
            }
            
            return f"{base_message} {solutions.get(error_type, solutions['default'])}"
            
        elif personality_type == "LONGEVITY":
            # Empathetic, reassuring error messages
            reassurances = {
                "connection": "No te preocupes, esto sucede ocasionalmente. Estamos aquí para ayudarte.",
                "timeout": "Tómate un momento mientras procesamos tu solicitud con cuidado.",
                "validation": "Revisemos juntos la información para asegurar los mejores resultados.",
                "server": "Estamos trabajando para resolver esto. Tu bienestar es nuestra prioridad.",
                "default": "Todo está bien, solo necesitamos un momento para ajustar las cosas."
            }
            
            return f"{base_message} {reassurances.get(error_type, reassurances['default'])}"
        
        else:
            # Neutral error message
            return f"{base_message} Por favor, intenta nuevamente o contacta soporte si el problema persiste."
