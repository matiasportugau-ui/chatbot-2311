#!/usr/bin/env python3
"""
Research opportunities stub + scoring system.
Ready to plug in real extractors (MLU/retailers/trends).

IMPORTANT: No invented data! If no real extractor is connected,
evidencia.url and evidencia.fecha remain null.

Outputs:
  - out/opportunities_YYYY-MM-DD.json
  - out/opportunities_YYYY-MM-DD.md
"""
import os
import json
import pathlib
import datetime as dt

import yaml

OUT_DIR = pathlib.Path("out")
OUT_DIR.mkdir(exist_ok=True)


def utc_iso():
    """Return current UTC time in ISO format."""
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def today_str():
    """Return today's date in ISO format."""
    return dt.date.today().isoformat()


def load_weights():
    """Load scoring weights from config file."""
    with open("config/weights.yml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def score(item: dict, w: dict) -> float:
    """Calculate weighted score for an opportunity."""
    return round(100 * (
        w["demanda"] * item.get("demanda", 0.0) +
        w["margen_potencial"] * item.get("margen_potencial", 0.0) +
        w["fit_bmc"] * item.get("fit_bmc", 0.0) +
        w["facilidad_logistica"] * item.get("facilidad_logistica", 0.0) +
        w["ventaja_competitiva"] * item.get("ventaja_competitiva", 0.0)
    ), 2)


def generate_candidates_stub(focus: str) -> list:
    """
    Generate candidate opportunities (STUB).
    
    TODO: Connect real extractors:
    - MercadoLibre API
    - Retailer scrapers
    - Google Trends API
    
    RULE: Without verifiable evidence, url/fecha = null (no invention!)
    """
    return [
        {
            "producto": "Espuma PU expansiva 750ml",
            "focus": focus,
            "evidencia": {
                "url": None,
                "fecha": None,
                "nota": "stub (sin extractor real conectado)"
            },
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
            "evidencia": {
                "url": None,
                "fecha": None,
                "nota": "stub (sin extractor real conectado)"
            },
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
            "evidencia": {
                "url": None,
                "fecha": None,
                "nota": "stub (sin extractor real conectado)"
            },
            "bundle": "membrana + primer + soplete",
            "riesgo": "Amarillo",
            "demanda": 0.80,
            "margen_potencial": 0.70,
            "fit_bmc": 0.75,
            "facilidad_logistica": 0.60,
            "ventaja_competitiva": 0.65
        },
        {
            "producto": "Sellador poliuretano 600ml",
            "focus": focus,
            "evidencia": {
                "url": None,
                "fecha": None,
                "nota": "stub (sin extractor real conectado)"
            },
            "bundle": "sellador + pistola aplicadora",
            "riesgo": "Verde",
            "demanda": 0.65,
            "margen_potencial": 0.60,
            "fit_bmc": 0.85,
            "facilidad_logistica": 0.90,
            "ventaja_competitiva": 0.45
        },
        {
            "producto": "Panel aislante XPS 50mm",
            "focus": focus,
            "evidencia": {
                "url": None,
                "fecha": None,
                "nota": "stub (sin extractor real conectado)"
            },
            "bundle": "panel + adhesivo + fijaciones",
            "riesgo": "Amarillo",
            "demanda": 0.70,
            "margen_potencial": 0.55,
            "fit_bmc": 0.70,
            "facilidad_logistica": 0.50,
            "ventaja_competitiva": 0.60
        }
    ]


def render_md(payload: dict) -> str:
    """Render opportunities report as Markdown."""
    lines = []
    lines.append(f"# Reporte diario oportunidades ({payload['date']})")
    lines.append("")
    lines.append(f"- **Market:** {payload['market']}")
    lines.append(f"- **Focus:** {payload['focus']}")
    lines.append(f"- **Created at (UTC):** {payload['created_at_utc']}")
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
    lines.append("---")
    lines.append("")
    lines.append("*Generado automáticamente por Cloud Agent*")
    return "\n".join(lines) + "\n"


def main():
    market = os.getenv("MARKET", "Uruguay")
    focus = os.getenv("FOCUS", "aislamiento, impermeabilización, construcción, techos, selladores")
    
    print(f"[research] Market: {market}")
    print(f"[research] Focus: {focus}")
    
    w = load_weights()
    print(f"[research] Weights loaded: {w}")

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
            "Bundle suggestions son estimaciones basadas en productos complementarios típicos."
        ]
    }

    # Write outputs
    json_path = OUT_DIR / f"opportunities_{payload['date']}.json"
    md_path = OUT_DIR / f"opportunities_{payload['date']}.md"
    
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_md(payload), encoding="utf-8")

    print(f"[done] Generated {len(top)} opportunities")
    print(f"[done] Outputs: {json_path}, {md_path}")


if __name__ == "__main__":
    main()

# EXPORT_SEAL v1
# project: bmc-uy
# prompt_id: cloud-agent-pack
# version: 1.0.0
# file: scripts/research_opportunities.py
# lang: py
# created_at: 2025-12-14T00:00:00Z
# author: Matias Portugau
# origin: github-cloud-agent-blueprint
# notes: Research stub + scoring; outputs JSON/MD to out/.
