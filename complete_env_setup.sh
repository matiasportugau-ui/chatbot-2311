#!/usr/bin/env bash
set -euo pipefail
ROOT="$(pwd)"
echo "🔎 Working in: $ROOT"

# 1) Traer archivos desde .cursor/plans si existen allí
for f in fill_env.py fill_env.sh mapping.json secrets.json; do
  if [ ! -f "$ROOT/$f" ] && [ -f "$ROOT/.cursor/plans/$f" ]; then
    echo "📦 copiando .cursor/plans/$f -> $f"
    cp -v "$ROOT/.cursor/plans/$f" "$ROOT/$f"
  fi
done

# 2) Asegurar .env.template (usar .env.unified o .env.example)
if [ ! -f ".env.template" ]; then
  if [ -f ".env.unified" ]; then
    cp -v .env.unified .env.template
    echo "✅ .env.template creado desde .env.unified"
  elif [ -f ".env.example" ]; then
    cp -v .env.example .env.template
    echo "✅ .env.template creado desde .env.example"
  else
    echo "❌ No existe .env.unified ni .env.example. Crea .env.template manualmente y re-ejecuta."
    exit 1
  fi
else
  echo "✅ .env.template ya existe"
fi

# 3) Asegurar secrets.json (plantilla) si no existe
if [ ! -f "secrets.json" ]; then
  cat > secrets.json <<'JSON'
{
  "NEXTAUTH_SECRET": "",
  "WHATSAPP_VERIFY_TOKEN": "",
  "WHATSAPP_ACCESS_TOKEN": "",
  "WHATSAPP_PHONE_NUMBER_ID": "",
  "WHATSAPP_BUSINESS_ID": "",
  "WHATSAPP_APP_SECRET": "",
  "GOOGLE_SHEETS_API_KEY": "",
  "SENTRY_DSN": "",
  "N8N_API_KEY": "",
  "N8N_PUBLIC_KEY": "",
  "N8N_PRIVATE_KEY": ""
}
JSON
  chmod 600 secrets.json
  echo "✅ secrets.json creado (modo plantilla, rellena los valores REPLACE_... si hace falta)"
else
  echo "✅ secrets.json ya existe (verifícalo)"
fi

# 4) Generar NEXTAUTH_SECRET si está vacío
NEEDS_SECRET=$(python3 - <<PY
import json, os,sys
f='secrets.json'
try:
    d=json.load(open(f))
except Exception:
    print("true"); sys.exit(0)
v=d.get('NEXTAUTH_SECRET')
print('true' if (v is None or v=='') else 'false')
PY
)
if [ "$NEEDS_SECRET" = "true" ]; then
  SECRET=$(openssl rand -hex 32)
  python3 - "$SECRET" <<PY
import json,sys
f='secrets.json'
d={}
try:
    d=json.load(open(f))
except Exception:
    d={}
d['NEXTAUTH_SECRET']=sys.argv[1]
json.dump(d, open(f,'w'), indent=2)
print("✅ NEXTAUTH_SECRET generado y guardado en secrets.json (no mostrado).")
PY
  unset SECRET
else
  echo "✅ NEXTAUTH_SECRET ya presente en secrets.json"
fi

# 5) Asegurar que fill_env.py exista (si no, avisar)
if [ ! -f "fill_env.py" ]; then
  echo "❌ fill_env.py no encontrado en la raíz. Intenta copiarlo desde .cursor/plans o crear el archivo."
  echo "Sugerencia: cp .cursor/plans/fill_env.py ."
  exit 1
fi

# 6) Ejecutar fill_env.py
echo "▶️ Generando .env usando fill_env.py"
python3 fill_env.py -t .env.template -o .env -m mapping.json -s secrets.json

# 7) Resultado
if [ -f .env ]; then
  chmod 600 .env
  echo "🎉 .env generado con permisos 600"
  ls -l .env
else
  echo "❌ .env no fue creado. Revisa errores anteriores."
  exit 2
fi

echo "FIN. Revisa secrets.json y .env localmente. No subas secrets.json ni .env al repo."
