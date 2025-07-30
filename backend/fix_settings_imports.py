#!/usr/bin/env python3
"""
Script to fix all settings imports to use lazy initialization.
"""

import os
import re
from pathlib import Path


def fix_settings_imports(directory: str):
    """Fix all settings imports in Python files."""
    fixed_files = []
    
    # Pattern to match various forms of settings imports
    patterns = [
        (r'from core\.settings import settings', 'from core.settings_lazy import settings'),
        (r'from \.\.core\.settings import settings', 'from ..core.settings_lazy import settings'),
        (r'from \.settings import settings', 'from .settings_lazy import settings'),
    ]
    
    # Walk through all Python files
    for root, dirs, files in os.walk(directory):
        # Skip some directories
        if any(skip in root for skip in ['.venv', '__pycache__', '.git', 'node_modules']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                
                # Skip settings.py and settings_lazy.py themselves
                if file in ['settings.py', 'settings_lazy.py']:
                    continue
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Apply all patterns
                    for pattern, replacement in patterns:
                        content = re.sub(pattern, replacement, content)
                    
                    # If content changed, write it back
                    if content != original_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        fixed_files.append(str(filepath))
                        print(f"Fixed: {filepath}")
                        
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    return fixed_files


if __name__ == "__main__":
    backend_dir = "/Users/aldoolivas/Desktop/NGX_Ecosystem/GENESIS_oficial_BETA/backend"
    
    print("Fixing settings imports...")
    fixed = fix_settings_imports(backend_dir)
    
    print(f"\nFixed {len(fixed)} files:")
    for f in sorted(fixed):
        print(f"  - {f}")
    
    print("\nDone!")