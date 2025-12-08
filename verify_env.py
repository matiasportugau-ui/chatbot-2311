import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv('.env.unified', override=True)

# List of required environment variables (extracted from .env template)
REQUIRED_VARS = [
    "NEXT_PUBLIC_API_URL",
    "NEXT_PUBLIC_WS_URL",
    "PY_CHAT_SERVICE_URL",
    "NEXTAUTH_URL",
    "NEXTAUTH_SECRET",
    "DATABASE_URL",
    "MONGODB_URI",
    "WHATSAPP_VERIFY_TOKEN",
    "WHATSAPP_ACCESS_TOKEN",
    "WHATSAPP_PHONE_NUMBER_ID",
    "WHATSAPP_BUSINESS_ID",
    "WHATSAPP_APP_SECRET",
    "N8N_WEBHOOK_URL_EXTERNAL",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "OPENAI_ORGANIZATION_ID",
    "OPENAI_PROJECT_ID",
    "GROQ_API_KEY",
    "GEMINI_API_KEY",
    "XAI_API_KEY",
    "MODEL_STRATEGY",
    "N8N_BASE_URL",
    "N8N_API_KEY",
    "N8N_PUBLIC_KEY",
    "N8N_PRIVATE_KEY",
    "MERCADO_LIBRE_APP_ID",
    "MERCADO_LIBRE_CLIENT_SECRET",
    "MERCADO_LIBRE_REDIRECT_URI",
    "MERCADO_LIBRE_SELLER_ID",
    "MERCADO_LIBRE_WEBHOOK_SECRET",
    "MERCADO_LIBRE_AUTH_URL",
    "MERCADO_LIBRE_API_URL",
    "MERCADO_LIBRE_SCOPES",
    "MERCADO_LIBRE_PKCE_ENABLED",
    "GOOGLE_SHEET_ID",
    "GOOGLE_SERVICE_ACCOUNT_EMAIL",
    "GOOGLE_PRIVATE_KEY",
    "GOOGLE_SHEETS_API_KEY",
    "NODE_ENV",
    "LOG_LEVEL",
    "ENABLE_REQUEST_TRACKING",
    "NEXT_PUBLIC_ENABLE_AI_INSIGHTS",
    "NEXT_PUBLIC_ENABLE_REAL_TIME_MONITORING",
    "NEXT_PUBLIC_ENABLE_EXPORT_IMPORT",
    "SHOPIFY_PAGE_SIZE",
    "RUN_SHOPIFY_SYNC",
    "MELI_REFRESH_TOKEN",
    "MELI_PAGE_SIZE",
    "RUN_MELI_SYNC",
    "GITHUB_API_KEY",
]

missing = []
for var in REQUIRED_VARS:
    if not os.getenv(var):
        missing.append(var)

if missing:
    print("Missing environment variables:")
    for var in missing:
        print(f" - {var}")
    exit(1)
else:
    print("All required environment variables are set.")
    exit(0)
