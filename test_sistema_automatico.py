#!/usr/bin/env python3
"""Script de prueba del sistema automático"""

import json
import os
from datetime import datetime

import requests

from mapeador_productos_web import MapeadorProductosWeb
from sistema_cotizaciones import SistemaCotizacionesBMC


def test_api_shopify():
    """Prueba acceso a API de Shopify"""
    try:
        url = "https://bmcuruguay.com.uy/products.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        productos = data.get("products", [])
        return True, len(productos)
    except Exception as e:
        return False, str(e)


def test_mapeador():
    """Prueba el mapeador de productos"""
    try:
        mapeador = MapeadorProductosWeb()
        return True, len(mapeador.enlaces_base)
    except Exception as e:
        return False, str(e)


def test_sistema_cotizaciones():
    """Prueba el sistema de cotizaciones"""
    try:
        sistema = SistemaCotizacionesBMC()
        return True, len(sistema.productos)
    except Exception as e:
        return False, str(e)


def verificar_archivos():
    """Verifica que los archivos clave existan"""
    archivos = [
        "mapeador_productos_web.py",
        "sistema_cotizaciones.py",
        "chat_interactivo.py",
        "background_agent.py",
        ".github/workflows/auto-update-products.yml",
        "productos_mapeados.json",
    ]
    resultados = {}
    for archivo in archivos:
        resultados[archivo] = os.path.exists(archivo)
    return resultados


def generar_reporte():
    """Genera reporte completo del sistema"""
    reporte = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tests": {},
        "archivos": {},
        "estado": "OK",
    }

    # Test API Shopify
    api_ok, api_result = test_api_shopify()
    reporte["tests"]["api_shopify"] = {
        "estado": "OK" if api_ok else "ERROR",
        "resultado": api_result,
    }

    # Test Mapeador
    map_ok, map_result = test_mapeador()
    reporte["tests"]["mapeador"] = {"estado": "OK" if map_ok else "ERROR", "resultado": map_result}

    # Test Sistema Cotizaciones
    sys_ok, sys_result = test_sistema_cotizaciones()
    reporte["tests"]["sistema_cotizaciones"] = {
        "estado": "OK" if sys_ok else "ERROR",
        "resultado": sys_result,
    }

    # Verificar archivos
    reporte["archivos"] = verificar_archivos()

    # Estado general
    todos_ok = api_ok and map_ok and sys_ok and all(reporte["archivos"].values())
    reporte["estado"] = "OK" if todos_ok else "ADVERTENCIA"

    return reporte


if __name__ == "__main__":
    print("=" * 70)
    print("REPORTE DEL SISTEMA AUTOMATICO - BMC URUGUAY")
    print("=" * 70)
    print()

    reporte = generar_reporte()

    print(f"Fecha: {reporte['fecha']}")
    print(f"Estado General: {reporte['estado']}")
    print()

    print("TESTS:")
    for test, info in reporte["tests"].items():
        estado_icon = "[OK]" if info["estado"] == "OK" else "[ERROR]"
        print(f"  {estado_icon} {test}: {info['estado']} - {info['resultado']}")
    print()

    print("ARCHIVOS:")
    for archivo, existe in reporte["archivos"].items():
        estado_icon = "[OK]" if existe else "[FALTA]"
        print(f"  {estado_icon} {archivo}")
    print()

    # Guardar reporte JSON
    with open("reporte_sistema_automatico.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)

    print("Reporte guardado en: reporte_sistema_automatico.json")
    print("=" * 70)

    if reporte["estado"] == "OK":
        print("\n[OK] SISTEMA LISTO Y FUNCIONANDO")
    else:
        print("\n[ADVERTENCIA] REVISAR CONFIGURACION")
