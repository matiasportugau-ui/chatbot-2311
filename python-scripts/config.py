#!/usr/bin/env python3
"""
Configuración del Sistema de Cotizaciones BMC Uruguay
Centraliza todas las configuraciones del sistema
"""

# Configuración general del sistema
SISTEMA_CONFIG = {
    "nombre": "Sistema de Cotizaciones BMC Uruguay",
    "version": "1.0.0",
    "descripcion": "Sistema para gestión de cotizaciones de productos de aislamiento térmico",
    "empresa": "BMC Uruguay",
    "web": "https://bmcuruguay.com.uy",
    "email": "info@bmcuruguay.com.uy",
    "telefono": "+598 XX XXX XXX",
}

# Configuración de moneda y precios
MONEDA_CONFIG = {
    "codigo": "UYU",
    "simbolo": "$",
    "decimales": 2,
    "iva_porcentaje": 22,
    "redondeo": "ROUND_HALF_UP",
}

# Configuración de archivos
ARCHIVOS_CONFIG = {
    "matriz_precios": "matriz_precios.json",
    "cotizaciones": "cotizaciones_bmc.json",
    "plantillas": "plantillas_cotizacion.json",
    "productos_mapeados": "productos_mapeados.json",
    "log": "sistema_cotizaciones.log",
}

# Configuración de productos
PRODUCTOS_CONFIG = {
    "productos_principales": ["isodec", "poliestireno", "lana_roca", "poliuretano", "fibra_vidrio"],
    "espesores_disponibles": ["25mm", "50mm", "75mm", "100mm", "125mm", "150mm"],
    "colores_disponibles": ["Blanco", "Gris", "Personalizado"],
    "rellenos_disponibles": ["EPS", "Poliuretano", "Lana de roca", "Fibra de vidrio"],
    "terminaciones_disponibles": ["Gotero", "Hormigón", "Aluminio"],
}

# Configuración de estados de cotización
ESTADOS_CONFIG = {
    "estados": ["Pendiente", "Asignado", "Enviado", "Listo", "Confirmado", "Rechazado"],
    "estado_inicial": "Pendiente",
    "estado_final": "Confirmado",
}

# Configuración de asignaciones
ASIGNACIONES_CONFIG = {
    "asignaciones": [
        "MA",  # Vendedor A
        "MO",  # Vendedor B
        "RA",  # Vendedor C
        "SPRT",  # Soporte técnico
        "Ref.",  # Referencia
    ],
    "asignacion_default": "MA",
}

# Configuración de zonas de entrega
ZONAS_CONFIG = {
    "montevideo": {"nombre": "Montevideo", "costo_traslado": 0.00, "factor_zona": 1.0},
    "interior": {"nombre": "Interior del país", "costo_traslado": 15.00, "factor_zona": 1.1},
    "punta_del_este": {"nombre": "Punta del Este", "costo_traslado": 20.00, "factor_zona": 1.15},
}

# Configuración de fórmulas de cálculo
FORMULAS_CONFIG = {
    "factores_espesor": {
        "25mm": 0.7,
        "50mm": 0.8,
        "75mm": 0.9,
        "100mm": 1.0,
        "125mm": 1.1,
        "150mm": 1.2,
    },
    "factores_color": {"Blanco": 1.0, "Gris": 1.05, "Personalizado": 1.15},
    "factores_terminacion": {"Gotero": 1.05, "Hormigón": 1.1, "Aluminio": 1.15},
    "factores_servicio": {
        "anclajes_incluido": 1.0,
        "anclajes_no_incluido": 0.95,
        "traslado_incluido": 1.0,
        "traslado_no_incluido": 0.9,
    },
}

# Configuración de descuentos
DESCUENTOS_CONFIG = {
    "volumen": {"min_metros_cuadrados": 100, "porcentaje_descuento": 5},
    "cliente_frecuente": {"min_cotizaciones": 3, "porcentaje_descuento": 3},
    "promocional": {
        "activo": False,
        "porcentaje_descuento": 10,
        "fecha_inicio": "2024-01-01",
        "fecha_fin": "2024-12-31",
    },
}

# Configuración de enlaces web
WEB_CONFIG = {
    "base_url": "https://bmcuruguay.com.uy",
    "productos_url": "https://bmcuruguay.com.uy/productos",
    "contacto_url": "https://bmcuruguay.com.uy/contacto",
    "timeout": 10,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# Configuración de plantillas
PLANTILLAS_CONFIG = {
    "plantillas_disponibles": ["isodec_estandar", "cotizacion_rapida", "cotizacion_detallada"],
    "formato_salida": ["html", "pdf"],
    "incluir_logo": True,
    "incluir_contacto": True,
}

# Configuración de logging
LOGGING_CONFIG = {
    "nivel": "INFO",
    "formato": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "archivo": "sistema_cotizaciones.log",
    "max_tamaño": "10MB",
    "backup_count": 5,
}

# Configuración de validación
VALIDACION_CONFIG = {
    "longitud_minima_nombre": 2,
    "longitud_maxima_nombre": 100,
    "formato_telefono": r"^[\d\s\-\+\(\)]+$",
    "dimensiones_minimas": {"largo": 0.1, "ancho": 0.1},
    "dimensiones_maximas": {"largo": 1000.0, "ancho": 1000.0},
}

# Configuración de exportación
EXPORTACION_CONFIG = {
    "formatos_soportados": ["json", "csv", "xlsx"],
    "incluir_metadata": True,
    "comprimir_archivos": False,
    "directorio_exportacion": "exportaciones",
}


# Función para obtener configuración
def obtener_configuracion(seccion: str = None):
    """
    Obtiene la configuración del sistema

    Args:
        seccion: Sección específica de configuración a obtener

    Returns:
        Diccionario con la configuración solicitada
    """
    configuraciones = {
        "sistema": SISTEMA_CONFIG,
        "moneda": MONEDA_CONFIG,
        "archivos": ARCHIVOS_CONFIG,
        "productos": PRODUCTOS_CONFIG,
        "estados": ESTADOS_CONFIG,
        "asignaciones": ASIGNACIONES_CONFIG,
        "zonas": ZONAS_CONFIG,
        "formulas": FORMULAS_CONFIG,
        "descuentos": DESCUENTOS_CONFIG,
        "web": WEB_CONFIG,
        "plantillas": PLANTILLAS_CONFIG,
        "logging": LOGGING_CONFIG,
        "validacion": VALIDACION_CONFIG,
        "exportacion": EXPORTACION_CONFIG,
    }

    if seccion:
        return configuraciones.get(seccion, {})

    return configuraciones


# Función para validar configuración
def validar_configuracion():
    """
    Valida que la configuración sea correcta

    Returns:
        Lista de errores encontrados
    """
    errores = []

    # Validar configuración de moneda
    if MONEDA_CONFIG["iva_porcentaje"] < 0 or MONEDA_CONFIG["iva_porcentaje"] > 100:
        errores.append("IVA debe estar entre 0 y 100")

    # Validar configuración de productos
    if not PRODUCTOS_CONFIG["productos_principales"]:
        errores.append("Debe haber al menos un producto principal")

    # Validar configuración de estados
    if not ESTADOS_CONFIG["estados"]:
        errores.append("Debe haber al menos un estado de cotización")

    return errores


if __name__ == "__main__":
    # Mostrar configuración actual
    print("CONFIGURACIÓN DEL SISTEMA DE COTIZACIONES BMC URUGUAY")
    print("=" * 60)

    configuracion = obtener_configuracion()
    for seccion, valores in configuracion.items():
        print(f"\n{seccion.upper()}:")
        for clave, valor in valores.items():
            print(f"  {clave}: {valor}")

    # Validar configuración
    errores = validar_configuracion()
    if errores:
        print("\nERRORES ENCONTRADOS:")
        for error in errores:
            print(f"  - {error}")
    else:
        print("\n✓ Configuración válida")
