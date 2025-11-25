#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para verificar el estado de la integración OpenAI"""

import os
import sys

print("=" * 70)
print("VERIFICACION DE INTEGRACION OPENAI")
print("=" * 70)
print()

# Verificar paquete
print("1. Verificando paquete openai...")
try:
    import openai
    print("   OK - Paquete openai instalado")
    print(f"   Version: {openai.__version__}")
    paquete_instalado = True
except ImportError:
    print("   ERROR - Paquete openai NO instalado")
    print("   Instalar con: pip install openai")
    paquete_instalado = False

print()

# Verificar API key
print("2. Verificando OPENAI_API_KEY...")
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    # Mostrar solo los primeros y últimos caracteres por seguridad
    masked_key = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 11 else "***"
    print(f"   OK - API Key configurada: {masked_key}")
    api_key_configurada = True
else:
    print("   ERROR - OPENAI_API_KEY NO configurada")
    print("   Configurar con: set OPENAI_API_KEY=sk-tu-key-aqui")
    api_key_configurada = False

print()

# Verificar modelo
print("3. Verificando modelo configurado...")
modelo = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
print(f"   Modelo: {modelo}")

print()

# Estado general
print("=" * 70)
print("ESTADO GENERAL")
print("=" * 70)

if paquete_instalado and api_key_configurada:
    print("[OK] OpenAI COMPLETAMENTE CONFIGURADO")
    print("   El chatbot usara OpenAI para respuestas avanzadas")
elif paquete_instalado and not api_key_configurada:
    print("[ADVERTENCIA] OpenAI parcialmente configurado")
    print("   Paquete instalado pero falta API Key")
    print("   El chatbot usara pattern matching")
elif not paquete_instalado:
    print("[INFO] OpenAI NO configurado")
    print("   El chatbot usara pattern matching (funciona sin OpenAI)")

print()
print("=" * 70)
print("INSTRUCCIONES")
print("=" * 70)
print()
print("Para activar OpenAI:")
print("1. Instalar: pip install openai")
print("2. Obtener API Key: https://platform.openai.com/api-keys")
print("3. Configurar: set OPENAI_API_KEY=sk-tu-key-aqui")
print("4. O crear archivo .env con: OPENAI_API_KEY=sk-tu-key-aqui")
print()
print("NOTA: El sistema funciona perfectamente sin OpenAI usando")
print("      pattern matching y base de conocimiento.")

