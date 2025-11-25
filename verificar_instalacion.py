#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de verificación de instalación"""

import sys
import os

print("=" * 70)
print("VERIFICACION DE INSTALACION - BMC Chatbot")
print("=" * 70)
print()

# Verificar Python
print(f"Python version: {sys.version}")
print()

# Verificar módulos básicos
print("Verificando módulos básicos...")
try:
    from sistema_cotizaciones import SistemaCotizacionesBMC
    print("✓ sistema_cotizaciones")
except ImportError as e:
    print(f"✗ sistema_cotizaciones: {e}")
    sys.exit(1)

try:
    from utils_cotizaciones import obtener_datos_faltantes
    print("✓ utils_cotizaciones")
except ImportError as e:
    print(f"✗ utils_cotizaciones: {e}")
    sys.exit(1)

# Verificar módulos opcionales
print("\nVerificando módulos opcionales...")
try:
    from base_conocimiento_dinamica import BaseConocimientoDinamica
    print("✓ base_conocimiento_dinamica")
except ImportError as e:
    print(f"⚠ base_conocimiento_dinamica: {e} (opcional)")

try:
    from ia_conversacional_integrada import IAConversacionalIntegrada
    print("✓ ia_conversacional_integrada")
except ImportError as e:
    print(f"⚠ ia_conversacional_integrada: {e} (opcional)")

# Verificar archivos de conocimiento
print("\nVerificando archivos de conocimiento...")
archivos_conocimiento = [
    "base_conocimiento_final.json",
    "conocimiento_completo.json",
    "base_conocimiento_exportada.json",
    "base_conocimiento_demo.json"
]

encontrados = []
for archivo in archivos_conocimiento:
    if os.path.exists(archivo):
        encontrados.append(archivo)
        print(f"✓ {archivo}")

if not encontrados:
    print("⚠ No se encontraron archivos de conocimiento (el sistema funcionará sin ellos)")

print("\n" + "=" * 70)
print("VERIFICACION COMPLETA")
print("=" * 70)
print("\nEl sistema está listo para ejecutarse.")
print("Ejecuta: python chat_interactivo.py")

