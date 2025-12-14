#!/usr/bin/env python3
"""
Build the daily GitHub issue body from cloud agent outputs.

Usage:
    python scripts/build_issue_body.py

Outputs:
    out/ISSUE_BODY.md - Markdown content for the daily issue

EXPORT_SEAL v1
project: bmc-uy
prompt_id: cloud-agent-pack
version: 1.0.0
file: scripts/build_issue_body.py
lang: py
created_at: 2025-12-14T00:00:00Z
author: Matias Portugau
origin: github-cloud-agent-blueprint
"""
import json
import pathlib
import datetime as dt
from typing import Optional

OUT_DIR = pathlib.Path("out")
OUT_DIR.mkdir(exist_ok=True)


def today() -> str:
    """Return today's date in ISO format."""
    return dt.date.today().isoformat()


def load_json(path: pathlib.Path) -> Optional[dict]:
    """Load JSON file if it exists."""
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    d = today()
    opp_json = OUT_DIR / f"opportunities_{d}.json"
    env_keys = OUT_DIR / "env_keys_unified.json"
    env_inventory = OUT_DIR / "env_inventory.json"

    lines = []
    lines.append(f"# Cloud Agent — Daily Report ({d})")
    lines.append("")
    
    # Opportunities section
    lines.append("## 🛒 Oportunidades eCommerce (UY)")
    lines.append("")
    if opp_json.exists():
        opp = load_json(opp_json)
        if opp and opp.get("top"):
            lines.append("| # | Producto | Score | Riesgo | Bundle |")
            lines.append("|---|----------|-------|--------|--------|")
            for i, o in enumerate(opp["top"][:10], 1):
                lines.append(f"| {i} | {o['producto']} | {o['score']} | {o['riesgo']} | {o['bundle']} |")
            lines.append("")
            lines.append(f"> **Focus**: {opp.get('focus', 'N/A')}")
            lines.append(f"> **Market**: {opp.get('market', 'Uruguay')}")
        else:
            lines.append("- (sin datos de oportunidades)")
    else:
        lines.append("- (sin reporte de oportunidades hoy)")

    lines.append("")
    
    # Env scan section
    lines.append("## 🔑 Unificación .env (keys-only)")
    lines.append("")
    if env_keys.exists():
        keys = load_json(env_keys)
        inventory = load_json(env_inventory) if env_inventory.exists() else []
        
        repos_with_env = sum(1 for r in inventory if r.get("branches"))
        total_repos = len(inventory) if inventory else 0
        
        lines.append(f"- **Total keys unificadas**: {len(keys)}")
        lines.append(f"- **Repos escaneados**: {total_repos}")
        lines.append(f"- **Repos con .env files**: {repos_with_env}")
        lines.append("")
        lines.append("**Archivos generados:**")
        lines.append("- `env/.env.unified.example` (template con placeholders)")
        lines.append("- `out/env_inventory.json` (inventario completo)")
        lines.append("- `out/env_keys_unified.json` (lista de keys)")
        lines.append("")
        if keys:
            lines.append("<details>")
            lines.append("<summary>Ver todas las keys encontradas</summary>")
            lines.append("")
            lines.append("```")
            for k in keys[:50]:  # Limit to first 50
                lines.append(k)
            if len(keys) > 50:
                lines.append(f"... y {len(keys) - 50} más")
            lines.append("```")
            lines.append("</details>")
    else:
        lines.append("- (sin inventario env hoy)")

    lines.append("")
    
    # Risk assessment section
    lines.append("## 🚦 Semáforo de Riesgos")
    lines.append("")
    lines.append("| Estado | Descripción |")
    lines.append("|--------|-------------|")
    lines.append("| 🟢 Verde | Keys-only (sin valores) + artifacts seguros |")
    lines.append("| 🟡 Amarillo | Muchos repos/branches → posibles rate limits |")
    lines.append("| 🔴 Rojo | Token con permisos excesivos (usar read-only) |")

    lines.append("")
    
    # Next steps section
    lines.append("## 📋 Próximos pasos")
    lines.append("")
    lines.append("1. [ ] Conectar extractores reales (MLU/retailers/trends)")
    lines.append("2. [ ] Agregar evidencia URL y fecha de verificación")
    lines.append("3. [ ] Ajustar `BRANCH_ALLOW_REGEX` y/o `BRANCH_LIMIT` para performance")
    lines.append("4. [ ] Integrar costos de proveedor para cálculo de ROI real")

    lines.append("")
    lines.append("---")
    lines.append(f"*Generado automáticamente por Cloud Agent - {d}*")

    body = "\n".join(lines) + "\n"
    (OUT_DIR / "ISSUE_BODY.md").write_text(body, encoding="utf-8")
    
    print(f"[done] Generated issue body: out/ISSUE_BODY.md")


if __name__ == "__main__":
    main()
