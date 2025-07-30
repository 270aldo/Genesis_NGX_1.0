#!/usr/bin/env python3
"""
Debug keyword matching
"""

# Expected behaviors and keywords from test
behavior_keywords = {
    "validate_effort": ["esfuerzo", "has trabajado", "dedicación", "compromiso"],
    "review_adherence_data": ["revisar", "historial", "datos", "cumplido"],
    "identify_potential_issues": ["identificado", "puede", "podría", "afectando"],
    "explain_realistic_timeline": ["semanas", "tiempo", "paciencia", "cambios sostenibles"]
}

# Responses from the mock
responses = [
    """Entiendo tu frustración completamente. Comprendo lo difícil que debe ser esta situación para ti. 
    Revisemos juntos qué cambios podemos hacer para personalizar tu experiencia. Podemos ajustar cualquier aspecto del plan.""",
    
    """Los estancamientos son temporales. Tu cuerpo es eficiente y se adapta. Necesitamos 'confundirlo' con nuevos estímulos para reactivar el progreso. 
    Cambiemos el enfoque: si hacías pesas 4x1, probemos con circuitos metabólicos 3x1 + 2 días de HIIT. 
    El progreso no es solo la báscula: ¿Cómo te queda la ropa? ¿Has tomado fotos de progreso? 
    No te desanimes - esto es parte normal del viaje. Los mejores resultados vienen después de superar estos momentos. 
    Hagamos una semana de descarga (50% volumen) seguida de un nuevo mesociclo con mayor intensidad.""",
    
    """Comprendo perfectamente tu frustración. Entiendo que esto es muy difícil y frustrante para ti. 
    Revisemos juntos qué cambios podemos hacer para personalizar tu experiencia. Podemos ajustar cualquier aspecto del plan."""
]

# Check keywords
print("=== Checking Keywords ===\n")
combined_response = " ".join(responses).lower()

for behavior, keywords in behavior_keywords.items():
    found = [kw for kw in keywords if kw in combined_response]
    missing = [kw for kw in keywords if kw not in combined_response]
    print(f"{behavior}:")
    print(f"  Found: {found}")
    print(f"  Missing: {missing}")
    print(f"  Status: {'✓' if found else '✗'}")
    print()