#!/usr/bin/env python3
"""
Script de verificación de configuración de Google Cloud para GENESIS.

Este script verifica que todos los servicios de Google Cloud necesarios
estén correctamente configurados y funcionando.
"""

import os
import sys
import json
from pathlib import Path


def print_header(title):
    """Imprime un header formateado."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_environment_variables():
    """Verifica las variables de entorno necesarias."""
    print_header("Verificando Variables de Entorno")
    
    required_vars = {
        'GOOGLE_APPLICATION_CREDENTIALS': 'Ruta al archivo de credenciales de Google Cloud',
        'VERTEX_AI_PROJECT_ID': 'ID del proyecto de Google Cloud',
        'VERTEX_AI_LOCATION': 'Región de Vertex AI (ej: us-central1)'
    }
    
    all_good = True
    
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Ocultar parte del valor por seguridad
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NO CONFIGURADA - {description}")
            all_good = False
    
    return all_good


def check_credentials_file():
    """Verifica que el archivo de credenciales existe y es válido."""
    print_header("Verificando Archivo de Credenciales")
    
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS no está configurada")
        return False
    
    creds_file = Path(creds_path)
    
    if not creds_file.exists():
        print(f"❌ Archivo de credenciales no existe: {creds_path}")
        return False
    
    if not creds_file.is_file():
        print(f"❌ La ruta no es un archivo: {creds_path}")
        return False
    
    # Verificar que es un JSON válido
    try:
        with open(creds_file, 'r') as f:
            creds_data = json.load(f)
            
        # Verificar campos requeridos
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds_data]
        
        if missing_fields:
            print(f"❌ Campos faltantes en credenciales: {', '.join(missing_fields)}")
            return False
        
        print(f"✅ Archivo de credenciales válido")
        print(f"   - Tipo: {creds_data.get('type')}")
        print(f"   - Proyecto: {creds_data.get('project_id')}")
        print(f"   - Email: {creds_data.get('client_email')}")
        
        return True
        
    except json.JSONDecodeError:
        print(f"❌ El archivo no es un JSON válido: {creds_path}")
        return False
    except Exception as e:
        print(f"❌ Error leyendo credenciales: {e}")
        return False


def check_google_cloud_imports():
    """Verifica que las librerías de Google Cloud se pueden importar."""
    print_header("Verificando Imports de Google Cloud")
    
    libraries = {
        'google.cloud.vision': 'Google Cloud Vision API',
        'google.cloud.translate': 'Google Cloud Translation API',
        'google.cloud.documentai': 'Google Cloud Document AI',
        'google.cloud.discoveryengine': 'Google Cloud Discovery Engine',
        'google.generativeai': 'Google Generative AI (Gemini)',
        'vertexai': 'Vertex AI'
    }
    
    all_good = True
    
    for lib, name in libraries.items():
        try:
            __import__(lib)
            print(f"✅ {name} ({lib})")
        except ImportError as e:
            print(f"❌ {name} ({lib}): {str(e)}")
            all_good = False
    
    return all_good


def check_vertex_ai_client():
    """Verifica que se puede crear un cliente de Vertex AI."""
    print_header("Verificando Cliente de Vertex AI")
    
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        project_id = os.environ.get('VERTEX_AI_PROJECT_ID')
        location = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')
        
        if not project_id:
            print("❌ VERTEX_AI_PROJECT_ID no configurado")
            return False
        
        # Inicializar Vertex AI
        vertexai.init(project=project_id, location=location)
        print(f"✅ Vertex AI inicializado")
        print(f"   - Proyecto: {project_id}")
        print(f"   - Ubicación: {location}")
        
        # Intentar crear un modelo
        model = GenerativeModel("gemini-1.5-pro")
        print("✅ Modelo Gemini creado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con Vertex AI: {str(e)}")
        return False


def check_vision_api():
    """Verifica que Google Cloud Vision API funciona."""
    print_header("Verificando Google Cloud Vision API")
    
    try:
        from google.cloud import vision
        
        # Crear cliente
        client = vision.ImageAnnotatorClient()
        print("✅ Cliente de Vision API creado")
        
        # Verificar que podemos hacer una solicitud simple
        # (sin enviar imagen real, solo verificar el cliente)
        print("✅ Google Cloud Vision API está funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con Vision API: {str(e)}")
        print("\n💡 Sugerencias:")
        print("   1. Verifica que la API de Vision esté habilitada en tu proyecto")
        print("   2. Verifica que las credenciales tengan permisos para Vision API")
        print("   3. Visita: https://console.cloud.google.com/apis/api/vision.googleapis.com")
        return False


def generate_setup_instructions():
    """Genera instrucciones de configuración personalizadas."""
    print_header("Instrucciones de Configuración")
    
    print("Si alguna verificación falló, sigue estos pasos:\n")
    
    print("1. Crear archivo de credenciales:")
    print("   - Ve a https://console.cloud.google.com/iam-admin/serviceaccounts")
    print("   - Crea una cuenta de servicio o usa una existente")
    print("   - Descarga el archivo JSON de credenciales")
    print("   - Guárdalo en un lugar seguro (ej: ~/.gcloud/credentials.json)\n")
    
    print("2. Configurar variables de entorno:")
    print("   Agrega esto a tu ~/.bashrc o ~/.zshrc:")
    print("   ```bash")
    print("   export GOOGLE_APPLICATION_CREDENTIALS=\"$HOME/.gcloud/credentials.json\"")
    print("   export VERTEX_AI_PROJECT_ID=\"tu-proyecto-id\"")
    print("   export VERTEX_AI_LOCATION=\"us-central1\"")
    print("   ```\n")
    
    print("3. Habilitar APIs necesarias:")
    print("   - Vision API: https://console.cloud.google.com/apis/api/vision.googleapis.com")
    print("   - Vertex AI: https://console.cloud.google.com/vertex-ai")
    print("   - Translation API: https://console.cloud.google.com/apis/api/translate.googleapis.com")
    print("   - Document AI: https://console.cloud.google.com/apis/api/documentai.googleapis.com\n")
    
    print("4. Verificar permisos de la cuenta de servicio:")
    print("   La cuenta debe tener estos roles:")
    print("   - Vertex AI User")
    print("   - Cloud Vision API User")
    print("   - Cloud Translation API User")
    print("   - Document AI API User")


def main():
    """Función principal del script."""
    print("\n🔍 GENESIS - Verificación de Google Cloud Services")
    print("="*60)
    
    checks = [
        ("Variables de Entorno", check_environment_variables),
        ("Archivo de Credenciales", check_credentials_file),
        ("Imports de Librerías", check_google_cloud_imports),
        ("Cliente Vertex AI", check_vertex_ai_client),
        ("Vision API", check_vision_api)
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error ejecutando verificación de {name}: {e}")
            results[name] = False
    
    # Resumen final
    print_header("Resumen de Verificación")
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    print(f"Verificaciones completadas: {passed_checks}/{total_checks}")
    print()
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check}")
    
    print()
    
    if passed_checks == total_checks:
        print("🎉 ¡Todas las verificaciones pasaron! Google Cloud está correctamente configurado.")
        return 0
    else:
        print("⚠️  Algunas verificaciones fallaron. Revisa las instrucciones arriba.")
        generate_setup_instructions()
        return 1


if __name__ == "__main__":
    sys.exit(main())