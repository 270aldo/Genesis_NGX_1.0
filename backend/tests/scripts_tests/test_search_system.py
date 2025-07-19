#!/usr/bin/env python3
"""
Script de prueba para el sistema de búsqueda de NGX Agents.

Verifica que la búsqueda de texto completo funcione correctamente
con Supabase.

Uso:
    python scripts/test_search_system.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from core.search_manager import search_manager
from clients.supabase_client import supabase_client
from core.logging_config import get_logger

logger = get_logger(__name__)


async def create_test_data():
    """Crea datos de prueba en las tablas."""
    print("\n📝 Creando datos de prueba...")

    # Inicializar cliente Supabase
    await supabase_client.initialize()

    # Usuario de prueba (usar el tuyo real o crear uno de prueba)
    test_user_id = "550e8400-e29b-41d4-a716-446655440000"  # UUID de ejemplo

    try:
        # Insertar conversaciones de prueba
        conversations = [
            {
                "user_id": test_user_id,
                "session_id": "550e8400-e29b-41d4-a716-446655440001",
                "user_message": "¿Cuál es el mejor ejercicio para ganar masa muscular?",
                "agent_response": "Los mejores ejercicios para ganar masa muscular son los compuestos como sentadillas, peso muerto, press de banca y dominadas.",
                "agent_name": "Elite Training Strategist",
                "intent": "training_advice",
                "confidence": 0.95,
            },
            {
                "user_id": test_user_id,
                "session_id": "550e8400-e29b-41d4-a716-446655440001",
                "user_message": "¿Cuánta proteína debo consumir al día?",
                "agent_response": "Para ganar masa muscular, se recomienda consumir entre 1.6 a 2.2 gramos de proteína por kilogramo de peso corporal.",
                "agent_name": "Precision Nutrition Architect",
                "intent": "nutrition_advice",
                "confidence": 0.92,
            },
        ]

        # Insertar planes de entrenamiento
        training_plans = [
            {
                "user_id": test_user_id,
                "name": "Plan de Fuerza para Principiantes",
                "description": "Un programa de 12 semanas diseñado para construir una base sólida de fuerza",
                "exercises": json.dumps(
                    [
                        {"name": "Sentadilla", "sets": 3, "reps": 8},
                        {"name": "Press de banca", "sets": 3, "reps": 8},
                        {"name": "Peso muerto", "sets": 3, "reps": 6},
                    ]
                ),
                "difficulty": "beginner",
                "duration_weeks": 12,
                "goal": "strength",
            }
        ]

        # Insertar registros de nutrición
        nutrition_logs = [
            {
                "user_id": test_user_id,
                "meal_name": "Desayuno rico en proteínas",
                "meal_type": "breakfast",
                "foods": json.dumps(["3 huevos", "1 taza de avena", "1 plátano"]),
                "calories": 450,
                "protein": 25,
                "carbs": 55,
                "fats": 15,
                "logged_at": datetime.now().isoformat(),
            }
        ]

        # Insertar métricas de progreso
        progress_metrics = [
            {
                "user_id": test_user_id,
                "metric_name": "Peso corporal",
                "value": 75.5,
                "unit": "kg",
                "category": "weight",
                "notes": "Peso matutino en ayunas",
                "recorded_at": datetime.now().isoformat(),
            },
            {
                "user_id": test_user_id,
                "metric_name": "Sentadilla 1RM",
                "value": 100,
                "unit": "kg",
                "category": "performance",
                "notes": "Nuevo récord personal en sentadilla",
                "recorded_at": datetime.now().isoformat(),
            },
        ]

        # Insertar notas del usuario
        user_notes = [
            {
                "user_id": test_user_id,
                "title": "Objetivos de entrenamiento 2025",
                "content": "Quiero lograr 100kg en press de banca y mejorar mi flexibilidad",
                "category": "goals",
                "tags": json.dumps(["objetivos", "2025", "fuerza"]),
            }
        ]

        # Insertar datos
        print(
            "✅ Datos de prueba creados (simulación - verificar si las tablas existen en Supabase)"
        )

        # En un entorno real, insertarías los datos así:
        # await supabase_client.table("conversations").insert(conversations).execute()
        # await supabase_client.table("training_plans").insert(training_plans).execute()
        # etc.

        return test_user_id

    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        return None


async def test_search_functionality(user_id: str):
    """Prueba las diferentes funcionalidades de búsqueda."""
    print("\n🔍 Probando sistema de búsqueda...")

    # Inicializar el gestor de búsqueda
    await search_manager.initialize()

    # Test 1: Búsqueda en conversaciones
    print("\n1️⃣ Búsqueda en conversaciones:")
    try:
        results = await search_manager.search(
            query="proteína", search_type="conversations", user_id=user_id, limit=5
        )
        print(f"   Encontrados {results['total_results']} resultados")
        for result_group in results["results"]:
            for item in result_group["results"][:2]:
                print(f"   - {item.get('user_message', '')[:60]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: Búsqueda en planes de entrenamiento
    print("\n2️⃣ Búsqueda en planes de entrenamiento:")
    try:
        results = await search_manager.search(
            query="fuerza principiantes",
            search_type="training_plans",
            user_id=user_id,
            limit=5,
        )
        print(f"   Encontrados {results['total_results']} resultados")
        for result_group in results["results"]:
            for item in result_group["results"]:
                print(
                    f"   - {item.get('name', '')}: {item.get('description', '')[:50]}..."
                )
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Búsqueda global
    print("\n3️⃣ Búsqueda global (todos los tipos):")
    try:
        results = await search_manager.search(
            query="sentadilla", search_type="all", user_id=user_id, limit=10
        )
        print(f"   Encontrados {results['total_results']} resultados totales")
        for result_group in results["results"]:
            if result_group["results"]:
                print(
                    f"   📁 {result_group['type']}: {len(result_group['results'])} resultados"
                )
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 4: Sugerencias de búsqueda
    print("\n4️⃣ Sugerencias de búsqueda:")
    try:
        suggestions = await search_manager.get_search_suggestions(
            partial_query="prot", search_type="all", user_id=user_id, limit=5
        )
        print(f"   Sugerencias para 'prot': {suggestions}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 5: Búsqueda con filtros
    print("\n5️⃣ Búsqueda con filtros:")
    try:
        results = await search_manager.search(
            query="peso",
            search_type="progress_metrics",
            user_id=user_id,
            limit=5,
            filters={"category": "weight"},
        )
        print(f"   Encontrados {results['total_results']} resultados de peso")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 6: Estadísticas
    print("\n6️⃣ Estadísticas del sistema:")
    try:
        stats = await search_manager.get_stats()
        print(f"   - Búsquedas realizadas: {stats['stats']['searches_performed']}")
        print(f"   - Resultados devueltos: {stats['stats']['results_returned']}")
        print(f"   - Tipos disponibles: {', '.join(stats['search_types_available'])}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def test_api_endpoints():
    """Prueba los endpoints de la API de búsqueda."""
    print("\n🌐 Probando endpoints de API...")

    # Este test requeriría un servidor corriendo
    # Por ahora solo mostramos los endpoints disponibles

    endpoints = [
        "POST /search/ - Búsqueda principal",
        "GET /search/quick?q=texto - Búsqueda rápida",
        "POST /search/suggestions - Obtener sugerencias",
        "GET /search/types - Tipos de búsqueda disponibles",
        "GET /search/stats - Estadísticas (admin)",
        "POST /search/reindex - Reindexar (admin)",
    ]

    print("   Endpoints disponibles:")
    for endpoint in endpoints:
        print(f"   - {endpoint}")

    print("\n   Para probar los endpoints, ejecuta el servidor con:")
    print("   make dev")
    print("   Y luego usa curl o Postman para probar")


async def main():
    """Función principal de prueba."""
    print("🚀 Iniciando pruebas del sistema de búsqueda NGX Agents\n")

    # Crear datos de prueba
    user_id = await create_test_data()

    if user_id:
        # Probar funcionalidad de búsqueda
        await test_search_functionality(user_id)

    # Información sobre endpoints
    await test_api_endpoints()

    print("\n✅ Pruebas completadas!")
    print("\n📝 Notas importantes:")
    print("1. Asegúrate de ejecutar el script SQL en Supabase primero")
    print("2. Los datos de prueba deben insertarse manualmente en Supabase")
    print("3. Configura las variables de entorno correctamente")
    print("4. Para búsqueda en español, ajusta los índices a 'spanish' en el SQL")


if __name__ == "__main__":
    asyncio.run(main())
