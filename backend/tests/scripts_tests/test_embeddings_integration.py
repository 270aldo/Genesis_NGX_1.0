#!/usr/bin/env python3
"""
Script de prueba para verificar la integración completa del sistema de embeddings.

Prueba:
1. Generación de embeddings con el nuevo modelo
2. Almacenamiento en GCS
3. Búsqueda con Vector Search
4. Búsqueda local como fallback

Uso:
    python scripts/test_embeddings_integration.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from core.embeddings_manager import embeddings_manager
from core.logging_config import get_logger

logger = get_logger(__name__)


async def test_embeddings_integration():
    """Prueba completa del sistema de embeddings."""

    print("\n🚀 Iniciando prueba de integración de embeddings...\n")

    # Test 1: Generar embedding
    print("📝 Test 1: Generando embedding para texto de prueba...")
    try:
        test_text = "NGX Agents es un sistema de coaching fitness personalizado con IA"
        embedding = await embeddings_manager.generate_embedding(test_text)
        print(f"✅ Embedding generado exitosamente")
        print(f"   - Dimensiones: {len(embedding)}")
        print(f"   - Primeros 5 valores: {embedding[:5]}")
    except Exception as e:
        print(f"❌ Error generando embedding: {e}")
        return

    # Test 2: Almacenar embedding
    print("\n📝 Test 2: Almacenando embedding con metadatos...")
    try:
        stored = await embeddings_manager.store_embedding(
            key="test_ngx_001",
            text=test_text,
            metadata={
                "category": "system_description",
                "agent": "test",
                "timestamp": "2025-05-31",
            },
            embedding=embedding,
        )
        if stored:
            print("✅ Embedding almacenado exitosamente en memoria y GCS")
        else:
            print("❌ Error al almacenar embedding")
    except Exception as e:
        print(f"❌ Error almacenando embedding: {e}")

    # Test 3: Almacenar más embeddings para búsqueda
    print("\n📝 Test 3: Almacenando múltiples embeddings...")
    test_data = [
        {
            "key": "fitness_001",
            "text": "Programa de entrenamiento de fuerza para principiantes",
            "metadata": {"category": "training", "level": "beginner"},
        },
        {
            "key": "nutrition_001",
            "text": "Plan de nutrición balanceada para pérdida de peso",
            "metadata": {"category": "nutrition", "goal": "weight_loss"},
        },
        {
            "key": "recovery_001",
            "text": "Técnicas de recuperación muscular post-entrenamiento",
            "metadata": {"category": "recovery", "type": "muscle"},
        },
        {
            "key": "biometrics_001",
            "text": "Análisis de composición corporal y métricas de salud",
            "metadata": {"category": "biometrics", "type": "body_composition"},
        },
    ]

    for item in test_data:
        try:
            stored = await embeddings_manager.store_embedding(
                key=item["key"], text=item["text"], metadata=item["metadata"]
            )
            if stored:
                print(f"✅ {item['key']} almacenado")
        except Exception as e:
            print(f"❌ Error con {item['key']}: {e}")

    # Esperar un poco para que GCS se actualice
    await asyncio.sleep(2)

    # Test 4: Búsqueda por similitud
    print("\n📝 Test 4: Búsqueda por similitud...")
    search_queries = [
        "ejercicios para ganar músculo",
        "dieta saludable",
        "cómo recuperarse después del gimnasio",
    ]

    for query in search_queries:
        print(f"\n🔍 Buscando: '{query}'")
        try:
            results = await embeddings_manager.find_similar(
                query=query, top_k=3, threshold=0.5
            )

            if results:
                print(f"✅ Encontrados {len(results)} resultados:")
                for i, result in enumerate(results, 1):
                    print(
                        f"   {i}. {result['key']} (similitud: {result['similarity']:.3f})"
                    )
                    print(f"      Texto: {result['text'][:60]}...")
                    print(f"      Metadata: {result['metadata']}")
            else:
                print("❌ No se encontraron resultados")
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")

    # Test 5: Obtener estadísticas
    print("\n📝 Test 5: Obteniendo estadísticas del sistema...")
    try:
        stats = await embeddings_manager.get_stats()
        print("✅ Estadísticas del sistema:")
        print(f"   - Embeddings en memoria: {stats['store_size']}")
        print(f"   - Caché de texto activo: {stats['cache_size']}")
        print(f"   - Dimensiones del vector: {stats['vector_dimension']}")
        print(f"   - GCS habilitado: {stats['use_gcs']}")
        print(f"   - GCS inicializado: {stats['gcs_initialized']}")
        print(f"   - Vector Search habilitado: {stats['use_vector_search']}")
        print(f"   - Vector Search inicializado: {stats['vector_search_initialized']}")
        if "gcs_embeddings_count" in stats:
            print(f"   - Embeddings en GCS: {stats['gcs_embeddings_count']}")
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")

    # Test 6: Limpieza (opcional)
    print("\n📝 Test 6: Limpiando datos de prueba...")
    cleanup = input("¿Deseas limpiar los datos de prueba? (s/n): ")
    if cleanup.lower() == "s":
        test_keys = [
            "test_ngx_001",
            "fitness_001",
            "nutrition_001",
            "recovery_001",
            "biometrics_001",
        ]
        for key in test_keys:
            try:
                deleted = await embeddings_manager.delete_by_key(key)
                if deleted:
                    print(f"✅ {key} eliminado")
            except Exception as e:
                print(f"❌ Error eliminando {key}: {e}")

    print("\n✅ Prueba de integración completada!")


if __name__ == "__main__":
    # Ejecutar prueba
    asyncio.run(test_embeddings_integration())
