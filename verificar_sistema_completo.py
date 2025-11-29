#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica el estado completo del entorno para ejecutar el chatbot BMC.
"""

import importlib.util
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).parent.resolve()
ENV_FILE = ROOT / ".env"
KB_FILES = [
    ROOT / "conocimiento_consolidado.json",  # Primary consolidated file
    ROOT / "base_conocimiento_final.json",
    ROOT / "conocimiento_completo.json",
    ROOT / "base_conocimiento_exportada.json",
    ROOT / "base_conocimiento_demo.json",
]
CRITICAL_MODULES = [
    ("openai", "openai"),
    ("dotenv", "python-dotenv"),
]
OPTIONAL_MODULES = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("pymongo", "pymongo"),
    ("requests", "requests"),
]


def print_header():
    print("=" * 70)
    print("VERIFICACIÓN COMPLETA DEL SISTEMA")
    print("=" * 70)
    print()


def check_python_version() -> Dict[str, str]:
    version = platform.python_version()
    info = {
        "version": version,
        "executable": sys.executable,
        "ok": tuple(map(int, version.split("."))) >= (3, 11, 0),
    }
    return info


def module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def check_modules(modules: List[tuple]) -> Dict[str, bool]:
    return {display: module_available(module) for module, display in modules}


def parse_env_file() -> Dict[str, str]:
    data: Dict[str, str] = {}
    if not ENV_FILE.exists():
        return data

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def check_env() -> Dict[str, str]:
    env_data = parse_env_file()
    return {
        "exists": ENV_FILE.exists(),
        "OPENAI_API_KEY": "***" if env_data.get("OPENAI_API_KEY") else "",
        "OPENAI_MODEL": env_data.get("OPENAI_MODEL", ""),
        "MONGODB_URI": env_data.get("MONGODB_URI", ""),
    }


def check_knowledge_files() -> Dict[str, bool]:
    return {str(path.name): path.exists() for path in KB_FILES}


def check_mongodb() -> Dict[str, bool]:
    status = {
        "socket_open": False,
        "docker_available": False,
        "docker_container_running": False,
    }

    # Intentar conexión directa a localhost:27017
    try:
        with socket.create_connection(("localhost", 27017), timeout=1):
            status["socket_open"] = True
    except OSError:
        status["socket_open"] = False

    # Verificar Docker
    docker_cmd = shutil.which("docker")
    status["docker_available"] = docker_cmd is not None

    if docker_cmd:
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=bmc-mongodb", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            status["docker_container_running"] = "bmc-mongodb" in result.stdout
        except Exception:
            status["docker_container_running"] = False

    return status


def print_results():
    python_info = check_python_version()
    critical_modules = check_modules(CRITICAL_MODULES)
    optional_modules = check_modules(OPTIONAL_MODULES)
    env_info = check_env()
    kb_info = check_knowledge_files()

    print(f"Python: {python_info['version']} ({python_info['executable']})")
    if not python_info["ok"]:
        print("  [ADVERTENCIA] Se requiere Python 3.11 o superior.")
    print()

    print("Dependencias críticas:")
    for module, available in critical_modules.items():
        status = "OK" if available else "FALTA"
        print(f"  - {module}: {status}")
    print()

    print("Dependencias opcionales:")
    for module, available in optional_modules.items():
        status = "OK" if available else "Opcional"
        print(f"  - {module}: {status}")
    print()

    print("Archivo .env:")
    if env_info["exists"]:
        print("  - Encontrado")
        key_status = "configurada" if env_info["OPENAI_API_KEY"] else "faltante"
        print(f"  - OPENAI_API_KEY: {key_status}")
        print(f"  - OPENAI_MODEL: {env_info['OPENAI_MODEL'] or 'no definido'}")
        print(f"  - MONGODB_URI: {env_info['MONGODB_URI'] or 'no definido'}")
    else:
        print("  [ADVERTENCIA] No existe archivo .env. Se creará durante la configuración.")
    print()

    print("Archivos de conocimiento encontrados:")
    for name, exists in kb_info.items():
        status = "OK" if exists else "No encontrado"
        print(f"  - {name}: {status}")
    print()


def main():
    print_header()
    print_results()
    print("=" * 70)
    print("Fin de verificación.")


if __name__ == "__main__":
    main()

