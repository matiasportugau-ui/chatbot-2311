#!/usr/bin/env python3
"""
Research eCommerce opportunities for Uruguay market.
This is a stub implementation ready to connect to real extractors (MLU/retailers/trends).

Usage:
    MARKET=Uruguay FOCUS="aislamiento, impermeabilización" python scripts/research_opportunities.py

Environment Variables:
    MARKET: Target market (default: Uruguay)
    FOCUS: Focus areas for product research

EXPORT_SEAL v1
project: bmc-uy
prompt_id: cloud-agent-pack
version: 1.0.0
file: scripts/research_opportunities.py
lang: py
created_at: 2025-12-14T00:00:00Z
author: Matias Portugau
origin: github-cloud-agent-blueprint
notes: Research stub + scoring; outputs JSON/MD to out/.
"""
import os
import json
import pathlib
import datetime as dt
from typing import Dict, List

import yaml

OUT_DIR = pathlib.Path("out")
OUT_DIR.mkdir(exist_ok=True)


def utc_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def today_str() -> str:
    """Return today's date in ISO format."""
    return dt.date.today().isoformat()


def load_weights() -> Dict:
    """Load scoring weights from config file."""
    with open("config/weights.yml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def score(item: Dict, w: Dict) -> float:
    """Calculate weighted score for an opportunity."""
    return round(100 * (
        w["demanda"] * item.get("demanda", 0.0) +
        w["margen_potencial"] * item.get("margen_potencial", 0.0) +
        w["fit_bmc"] * item.get("fit_bmc", 0.0) +
        w["facilidad_logistica"] * item.get("facilidad_logistica", 0.0) +
        w["ventaja_competitiva"] * item.get("ventaja_competitiva", 0.0)
    ), 2)


def generate_candidates_stub(focus: str) -> List[Dict]:
    """
    Generate candidate products for evaluation.
    
    TODO: Connect real extractors:
    - MercadoLibre API for demand data
    - Retailer scrapers for pricing
    - Google Trends for search volume
    
    Rule: Without verifiable evidence -> url/fecha = null, don't invent volumes/CPC/ROI
    """
    return [
        {
            "producto": "Espuma PU expansiva 750ml",
            "focus": focus,
            "evidencia": {"url": None, "fecha": None, "nota": "stub (sin extractor real)"},
            "bundle": "espuma + limpiador + boquillas + guantes",
            "riesgo": "Verde",
            "demanda": 0.75,
            "margen_potencial": 0.65,
            "fit_bmc": 0.70,
            "facilidad_logistica": 0.90,
            "ventaja_competitiva": 0.55
        },
        {
            "producto": "Cinta aluminio reforzada",
            "focus": focus,
            "evidencia": {"url": None, "fecha": None, "nota": "stub (sin extractor real)"},
            "bundle": "cinta + rollo aislante",
            "riesgo": "Verde",
            "demanda": 0.70,
            "margen_potencial": 0.55,
            "fit_bmc": 0.80,
            "facilidad_logistica": 0.95,
            "ventaja_competitiva": 0.50
        },
        {
            "producto": "Membrana asfáltica 4mm",
            "focus": focus,
            "evidencia": {"url": None, "fecha": None, "nota": "stub (sin extractor real)"},
            "bundle": "membrana + primer + soplete",
            "riesgo": "Amarillo",
            "demanda": 0.80,
            "margen_potencial": 0.60,
            "fit_bmc": 0.85,
            "facilidad_logistica": 0.70,
            "ventaja_competitiva": 0.65
        },
        {
            "producto": "Sellador poliuretano 600ml",
            "focus": focus,
            "evidencia": {"url": None, "fecha": None, "nota": "stub (sin extractor real)"},
            "bundle": "sellador + aplicador + guantes",
            "riesgo": "Verde",
            "demanda": 0.65,
            "margen_potencial": 0.70,
            "fit_bmc": 0.75,
            "facilidad_logistica": 0.95,
            "ventaja_competitiva": 0.60
        },
        {
            "producto": "Lana de vidrio rollo 50mm",
            "focus": focus,
            "evidencia": {"url": None, "fecha": None, "nota": "stub (sin extractor real)"},
            "bundle": "lana + cinta + guantes + mascara",
            "riesgo": "Verde",
            "demanda": 0.60,
            "margen_potencial": 0.50,
            "fit_bmc": 0.70,
            "facilidad_logistica": 0.80,
            "ventaja_competitiva": 0.45
        }
    ]


def render_md(payload: Dict) -> str:
    """Render the opportunities report as Markdown."""
    lines = []
    lines.append(f"# Reporte diario oportunidades ({payload['date']})")
    lines.append("")
    lines.append(f"- **market**: {payload['market']}")
    lines.append(f"- **focus**: {payload['focus']}")
    lines.append(f"- **created_at_utc**: {payload['created_at_utc']}")
    lines.append("")
    lines.append("## Top oportunidades")
    lines.append("")
    lines.append("| # | Producto | Score | Riesgo | Bundle |")
    lines.append("|---|----------|-------|--------|--------|")
    for i, o in enumerate(payload["top"], 1):
        lines.append(f"| {i} | {o['producto']} | {o['score']} | {o['riesgo']} | {o['bundle']} |")
    lines.append("")
    lines.append("## #ZonaDesconocida")
    lines.append("")
    for z in payload["zona_desconocida"]:
        lines.append(f"- {z}")
    lines.append("")
    lines.append("## Próximos pasos")
    lines.append("")
    lines.append("1. Conectar extractores reales (MLU/retailers/trends)")
    lines.append("2. Agregar evidencia URL y fecha de verificación")
    lines.append("3. Calcular ROI real con costos de proveedor")
    lines.append("")
    return "\n".join(lines)


def main():
    market = os.getenv("MARKET", "Uruguay")
    focus = os.getenv("FOCUS", "aislamiento, impermeabilización, construcción, techos, selladores")
    w = load_weights()

    candidates = generate_candidates_stub(focus)
    for c in candidates:
        c["score"] = score(c, w)

    top = sorted(candidates, key=lambda x: x["score"], reverse=True)[:10]

    payload = {
        "date": today_str(),
        "market": market,
        "focus": focus,
        "created_at_utc": utc_iso(),
        "top": top,
        "zona_desconocida": [
            "Extractores reales (MLU/retailers/trends) aún no conectados; evidencia url/fecha queda en null.",
            "Faltan costos de proveedor para ROI/margen real (no se inventan).",
            "Datos de competencia y volumen de búsqueda pendientes."
        ]
    }

    (OUT_DIR / f"opportunities_{payload['date']}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / f"opportunities_{payload['date']}.md").write_text(
        render_md(payload), encoding="utf-8"
    )

    print(f"[done] Generated opportunities report for {payload['date']}")
    print(f"[info] Top product: {top[0]['producto']} (score: {top[0]['score']})")


if __name__ == "__main__":
    main()
