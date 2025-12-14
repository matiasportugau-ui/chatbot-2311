#!/usr/bin/env python3
import os, json, pathlib, datetime as dt
import yaml

OUT_DIR = pathlib.Path("out")
OUT_DIR.mkdir(exist_ok=True)

def utc_iso():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

def today_str():
    return dt.date.today().isoformat()

def load_weights():
    with open("config/weights.yml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def score(item, w):
    return round(100 * (
        w["demanda"] * item.get("demanda", 0.0) +
        w["margen_potencial"] * item.get("margen_potencial", 0.0) +
        w["fit_bmc"] * item.get("fit_bmc", 0.0) +
        w["facilidad_logistica"] * item.get("facilidad_logistica", 0.0) +
        w["ventaja_competitiva"] * item.get("ventaja_competitiva", 0.0)
    ), 2)

def generate_candidates_stub(focus: str):
    # TODO: conectar extractores reales (MLU/retailers/trends)
    # Regla: sin evidencia verificable -> url/fecha = null, no inventar volúmenes/CPC/ROI
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
        }
    ]

def render_md(payload):
    lines = []
    lines.append(f"# Reporte diario oportunidades ({payload['date']})")
    lines.append("")
    lines.append(f"- market: {payload['market']}")
    lines.append(f"- focus: {payload['focus']}")
    lines.append(f"- created_at_utc: {payload['created_at_utc']}")
    lines.append("")
    lines.append("## Top oportunidades")
    for i, o in enumerate(payload["top"], 1):
        lines.append(f"{i}. **{o['producto']}** — score: {o['score']} — riesgo: {o['riesgo']} — bundle: {o['bundle']}")
    lines.append("")
    lines.append("## #ZonaDesconocida")
    for z in payload["zona_desconocida"]:
        lines.append(f"- {z}")
    return "\n".join(lines) + "\n"

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
            "Faltan costos de proveedor para ROI/margen real (no se inventan)."
        ]
    }

    (OUT_DIR / f"opportunities_{payload['date']}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / f"opportunities_{payload['date']}.md").write_text(render_md(payload), encoding="utf-8")

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
# body_sha256: TBD
# notes: Research stub + scoring; outputs JSON/MD to out/.
