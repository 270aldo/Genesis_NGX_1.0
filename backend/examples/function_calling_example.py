#!/usr/bin/env python3
"""
Ejemplo de uso de Function Calling y Grounding con Vertex AI.

Este ejemplo muestra cómo implementar function calling para que los agentes
puedan interactuar con APIs externas y bases de datos.
"""

import asyncio
import json
from typing import Dict, Any, List
from clients.vertex_ai.client import VertexAIClient


# Definir funciones disponibles para el modelo
AVAILABLE_FUNCTIONS = [
    {
        "name": "get_user_fitness_data",
        "description": "Obtiene datos de fitness del usuario como peso, altura, actividad física",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "ID del usuario"
                },
                "metric_type": {
                    "type": "string",
                    "description": "Tipo de métrica: weight, height, activity, heart_rate",
                    "enum": ["weight", "height", "activity", "heart_rate"]
                },
                "date_range": {
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string", "format": "date"},
                        "end_date": {"type": "string", "format": "date"}
                    }
                }
            },
            "required": ["user_id", "metric_type"]
        }
    },
    {
        "name": "calculate_calories",
        "description": "Calcula las calorías quemadas basándose en la actividad física",
        "parameters": {
            "type": "object",
            "properties": {
                "activity_type": {
                    "type": "string",
                    "description": "Tipo de actividad: running, walking, cycling, swimming"
                },
                "duration_minutes": {
                    "type": "number",
                    "description": "Duración de la actividad en minutos"
                },
                "user_weight_kg": {
                    "type": "number",
                    "description": "Peso del usuario en kilogramos"
                }
            },
            "required": ["activity_type", "duration_minutes", "user_weight_kg"]
        }
    },
    {
        "name": "search_nutrition_info",
        "description": "Busca información nutricional de alimentos",
        "parameters": {
            "type": "object",
            "properties": {
                "food_name": {
                    "type": "string",
                    "description": "Nombre del alimento a buscar"
                },
                "portion_size": {
                    "type": "string",
                    "description": "Tamaño de la porción (e.g., '100g', '1 cup')"
                }
            },
            "required": ["food_name"]
        }
    }
]


# Implementación simulada de las funciones
async def get_user_fitness_data(user_id: str, metric_type: str, date_range: Dict = None) -> Dict[str, Any]:
    """Simula obtener datos de fitness del usuario."""
    # En producción, esto consultaría una base de datos real
    mock_data = {
        "weight": {"value": 75.5, "unit": "kg", "timestamp": "2024-01-15"},
        "height": {"value": 175, "unit": "cm", "timestamp": "2024-01-01"},
        "activity": {"steps": 8500, "calories": 350, "distance_km": 6.2},
        "heart_rate": {"resting": 65, "average": 78, "max": 145}
    }
    
    return {
        "user_id": user_id,
        "metric_type": metric_type,
        "data": mock_data.get(metric_type, {}),
        "date_range": date_range
    }


async def calculate_calories(activity_type: str, duration_minutes: float, user_weight_kg: float) -> Dict[str, Any]:
    """Calcula calorías quemadas basándose en METs (Metabolic Equivalent of Task)."""
    # METs aproximados por actividad
    mets = {
        "running": 9.8,
        "walking": 3.5,
        "cycling": 7.5,
        "swimming": 8.0
    }
    
    met_value = mets.get(activity_type, 5.0)
    calories = met_value * user_weight_kg * (duration_minutes / 60)
    
    return {
        "activity_type": activity_type,
        "duration_minutes": duration_minutes,
        "calories_burned": round(calories, 1),
        "met_value": met_value
    }


async def search_nutrition_info(food_name: str, portion_size: str = "100g") -> Dict[str, Any]:
    """Busca información nutricional de alimentos."""
    # En producción, esto consultaría una API de nutrición real
    mock_nutrition = {
        "apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "fiber": 2.4},
        "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0},
        "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "fiber": 0.4},
        "broccoli": {"calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4, "fiber": 2.6}
    }
    
    food_key = food_name.lower().split()[0]  # Simplificación
    nutrition = mock_nutrition.get(food_key, {"calories": 100, "protein": 5, "carbs": 20, "fat": 3, "fiber": 2})
    
    return {
        "food_name": food_name,
        "portion_size": portion_size,
        "nutrition_per_portion": nutrition,
        "unit": "per " + portion_size
    }


# Mapeo de nombres de función a implementaciones
FUNCTION_IMPLEMENTATIONS = {
    "get_user_fitness_data": get_user_fitness_data,
    "calculate_calories": calculate_calories,
    "search_nutrition_info": search_nutrition_info
}


async def process_function_calls(function_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Procesa las llamadas a funciones del modelo."""
    results = []
    
    for call in function_calls:
        func_name = call["name"]
        func_args = call["args"]
        
        if func_name in FUNCTION_IMPLEMENTATIONS:
            try:
                # Ejecutar la función
                result = await FUNCTION_IMPLEMENTATIONS[func_name](**func_args)
                results.append({
                    "function_name": func_name,
                    "result": result,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "function_name": func_name,
                    "error": str(e),
                    "status": "error"
                })
        else:
            results.append({
                "function_name": func_name,
                "error": "Function not implemented",
                "status": "error"
            })
    
    return results


async def main():
    """Ejemplo principal de uso de function calling."""
    print("=== Ejemplo de Function Calling con Vertex AI ===\n")
    
    # Inicializar cliente
    client = VertexAIClient()
    
    # Configuración de grounding (búsqueda web)
    grounding_config = {
        "enable_web_search": True,
        "search_config": {
            "max_results": 5,
            "filter_duplicates": True
        }
    }
    
    # Ejemplo 1: Consulta que requiere datos del usuario
    print("📊 Ejemplo 1: Análisis de progreso de fitness")
    prompt1 = "Analiza mi progreso de fitness. ¿Cuántas calorías he quemado hoy y cuál es mi peso actual?"
    
    response1 = await client.generate_with_functions(
        prompt=prompt1,
        functions=AVAILABLE_FUNCTIONS,
        system_instruction="Eres un asistente de fitness que ayuda a los usuarios a monitorear su progreso. Usa las funciones disponibles para obtener datos reales del usuario.",
        grounding_config=grounding_config
    )
    
    print(f"Respuesta del modelo: {response1['text']}")
    
    if response1["function_calls"]:
        print("\n🔧 Llamadas a funciones detectadas:")
        for call in response1["function_calls"]:
            print(f"  - {call['name']}({json.dumps(call['args'], indent=2)})")
        
        # Procesar las llamadas a funciones
        results = await process_function_calls(response1["function_calls"])
        print("\n📊 Resultados de las funciones:")
        for result in results:
            print(f"  - {result['function_name']}: {json.dumps(result.get('result', result.get('error')), indent=2)}")
    
    # Ejemplo 2: Consulta nutricional con grounding
    print("\n\n🥗 Ejemplo 2: Análisis nutricional con búsqueda web")
    prompt2 = "¿Cuántas calorías tiene una manzana y cuáles son sus beneficios para la salud según estudios recientes?"
    
    response2 = await client.generate_with_functions(
        prompt=prompt2,
        functions=AVAILABLE_FUNCTIONS,
        system_instruction="Eres un nutricionista experto. Usa las funciones para obtener datos nutricionales y complementa con información actualizada de la web.",
        grounding_config=grounding_config
    )
    
    print(f"Respuesta del modelo: {response2['text'][:200]}...")
    
    if response2["grounding_metadata"]:
        print("\n🔍 Información de grounding:")
        print(f"  - Consultas de búsqueda: {response2['grounding_metadata'].get('search_queries', [])}")
        print(f"  - Resultados web utilizados: {len(response2['grounding_metadata'].get('web_search_results', []))}")
    
    # Ejemplo 3: Cálculo de calorías con múltiples actividades
    print("\n\n🏃 Ejemplo 3: Plan de ejercicios personalizado")
    prompt3 = "Si peso 70kg y quiero quemar 500 calorías, ¿cuánto tiempo debo correr y nadar?"
    
    response3 = await client.generate_with_functions(
        prompt=prompt3,
        functions=AVAILABLE_FUNCTIONS,
        system_instruction="Eres un entrenador personal. Calcula con precisión las calorías y proporciona recomendaciones basadas en datos.",
        temperature=0.3  # Temperatura más baja para cálculos precisos
    )
    
    print(f"Respuesta del modelo: {response3['text']}")
    
    if response3["function_calls"]:
        results = await process_function_calls(response3["function_calls"])
        print("\n📊 Cálculos realizados:")
        for result in results:
            if result["status"] == "success":
                print(f"  - {result['result']}")
    
    print("\n✅ Ejemplo completado")


if __name__ == "__main__":
    asyncio.run(main())