#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración Automática del Chatbot BMC
Crea archivo .env con valores por defecto para desarrollo local
"""

import os
import secrets
from pathlib import Path

def create_env_file():
    """Crea archivo .env con configuración por defecto"""
    
    env_file = Path('.env.local')
    env_example = Path('env.example')
    
    # Leer env.example si existe
    base_config = {}
    if env_example.exists():
        for line in env_example.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                base_config[key.strip()] = value.strip().strip('"').strip("'")
    
    # Valores por defecto para desarrollo local
    default_config = {
        # API Configuration
        'NEXT_PUBLIC_API_URL': 'http://localhost:3001/api',
        'NEXT_PUBLIC_WS_URL': 'ws://localhost:3001/ws',
        'PY_CHAT_SERVICE_URL': 'http://localhost:8000',
        
        # Authentication
        'NEXTAUTH_URL': 'http://localhost:3000',
        'NEXTAUTH_SECRET': secrets.token_urlsafe(32),
        
        # Database
        'DATABASE_URL': 'postgresql://username:password@localhost:5432/bmc_dashboard',
        'MONGODB_URI': 'mongodb://localhost:27017/bmc_chat',
        'MELI_ACCESS_TOKEN': '',
        'MELI_SELLER_ID': '',
        
        # WhatsApp (opcional)
        'WHATSAPP_VERIFY_TOKEN': secrets.token_urlsafe(16),
        'WHATSAPP_ACCESS_TOKEN': '',
        'WHATSAPP_PHONE_NUMBER_ID': '',
        'WHATSAPP_BUSINESS_ID': '',
        'WHATSAPP_APP_SECRET': '',
        'N8N_WEBHOOK_URL_EXTERNAL': 'http://localhost:5678/webhook/whatsapp',
        
        # OpenAI (dejar vacío para usar pattern matching)
        'OPENAI_API_KEY': '',
        'OPENAI_MODELS': 'gpt-4o-mini,gpt-4o,gpt-3.5-turbo',
        'OPENAI_ORGANIZATION_ID': '',
        'OPENAI_PROJECT_ID': '',
        
        # Groq (opcional)
        'GROQ_API_KEY': '',
        'GROQ_MODELS': 'llama-3.1-70b-versatile,llama-3.1-8b-instant,mixtral-8x7b-32768',
        
        # Gemini (opcional)
        'GEMINI_API_KEY': '',
        'GEMINI_MODELS': 'gemini-2.5-flash,gemini-1.5-pro,gemini-3-pro',
        
        # Grok (opcional)
        'GROK_API_KEY': '',
        'GROK_MODELS': 'grok-beta,grok-2-1212,grok-4-latest',
        
        # Model Selection
        'MODEL_STRATEGY': 'balanced',
        
        # n8n
        'N8N_BASE_URL': 'http://localhost:5678',
        'N8N_API_KEY': '',
        'N8N_PUBLIC_KEY': '',
        'N8N_PRIVATE_KEY': '',
        
        # Mercado Libre
        'MERCADO_LIBRE_APP_ID': '',
        'MERCADO_LIBRE_CLIENT_SECRET': '',
        'MERCADO_LIBRE_REDIRECT_URI': 'http://localhost:3000/api/mercado-libre/auth/callback',
        'MERCADO_LIBRE_SELLER_ID': '',
        'MERCADO_LIBRE_WEBHOOK_SECRET': '',
        'MERCADO_LIBRE_AUTH_URL': 'https://auth.mercadolibre.com.uy',
        'MERCADO_LIBRE_API_URL': 'https://api.mercadolibre.com',
        'MERCADO_LIBRE_SCOPES': 'offline_access read write',
        'MERCADO_LIBRE_PKCE_ENABLED': 'true',
        
        # Google Sheets
        'GOOGLE_SHEET_ID': '1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0',
        'GOOGLE_SERVICE_ACCOUNT_EMAIL': '',
        'GOOGLE_PRIVATE_KEY': '',
        'GOOGLE_SHEETS_API_KEY': '',
        
        # System
        'NODE_ENV': 'development',
        'LOG_LEVEL': 'INFO',
        'ENABLE_REQUEST_TRACKING': 'true',
        
        # Feature Flags
        'NEXT_PUBLIC_ENABLE_AI_INSIGHTS': 'true',
        'NEXT_PUBLIC_ENABLE_REAL_TIME_MONITORING': 'true',
        'NEXT_PUBLIC_ENABLE_EXPORT_IMPORT': 'true',
        
        # Shopify
        'SHOPIFY_PAGE_SIZE': '250',
        'RUN_SHOPIFY_SYNC': 'true',
        
        # Mercado Libre ingestion
        'MELI_REFRESH_TOKEN': '',
        'MELI_PAGE_SIZE': '250',
        'RUN_MELI_SYNC': 'true',
    }
    
    # Combinar: base_config (de env.example) tiene prioridad, luego default_config
    final_config = {**default_config, **base_config}
    
    # Si existe .env.local, leerlo y preservar valores existentes
    if env_file.exists():
        existing_config = {}
        for line in env_file.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                value = value.strip().strip('"').strip("'")
                if value:  # Solo preservar si tiene valor
                    existing_config[key.strip()] = value
        
        # Preservar valores existentes
        for key, value in existing_config.items():
            if value:
                final_config[key] = value
    
    # Escribir archivo .env.local
    lines = [
        "# ============================================",
        "# Archivo de configuración del Chatbot BMC",
        "# Generado automáticamente por configurar_auto.py",
        "# Puedes editarlo manualmente según tus necesidades",
        "# ============================================",
        "",
        "# API Configuration",
        f"NEXT_PUBLIC_API_URL={final_config.get('NEXT_PUBLIC_API_URL', 'http://localhost:3001/api')}",
        f"NEXT_PUBLIC_WS_URL={final_config.get('NEXT_PUBLIC_WS_URL', 'ws://localhost:3001/ws')}",
        f"PY_CHAT_SERVICE_URL={final_config.get('PY_CHAT_SERVICE_URL', 'http://localhost:8000')}",
        "",
        "# Authentication",
        f"NEXTAUTH_URL={final_config.get('NEXTAUTH_URL', 'http://localhost:3000')}",
        f"NEXTAUTH_SECRET={final_config.get('NEXTAUTH_SECRET', secrets.token_urlsafe(32))}",
        "",
        "# Database",
        f"DATABASE_URL={final_config.get('DATABASE_URL', 'postgresql://username:password@localhost:5432/bmc_dashboard')}",
        f"MONGODB_URI={final_config.get('MONGODB_URI', 'mongodb://localhost:27017/bmc_chat')}",
        f"MELI_ACCESS_TOKEN={final_config.get('MELI_ACCESS_TOKEN', '')}",
        f"MELI_SELLER_ID={final_config.get('MELI_SELLER_ID', '')}",
        "",
        "# WhatsApp Configuration (Opcional)",
        f"WHATSAPP_VERIFY_TOKEN={final_config.get('WHATSAPP_VERIFY_TOKEN', secrets.token_urlsafe(16))}",
        f"WHATSAPP_ACCESS_TOKEN={final_config.get('WHATSAPP_ACCESS_TOKEN', '')}",
        f"WHATSAPP_PHONE_NUMBER_ID={final_config.get('WHATSAPP_PHONE_NUMBER_ID', '')}",
        f"WHATSAPP_BUSINESS_ID={final_config.get('WHATSAPP_BUSINESS_ID', '')}",
        f"WHATSAPP_APP_SECRET={final_config.get('WHATSAPP_APP_SECRET', '')}",
        f"N8N_WEBHOOK_URL_EXTERNAL={final_config.get('N8N_WEBHOOK_URL_EXTERNAL', 'http://localhost:5678/webhook/whatsapp')}",
        "",
        "# OpenAI Configuration",
        f"# Get your API key from https://platform.openai.com/api-keys",
        f"OPENAI_API_KEY={final_config.get('OPENAI_API_KEY', '')}",
        f"OPENAI_MODELS={final_config.get('OPENAI_MODELS', 'gpt-4o-mini,gpt-4o,gpt-3.5-turbo')}",
        f"OPENAI_ORGANIZATION_ID={final_config.get('OPENAI_ORGANIZATION_ID', '')}",
        f"OPENAI_PROJECT_ID={final_config.get('OPENAI_PROJECT_ID', '')}",
        "",
        "# Groq Configuration (Opcional - Free tier available)",
        f"# Get your API key from https://console.groq.com/keys",
        f"GROQ_API_KEY={final_config.get('GROQ_API_KEY', '')}",
        f"GROQ_MODELS={final_config.get('GROQ_MODELS', 'llama-3.1-70b-versatile,llama-3.1-8b-instant,mixtral-8x7b-32768')}",
        "",
        "# Google Gemini Configuration (Opcional)",
        f"# Get your API key from https://makersuite.google.com/app/apikey",
        f"GEMINI_API_KEY={final_config.get('GEMINI_API_KEY', '')}",
        f"GEMINI_MODELS={final_config.get('GEMINI_MODELS', 'gemini-2.5-flash,gemini-1.5-pro,gemini-3-pro')}",
        "",
        "# xAI (Grok) Configuration (Opcional)",
        f"GROK_API_KEY={final_config.get('GROK_API_KEY', '')}",
        f"GROK_MODELS={final_config.get('GROK_MODELS', 'grok-beta,grok-2-1212,grok-4-latest')}",
        "",
        "# Model Selection Strategy",
        f"MODEL_STRATEGY={final_config.get('MODEL_STRATEGY', 'balanced')}",
        "",
        "# n8n Configuration (Opcional)",
        f"N8N_BASE_URL={final_config.get('N8N_BASE_URL', 'http://localhost:5678')}",
        f"N8N_API_KEY={final_config.get('N8N_API_KEY', '')}",
        f"N8N_PUBLIC_KEY={final_config.get('N8N_PUBLIC_KEY', '')}",
        f"N8N_PRIVATE_KEY={final_config.get('N8N_PRIVATE_KEY', '')}",
        "",
        "# Mercado Libre Configuration (Opcional)",
        f"MERCADO_LIBRE_APP_ID={final_config.get('MERCADO_LIBRE_APP_ID', '')}",
        f"MERCADO_LIBRE_CLIENT_SECRET={final_config.get('MERCADO_LIBRE_CLIENT_SECRET', '')}",
        f"MERCADO_LIBRE_REDIRECT_URI={final_config.get('MERCADO_LIBRE_REDIRECT_URI', 'http://localhost:3000/api/mercado-libre/auth/callback')}",
        f"MERCADO_LIBRE_SELLER_ID={final_config.get('MERCADO_LIBRE_SELLER_ID', '')}",
        f"MERCADO_LIBRE_WEBHOOK_SECRET={final_config.get('MERCADO_LIBRE_WEBHOOK_SECRET', '')}",
        f"MERCADO_LIBRE_AUTH_URL={final_config.get('MERCADO_LIBRE_AUTH_URL', 'https://auth.mercadolibre.com.uy')}",
        f"MERCADO_LIBRE_API_URL={final_config.get('MERCADO_LIBRE_API_URL', 'https://api.mercadolibre.com')}",
        f"MERCADO_LIBRE_SCOPES={final_config.get('MERCADO_LIBRE_SCOPES', 'offline_access read write')}",
        f"MERCADO_LIBRE_PKCE_ENABLED={final_config.get('MERCADO_LIBRE_PKCE_ENABLED', 'true')}",
        "",
        "# Google Sheets Configuration (Opcional)",
        f"GOOGLE_SHEET_ID={final_config.get('GOOGLE_SHEET_ID', '1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0')}",
        f"GOOGLE_SERVICE_ACCOUNT_EMAIL={final_config.get('GOOGLE_SERVICE_ACCOUNT_EMAIL', '')}",
        f"GOOGLE_PRIVATE_KEY={final_config.get('GOOGLE_PRIVATE_KEY', '')}",
        f"GOOGLE_SHEETS_API_KEY={final_config.get('GOOGLE_SHEETS_API_KEY', '')}",
        "",
        "# System Configuration",
        f"NODE_ENV={final_config.get('NODE_ENV', 'development')}",
        f"LOG_LEVEL={final_config.get('LOG_LEVEL', 'INFO')}",
        f"ENABLE_REQUEST_TRACKING={final_config.get('ENABLE_REQUEST_TRACKING', 'true')}",
        "",
        "# Feature Flags",
        f"NEXT_PUBLIC_ENABLE_AI_INSIGHTS={final_config.get('NEXT_PUBLIC_ENABLE_AI_INSIGHTS', 'true')}",
        f"NEXT_PUBLIC_ENABLE_REAL_TIME_MONITORING={final_config.get('NEXT_PUBLIC_ENABLE_REAL_TIME_MONITORING', 'true')}",
        f"NEXT_PUBLIC_ENABLE_EXPORT_IMPORT={final_config.get('NEXT_PUBLIC_ENABLE_EXPORT_IMPORT', 'true')}",
        "",
        "# Shopify Configuration",
        f"SHOPIFY_PAGE_SIZE={final_config.get('SHOPIFY_PAGE_SIZE', '250')}",
        f"RUN_SHOPIFY_SYNC={final_config.get('RUN_SHOPIFY_SYNC', 'true')}",
        "",
        "# Mercado Libre Ingestion",
        f"MELI_REFRESH_TOKEN={final_config.get('MELI_REFRESH_TOKEN', '')}",
        f"MELI_PAGE_SIZE={final_config.get('MELI_PAGE_SIZE', '250')}",
        f"RUN_MELI_SYNC={final_config.get('RUN_MELI_SYNC', 'true')}",
        "",
    ]
    
    env_file.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✅ Archivo {env_file} creado/actualizado exitosamente")
    print(f"   Ubicación: {env_file.resolve()}")
    print()
    print("📝 Próximos pasos:")
    print("   1. Edita .env.local y agrega tus API keys (OpenAI, Groq, Gemini, etc.)")
    print("   2. Si usas MongoDB Atlas, actualiza MONGODB_URI")
    print("   3. Si usas Google Sheets, configura GOOGLE_SERVICE_ACCOUNT_EMAIL y GOOGLE_PRIVATE_KEY")
    print("   4. Ejecuta: python unified_launcher.py")
    print()

if __name__ == "__main__":
    create_env_file()

