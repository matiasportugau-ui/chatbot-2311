#!/usr/bin/env python3
"""
Crea o actualiza el archivo .env con la configuración requerida para OpenAI y MongoDB.
"""

import os
from pathlib import Path

ENV_FILE = Path(".env")
DEFAULTS = {
    "OPENAI_MODEL": "gpt-4o-mini",
    "MONGODB_URI": "mongodb://localhost:27017/bmc_chat",
}


def print_header():
    print("=" * 70)
    print("CONFIGURACIÓN DE ENTORNO (.env)")
    print("=" * 70)
    print()


def read_env() -> dict[str, str]:
    data: dict[str, str] = {}
    if not ENV_FILE.exists():
        return data

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def write_env(env_data: dict[str, str]):
    lines = [
        "# Archivo generado automáticamente por configurar_entorno.py",
        "# Puedes editarlo manualmente si lo necesitas.",
        "",
    ]
    for key, value in env_data.items():
        lines.append(f"{key}={value}")
    ENV_FILE.write_text("\n".join(lines), encoding="utf-8")


def prompt_api_key() -> str:
    print("No se encontró una OPENAI_API_KEY configurada.")
    print("Ingresa tu API key de OpenAI (se mantendrá privada en el archivo .env):")
    api_key = input("> ").strip()
    return api_key


def main():
    print_header()

    env_data = read_env()

    # Intentar obtener API key desde entorno actual si no existe
    api_key = env_data.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
    while not api_key:
        api_key = prompt_api_key()
        if not api_key:
            print("[ADVERTENCIA] La API key es obligatoria. Inténtalo nuevamente.")

    env_data["OPENAI_API_KEY"] = api_key

    # Configurar valores por defecto si no existen
    for key, default_value in DEFAULTS.items():
        env_data.setdefault(key, default_value)

    write_env(env_data)

    print()
    print("✅ Archivo .env configurado correctamente.")
    print(f"   Ubicación: {ENV_FILE.resolve()}")


if __name__ == "__main__":
    main()
