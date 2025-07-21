#!/usr/bin/env python3
"""
Script para resolver problemas con el namespace de google.cloud.

Este script verifica y corrige los problemas de importación con las
librerías de Google Cloud.
"""

import sys
import os
import site
import subprocess


def print_header(title):
    """Imprime un header formateado."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_google_namespace():
    """Verifica el estado actual del namespace de google."""
    print_header("Verificando Namespace de Google")
    
    # Verificar si existe el paquete google
    try:
        import google
        print("✅ Paquete 'google' encontrado")
        print(f"   Ubicación: {google.__file__ if hasattr(google, '__file__') else 'Built-in'}")
    except ImportError:
        print("❌ Paquete 'google' no encontrado")
        return False
    
    # Verificar si existe google.cloud
    try:
        import google.cloud
        print("✅ Namespace 'google.cloud' encontrado")
        print(f"   Ubicación: {google.cloud.__file__ if hasattr(google.cloud, '__file__') else 'Namespace package'}")
    except ImportError:
        print("❌ Namespace 'google.cloud' no encontrado")
        return False
    
    # Verificar módulos específicos
    modules = ['vision', 'translate', 'documentai', 'discoveryengine']
    all_good = True
    
    for module in modules:
        try:
            mod = __import__(f'google.cloud.{module}')
            print(f"✅ google.cloud.{module} importado correctamente")
        except ImportError as e:
            print(f"❌ google.cloud.{module}: {e}")
            all_good = False
    
    return all_good


def fix_namespace_packages():
    """Intenta arreglar los problemas de namespace."""
    print_header("Arreglando Namespace Packages")
    
    # Verificar si tenemos el archivo __init__.py en google y google.cloud
    site_packages = site.getsitepackages()
    
    for sp in site_packages:
        google_path = os.path.join(sp, 'google')
        cloud_path = os.path.join(sp, 'google', 'cloud')
        
        if os.path.exists(google_path):
            print(f"\n📁 Verificando: {google_path}")
            
            # Verificar __init__.py en google/
            init_file = os.path.join(google_path, '__init__.py')
            if not os.path.exists(init_file):
                print("⚠️  Falta __init__.py en google/, creándolo...")
                with open(init_file, 'w') as f:
                    f.write("# Namespace package for google\n")
                    f.write("__import__('pkg_resources').declare_namespace(__name__)\n")
                print("✅ __init__.py creado")
            
            # Verificar google/cloud/
            if os.path.exists(cloud_path):
                print(f"📁 Verificando: {cloud_path}")
                cloud_init = os.path.join(cloud_path, '__init__.py')
                if not os.path.exists(cloud_init):
                    print("⚠️  Falta __init__.py en google/cloud/, creándolo...")
                    with open(cloud_init, 'w') as f:
                        f.write("# Namespace package for google.cloud\n")
                        f.write("__import__('pkg_resources').declare_namespace(__name__)\n")
                    print("✅ __init__.py creado")


def reinstall_google_packages():
    """Reinstala los paquetes de Google usando Poetry."""
    print_header("Reinstalando Paquetes de Google Cloud")
    
    packages = [
        'google-cloud-vision',
        'google-cloud-translate',
        'google-cloud-documentai',
        'google-cloud-discoveryengine'
    ]
    
    print("1. Removiendo paquetes...")
    for pkg in packages:
        subprocess.run(['poetry', 'remove', pkg], capture_output=True)
    
    print("\n2. Instalando paquetes nuevamente...")
    for pkg in packages:
        print(f"   Instalando {pkg}...")
        result = subprocess.run(['poetry', 'add', pkg], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ {pkg} instalado")
        else:
            print(f"   ❌ Error instalando {pkg}: {result.stderr}")


def main():
    """Función principal."""
    print("🔧 Resolviendo problemas de namespace de Google Cloud\n")
    
    # 1. Verificar estado actual
    if check_google_namespace():
        print("\n✅ Todos los namespaces funcionan correctamente")
        return 0
    
    # 2. Intentar arreglar namespace packages
    print("\n🔧 Intentando arreglar namespaces...")
    fix_namespace_packages()
    
    # 3. Verificar de nuevo
    print("\n🔍 Verificando después de correcciones...")
    if check_google_namespace():
        print("\n✅ Namespaces arreglados correctamente")
        return 0
    
    # 4. Si todavía falla, sugerir reinstalación
    print("\n⚠️  Los namespaces todavía tienen problemas")
    print("\nOpciones para resolver:")
    print("1. Ejecutar: poetry cache clear pypi --all")
    print("2. Ejecutar: poetry install --with dev,test,telemetry")
    print("3. Si persiste, considerar reinstalar en un ambiente virtual limpio")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())