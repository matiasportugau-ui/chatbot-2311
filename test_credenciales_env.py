#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la carga de credenciales desde .env
"""

import os
import sys

def test_carga_dotenv():
    """Prueba la carga de python-dotenv"""
    print("=" * 70)
    print("PRUEBA DE CARGA DE CREDENCIALES DESDE .ENV")
    print("=" * 70)
    
    # 1. Verificar python-dotenv
    print("\n[1] Verificando python-dotenv...")
    try:
        from dotenv import load_dotenv
        print("   [OK] python-dotenv esta instalado")
    except ImportError:
        print("   [ERROR] python-dotenv NO esta instalado")
        print("   [INFO] Instala con: pip install python-dotenv")
        return False
    
    # 2. Intentar cargar archivos .env
    print("\n[2] Buscando archivos .env...")
    archivos_env = ['.env.local', '.env']
    archivo_encontrado = None
    
    for archivo in archivos_env:
        if os.path.exists(archivo):
            print(f"   [OK] Encontrado: {archivo}")
            archivo_encontrado = archivo
            break
        else:
            print(f"   [-] No encontrado: {archivo}")
    
    if not archivo_encontrado:
        print("\n   [WARNING] No se encontro ningun archivo .env")
        print("   [INFO] Crea .env.local o .env con tus credenciales")
        print("   [INFO] O ejecuta: python configurar_env.py")
        return False
    
    # 3. Cargar variables de entorno
    print(f"\n[3] Cargando variables desde {archivo_encontrado}...")
    try:
        load_dotenv(archivo_encontrado, override=True)
        print(f"   [OK] Variables cargadas desde {archivo_encontrado}")
    except Exception as e:
        print(f"   [ERROR] Error cargando {archivo_encontrado}: {e}")
        return False
    
    # 4. Verificar variables de Google Sheets
    print("\n[4] Verificando variables de Google Sheets...")
    variables = {
        'GOOGLE_SHEET_ID': os.getenv('GOOGLE_SHEET_ID'),
        'GOOGLE_SERVICE_ACCOUNT_EMAIL': os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL'),
        'GOOGLE_PRIVATE_KEY': os.getenv('GOOGLE_PRIVATE_KEY'),
    }
    
    todas_configuradas = True
    for var, valor in variables.items():
        if valor:
            if var == 'GOOGLE_PRIVATE_KEY':
                # Verificar formato
                if 'BEGIN PRIVATE KEY' in valor and 'END PRIVATE KEY' in valor:
                    preview = valor[:30] + "..." + valor[-30:] if len(valor) > 60 else valor
                    print(f"   [OK] {var}: {preview}")
                else:
                    print(f"   [WARNING] {var}: Formato incorrecto (debe incluir BEGIN/END PRIVATE KEY)")
                    todas_configuradas = False
            else:
                print(f"   [OK] {var}: {valor}")
        else:
            print(f"   [ERROR] {var}: No configurada")
            todas_configuradas = False
    
    # 5. Probar carga en integracion_google_sheets
    print("\n[5] Probando carga en integracion_google_sheets...")
    try:
        from integracion_google_sheets import IntegracionGoogleSheets
        print("   [OK] Modulo importado correctamente")
        
        # Crear instancia (esto deberia cargar las credenciales)
        sheets = IntegracionGoogleSheets()
        print("   [OK] Instancia creada")
        
        # Verificar si tiene credenciales
        if sheets.credenciales:
            print("   [OK] Credenciales configuradas correctamente")
            print(f"   [OK] Sheet ID: {sheets.sheet_id}")
            
            # Intentar conectar
            print("\n[6] Intentando conectar a Google Sheets...")
            if sheets.conectar_google_sheets():
                print("   [OK] Conexion exitosa a Google Sheets")
                return True
            else:
                print("   [WARNING] No se pudo conectar (puede ser por permisos o credenciales incorrectas)")
                print("   [INFO] Verifica que el Sheet este compartido con el Service Account")
                return todas_configuradas  # Retornar True si las credenciales estan configuradas
        else:
            print("   [WARNING] Credenciales no configuradas (modo simulado)")
            print("   [INFO] Verifica que las variables esten correctas en .env")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return todas_configuradas


def test_chat_interactivo():
    """Prueba la carga en chat_interactivo"""
    print("\n" + "=" * 70)
    print("PRUEBA DE CARGA EN CHAT INTERACTIVO")
    print("=" * 70)
    
    try:
        from chat_interactivo import AgenteInteractivo
        print("\n[OK] Importando AgenteInteractivo...")
        
        agente = AgenteInteractivo()
        print("[OK] Agente creado")
        
        if hasattr(agente, 'google_sheets') and agente.google_sheets:
            if agente.google_sheets.credenciales:
                print("[OK] Google Sheets configurado con credenciales")
                return True
            else:
                print("[WARNING] Google Sheets en modo simulado")
                return False
        else:
            print("[WARNING] Google Sheets no inicializado")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("INICIANDO PRUEBAS DE CREDENCIALES")
    print("=" * 70 + "\n")
    
    # Prueba 1: Carga de dotenv
    resultado1 = test_carga_dotenv()
    
    # Prueba 2: Chat interactivo
    resultado2 = test_chat_interactivo()
    
    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE PRUEBAS")
    print("=" * 70)
    print(f"\n[OK] Carga de credenciales: {'PASO' if resultado1 else 'FALLO'}")
    print(f"[OK] Chat interactivo: {'PASO' if resultado2 else 'FALLO'}")
    
    if resultado1 and resultado2:
        print("\n[OK] TODAS LAS PRUEBAS PASARON!")
        print("[OK] Las credenciales se estan cargando correctamente desde .env")
        return 0
    else:
        print("\n[WARNING] ALGUNAS PRUEBAS FALLARON")
        print("[INFO] Revisa los mensajes anteriores para mas detalles")
        return 1


if __name__ == "__main__":
    sys.exit(main())

