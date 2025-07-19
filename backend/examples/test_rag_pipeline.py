"""
Script de ejemplo para probar el pipeline RAG de NGX Agents.

Este script demuestra cómo usar el pipeline RAG para:
- Generar embeddings
- Buscar en la knowledge base
- Generar respuestas aumentadas
"""

import asyncio
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.pipeline import RAGPipeline
from rag.embeddings.vertex_embeddings import VertexEmbeddingsClient
from rag.search.vertex_search import VertexSearchClient
from rag.generation.flash_client import VertexFlashClient

from core.logging_config import get_logger

logger = get_logger(__name__)


async def test_embeddings():
    """Prueba la generación de embeddings."""
    print("\n=== Probando Embeddings ===")

    client = VertexEmbeddingsClient()

    # Texto de prueba
    test_text = "¿Cuál es el mejor ejercicio para desarrollar fuerza en las piernas?"

    # Generar embedding
    embedding = await client.embed_for_search(test_text)

    print(f"Texto: {test_text}")
    print(f"Dimensiones del embedding: {len(embedding)}")
    print(f"Primeros 10 valores: {embedding[:10]}")

    # Probar batch
    texts = [
        "Rutina de entrenamiento para principiantes",
        "Plan de nutrición para ganar masa muscular",
        "Técnicas de recuperación post-entrenamiento",
    ]

    embeddings = await client.embed_batch(texts)
    print(f"\nBatch procesado: {len(embeddings)} embeddings generados")

    # Estadísticas de caché
    stats = client.get_cache_stats()
    print(f"\nEstadísticas de caché: {stats}")


async def test_search():
    """Prueba la búsqueda en Vertex AI Search."""
    print("\n=== Probando Búsqueda ===")

    client = VertexSearchClient()

    # Búsqueda simple
    query = "ejercicios para abdominales"
    results = await client.search(query, max_results=3)

    print(f"Query: {query}")
    print(f"Resultados encontrados: {len(results)}")

    for i, result in enumerate(results, 1):
        print(f"\nResultado {i}:")
        print(f"  ID: {result.get('id')}")
        print(f"  Score: {result.get('score', 'N/A')}")
        print(f"  Metadata: {result.get('metadata', {})}")
        print(f"  Contenido: {result.get('content', '')[:200]}...")

    # Búsqueda por dominio
    domain_results = await client.search_by_domain(
        "plan de alimentación", "nutrition", max_results=2
    )
    print(f"\nBúsqueda en dominio 'nutrition': {len(domain_results)} resultados")


async def test_generation():
    """Prueba la generación con contexto."""
    print("\n=== Probando Generación ===")

    client = VertexFlashClient()

    # Documentos de contexto simulados
    context_docs = [
        {
            "id": "doc1",
            "content": "Las sentadillas son uno de los ejercicios más efectivos para desarrollar fuerza en las piernas. Trabajan cuádriceps, glúteos y isquiotibiales.",
            "metadata": {
                "title": "Ejercicios de Piernas",
                "domain": "fitness",
                "category": "strength",
            },
            "score": 0.95,
        },
        {
            "id": "doc2",
            "content": "El peso muerto rumano es excelente para fortalecer la cadena posterior, especialmente isquiotibiales y glúteos.",
            "metadata": {
                "title": "Ejercicios de Cadena Posterior",
                "domain": "fitness",
                "category": "strength",
            },
            "score": 0.88,
        },
    ]

    query = "¿Cuáles son los mejores ejercicios para piernas?"

    response = await client.generate_with_context(
        query,
        context_docs,
        user_context={
            "fitness_level": "intermediate",
            "goals": ["strength", "muscle_gain"],
        },
    )

    print(f"Query: {query}")
    print(f"Respuesta generada:\n{response}")


async def test_full_pipeline():
    """Prueba el pipeline RAG completo."""
    print("\n=== Probando Pipeline RAG Completo ===")

    pipeline = RAGPipeline()

    # Consulta de prueba
    query = "Necesito una rutina de entrenamiento para ganar fuerza en todo el cuerpo"

    # Contexto del usuario
    user_context = {
        "user_id": "test_user_123",
        "fitness_level": "intermediate",
        "goals": ["strength", "muscle_gain"],
        "preferences": {
            "workout_days": 4,
            "session_duration": 60,
            "equipment": ["barbell", "dumbbells", "rack"],
        },
    }

    # Procesar consulta
    result = await pipeline.process_query(
        query, domain="fitness", user_context=user_context
    )

    print(f"Query: {query}")
    print(f"\nRespuesta:\n{result['response']}")
    print(f"\nMetadata:")
    print(f"  Documentos totales: {result['metadata']['total_documents']}")
    print(f"  Documentos relevantes: {result['metadata']['relevant_documents']}")
    print(f"  Longitud de respuesta: {result['metadata']['response_length']}")

    # Probar búsqueda por agente
    print("\n=== Probando Pipeline por Agente ===")

    nutrition_result = await pipeline.process_by_agent(
        "¿Qué debo comer para ganar masa muscular?", "nutrition", user_context
    )

    print(f"\nRespuesta del Nutrition Architect:")
    print(nutrition_result["response"][:500] + "...")


async def test_multi_turn_conversation():
    """Prueba una conversación multi-turno."""
    print("\n=== Probando Conversación Multi-turno ===")

    pipeline = RAGPipeline()

    # Historial de conversación
    messages = [
        {"role": "user", "content": "Quiero empezar a entrenar para ganar fuerza"},
        {
            "role": "assistant",
            "content": "Excelente decisión. Para ganar fuerza, es importante enfocarse en ejercicios compuestos...",
        },
        {"role": "user", "content": "¿Cuántas veces a la semana debería entrenar?"},
        {
            "role": "assistant",
            "content": "Para principiantes en entrenamiento de fuerza, recomiendo empezar con 3 días...",
        },
        {
            "role": "user",
            "content": "¿Y qué ejercicios específicos me recomiendas para empezar?",
        },
    ]

    result = await pipeline.process_multi_turn(
        messages, domain="fitness", user_context={"fitness_level": "beginner"}
    )

    print("Última pregunta:", messages[-1]["content"])
    print(f"\nRespuesta contextualizada:\n{result['response']}")
    print(f"\nTurnos de conversación: {result['metadata']['turn_count']}")


async def main():
    """Ejecuta todas las pruebas."""
    print("🚀 Iniciando pruebas del pipeline RAG de NGX Agents")

    try:
        # Verificar configuración
        project_id = os.getenv("GCP_PROJECT_ID")
        if not project_id:
            print("⚠️  Advertencia: GCP_PROJECT_ID no está configurado")
            print("Por favor, configura las variables de entorno primero")
            return

        print(f"Proyecto GCP: {project_id}")

        # Ejecutar pruebas
        await test_embeddings()
        await test_search()
        await test_generation()
        await test_full_pipeline()
        await test_multi_turn_conversation()

        print("\n✅ Todas las pruebas completadas")

    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
