#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestiona servicios opcionales necesarios para el chatbot (p.ej., MongoDB).
"""

import shutil
import socket
import subprocess
from time import sleep


MONGO_CONTAINER = "bmc-mongodb"


def print_header():
    print("=" * 70)
    print("GESTIÓN DE SERVICIOS OPCIONALES")
    print("=" * 70)
    print()


def docker_available() -> bool:
    return shutil.which("docker") is not None


def run_docker_command(args):
    try:
        result = subprocess.run(
            ["docker"] + args,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as exc:
        return False, str(exc)


def container_exists(name: str) -> bool:
    ok, output = run_docker_command(["ps", "-a", "--filter", f"name={name}", "--format", "{{.Names}}"])
    return ok and name in output.splitlines()


def container_running(name: str) -> bool:
    ok, output = run_docker_command(["ps", "--filter", f"name={name}", "--format", "{{.Names}}"])
    return ok and name in output.splitlines()


def start_container():
    print(f"Iniciando contenedor {MONGO_CONTAINER}...")
    ok, output = run_docker_command(["start", MONGO_CONTAINER])
    if ok:
        print("MongoDB iniciado.")
    else:
        print("No se pudo iniciar el contenedor existente.")
        print(output)


def create_container():
    print("Creando contenedor MongoDB (mongo:7.0)...")
    ok, output = run_docker_command([
        "run",
        "-d",
        "--name",
        MONGO_CONTAINER,
        "-p",
        "27017:27017",
        "mongo:7.0",
    ])
    if ok:
        print("Contenedor MongoDB creado e iniciado.")
    else:
        print("No se pudo crear el contenedor MongoDB.")
        print(output)


def check_mongo_socket() -> bool:
    try:
        with socket.create_connection(("localhost", 27017), timeout=1):
            return True
    except OSError:
        return False


def main():
    print_header()

    if not docker_available():
        print("Docker no está disponible en este equipo. Saltando creación automática de MongoDB.")
        print("Si necesitas persistencia, instala Docker Desktop y ejecuta este script nuevamente.")
    else:
        print("Docker detectado.")
        if not container_exists(MONGO_CONTAINER):
            create_container()
        elif not container_running(MONGO_CONTAINER):
            start_container()
        else:
            print("Contenedor MongoDB ya se encuentra en ejecución.")

    # Esperar un momento antes de verificar el socket
    sleep(2)

    if check_mongo_socket():
        print("MongoDB accesible en localhost:27017")
    else:
        print("No se detecta MongoDB en localhost:27017. El chatbot funcionará sin persistencia.")

    print()
    print("Gestión de servicios completada.")


if __name__ == "__main__":
    main()

