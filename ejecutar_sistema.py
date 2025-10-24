#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ejecutar el Sistema de Cotizaciones BMC Uruguay
Proporciona diferentes opciones de ejecución
"""

import sys
import os
from decimal import Decimal


def verificar_dependencias():
    """Verifica que las dependencias estén disponibles"""
    try:
        import json
        import datetime
        from decimal import Decimal
        from dataclasses import dataclass
        print("✓ Dependencias básicas disponibles")
        return True
    except ImportError as e:
        print(f"✗ Error de dependencias: {e}")
        return False


def ejecutar_demo():
    """Ejecuta el demo del sistema"""
    print("Ejecutando demo del sistema...")
    try:
        from demo import main as demo_main
        demo_main()
    except Exception as e:
        print(f"Error ejecutando demo: {e}")


def ejecutar_sistema_interactivo():
    """Ejecuta el sistema interactivo"""
    print("Ejecutando sistema interactivo...")
    try:
        from main import main as main_interactivo
        main_interactivo()
    except Exception as e:
        print(f"Error ejecutando sistema interactivo: {e}")


def ejecutar_mapeador():
    """Ejecuta el mapeador de productos web"""
    print("Ejecutando mapeador de productos...")
    try:
        from mapeador_productos_web import main as mapeador_main
        mapeador_main()
    except Exception as e:
        print(f"Error ejecutando mapeador: {e}")


def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "="*60)
    print("SISTEMA DE COTIZACIONES BMC URUGUAY")
    print("="*60)
    print("1. Ejecutar demo del sistema")
    print("2. Ejecutar sistema interactivo")
    print("3. Ejecutar mapeador de productos web")
    print("4. Verificar dependencias")
    print("5. Mostrar ayuda")
    print("6. Salir")
    print("="*60)


def mostrar_ayuda():
    """Muestra la ayuda del sistema"""
    print("\n" + "="*60)
    print("AYUDA - SISTEMA DE COTIZACIONES BMC URUGUAY")
    print("="*60)
    print("""
Este sistema permite gestionar cotizaciones de productos de aislamiento
térmico para BMC Uruguay.

OPCIONES DISPONIBLES:

1. Demo del sistema:
   - Muestra las funcionalidades principales
   - Crea cotizaciones de ejemplo
   - Demuestra búsquedas y estadísticas

2. Sistema interactivo:
   - Interfaz de usuario completa
   - Crear, buscar y gestionar cotizaciones
   - Exportar datos

3. Mapeador de productos web:
   - Obtiene información de productos desde bmcuruguay.com.uy
   - Actualiza enlaces y precios
   - Sincroniza con la matriz de precios

ARCHIVOS PRINCIPALES:
- sistema_cotizaciones.py: Lógica principal
- main.py: Sistema interactivo
- demo.py: Demostración del sistema
- matriz_precios.json: Matriz de precios y productos
- mapeador_productos_web.py: Mapeador web

REQUISITOS:
- Python 3.7 o superior
- Módulos estándar: json, datetime, decimal, dataclasses
- Opcional: requests, beautifulsoup4 (para mapeador web)

USO:
python ejecutar_sistema.py
    """)


def main():
    """Función principal"""
    print("Iniciando Sistema de Cotizaciones BMC Uruguay...")
    
    # Verificar dependencias básicas
    if not verificar_dependencias():
        print("No se pueden ejecutar las funcionalidades básicas")
        return
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\nSeleccione una opción (1-6): ").strip()
            
            if opcion == "1":
                ejecutar_demo()
            elif opcion == "2":
                ejecutar_sistema_interactivo()
            elif opcion == "3":
                ejecutar_mapeador()
            elif opcion == "4":
                verificar_dependencias()
            elif opcion == "5":
                mostrar_ayuda()
            elif opcion == "6":
                print("¡Hasta luego!")
                break
            else:
                print("⚠ Opción inválida. Por favor, seleccione 1-6.")
                
        except KeyboardInterrupt:
            print("\n\nSistema interrumpido por el usuario")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Por favor, intente nuevamente.")


if __name__ == "__main__":
    main()
