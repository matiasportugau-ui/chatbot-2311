#!/usr/bin/env python3
"""
Version Checker - Verificador de versiones.
Fase -1: Validación y Testing Base
"""

import subprocess
import sys
from typing import Dict, Any, Optional


class VersionChecker:
    """Verifica versiones de dependencias."""
    
    def check_python_version(self, min_version: str = "3.8") -> Dict[str, Any]:
        """Verifica la versión de Python."""
        version = sys.version_info
        current_version = f"{version.major}.{version.minor}.{version.micro}"
        
        min_major, min_minor = map(int, min_version.split('.'))
        
        meets_requirement = (
            version.major > min_major or
            (version.major == min_major and version.minor >= min_minor)
        )
        
        return {
            "current": current_version,
            "required": min_version,
            "meets_requirement": meets_requirement
        }
    
    def check_package_version(self, package_name: str) -> Optional[str]:
        """Obtiene la versión de un paquete."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        return line.split(':', 1)[1].strip()
        except Exception:
            pass
        
        return None

