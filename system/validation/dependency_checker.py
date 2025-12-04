#!/usr/bin/env python3
"""
Dependency Checker - Verificador de dependencias.
Fase -1: Validación y Testing Base
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List


class DependencyChecker:
    """Verifica dependencias del sistema."""
    
    def __init__(self):
        pass
    
    def check_python_dependencies(self, requirements_file: str = "requirements.txt") -> Dict[str, Any]:
        """Verifica dependencias de Python."""
        result = {
            "all_installed": True,
            "missing": [],
            "installed": []
        }
        
        req_file = Path(requirements_file)
        if not req_file.exists():
            return {
                "all_installed": False,
                "error": f"Requirements file not found: {requirements_file}"
            }
        
        try:
            with open(req_file, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            for req in requirements:
                package_name = req.split('==')[0].split('>=')[0].split('<=')[0].strip()
                if self._is_installed(package_name):
                    result["installed"].append(package_name)
                else:
                    result["missing"].append(package_name)
                    result["all_installed"] = False
        
        except Exception as e:
            result["all_installed"] = False
            result["error"] = str(e)
        
        return result
    
    def _is_installed(self, package_name: str) -> bool:
        """Verifica si un paquete está instalado."""
        try:
            __import__(package_name.replace('-', '_'))
            return True
        except ImportError:
            # Try pip list as fallback
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "list"],
                    capture_output=True,
                    text=True
                )
                return package_name.lower() in result.stdout.lower()
            except Exception:
                return False
    
    def check_system_dependencies(self) -> Dict[str, Any]:
        """Verifica dependencias del sistema."""
        result = {
            "all_available": True,
            "missing": [],
            "available": []
        }
        
        system_tools = {
            "git": "git --version",
            "python": "python3 --version"
        }
        
        for tool, command in system_tools.items():
            try:
                subprocess.run(
                    command.split(),
                    capture_output=True,
                    check=True
                )
                result["available"].append(tool)
            except (subprocess.CalledProcessError, FileNotFoundError):
                result["missing"].append(tool)
                result["all_available"] = False
        
        return result

