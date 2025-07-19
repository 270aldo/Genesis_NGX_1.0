"""
Transformador de respuestas para adaptación de personalidad.

Este módulo implementa la lógica de transformación de respuestas genéricas
en comunicación ultra-personalizada según el programa del usuario.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from .communication_styles import CommunicationStyles, CommunicationStyle

logger = logging.getLogger(__name__)


@dataclass
class TransformationContext:
    """
    Contexto para la transformación de respuestas.
    """

    program_type: str
    agent_id: str
    user_context: Optional[Dict[str, Any]] = None
    session_context: Optional[Dict[str, Any]] = None
    emotional_state: Optional[str] = None
    interaction_history: Optional[List[Dict[str, Any]]] = None


class ResponseTransformer:
    """
    Transformador de respuestas que adapta mensajes según el programa del usuario.
    """

    def __init__(self):
        self.communication_styles = CommunicationStyles()
        self._transformation_cache: Dict[str, str] = {}

    def transform_response(
        self, original_message: str, context: TransformationContext
    ) -> str:
        """
        Transforma una respuesta original adaptándola al programa del usuario.

        Args:
            original_message: Mensaje original del agente
            context: Contexto de transformación

        Returns:
            str: Mensaje transformado según el programa
        """
        try:
            # Obtener estilo de comunicación
            base_style = self.communication_styles.get_style_for_program(
                context.program_type
            )
            agent_adaptations = self.communication_styles.get_agent_adaptations(
                context.agent_id, context.program_type
            )

            # Aplicar transformaciones en secuencia
            transformed_message = original_message

            # 1. Transformación de tono y estructura
            transformed_message = self._apply_tone_transformation(
                transformed_message, base_style, agent_adaptations
            )

            # 2. Adaptación de vocabulario
            transformed_message = self._apply_vocabulary_adaptation(
                transformed_message, base_style, agent_adaptations
            )

            # 3. Ajuste de estructura y formato
            transformed_message = self._apply_structural_adaptation(
                transformed_message, base_style, agent_adaptations, context
            )

            # 4. Aplicación de patrones específicos del agente
            transformed_message = self._apply_agent_patterns(
                transformed_message, agent_adaptations, context
            )

            # 5. Ajuste final de longitud y urgencia
            transformed_message = self._apply_final_adjustments(
                transformed_message, base_style, context
            )

            logger.info(
                f"Response transformed for {context.agent_id} - {context.program_type}"
            )
            return transformed_message

        except Exception as e:
            logger.error(f"Error transforming response: {e}")
            return original_message  # Fallback a mensaje original

    def _apply_tone_transformation(
        self, message: str, style: CommunicationStyle, adaptations: Dict[str, Any]
    ) -> str:
        """
        Aplica transformación de tono según el estilo de comunicación.
        """
        tone_modifiers = adaptations.get("tone_modifiers", {})

        # Ajustes específicos por tono
        if style.tone.value == "strategic_executive":
            # Tono ejecutivo: directo, orientado a resultados
            message = self._make_more_direct(message)
            message = self._add_result_orientation(message)

        elif style.tone.value == "consultive_educational":
            # Tono consultivo: educativo, supportivo
            message = self._make_more_explanatory(message)
            message = self._add_supportive_language(message)

        return message

    def _apply_vocabulary_adaptation(
        self, message: str, style: CommunicationStyle, adaptations: Dict[str, Any]
    ) -> str:
        """
        Adapta el vocabulario según el programa y agente.
        """
        # Vocabulario base del estilo
        base_vocabulary = (
            style.agent_specific_adaptations.get("vocabulary", {})
            if style.agent_specific_adaptations
            else {}
        )

        # Vocabulario específico del agente
        agent_vocabulary = adaptations.get("vocabulary_enhancements", [])

        # Términos preferidos y a evitar
        preferred_terms = base_vocabulary.get("preferred_terms", [])
        avoid_terms = base_vocabulary.get("avoid_terms", [])

        # Aplicar reemplazos de vocabulario
        message = self._replace_vocabulary(message, preferred_terms, avoid_terms)

        return message

    def _apply_structural_adaptation(
        self,
        message: str,
        style: CommunicationStyle,
        adaptations: Dict[str, Any],
        context: TransformationContext,
    ) -> str:
        """
        Adapta la estructura del mensaje según el estilo.
        """
        communication_patterns = (
            style.agent_specific_adaptations.get("communication_patterns", {})
            if style.agent_specific_adaptations
            else {}
        )

        # Ajustar según preferencia de longitud
        if style.response_length == "concise_strategic":
            message = self._make_more_concise(message)
        elif style.response_length == "detailed_explanatory":
            message = self._add_more_detail(message)

        # Aplicar estructura específica
        structure = communication_patterns.get("structure", "")
        if structure == "bullets_action_items":
            message = self._format_as_action_items(message)
        elif structure == "educational_step_by_step":
            message = self._format_as_steps(message)

        return message

    def _apply_agent_patterns(
        self, message: str, adaptations: Dict[str, Any], context: TransformationContext
    ) -> str:
        """
        Aplica patrones específicos del agente.
        """
        message_patterns = adaptations.get("message_patterns", {})

        # Detectar tipo de mensaje y aplicar patrón correspondiente
        if "entrenamiento" in message.lower() or "workout" in message.lower():
            pattern = message_patterns.get("workout_intro")
            if pattern:
                message = self._apply_pattern_template(message, pattern)

        elif "análisis" in message.lower() or "resultado" in message.lower():
            pattern = message_patterns.get("performance_feedback")
            if pattern:
                message = self._apply_pattern_template(message, pattern)

        elif "recuperación" in message.lower() or "recovery" in message.lower():
            pattern = message_patterns.get("recovery_guidance")
            if pattern:
                message = self._apply_pattern_template(message, pattern)

        return message

    def _apply_final_adjustments(
        self, message: str, style: CommunicationStyle, context: TransformationContext
    ) -> str:
        """
        Aplica ajustes finales según urgencia y contexto.
        """
        # Ajustar urgencia
        if style.urgency_level == "high_priority":
            message = self._add_urgency_indicators(message)
        elif style.urgency_level == "moderate_pace":
            message = self._add_calm_indicators(message)

        # Ajustar según estado emocional del usuario si está disponible
        if context.emotional_state:
            message = self._adjust_for_emotional_state(message, context.emotional_state)

        return message

    # Métodos auxiliares de transformación

    def _make_more_direct(self, message: str) -> str:
        """Hace el mensaje más directo y ejecutivo."""
        # Eliminar palabras de relleno
        filler_words = ["tal vez", "quizás", "posiblemente", "podríamos"]
        for word in filler_words:
            message = message.replace(word, "")

        # Hacer afirmaciones más directas
        message = re.sub(r"Podrías considerar", "Implementa", message)
        message = re.sub(r"Sería bueno si", "Necesitas", message)

        return message.strip()

    def _add_result_orientation(self, message: str) -> str:
        """Añade orientación a resultados."""
        if "beneficio" in message.lower():
            message = re.sub(r"beneficio", "ROI directo", message, flags=re.IGNORECASE)
        return message

    def _make_more_explanatory(self, message: str) -> str:
        """Hace el mensaje más explicativo y educativo."""
        # Añadir contexto educativo
        if not message.startswith(("Esto", "Esta", "El", "La")):
            message = "Te explico: " + message

        return message

    def _add_supportive_language(self, message: str) -> str:
        """Añade lenguaje más supportivo."""
        supportive_phrases = [
            "Vamos juntos en este proceso",
            "Cada paso cuenta para tu bienestar",
            "Tu progreso es valioso",
        ]

        # Añadir aleatoriamente una frase supportiva
        import random

        if random.random() < 0.3:  # 30% de probabilidad
            phrase = random.choice(supportive_phrases)
            message = f"{message} {phrase}."

        return message

    def _replace_vocabulary(
        self, message: str, preferred_terms: List[str], avoid_terms: List[str]
    ) -> str:
        """Reemplaza vocabulario según preferencias."""
        # Diccionario de reemplazos
        replacements = {
            # Para PRIME
            "ejercicio": "protocolo de optimización",
            "rutina": "sistema estratégico",
            "descanso": "recuperación acelerada",
            # Para LONGEVITY
            "intenso": "gradual",
            "agresivo": "progresivo",
            "rápido": "sostenible",
        }

        for old_term, new_term in replacements.items():
            if old_term in avoid_terms:
                message = re.sub(old_term, new_term, message, flags=re.IGNORECASE)

        return message

    def _make_more_concise(self, message: str) -> str:
        """Hace el mensaje más conciso."""
        # Eliminar oraciones redundantes
        sentences = message.split(". ")
        if len(sentences) > 3:
            # Mantener las 3 primeras oraciones más impactantes
            message = ". ".join(sentences[:3]) + "."

        return message

    def _add_more_detail(self, message: str) -> str:
        """Añade más detalle explicativo."""
        # Si el mensaje es muy corto, añadir contexto
        if len(message) < 100:
            message += " Te explico el contexto: este enfoque está basado en evidencia científica y se adapta específicamente a tus necesidades."

        return message

    def _format_as_action_items(self, message: str) -> str:
        """Formatea como bullets de acción."""
        # Identificar acciones y formatear
        sentences = message.split(". ")
        if len(sentences) > 1:
            formatted = "**Acciones clave:**\n"
            for i, sentence in enumerate(sentences[:3], 1):
                if sentence.strip():
                    formatted += f"• {sentence.strip()}\n"
            return formatted
        return message

    def _format_as_steps(self, message: str) -> str:
        """Formatea como pasos educativos."""
        sentences = message.split(". ")
        if len(sentences) > 1:
            formatted = "**Proceso paso a paso:**\n"
            for i, sentence in enumerate(sentences[:4], 1):
                if sentence.strip():
                    formatted += f"{i}. {sentence.strip()}\n"
            return formatted
        return message

    def _apply_pattern_template(self, message: str, pattern: str) -> str:
        """Aplica un patrón de template específico."""
        # Por ahora, retorna el patrón como prefijo
        # En una implementación más avanzada, se extraerían variables del mensaje original
        return f"{pattern} {message}"

    def _add_urgency_indicators(self, message: str) -> str:
        """Añade indicadores de urgencia."""
        urgency_prefixes = [
            "**Acción inmediata:**",
            "**Protocolo prioritario:**",
            "**Implementación estratégica:**",
        ]

        import random

        prefix = random.choice(urgency_prefixes)
        return f"{prefix} {message}"

    def _add_calm_indicators(self, message: str) -> str:
        """Añade indicadores de calma."""
        calm_prefixes = ["Con tranquilidad:", "Paso a paso:", "Progresivamente:"]

        import random

        prefix = random.choice(calm_prefixes)
        return f"{prefix} {message}"

    def _adjust_for_emotional_state(self, message: str, emotional_state: str) -> str:
        """Ajusta el mensaje según el estado emocional."""
        if emotional_state == "stressed":
            message = f"Entiendo que puede ser un momento desafiante. {message}"
        elif emotional_state == "motivated":
            message = f"Veo tu energía positiva! {message}"
        elif emotional_state == "frustrated":
            message = f"Es normal sentir esto en el proceso. {message}"

        return message
