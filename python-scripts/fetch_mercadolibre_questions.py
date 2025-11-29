#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincroniza preguntas y respuestas del vendedor en Mercado Libre para
transformarlas en interacciones aprovechables por el chatbot.
Puede consumir la API oficial o un CSV exportado manualmente.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


MELI_API_BASE = "https://api.mercadolibre.com"
DEFAULT_LIMIT = 50


@dataclass
class MercadoLibreQuestion:
    """Pregunta realizada por un comprador en Mercado Libre."""

    id: str
    date_created: str
    item_id: str
    status: str
    text: str
    answer_text: Optional[str]
    answer_status: Optional[str]
    seller_id: str
    buyer_id: Optional[str]


class MercadoLibreConversationSync:
    """Cliente sencillo para descargar preguntas via API oficial o CSV."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        seller_id: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
        output_dir: Path | None = None,
        knowledge_filename: str = "conocimiento_mercadolibre.json",
        csv_export: Optional[str] = None,
    ):
        self.access_token = access_token or os.getenv("MELI_ACCESS_TOKEN")
        self.seller_id = seller_id or os.getenv("MELI_SELLER_ID")
        self.limit = limit
        self.output_dir = output_dir or Path("data/mercadolibre")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_path = Path(knowledge_filename)
        self.csv_export = Path(csv_export).expanduser() if csv_export else None

        if not self.csv_export and (not self.access_token or not self.seller_id):
            raise RuntimeError(
                "Debe definir MELI_ACCESS_TOKEN y MELI_SELLER_ID o utilizar --csv-export "
                "para sincronizar las preguntas."
            )

    def run(self) -> None:
        """Descarga preguntas, genera archivos crudos y transformados."""
        if self.csv_export:
            raw_source = str(self.csv_export)
            questions = self._load_csv_questions(self.csv_export)
        else:
            raw_source = MELI_API_BASE
            questions = self._fetch_questions()

        normalized = [self._normalize_question(q) for q in questions]
        timestamp = datetime.now(timezone.utc).isoformat()

        raw_payload = {
            "metadata": {
                "source": raw_source,
                "generated_at": timestamp,
                "total_questions": len(questions),
            },
            "questions": questions,
        }
        raw_path = self.output_dir / "mercadolibre_questions_raw.json"
        self._write_json(raw_path, raw_payload)

        knowledge_payload = self._build_knowledge_payload(normalized, timestamp)
        self._write_json(self.knowledge_path, knowledge_payload)

        print(
            f"✅ Mercado Libre sync completado: {len(questions)} preguntas → "
            f"{raw_path} / {self.knowledge_path}"
        )

    def _fetch_questions(self) -> List[Dict[str, Any]]:
        """Pagina todas las preguntas del vendedor."""
        offset = 0
        questions: List[Dict[str, Any]] = []

        headers = {"Authorization": f"Bearer {self.access_token}"}

        while True:
            params = {
                "seller_id": self.seller_id,
                "offset": offset,
                "limit": self.limit,
                "sort_fields": "date_created",
                "sort_types": "DESC",
            }
            response = requests.get(
                f"{MELI_API_BASE}/questions/search", params=params, headers=headers, timeout=30
            )

            if response.status_code == 401:
                raise RuntimeError("Token de Mercado Libre inválido o expirado.")
            response.raise_for_status()
            data = response.json()
            chunk = data.get("questions", [])
            if not chunk:
                break
            questions.extend(chunk)
            print(f"  • Offset {offset}: {len(chunk)} preguntas")
            if len(chunk) < self.limit:
                break
            offset += self.limit

        return questions

    def _load_csv_questions(self, csv_path: Path) -> List[Dict[str, Any]]:
        """Convierte un CSV exportado manualmente en el formato esperado."""
        if not csv_path.exists():
            raise RuntimeError(f"No se encontró el archivo CSV: {csv_path}")

        def pick(row: Dict[str, str], keys: List[str], default: str = "") -> str:
            for key in keys:
                if key in row and row[key]:
                    return row[key]
            return default

        mapped: List[Dict[str, Any]] = []
        with csv_path.open("r", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            for idx, row in enumerate(reader, start=1):
                mapped.append(
                    {
                        "id": pick(row, ["id", "question_id", "pregunta_id", "codigo"]) or f"csv_{idx}",
                        "date_created": pick(
                            row,
                            [
                                "date_created",
                                "date",
                                "fecha",
                                "fecha_pregunta",
                            ],
                        ),
                        "item_id": pick(row, ["item_id", "publicacion", "listing_id"]),
                        "status": pick(row, ["status", "estado_pregunta"], "UNANSWERED"),
                        "text": pick(row, ["text", "question", "pregunta", "mensaje"]),
                        "answer": {
                            "text": pick(row, ["answer_text", "respuesta", "respuesta_texto"]),
                            "status": pick(row, ["answer_status", "estado_respuesta"], "UNANSWERED"),
                        },
                        "seller_id": pick(row, ["seller_id", "vendedor"]),
                        "from": {"id": pick(row, ["buyer_id", "usuario", "user_id"])},
                    }
                )
        return mapped

    def _normalize_question(self, question: Dict[str, Any]) -> MercadoLibreQuestion:
        """Simplifica la pregunta para facilitar su transformación posterior."""
        answer = question.get("answer") or {}

        return MercadoLibreQuestion(
            id=str(question.get("id")),
            date_created=question.get("date_created"),
            item_id=question.get("item_id"),
            status=question.get("status"),
            text=question.get("text", "").strip(),
            answer_text=answer.get("text"),
            answer_status=answer.get("status"),
            seller_id=str(question.get("seller_id") or ""),
            buyer_id=str((question.get("from") or {}).get("id") or ""),
        )

    def _build_knowledge_payload(
        self, questions: List[MercadoLibreQuestion], timestamp: str
    ) -> Dict[str, Any]:
        """Convierte las preguntas en interacciones para el consolidado."""
        interacciones: List[Dict[str, Any]] = []
        for question in questions:
            resultado = "respondido" if question.answer_text else "pendiente"
            interacciones.append(
                {
                    "id": f"meli_{question.id}",
                    "timestamp": question.date_created,
                    "cliente_id": question.buyer_id or "mercadolibre_cliente",
                    "tipo_interaccion": "consulta",
                    "mensaje_cliente": question.text,
                    "respuesta_agente": question.answer_text or "",
                    "contexto": {
                        "canal": "mercadolibre",
                        "item_id": question.item_id,
                        "estado_pregunta": question.status,
                        "estado_respuesta": question.answer_status,
                        "seller_id": question.seller_id,
                    },
                    "resultado": resultado,
                    "valor_cotizacion": None,
                    "valor_venta": None,
                    "satisfaccion_cliente": None,
                    "lecciones_aprendidas": [],
                }
            )

        return {
            "fuente": "mercadolibre_api",
            "descripcion": "Historial de preguntas/respuestas de Mercado Libre",
            "fecha_exportacion": timestamp,
            "interacciones": interacciones,
        }

    @staticmethod
    def _write_json(path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
    try:
        limit = int(os.getenv("MELI_PAGE_SIZE", str(DEFAULT_LIMIT)))
    except ValueError:
        limit = DEFAULT_LIMIT
    parser = argparse.ArgumentParser(description="Sincroniza preguntas de Mercado Libre")
    parser.add_argument(
        "--csv-export",
        dest="csv_export",
        help="Ruta a un CSV exportado manualmente desde Mercado Libre (opcional).",
    )
    args = parser.parse_args()

    try:
        syncer = MercadoLibreConversationSync(limit=limit, csv_export=args.csv_export)
        syncer.run()
    except RuntimeError as exc:
        print(f"⚠️  {exc}", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as exc:
        print(f"❌ Error HTTP al consultar Mercado Libre: {exc}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"❌ Error de red al consultar Mercado Libre: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

