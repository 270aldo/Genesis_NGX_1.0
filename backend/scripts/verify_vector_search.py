#!/usr/bin/env python3
"""
Script para verificar la configuración de Vertex AI Vector Search.

Este script valida que el índice y endpoint de Vector Search estén
correctamente configurados y accesibles.
"""

import asyncio
import os
import sys
from pathlib import Path

# Añadir el directorio raíz del proyecto al path
sys.path.append(str(Path(__file__).parent.parent))

from google.cloud import aiplatform
from google.api_core import exceptions
from config.secrets import settings
from core.logging_config import get_logger

logger = get_logger(__name__)


def check_credentials():
    """Verifica que las credenciales de Google Cloud estén configuradas."""
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS no está configurada")
        return False
    
    if not os.path.exists(creds_path):
        print(f"❌ El archivo de credenciales no existe: {creds_path}")
        return False
    
    print(f"✅ Credenciales encontradas: {creds_path}")
    return True


def check_project_settings():
    """Verifica la configuración del proyecto."""
    project_id = os.environ.get("GCP_PROJECT_ID", "agentes-ngx")
    location = os.environ.get("GCP_REGION", "us-central1")
    
    print(f"📋 Configuración del proyecto:")
    print(f"   - Project ID: {project_id}")
    print(f"   - Location: {location}")
    print(f"   - Index ID: {settings.VERTEX_AI_INDEX_ID}")
    print(f"   - Endpoint ID: {settings.VERTEX_AI_INDEX_ENDPOINT_ID}")
    
    return project_id, location


async def verify_vector_search_index(project_id: str, location: str):
    """Verifica que el índice de Vector Search exista y esté accesible."""
    try:
        # Inicializar AI Platform
        aiplatform.init(project=project_id, location=location)
        
        print("\n🔍 Verificando índice de Vector Search...")
        
        # Intentar obtener el índice
        try:
            from google.cloud.aiplatform import MatchingEngineIndex
            
            index = MatchingEngineIndex(index_name=settings.VERTEX_AI_INDEX_ID)
            
            print(f"✅ Índice encontrado:")
            print(f"   - Nombre: {index.display_name}")
            print(f"   - Estado: {index.state}")
            print(f"   - Dimensiones: {index.metadata.config.dimensions if hasattr(index.metadata, 'config') else 'N/A'}")
            print(f"   - Algoritmo: {index.metadata.config.algorithm_config if hasattr(index.metadata, 'config') else 'N/A'}")
            
            return True
            
        except exceptions.NotFound:
            print(f"❌ Índice no encontrado: {settings.VERTEX_AI_INDEX_ID}")
            print("   Verifica que el ID sea correcto y que el índice exista en tu proyecto")
            return False
            
        except Exception as e:
            print(f"❌ Error al acceder al índice: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Error al inicializar AI Platform: {str(e)}")
        return False


async def verify_vector_search_endpoint(project_id: str, location: str):
    """Verifica que el endpoint de Vector Search exista y esté desplegado."""
    try:
        print("\n🔍 Verificando endpoint de Vector Search...")
        
        # Intentar obtener el endpoint
        try:
            from google.cloud.aiplatform import MatchingEngineIndexEndpoint
            
            endpoint = MatchingEngineIndexEndpoint(
                index_endpoint_name=settings.VERTEX_AI_INDEX_ENDPOINT_ID
            )
            
            print(f"✅ Endpoint encontrado:")
            print(f"   - Nombre: {endpoint.display_name}")
            print(f"   - Estado: {endpoint.state if hasattr(endpoint, 'state') else 'N/A'}")
            
            # Verificar índices desplegados
            deployed_indexes = endpoint.deployed_indexes
            if deployed_indexes:
                print(f"   - Índices desplegados: {len(deployed_indexes)}")
                for idx in deployed_indexes:
                    print(f"     • {idx.id}: {idx.index}")
            else:
                print("   ⚠️  No hay índices desplegados en este endpoint")
            
            return True
            
        except exceptions.NotFound:
            print(f"❌ Endpoint no encontrado: {settings.VERTEX_AI_INDEX_ENDPOINT_ID}")
            print("   Verifica que el ID sea correcto y que el endpoint exista en tu proyecto")
            return False
            
        except Exception as e:
            print(f"❌ Error al acceder al endpoint: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        return False


async def test_vector_search_client():
    """Prueba el cliente de Vector Search."""
    print("\n🧪 Probando cliente de Vector Search...")
    
    try:
        from clients.vertex_ai.vector_search_client import vector_search_client
        
        # Inicializar el cliente
        await vector_search_client.initialize()
        print("✅ Cliente inicializado correctamente")
        
        # Probar una búsqueda simple
        test_vector = [0.1] * 3072  # Vector de prueba de 3072 dimensiones
        
        print("🔍 Realizando búsqueda de prueba...")
        results = await vector_search_client.search_similar(
            query_vector=test_vector,
            top_k=5
        )
        
        if results:
            print(f"✅ Búsqueda exitosa: {len(results)} resultados encontrados")
            for i, result in enumerate(results[:3], 1):
                print(f"   {i}. ID: {result['id']}, Distancia: {result['distance']:.4f}")
        else:
            print("⚠️  La búsqueda no retornó resultados (esto puede ser normal si el índice está vacío)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al probar el cliente: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Función principal."""
    print("=== Verificación de Vertex AI Vector Search ===\n")
    
    # 1. Verificar credenciales
    if not check_credentials():
        print("\n⚠️  Configura GOOGLE_APPLICATION_CREDENTIALS antes de continuar")
        return
    
    # 2. Verificar configuración del proyecto
    project_id, location = check_project_settings()
    
    # 3. Verificar índice
    index_ok = await verify_vector_search_index(project_id, location)
    
    # 4. Verificar endpoint
    endpoint_ok = await verify_vector_search_endpoint(project_id, location)
    
    # 5. Probar cliente
    if index_ok and endpoint_ok:
        client_ok = await test_vector_search_client()
    else:
        print("\n⚠️  Saltando prueba del cliente debido a errores anteriores")
        client_ok = False
    
    # Resumen
    print("\n=== Resumen de Verificación ===")
    print(f"{'✅' if index_ok else '❌'} Índice de Vector Search")
    print(f"{'✅' if endpoint_ok else '❌'} Endpoint de Vector Search")
    print(f"{'✅' if client_ok else '❌'} Cliente de Vector Search")
    
    if not (index_ok and endpoint_ok):
        print("\n📝 Próximos pasos:")
        print("1. Verifica que los IDs en config/secrets.py sean correctos")
        print("2. Asegúrate de que el índice y endpoint existan en tu proyecto de GCP")
        print("3. Si no existen, consulta la documentación para crearlos:")
        print("   https://cloud.google.com/vertex-ai/docs/vector-search/overview")


if __name__ == "__main__":
    asyncio.run(main())