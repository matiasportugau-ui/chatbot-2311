#!/usr/bin/env python3
# upload_secrets_gh.py — sube claves no vacías desde secrets.json a GitHub (stdin)
import json, os, subprocess, sys

REPO = "matiasportugau-ui/chatbot-2311"   # <-- confirma si es correcto
APP  = "codespaces"                       # "codespaces" o "actions"

F = "secrets.json"
if not os.path.exists(F):
    print(f"ERROR: {F} no existe")
    sys.exit(1)

with open(F, "r", encoding="utf-8") as fh:
    try:
        data = json.load(fh)
    except Exception as e:
        print("ERROR: no pude parsear secrets.json:", e)
        sys.exit(1)

count_total = 0
count_uploaded = 0
for k, v in data.items():
    count_total += 1
    if v is None or str(v).strip() == "":
        print(f"SKIP  {k}: vacío")
        continue
    # call gh using stdin to avoid exposing value on cmdline
    p = subprocess.run(
        ["gh", "secret", "set", k, "--repo", REPO, "--app", APP],
        input=str(v).encode("utf-8"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if p.returncode == 0:
        print(f"✅ {k}")
        count_uploaded += 1
    else:
        err = p.stderr.decode().strip()
        print(f"❌ {k}: {err}")

print(f"\nResumen: {count_uploaded}/{count_total} secrets subidos (no vacíos).")
if count_uploaded > 0:
    print("Verifica: gh secret list --repo", REPO, "--app", APP)
