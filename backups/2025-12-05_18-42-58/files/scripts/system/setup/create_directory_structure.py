#!/usr/bin/env python3
"""
Script para crear la estructura de directorios base del sistema.
Fase -8: Sistema de Trabajo Base
"""

import os
import json
from pathlib import Path

def create_directory_structure(base_path: str = "."):
    """Crea la estructura completa de directorios del sistema."""
    
    base = Path(base_path)
    
    # Estructura principal
    directories = [
        # Sistema base
        "system/workflow",
        "system/context",
        "system/context/checkpoints",
        "system/backup",
        "system/logging",
        "system/logs",
        "system/config",
        "system/validation",
        "system/automation",
        
        # Scripts del sistema
        "scripts/system/setup",
        "scripts/system/context",
        "scripts/system/scripts",
        "scripts/system/backup",
        "scripts/system/automation",
        "scripts/system/logging",
        "scripts/system/config",
        "scripts/system/validation",
        "scripts/utils",
        "scripts/automation",
        
        # Consolidación y outputs
        "consolidation",
        "consolidation/discovery",
        "consolidation/security",
        "consolidation/infrastructure",
        "consolidation/observability",
        "consolidation/performance",
        "consolidation/cicd",
        "consolidation/disaster_recovery",
        "consolidation/validation",
        
        # Documentación
        "docs",
    ]
    
    created_dirs = []
    for directory in directories:
        dir_path = base / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(dir_path.relative_to(base)))
        print(f"✓ Created: {directory}")
    
    # Crear archivo de estructura
    structure_data = {
        "created_at": str(Path.cwd()),
        "directories": sorted(created_dirs),
        "total_directories": len(created_dirs)
    }
    
    output_file = base / "system/workflow/directory_structure.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Structure saved to: {output_file}")
    return structure_data

if __name__ == "__main__":
    import sys
    base_path = sys.argv[1] if len(sys.argv) > 1 else "."
    create_directory_structure(base_path)

