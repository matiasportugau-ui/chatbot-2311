#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de ayuda para configurar variables de entorno
Crea archivo .env.local con las credenciales necesarias
"""

import os

def crear_archivo_env():
    """Crea archivo .env.local con plantilla"""
    
    archivo_env = '.env.local'
    
    if os.path.exists(archivo_env):
        respuesta = input(f"⚠️  El archivo {archivo_env} ya existe. ¿Deseas sobrescribirlo? (s/n): ")
        if respuesta.lower() != 's':
            print("❌ Operación cancelada")
            return False
    
    print("\n📝 Configurando archivo .env.local")
    print("=" * 60)
    
    # Solicitar credenciales
    print("\n1️⃣ Google Sheets API:")
    google_sheet_id = input("   GOOGLE_SHEET_ID [1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0]: ").strip()
    if not google_sheet_id:
        google_sheet_id = "1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0"
    
    google_email = input("   GOOGLE_SERVICE_ACCOUNT_EMAIL: ").strip()
    google_key = input("   GOOGLE_PRIVATE_KEY (pega la clave completa): ").strip()
    
    print("\n2️⃣ OpenAI API (opcional):")
    openai_key = input("   OPENAI_API_KEY: ").strip()
    
    print("\n3️⃣ MongoDB (opcional):")
    mongodb_uri = input("   MONGODB_URI: ").strip()
    
    # Construir contenido del archivo
    contenido = f"""# 🔐 Variables de Entorno - Sistema BMC Cotizaciones
# Generado automáticamente por configurar_env.py

# Google Sheets API
GOOGLE_SHEET_ID={google_sheet_id}
"""
    
    if google_email:
        contenido += f"GOOGLE_SERVICE_ACCOUNT_EMAIL={google_email}\n"
    
    if google_key:
        # Escapar comillas y saltos de línea
        google_key_escaped = google_key.replace('"', '\\"').replace('\n', '\\n')
        contenido += f'GOOGLE_PRIVATE_KEY="{google_key_escaped}"\n'
    
    if openai_key:
        contenido += f"\n# OpenAI API\nOPENAI_API_KEY={openai_key}\n"
    
    if mongodb_uri:
        contenido += f"\n# MongoDB Atlas\nMONGODB_URI={mongodb_uri}\n"
    
    contenido += """
# Configuración del Sistema
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
"""
    
    # Escribir archivo
    try:
        with open(archivo_env, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f"\n✅ Archivo {archivo_env} creado exitosamente")
        print("\n📋 Próximos pasos:")
        print("   1. Verifica que las credenciales estén correctas")
        print("   2. Asegúrate de compartir el Google Sheet con el Service Account")
        print("   3. Ejecuta el chat interactivo: python chat_interactivo.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creando archivo: {e}")
        return False


def verificar_env():
    """Verifica que las variables de entorno estén configuradas"""
    print("\n🔍 Verificando variables de entorno...")
    print("=" * 60)
    
    # Cargar dotenv si está disponible
    try:
        from dotenv import load_dotenv
        if os.path.exists('.env.local'):
            load_dotenv('.env.local')
        elif os.path.exists('.env'):
            load_dotenv('.env')
        else:
            load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv no instalado")
    
    variables = {
        'GOOGLE_SHEET_ID': os.getenv('GOOGLE_SHEET_ID'),
        'GOOGLE_SERVICE_ACCOUNT_EMAIL': os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL'),
        'GOOGLE_PRIVATE_KEY': os.getenv('GOOGLE_PRIVATE_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    }
    
    todas_ok = True
    for var, valor in variables.items():
        if valor:
            if var == 'GOOGLE_PRIVATE_KEY':
                # Mostrar solo los primeros y últimos caracteres
                preview = valor[:20] + "..." + valor[-20:] if len(valor) > 40 else valor[:40]
                print(f"✅ {var}: {preview}")
            elif var == 'OPENAI_API_KEY':
                preview = valor[:10] + "..." + valor[-4:] if len(valor) > 14 else valor
                print(f"✅ {var}: {preview}")
            else:
                print(f"✅ {var}: {valor}")
        else:
            print(f"❌ {var}: No configurada")
            todas_ok = False
    
    if todas_ok:
        print("\n✅ Todas las variables de entorno están configuradas")
    else:
        print("\n⚠️  Algunas variables no están configuradas")
        print("   Ejecuta este script para configurarlas")
    
    return todas_ok


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'verificar':
        verificar_env()
    else:
        print("🔧 Configurador de Variables de Entorno - BMC Cotizaciones")
        print("=" * 60)
        print("\nOpciones:")
        print("  1. Crear/actualizar .env.local")
        print("  2. Verificar variables configuradas")
        print()
        
        opcion = input("Selecciona una opción (1/2) [1]: ").strip() or "1"
        
        if opcion == "1":
            crear_archivo_env()
        elif opcion == "2":
            verificar_env()
        else:
            print("❌ Opción inválida")

