#!/usr/bin/env python3
"""
Ejemplo simple de uso del extractor de datos
"""

from extraer_datos_entrenamiento import ExtractorDatosEntrenamiento
from datetime import datetime, timedelta

def ejemplo_whatsapp_mongodb():
    """Ejemplo: Extraer WhatsApp desde MongoDB"""
    print("📱 Extrayendo WhatsApp desde MongoDB...")
    
    extractor = ExtractorDatosEntrenamiento()
    
    # Extraer últimos 1000 mensajes
    datos = extractor.extraer_whatsapp_mongodb(limite=1000)
    
    # Guardar
    extractor.guardar_para_entrenamiento(datos, "whatsapp_entrenamiento.json")
    
    # Mostrar resumen
    resumen = extractor.generar_resumen(datos)
    print("\n📊 Resumen:")
    print(f"Total: {resumen['total']}")
    print(f"Por fuente: {resumen['por_fuente']}")
    
    extractor.desconectar_mongodb()


def ejemplo_whatsapp_archivo():
    """Ejemplo: Extraer WhatsApp desde archivo"""
    print("📱 Extrayendo WhatsApp desde archivo...")
    
    extractor = ExtractorDatosEntrenamiento()
    
    # Extraer desde archivo (ajusta la ruta)
    datos = extractor.extraer_whatsapp_archivo("conversaciones_backup.json")
    
    # Guardar
    extractor.guardar_para_entrenamiento(datos, "whatsapp_desde_archivo.json")
    
    extractor.desconectar_mongodb()


def ejemplo_mercado_libre_archivo():
    """Ejemplo: Extraer Mercado Libre desde archivo"""
    print("🛒 Extrayendo Mercado Libre desde archivo...")
    
    extractor = ExtractorDatosEntrenamiento()
    
    # Extraer desde archivo (ajusta la ruta)
    datos = extractor.extraer_mercado_libre_archivo("preguntas_ml.json")
    
    # Guardar
    extractor.guardar_para_entrenamiento(datos, "mercado_libre_entrenamiento.json")
    
    extractor.desconectar_mongodb()


def ejemplo_mercado_libre_api():
    """Ejemplo: Extraer Mercado Libre desde API"""
    print("🛒 Extrayendo Mercado Libre desde API...")
    
    import os
    
    extractor = ExtractorDatosEntrenamiento()
    
    # Obtener token desde variable de entorno o hardcodeado
    access_token = os.getenv("MERCADO_LIBRE_ACCESS_TOKEN", "TU_TOKEN_AQUI")
    seller_id = os.getenv("MERCADO_LIBRE_SELLER_ID", None)
    
    if access_token == "TU_TOKEN_AQUI":
        print("⚠️  Configura MERCADO_LIBRE_ACCESS_TOKEN en .env o edita este script")
        return
    
    # Extraer desde API
    datos = extractor.extraer_mercado_libre_api(
        access_token=access_token,
        seller_id=seller_id,
        limite=100
    )
    
    # Guardar
    extractor.guardar_para_entrenamiento(datos, "mercado_libre_api.json")
    
    extractor.desconectar_mongodb()


def ejemplo_combinado():
    """Ejemplo: Combinar múltiples fuentes"""
    print("🔄 Combinando datos de múltiples fuentes...")
    
    extractor = ExtractorDatosEntrenamiento()
    todos_los_datos = []
    
    # Extraer WhatsApp
    print("\n1. Extrayendo WhatsApp...")
    datos_wa = extractor.extraer_whatsapp_mongodb(limite=500)
    todos_los_datos.extend(datos_wa)
    
    # Extraer Mercado Libre desde archivo (si existe)
    print("\n2. Extrayendo Mercado Libre...")
    try:
        datos_ml = extractor.extraer_mercado_libre_archivo("preguntas_ml.json")
        todos_los_datos.extend(datos_ml)
    except:
        print("   (Archivo no encontrado, continuando...)")
    
    # Guardar todo junto
    print("\n3. Guardando datos combinados...")
    extractor.guardar_para_entrenamiento(
        todos_los_datos,
        "datos_combinados_entrenamiento.json"
    )
    
    # Resumen final
    resumen = extractor.generar_resumen(todos_los_datos)
    print("\n📊 RESUMEN FINAL:")
    print(f"Total de registros: {resumen['total']}")
    print(f"Por fuente: {resumen['por_fuente']}")
    if resumen.get('intents'):
        print(f"Intents encontrados: {len(resumen['intents'])}")
    
    extractor.desconectar_mongodb()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        opcion = sys.argv[1]
        
        if opcion == "whatsapp-mongodb":
            ejemplo_whatsapp_mongodb()
        elif opcion == "whatsapp-archivo":
            ejemplo_whatsapp_archivo()
        elif opcion == "mercado-libre-archivo":
            ejemplo_mercado_libre_archivo()
        elif opcion == "mercado-libre-api":
            ejemplo_mercado_libre_api()
        elif opcion == "combinado":
            ejemplo_combinado()
        else:
            print("Opciones disponibles:")
            print("  whatsapp-mongodb")
            print("  whatsapp-archivo")
            print("  mercado-libre-archivo")
            print("  mercado-libre-api")
            print("  combinado")
    else:
        # Ejecutar ejemplo combinado por defecto
        ejemplo_combinado()




