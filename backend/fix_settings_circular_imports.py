#!/usr/bin/env python3
"""
Fix circular imports and global Settings() instantiations in GENESIS backend.

This script updates all files that create Settings() instances at module level
to use lazy initialization instead.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def find_files_with_settings_import(root_dir: Path) -> List[Path]:
    """Find all Python files that instantiate Settings at module level."""
    files_to_fix = []
    
    # Pattern to match Settings instantiation at module level
    patterns = [
        (r'from core\.settings import Settings\s*\n\s*settings = Settings\(\)', 
         'from core.settings_lazy import settings'),
        (r'settings = Settings\(\)\s*\n', ''),  # Remove standalone instantiation
    ]
    
    for file_path in root_dir.rglob("*.py"):
        if file_path.is_file() and not file_path.name.startswith('test_'):
            try:
                content = file_path.read_text()
                for pattern, _ in patterns:
                    if re.search(pattern, content):
                        files_to_fix.append(file_path)
                        break
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return files_to_fix


def fix_settings_imports(file_path: Path) -> bool:
    """Fix Settings imports in a single file."""
    try:
        content = file_path.read_text()
        original_content = content
        
        # Apply fixes
        replacements = [
            # Replace Settings import and instantiation pattern
            (r'from core\.settings import Settings\s*\n\s*settings = Settings\(\)',
             'from core.settings_lazy import settings'),
            
            # Remove standalone Settings instantiation (if import is separate)
            (r'(\nfrom core\.settings import Settings\s*\n)(.*?\n)(settings = Settings\(\)\s*\n)',
             r'\1from core.settings_lazy import settings\n\2'),
             
            # Fix config files that use Settings()
            (r'settings = Settings\(\)\s*\n(\s*)', r'\1'),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Special handling for files that need to access settings attributes
        if 'settings = Settings()' in original_content and 'from core.settings import Settings' in original_content:
            # Ensure we import from settings_lazy
            if 'from core.settings_lazy import settings' not in content:
                content = re.sub(
                    r'from core\.settings import Settings',
                    'from core.settings_lazy import settings',
                    content
                )
        
        # Write back if changed
        if content != original_content:
            file_path.write_text(content)
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            print(f"⏭️  Skipped (no changes): {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Main function to fix all Settings circular imports."""
    root_dir = Path(__file__).parent
    
    print("🔍 Searching for files with Settings instantiation at module level...")
    files_to_fix = find_files_with_settings_import(root_dir)
    
    print(f"\nFound {len(files_to_fix)} files to fix:")
    for file_path in files_to_fix:
        print(f"  - {file_path.relative_to(root_dir)}")
    
    if not files_to_fix:
        print("\n✅ No files need fixing!")
        return
    
    print("\n🔧 Fixing imports...")
    fixed_count = 0
    for file_path in files_to_fix:
        if fix_settings_imports(file_path):
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count}/{len(files_to_fix)} files")
    
    # Additional files to check manually
    print("\n📋 Additional files to verify manually:")
    manual_check = [
        "agents/orchestrator/config.py",
        "agents/code_genetic_specialist/config.py", 
        "agents/elite_training_strategist/config.py",
        "agents/precision_nutrition_architect/config.py",
    ]
    
    for file_name in manual_check:
        file_path = root_dir / file_name
        if file_path.exists():
            print(f"  - {file_name}")


if __name__ == "__main__":
    main()