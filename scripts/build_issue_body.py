#!/usr/bin/env python3
import json, pathlib, datetime as dt

OUT_DIR = pathlib.Path("out")
OUT_DIR.mkdir(exist_ok=True)

def today():
    return dt.date.today().isoformat()

def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    d = today()
    opp_json = OUT_DIR / f"opportunities_{d}.json"
    env_keys = OUT_DIR / "env_keys_unified.json"

    lines = []
    lines.append(f"# Cloud Agent — Daily ({d})")
    lines.append("")
    lines.append("## Oportunidades eCommerce (UY)")
    if opp_json.exists():
        opp = load_json(opp_json)
        for i, o in enumerate(opp["top"][:10], 1):
            lines.append(f"{i}. **{o['producto']}** — score {o['score']} — riesgo {o['riesgo']} — bundle: {o['bundle']}")
    else:
        lines.append("- (sin reporte de oportunidades hoy)")

    lines.append("")
    lines.append("## Unificación .env (keys-only)")
    if env_keys.exists():
        keys = load_json(env_keys)
        lines.append(f"- Total keys unificadas: **{len(keys)}**")
        lines.append("- Archivo: `env/.env.unified.example` (placeholders)")
        lines.append("- Artifacts: `env_inventory.json`, `env_keys_unified.json`")
    else:
        lines.append("- (sin inventario env hoy)")

    lines.append("")
    lines.append("## Riesgos (semáforo)")
    lines.append("- Verde: keys-only (sin valores) + artifacts")
    lines.append("- Amarillo: all repos + all branches puede pegar rate limits / tiempo")
    lines.append("- Rojo: token con permisos excesivos (usar read-only)")

    lines.append("")
    lines.append("## Próximos pasos")
    lines.append("- Conectar extractores reales (MLU/retailers/trends) y agregar evidencia url/fecha.")
    lines.append("- Ajustar `^(main|master|develop|dev|staging|production|release/|hotfix/)` y/o `50` para performance.")

    body = "\n".join(lines) + "\n"
    (OUT_DIR / "ISSUE_BODY.md").write_text(body, encoding="utf-8")

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
# body_sha256: TBD
