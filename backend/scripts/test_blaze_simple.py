#!/usr/bin/env python3
"""
Test Simple para BLAZE - Sin importar ADK directamente
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_blaze_refactoring():
    """Test que BLAZE está correctamente refactorizado."""
    print("\n🔥 Verificando refactorización de BLAZE...")
    print("=" * 50)
    
    # 1. Verificar estructura de archivos
    blaze_dir = Path("agents/elite_training_strategist")
    
    files_to_check = {
        "agent_refactored.py": "Archivo principal refactorizado",
        "config.py": "Configuración",
        "prompts/__init__.py": "Módulo de prompts",
        "skills/__init__.py": "Módulo de skills",
        "services/__init__.py": "Módulo de servicios"
    }
    
    all_good = True
    for file, desc in files_to_check.items():
        file_path = blaze_dir / file
        if file_path.exists():
            print(f"✅ {desc}: {file}")
        else:
            print(f"❌ FALTA: {file}")
            all_good = False
    
    # 2. Verificar tamaño del archivo refactorizado
    refactored_file = blaze_dir / "agent_refactored.py"
    if refactored_file.exists():
        lines = len(refactored_file.read_text().splitlines())
        print(f"\n📏 Tamaño de agent_refactored.py: {lines} líneas")
        
        if lines < 300:
            print("✅ Cumple con el objetivo de < 300 líneas")
        else:
            print("⚠️  Excede las 300 líneas objetivo")
    
    # 3. Verificar que hereda de BaseNGXAgent
    if refactored_file.exists():
        content = refactored_file.read_text()
        if "class EliteTrainingStrategistRefactored(BaseNGXAgent):" in content:
            print("✅ Hereda correctamente de BaseNGXAgent")
        else:
            print("❌ NO hereda de BaseNGXAgent")
            all_good = False
        
        # Verificar que usa a2a_adapter
        if "a2a_adapter" in content:
            print("✅ Usa a2a_adapter para comunicación A2A")
        else:
            print("❌ NO usa a2a_adapter")
            all_good = False
        
        # Verificar que define ADK skills
        if "_adk_" in content and "Skill(" in content:
            print("✅ Define ADK skills correctamente")
        else:
            print("❌ NO define ADK skills")
            all_good = False
    
    # 4. Verificar skills modulares
    skills_dir = blaze_dir / "skills"
    expected_skills = [
        "training_plan_generation.py",
        "exercise_optimization.py",
        "performance_analysis.py",
        "recovery_protocol.py",
        "injury_prevention.py"
    ]
    
    print("\n📦 Skills modulares:")
    for skill in expected_skills:
        skill_path = skills_dir / skill
        if skill_path.exists():
            print(f"  ✅ {skill}")
        else:
            print(f"  ❌ FALTA: {skill}")
    
    # 5. Comparación con original
    original_file = blaze_dir / "agent.py"
    if original_file.exists() and refactored_file.exists():
        original_lines = len(original_file.read_text().splitlines())
        refactored_lines = len(refactored_file.read_text().splitlines())
        reduction = ((original_lines - refactored_lines) / original_lines) * 100
        
        print(f"\n📊 Reducción de código:")
        print(f"   Original: {original_lines} líneas")
        print(f"   Refactorizado: {refactored_lines} líneas")
        print(f"   Reducción: {reduction:.1f}%")
        
        if reduction > 90:
            print("   ✅ Excelente reducción!")
        elif reduction > 80:
            print("   ✅ Buena reducción")
        else:
            print("   ⚠️  Reducción menor a la esperada")
    
    if all_good:
        print("\n✨ BLAZE está correctamente refactorizado!")
        print("   - Hereda de BaseNGXAgent ✓")
        print("   - Usa protocolo A2A ✓")
        print("   - Define ADK skills ✓")
        print("   - Estructura modular ✓")
        return True
    else:
        print("\n❌ BLAZE necesita correcciones")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_blaze_refactoring())
    sys.exit(0 if success else 1)