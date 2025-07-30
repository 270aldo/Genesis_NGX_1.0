#!/usr/bin/env python3
"""
Script to add missing behavior patterns to test validation
"""

missing_patterns = {
    "validate_feelings": ["válidos", "válido", "es normal sentir", "normal sentir"],
    "focus_on_health_not_appearance": ["salud", "cómo te sientes", "no solo en cómo te ves", "bienestar"],
    "step_by_step_instructions": ["paso a paso", "paso 1", "primero", "te guiaré paso"],
    "offer_visual_help": ["capturas", "video", "imágenes", "envío capturas"],
    "simplify_language": ["simple", "sencilla", "otra manera", "simplificar"],
    "offer_human_support": ["equipo de soporte", "especialista", "te llame", "hablar con alguien"],
    "express_empathy": ["lamento", "siento que", "frustrante que", "sé lo frustrante"],
    "adapt_plan_for_injury": ["adaptar", "evitar", "modificaré", "trabajar alrededor"],
    "suggest_alternative_exercises": ["mientras", "alternativas", "ejercicios", "en lugar"],
    "focus_on_recovery": ["recuperación", "prioridad", "rehabilitación", "descanso"],
    "maintain_motivation": ["temporal", "volverás", "más fuerte", "muchos atletas"],
    "review_adherence_data": ["revisar", "historial", "datos", "cumplido"],
    "suggest_adjustments": ["ajustar", "sugiero", "ajustes", "cambiar"],
    "identify_potential_issues": ["identificado", "puede", "podría", "afectando"],
    "explain_realistic_timeline": ["semanas", "tiempo", "paciencia", "cambios sostenibles"],
    "acknowledge_concern": ["entiendo", "preocupación", "comprendo", "consideración"],
    "highlight_value": ["recibes", "incluye", "menos de", "por día"],
    "no_pressure_tactics": ["no hay presión", "toma el tiempo", "sin presión"],
    "respect_decision": ["respeto", "decisión", "completamente"],
    "acknowledge_challenge": ["agotador", "comprendo", "desafío", "entiendo que"],
    "offer_time_efficient_solutions": ["rutinas de", "minutos", "eficiente", "máximo resultado"],
    "micro_workout_options": ["minutos", "micro", "ejercicio", "mientras"],
    "prioritize_essentials": ["esencial", "priorizar", "enfoquémonos", "lo más importante"],
    "flexible_scheduling": ["flexible", "cuando puedas", "tú decides"],
    "address_comparison_trap": ["redes sociales", "trampa", "compararte", "instagram"],
    "celebrate_small_wins": ["victoria", "logros", "celebrar", "triunfo"],
    "provide_perspective": ["recuerda", "nadie publica", "transformaciones"],
    "suggest_social_media_limits": ["limitar", "detox", "dejar de seguir"],
    "focus_on_personal_journey": ["tu viaje", "tu progreso", "único"],
    "explain_plateau_science": ["plateau", "metabolismo", "adapta", "normal"],
    "suggest_plan_variations": ["variación", "cambiar", "periodización", "nuevo"],
    "review_other_progress_markers": ["otros indicadores", "fuerza", "resistencia", "medidas"],
    "maintain_hope": ["temporal", "superaremos", "confía", "no te desanimes"],
    "strategic_adjustments": ["refeed", "descarga", "mesociclo", "déficit"],
    "set_boundaries_respectfully": ["respeto mutuo", "comunicación respetuosa", "trabajemos juntos"],
    "remain_professional": ["objetivo es ayudarte", "constructiva", "respeto"],
    "de_escalate_situation": ["respirar", "centrémonos", "momento", "calma"],
    "document_interaction": ["registrado", "documentada", "tomado nota"],
    "offer_alternatives": ["alternativa", "opción", "también puede", "otra forma"]
}

# Print as Python code to paste
print("# Add these to the behavior_patterns dictionary in _analyze_response:")
for behavior, patterns in missing_patterns.items():
    print(f'            "{behavior}": {patterns},')