#!/usr/bin/env python3
"""
Build the daily GitHub issue body from generated outputs.

Reads:
  - out/opportunities_YYYY-MM-DD.json
  - out/env_keys_unified.json

Outputs:
  - out/ISSUE_BODY.md
"""
import json
import pathlib
import datetime as dt

OUT_DIR = pathlib.Path("out")
OUT_DIR.mkdir(exist_ok=True)


def today():
    """Return today's date in ISO format."""
    return dt.date.today().isoformat()


def load_json(path: pathlib.Path) -> dict | list:
    """Load JSON file if it exists."""
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    d = today()
    opp_json = OUT_DIR / f"opportunities_{d}.json"
    env_keys = OUT_DIR / "env_keys_unified.json"

    lines = []
    lines.append(f"# ☁️ Cloud Agent — Daily Report ({d})")
    lines.append("")
    
    # Opportunities section
    lines.append("## 🛒 Oportunidades eCommerce (UY)")
    lines.append("")
    if opp_json.exists():
        opp = load_json(opp_json)
        lines.append(f"**Market:** {opp.get('market', 'N/A')} | **Focus:** {opp.get('focus', 'N/A')}")
        lines.append("")
        lines.append("| # | Producto | Score | Riesgo | Bundle |")
        lines.append("|---|----------|-------|--------|--------|")
        for i, o in enumerate(opp.get("top", [])[:10], 1):
            lines.append(f"| {i} | {o['producto']} | {o['score']} | {o['riesgo']} | {o['bundle']} |")
        lines.append("")
        lines.append("<details>")
        lines.append("<summary>📋 Zona Desconocida (gaps pendientes)</summary>")
        lines.append("")
        for z in opp.get("zona_desconocida", []):
            lines.append(f"- {z}")
        lines.append("")
        lines.append("</details>")
    else:
        lines.append("- ⚠️ Sin reporte de oportunidades hoy")
    lines.append("")

    # Env scan section
    lines.append("## 🔑 Unificación .env (keys-only)")
    lines.append("")
    if env_keys.exists():
        keys = load_json(env_keys)
        lines.append(f"- **Total keys unificadas:** `{len(keys)}`")
        lines.append("- **Archivo:** `env/.env.unified.example` (placeholders)")
        lines.append("- **Artifacts:** `env_inventory.json`, `env_keys_unified.json`")
        lines.append("")
        if keys:
            lines.append("<details>")
            lines.append("<summary>📋 Keys encontradas (expandir)</summary>")
            lines.append("")
            lines.append("```")
            for k in keys[:50]:  # Limit display
                lines.append(k)
            if len(keys) > 50:
                lines.append(f"... y {len(keys) - 50} más")
            lines.append("```")
            lines.append("")
            lines.append("</details>")
    else:
        lines.append("- ⚠️ Sin inventario env hoy")
    lines.append("")

    # Risk semaphore
    lines.append("## 🚦 Riesgos (semáforo)")
    lines.append("")
    lines.append("| Estado | Descripción |")
    lines.append("|--------|-------------|")
    lines.append("| 🟢 Verde | Keys-only scan (sin valores secretos) + artifacts generados |")
    lines.append("| 🟡 Amarillo | All repos + all branches puede causar rate limits / timeout |")
    lines.append("| 🔴 Rojo | Token con permisos excesivos (usar read-only, rotar si se expone) |")
    lines.append("")

    # Next steps
    lines.append("## 📌 Próximos pasos")
    lines.append("")
    lines.append("- [ ] Conectar extractores reales (MLU/retailers/trends) y agregar evidencia url/fecha")
    lines.append("- [ ] Ajustar `BRANCH_ALLOW_REGEX` y/o `BRANCH_LIMIT` para optimizar performance")
    lines.append("- [ ] Configurar costos de proveedor para cálculo de ROI/margen real")
    lines.append("- [ ] Revisar keys unificadas y actualizar `.env` de desarrollo")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*🤖 Generado automáticamente por [Cloud Agent](../../.github/workflows/cloud-agent-daily.yml)*")

    body = "\n".join(lines) + "\n"
    issue_path = OUT_DIR / "ISSUE_BODY.md"
    issue_path.write_text(body, encoding="utf-8")
    
    print(f"[done] Issue body written to {issue_path}")


if __name__ == "__main__":
    main()

# EXPORT_SEAL v1
# project: bmc-uy
# prompt_id: cloud-agent-pack
# version: 1.0.0
# file: scripts/build_issue_body.py
# lang: py
# created_at: 2025-12-14T00:00:00Z
# author: Matias Portugau
# origin: github-cloud-agent-blueprint
