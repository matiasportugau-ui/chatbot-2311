#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Almacenamiento ligero en SQLite para snapshots de preguntas de Mercado Libre.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
PERSISTENCE_DIR = DATA_DIR / "persistence"
PERSISTENCE_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = PERSISTENCE_DIR / "ingestion.sqlite3"


class MercadoLibreStore:
    """Encapsula operaciones básicas sobre SQLite."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mercadolibre_qna (
                question_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                item_id TEXT,
                seller_id TEXT,
                buyer_id TEXT,
                status TEXT,
                answered INTEGER,
                run_id TEXT NOT NULL,
                source_file TEXT,
                hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                imported_at TEXT NOT NULL
            )
            """
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_qna_run ON mercadolibre_qna (run_id, imported_at)"
        )
        self.conn.commit()

    def store_snapshot(self, run_id: str, payload: Dict[str, Any]) -> None:
        """Inserta/actualiza preguntas desde un snapshot crudo."""
        source_file = payload.get("metadata", {}).get("source_file", "")
        preguntas = payload.get("questions", [])
        now = datetime.now(timezone.utc).isoformat()
        registros = 0
        with self.conn:
            for question in preguntas:
                question_id = str(question.get("id"))
                registro = self._prepare_record(question, run_id, source_file, now)
                self.conn.execute(
                    """
                    INSERT INTO mercadolibre_qna (
                        question_id, payload, item_id, seller_id, buyer_id, status,
                        answered, run_id, source_file, hash, created_at, imported_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(question_id) DO UPDATE SET
                        payload=excluded.payload,
                        status=excluded.status,
                        answered=excluded.answered,
                        run_id=excluded.run_id,
                        source_file=excluded.source_file,
                        hash=excluded.hash,
                        imported_at=excluded.imported_at
                    """,
                    registro,
                )
                registros += 1
        print(f"💾 {registros} preguntas almacenadas en SQLite (run_id={run_id}).")

    def _prepare_record(
        self, question: Dict[str, Any], run_id: str, source_file: str, imported_at: str
    ) -> Tuple[Any, ...]:
        payload_str = json.dumps(question, ensure_ascii=False)
        hash_value = hashlib.sha1(payload_str.encode("utf-8")).hexdigest()
        answer = question.get("answer") or {}
        answered = 1 if answer.get("text") else 0
        buyer_id = (question.get("from") or {}).get("id")
        created_at = question.get("date_created") or imported_at

        return (
            str(question.get("id")),
            payload_str,
            question.get("item_id"),
            str(question.get("seller_id") or ""),
            str(buyer_id or ""),
            question.get("status"),
            answered,
            run_id,
            source_file,
            hash_value,
            created_at,
            imported_at,
        )

    def list_snapshots(self) -> List[sqlite3.Row]:
        query = """
        SELECT run_id,
               COUNT(*) AS total,
               MIN(created_at) AS desde,
               MAX(created_at) AS hasta,
               MAX(imported_at) AS importado
        FROM mercadolibre_qna
        GROUP BY run_id
        ORDER BY importado DESC
        """
        cur = self.conn.execute(query)
        return cur.fetchall()

    def export_snapshot(self, output_path: Path) -> None:
        """Exporta el snapshot más reciente a conocimiento_mercadolibre.json."""
        run_id = self._latest_run_id()
        if not run_id:
            print("⚠️  No hay datos de Mercado Libre para exportar.")
            return
        registros = self._rows_for_run(run_id)
        interacciones = [
            self._row_to_interaccion(row)  # type: ignore[arg-type]
            for row in registros
        ]
        payload = {
            "fuente": "mercadolibre_api",
            "descripcion": "Historial de preguntas/respuestas de Mercado Libre",
            "fecha_exportacion": datetime.now(timezone.utc).isoformat(),
            "interacciones": interacciones,
        }
        with output_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        print(f"📤 Snapshot {run_id} exportado a {output_path} ({len(interacciones)} interacciones).")

    def purge_old_runs(self, keep: int) -> None:
        """Conserva únicamente los últimos 'keep' snapshots."""
        runs = [row["run_id"] for row in self.list_snapshots()]
        to_delete = runs[keep:]
        if not to_delete:
            print("ℹ️  No hay snapshots para purgar.")
            return
        with self.conn:
            self.conn.executemany(
                "DELETE FROM mercadolibre_qna WHERE run_id = ?", [(run,) for run in to_delete]
            )
        print(f"🧹 {len(to_delete)} snapshots purgados: {', '.join(to_delete)}")

    def _latest_run_id(self) -> str | None:
        cur = self.conn.execute(
            "SELECT run_id FROM mercadolibre_qna ORDER BY imported_at DESC LIMIT 1"
        )
        row = cur.fetchone()
        return row["run_id"] if row else None

    def _rows_for_run(self, run_id: str) -> Iterable[sqlite3.Row]:
        cur = self.conn.execute(
            "SELECT * FROM mercadolibre_qna WHERE run_id = ? ORDER BY created_at ASC", (run_id,)
        )
        return cur.fetchall()

    @staticmethod
    def _row_to_interaccion(row: sqlite3.Row) -> Dict[str, Any]:
        question = json.loads(row["payload"])
        answer = question.get("answer") or {}
        resultado = "respondido" if answer.get("text") else "pendiente"
        return {
            "id": f"meli_{row['question_id']}",
            "timestamp": row["created_at"],
            "cliente_id": str((question.get("from") or {}).get("id") or "mercadolibre_cliente"),
            "tipo_interaccion": "consulta",
            "mensaje_cliente": question.get("text", ""),
            "respuesta_agente": answer.get("text") or "",
            "contexto": {
                "canal": "mercadolibre",
                "item_id": question.get("item_id"),
                "estado_pregunta": question.get("status"),
                "estado_respuesta": answer.get("status"),
                "seller_id": str(question.get("seller_id") or ""),
            },
            "resultado": resultado,
            "valor_cotizacion": None,
            "valor_venta": None,
            "satisfaccion_cliente": None,
            "lecciones_aprendidas": [],
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Herramientas para snapshots de Mercado Libre.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="Lista snapshots disponibles")

    export_parser = subparsers.add_parser("export", help="Exporta el snapshot más reciente")
    export_parser.add_argument(
        "--output",
        type=Path,
        default=Path("conocimiento_mercadolibre.json"),
        help="Archivo de destino",
    )

    purge_parser = subparsers.add_parser("purge", help="Purgar snapshots antiguos")
    purge_parser.add_argument(
        "--keep",
        type=int,
        default=3,
        help="Cantidad de snapshots recientes a conservar",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    store = MercadoLibreStore()
    if args.command == "list":
        rows = store.list_snapshots()
        if not rows:
            print("ℹ️  Aún no hay snapshots almacenados.")
            return
        for row in rows:
            print(
                f"- run_id={row['run_id']} · preguntas={row['total']} · "
                f"{row['desde']} → {row['hasta']} · importado={row['importado']}"
            )
    elif args.command == "export":
        store.export_snapshot(args.output)
    elif args.command == "purge":
        store.purge_old_runs(args.keep)
    else:
        print("Comandos disponibles: list | export | purge")


if __name__ == "__main__":
    main()

