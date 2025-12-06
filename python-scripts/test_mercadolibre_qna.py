#!/usr/bin/env python3
"""
Valida rápidamente que el conocimiento importado desde Mercado Libre
esté disponible para pruebas del chatbot.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_interactions(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró {path}. Ejecuta fetch_mercadolibre_questions.py primero."
        )
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("interacciones", [])


def summarize(interactions: list[dict]) -> tuple[int, int]:
    answered = sum(1 for inter in interactions if inter.get("respuesta_agente"))
    pending = len(interactions) - answered
    return answered, pending


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Revisa que las preguntas de Mercado Libre estén listas para pruebas."
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("conocimiento_mercadolibre.json"),
        help="Archivo de conocimiento a validar",
    )
    args = parser.parse_args()

    interactions = load_interactions(args.path)
    answered, pending = summarize(interactions)

    print(
        f"Mercado Libre Q&A listo para pruebas: total={len(interactions)} · "
        f"respondidas={answered} · pendientes={pending}"
    )
    if pending:
        print("⚠️  Hay preguntas sin respuesta. Considera revisarlas antes de testear con clientes.")


if __name__ == "__main__":
    main()
