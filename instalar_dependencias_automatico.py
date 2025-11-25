#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instala automáticamente todas las dependencias necesarias para el chatbot BMC.
"""

import subprocess
import sys
from pathlib import Path


REQ_FILE = Path("requirements.txt")


def print_header():
    print("=" * 70)
    print("INSTALACION AUTOMATICA DE DEPENDENCIAS")
    print("=" * 70)
    print()


def ensure_requirements_file():
    if REQ_FILE.exists():
        return True

    print("❌ No se encontró requirements.txt en el directorio actual.")
    print("   Asegúrate de ejecutar este script desde la raíz del proyecto.")
    return False


def upgrade_pip():
    print("Actualizando pip...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        check=False,
    )
    print()


def install_requirements():
    print("Instalando dependencias desde requirements.txt...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(REQ_FILE)],
            check=True,
        )
        print("Dependencias instaladas correctamente.")
    except subprocess.CalledProcessError as exc:
        print("Error instalando dependencias:")
        print(exc)
        sys.exit(1)


def main():
    print_header()

    if not ensure_requirements_file():
        sys.exit(1)

    upgrade_pip()
    install_requirements()

    print()
    print("Si ves algún error, ejecuta este script nuevamente o revisa el registro anterior.")


if __name__ == "__main__":
    main()

