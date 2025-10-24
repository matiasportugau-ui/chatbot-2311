#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador del Sistema de Cotizaciones BMC Uruguay
Configura el sistema y verifica dependencias
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def verificar_python():
    """Verifica la versión de Python"""
    print("Verificando versión de Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"✗ Python {version.major}.{version.minor} detectado")
        print("  Se requiere Python 3.7 o superior")
        return False
    
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detectado")
    return True


def verificar_dependencias_basicas():
    """Verifica dependencias básicas de Python"""
    print("\nVerificando dependencias básicas...")
    
    dependencias_basicas = [
        'json', 'datetime', 'decimal', 'dataclasses', 
        'typing', 'csv', 'pathlib'
    ]
    
    dependencias_faltantes = []
    
    for dep in dependencias_basicas:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep}")
            dependencias_faltantes.append(dep)
    
    if dependencias_faltantes:
        print(f"\n✗ Dependencias faltantes: {', '.join(dependencias_faltantes)}")
        return False
    
    print("✓ Todas las dependencias básicas están disponibles")
    return True


def verificar_dependencias_opcionales():
    """Verifica dependencias opcionales"""
    print("\nVerificando dependencias opcionales...")
    
    dependencias_opcionales = {
        'requests': 'Para mapeador de productos web',
        'beautifulsoup4': 'Para parsing de HTML',
        'reportlab': 'Para generación de PDFs',
        'pandas': 'Para procesamiento de datos',
        'flask': 'Para interfaz web'
    }
    
    dependencias_disponibles = []
    dependencias_faltantes = []
    
    for dep, descripcion in dependencias_opcionales.items():
        try:
            __import__(dep)
            print(f"  ✓ {dep} - {descripcion}")
            dependencias_disponibles.append(dep)
        except ImportError:
            print(f"  ✗ {dep} - {descripcion}")
            dependencias_faltantes.append(dep)
    
    if dependencias_faltantes:
        print(f"\n⚠ Dependencias opcionales faltantes: {', '.join(dependencias_faltantes)}")
        print("  Algunas funcionalidades pueden no estar disponibles")
    
    return dependencias_disponibles, dependencias_faltantes


def instalar_dependencias():
    """Instala dependencias opcionales"""
    print("\n¿Desea instalar las dependencias opcionales? (s/n): ", end="")
    respuesta = input().strip().lower()
    
    if respuesta != 's':
        print("Saltando instalación de dependencias opcionales")
        return True
    
    print("Instalando dependencias opcionales...")
    
    try:
        # Instalar desde requirements.txt si existe
        if os.path.exists('requirements.txt'):
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✓ Dependencias instaladas desde requirements.txt")
        else:
            # Instalar dependencias principales
            dependencias = ['requests', 'beautifulsoup4', 'reportlab']
            for dep in dependencias:
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
                    print(f"  ✓ {dep} instalado")
                except subprocess.CalledProcessError:
                    print(f"  ✗ Error instalando {dep}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error instalando dependencias: {e}")
        return False


def crear_directorios():
    """Crea directorios necesarios"""
    print("\nCreando directorios necesarios...")
    
    directorios = [
        'exportaciones',
        'logs',
        'backups',
        'plantillas'
    ]
    
    for directorio in directorios:
        try:
            os.makedirs(directorio, exist_ok=True)
            print(f"  ✓ {directorio}/")
        except OSError as e:
            print(f"  ✗ Error creando {directorio}/: {e}")
            return False
    
    return True


def verificar_archivos_sistema():
    """Verifica que los archivos del sistema estén presentes"""
    print("\nVerificando archivos del sistema...")
    
    archivos_requeridos = [
        'sistema_cotizaciones.py',
        'main.py',
        'demo.py',
        'config.py',
        'matriz_precios.json'
    ]
    
    archivos_faltantes = []
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"  ✓ {archivo}")
        else:
            print(f"  ✗ {archivo}")
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print(f"\n✗ Archivos faltantes: {', '.join(archivos_faltantes)}")
        return False
    
    print("✓ Todos los archivos del sistema están presentes")
    return True


def crear_archivo_configuracion():
    """Crea archivo de configuración personalizada"""
    print("\nCreando archivo de configuración...")
    
    config_personalizada = {
        "instalacion": {
            "fecha": "2024-12-19",
            "version": "1.0.0",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "directorio_instalacion": os.getcwd()
        },
        "configuracion_inicial": {
            "precio_base_isodec": 150.00,
            "iva_porcentaje": 22,
            "moneda": "UYU"
        }
    }
    
    try:
        with open('configuracion_instalacion.json', 'w', encoding='utf-8') as f:
            json.dump(config_personalizada, f, ensure_ascii=False, indent=2)
        print("  ✓ configuracion_instalacion.json creado")
        return True
    except Exception as e:
        print(f"  ✗ Error creando configuración: {e}")
        return False


def ejecutar_prueba_sistema():
    """Ejecuta una prueba básica del sistema"""
    print("\nEjecutando prueba del sistema...")
    
    try:
        # Importar sistema
        from sistema_cotizaciones import SistemaCotizacionesBMC, Cliente, EspecificacionCotizacion
        from decimal import Decimal
        
        # Crear sistema
        sistema = SistemaCotizacionesBMC()
        sistema.actualizar_precio_producto("isodec", Decimal('150.00'))
        
        # Crear cotización de prueba
        cliente = Cliente(
            nombre="Cliente Prueba",
            telefono="099123456",
            direccion="Dirección Prueba",
            zona="Montevideo"
        )
        
        especificaciones = EspecificacionCotizacion(
            producto="isodec",
            espesor="100mm",
            relleno="EPS",
            largo_metros=Decimal('5.0'),
            ancho_metros=Decimal('3.0'),
            color="Blanco"
        )
        
        cotizacion = sistema.crear_cotizacion(
            cliente=cliente,
            especificaciones=especificaciones,
            asignado_a="MA"
        )
        
        print(f"  ✓ Cotización de prueba creada: {cotizacion.id}")
        print(f"  ✓ Precio calculado: ${cotizacion.precio_total}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error en prueba del sistema: {e}")
        return False


def mostrar_resumen_instalacion():
    """Muestra resumen de la instalación"""
    print("\n" + "="*60)
    print("RESUMEN DE INSTALACIÓN")
    print("="*60)
    print("✓ Sistema de Cotizaciones BMC Uruguay instalado")
    print("✓ Archivos del sistema verificados")
    print("✓ Directorios creados")
    print("✓ Configuración inicial establecida")
    print("\nARCHIVOS PRINCIPALES:")
    print("  - sistema_cotizaciones.py: Lógica principal")
    print("  - main.py: Sistema interactivo")
    print("  - demo.py: Demostración del sistema")
    print("  - config.py: Configuración del sistema")
    print("  - matriz_precios.json: Matriz de precios")
    print("\nCOMANDOS DISPONIBLES:")
    print("  python ejecutar_sistema.py  - Ejecutar sistema completo")
    print("  python demo.py             - Ejecutar demo")
    print("  python main.py             - Sistema interactivo")
    print("\nDOCUMENTACIÓN:")
    print("  - README.md: Documentación completa")
    print("  - requirements.txt: Dependencias opcionales")
    print("\n¡Sistema listo para usar!")


def main():
    """Función principal de instalación"""
    print("INSTALADOR - SISTEMA DE COTIZACIONES BMC URUGUAY")
    print("="*60)
    
    # Verificar Python
    if not verificar_python():
        print("\n✗ Instalación cancelada: Versión de Python incompatible")
        return False
    
    # Verificar dependencias básicas
    if not verificar_dependencias_basicas():
        print("\n✗ Instalación cancelada: Dependencias básicas faltantes")
        return False
    
    # Verificar dependencias opcionales
    disponibles, faltantes = verificar_dependencias_opcionales()
    
    # Instalar dependencias opcionales si se solicita
    if faltantes:
        instalar_dependencias()
    
    # Crear directorios
    if not crear_directorios():
        print("\n✗ Instalación cancelada: Error creando directorios")
        return False
    
    # Verificar archivos del sistema
    if not verificar_archivos_sistema():
        print("\n✗ Instalación cancelada: Archivos del sistema faltantes")
        return False
    
    # Crear configuración
    if not crear_archivo_configuracion():
        print("\n⚠ Advertencia: Error creando configuración personalizada")
    
    # Ejecutar prueba del sistema
    if not ejecutar_prueba_sistema():
        print("\n⚠ Advertencia: Error en prueba del sistema")
    
    # Mostrar resumen
    mostrar_resumen_instalacion()
    
    return True


if __name__ == "__main__":
    try:
        exito = main()
        if exito:
            print("\n✓ Instalación completada exitosamente")
        else:
            print("\n✗ Instalación falló")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInstalación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error durante la instalación: {e}")
        sys.exit(1)
