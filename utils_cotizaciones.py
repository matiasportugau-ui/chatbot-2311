#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades para Cotizaciones BMC Uruguay
Funciones centralizadas para validación de datos y formateo de mensajes
"""

from typing import Dict, Any, List, Optional


# Campos obligatorios para generar una cotización
# Para extender la lista de campos obligatorios en el futuro:
# 1. Agregar el nombre del campo a esta lista
# 2. Actualizar la función obtener_datos_faltantes si requiere lógica especial
# 3. Actualizar formatear_mensaje_faltantes si necesita mensajes específicos
CAMPOS_OBLIGATORIOS = [
    "nombre",
    "apellido",
    "telefono",
    "producto",
    "espesor",
    "largo",
    "ancho"
]


def obtener_datos_faltantes(contexto: dict) -> list[str]:
    """
    Revisa la presencia de campos obligatorios en el contexto.
    
    Args:
        contexto: Diccionario con los datos actuales del cliente y producto.
                  Debe contener keys: nombre, apellido, telefono, producto, 
                  espesor, largo, ancho.
    
    Returns:
        Lista con los nombres de campos faltantes. Lista vacía si todos 
        los campos están completos.
    
    Criterio de campo faltante:
        - None
        - "" (string vacío)
        - 0 (cero numérico)
        - False (booleano)
    
    Ejemplos:
        >>> obtener_datos_faltantes({"nombre": "Juan", "apellido": "", "telefono": "099123456", 
        ...                          "producto": "isodec", "espesor": "100mm", 
        ...                          "largo": 10, "ancho": 5})
        ['apellido']
        
        >>> obtener_datos_faltantes({"nombre": "Juan", "apellido": "Perez", 
        ...                          "telefono": "099123456", "producto": "isodec", 
        ...                          "espesor": "100mm", "largo": 10, "ancho": 5})
        []
    """
    faltantes = []
    
    for campo in CAMPOS_OBLIGATORIOS:
        valor = contexto.get(campo)
        
        # Considerar como faltante si es None, "", 0, False
        if valor is None or valor == "" or valor == 0 or valor is False:
            faltantes.append(campo)
    
    return faltantes


def formatear_mensaje_faltantes(faltantes: list[str]) -> str:
    """
    Formatea un mensaje amigable en español solicitando los datos faltantes.
    
    Args:
        faltantes: Lista de nombres de campos faltantes.
    
    Returns:
        Mensaje en español solicitando los datos faltantes de forma natural.
    
    El mensaje se adapta según la cantidad y tipo de datos faltantes:
        - Un solo campo: mensaje directo y específico
        - Múltiples campos: lista amigable de lo que se necesita
        - Incluye ejemplos y formato esperado cuando es relevante
    
    Ejemplos:
        >>> formatear_mensaje_faltantes(["producto"])
        'Para poder cotizar necesito que me indiques qué producto te interesa...'
        
        >>> formatear_mensaje_faltantes(["nombre", "apellido"])
        'Para poder cotizar necesito: tu nombre completo (nombre y apellido)...'
    """
    if not faltantes:
        return ""
    
    # Diccionario de mensajes específicos para cada campo
    mensajes_campo = {
        "nombre": "tu nombre",
        "apellido": "tu apellido",
        "telefono": "tu número de teléfono",
        "producto": "qué producto te interesa (Isodec, Poliestireno o Lana de Roca)",
        "espesor": "el espesor que necesitas (50mm, 75mm, 100mm, 125mm o 150mm)",
        "largo": "el largo en metros",
        "ancho": "el ancho en metros"
    }
    
    # Caso especial: si faltan tanto largo como ancho, agruparlos como "dimensiones"
    tiene_largo = "largo" in faltantes
    tiene_ancho = "ancho" in faltantes
    
    if tiene_largo and tiene_ancho:
        # Remover largo y ancho de la lista y agregar "dimensiones"
        faltantes_agrupados = [f for f in faltantes if f not in ["largo", "ancho"]]
        faltantes_agrupados.append("dimensiones")
        faltantes = faltantes_agrupados
        mensajes_campo["dimensiones"] = "las dimensiones (largo x ancho en metros, por ejemplo: 10m x 5m)"
    
    # Caso especial: si faltan nombre y apellido, agrupar
    tiene_nombre = "nombre" in faltantes
    tiene_apellido = "apellido" in faltantes
    
    if tiene_nombre and tiene_apellido:
        faltantes_agrupados = [f for f in faltantes if f not in ["nombre", "apellido"]]
        faltantes_agrupados.insert(0, "nombre_completo")
        faltantes = faltantes_agrupados
        mensajes_campo["nombre_completo"] = "tu nombre completo (nombre y apellido)"
    
    # Si falta solo un dato
    if len(faltantes) == 1:
        campo = faltantes[0]
        descripcion = mensajes_campo.get(campo, campo)
        
        if campo == "producto":
            return (f"Para poder cotizar necesito que me indiques {descripcion}. "
                   "¿Cuál te interesa?")
        elif campo == "espesor":
            return (f"Para poder cotizar necesito saber {descripcion}. "
                   "¿Qué espesor necesitas?")
        elif campo == "dimensiones":
            return (f"Para poder cotizar necesito {descripcion}. "
                   "¿Cuáles son las dimensiones?")
        elif campo == "telefono":
            return (f"Para poder cotizar necesito {descripcion} para contactarte. "
                   "¿Cuál es tu teléfono?")
        elif campo in ["nombre", "apellido", "nombre_completo"]:
            return f"Para poder cotizar necesito {descripcion}. ¿Cómo te llamas?"
        else:
            return f"Para poder cotizar necesito {descripcion}. ¿Podrías indicármelo?"
    
    # Si faltan múltiples datos
    descripciones = []
    for campo in faltantes:
        descripcion = mensajes_campo.get(campo, campo)
        descripciones.append(descripcion)
    
    # Formatear la lista de forma amigable
    if len(descripciones) == 2:
        lista_texto = " y ".join(descripciones)
    else:
        lista_texto = ", ".join(descripciones[:-1]) + " y " + descripciones[-1]
    
    return (f"Para poder cotizar necesito los siguientes datos: {lista_texto}. "
           "¿Podrías indicarme esa información?")


def validar_datos_completos(contexto: dict) -> tuple[bool, Optional[str]]:
    """
    Valida si todos los datos obligatorios están completos y retorna
    un mensaje si falta algo.
    
    Args:
        contexto: Diccionario con los datos del cliente y producto.
    
    Returns:
        Tupla (datos_completos: bool, mensaje: Optional[str])
        - datos_completos: True si todos los datos están presentes
        - mensaje: None si datos completos, mensaje formateado si faltan datos
    
    Esta función combina obtener_datos_faltantes y formatear_mensaje_faltantes
    para simplificar la validación en los flujos conversacionales.
    
    Ejemplo:
        >>> validar_datos_completos({"nombre": "Juan", "apellido": "Perez",
        ...                          "telefono": "099123456", "producto": "isodec",
        ...                          "espesor": "100mm", "largo": 10, "ancho": 5})
        (True, None)
        
        >>> validar_datos_completos({"nombre": "Juan", "apellido": "",
        ...                          "telefono": "099123456", "producto": "isodec",
        ...                          "espesor": "100mm", "largo": 10, "ancho": 5})
        (False, "Para poder cotizar necesito tu apellido. ¿Cómo te llamas?")
    """
    faltantes = obtener_datos_faltantes(contexto)
    
    if not faltantes:
        return (True, None)
    
    mensaje = formatear_mensaje_faltantes(faltantes)
    return (False, mensaje)


# Función auxiliar para construir el contexto de validación desde diferentes estructuras
def construir_contexto_validacion(datos_cliente: dict, datos_producto: dict) -> dict:
    """
    Construye un contexto de validación a partir de diccionarios de datos de cliente y producto.
    
    Esta función auxiliar facilita la construcción del contexto esperado por 
    obtener_datos_faltantes desde las estructuras de datos usadas en los diferentes
    módulos del sistema.
    
    Args:
        datos_cliente: Diccionario con datos del cliente (nombre, apellido, telefono, etc.)
        datos_producto: Diccionario con datos del producto (producto, espesor, largo, ancho, etc.)
    
    Returns:
        Diccionario con todos los campos unificados para validación.
    
    Ejemplo:
        >>> cliente = {"nombre": "Juan", "apellido": "Perez", "telefono": "099123456"}
        >>> producto = {"producto": "isodec", "espesor": "100mm", "largo": 10, "ancho": 5}
        >>> contexto = construir_contexto_validacion(cliente, producto)
        >>> contexto
        {'nombre': 'Juan', 'apellido': 'Perez', 'telefono': '099123456', 
         'producto': 'isodec', 'espesor': '100mm', 'largo': 10, 'ancho': 5}
    """
    return {
        "nombre": datos_cliente.get("nombre"),
        "apellido": datos_cliente.get("apellido"),
        "telefono": datos_cliente.get("telefono"),
        "producto": datos_producto.get("producto"),
        "espesor": datos_producto.get("espesor"),
        "largo": datos_producto.get("largo"),
        "ancho": datos_producto.get("ancho"),
    }


if __name__ == "__main__":
    # Ejemplos de uso
    print("=== Utilidades de Validación de Cotizaciones ===\n")
    
    # Ejemplo 1: Contexto completo
    print("📋 Ejemplo 1: Datos completos")
    contexto_completo = {
        "nombre": "Juan",
        "apellido": "Perez",
        "telefono": "099123456",
        "producto": "isodec",
        "espesor": "100mm",
        "largo": 10,
        "ancho": 5
    }
    faltantes = obtener_datos_faltantes(contexto_completo)
    print(f"Datos faltantes: {faltantes}")
    if faltantes:
        print(f"Mensaje: {formatear_mensaje_faltantes(faltantes)}")
    else:
        print("✅ Todos los datos están completos\n")
    
    # Ejemplo 2: Falta un campo
    print("📋 Ejemplo 2: Falta el apellido")
    contexto_sin_apellido = {
        "nombre": "Juan",
        "apellido": "",
        "telefono": "099123456",
        "producto": "isodec",
        "espesor": "100mm",
        "largo": 10,
        "ancho": 5
    }
    faltantes = obtener_datos_faltantes(contexto_sin_apellido)
    print(f"Datos faltantes: {faltantes}")
    print(f"Mensaje: {formatear_mensaje_faltantes(faltantes)}\n")
    
    # Ejemplo 3: Faltan múltiples campos
    print("📋 Ejemplo 3: Faltan varios campos")
    contexto_incompleto = {
        "nombre": "Juan",
        "apellido": None,
        "telefono": "",
        "producto": "isodec",
        "espesor": "",
        "largo": 10,
        "ancho": 5
    }
    faltantes = obtener_datos_faltantes(contexto_incompleto)
    print(f"Datos faltantes: {faltantes}")
    print(f"Mensaje: {formatear_mensaje_faltantes(faltantes)}\n")
    
    # Ejemplo 4: Faltan dimensiones
    print("📋 Ejemplo 4: Faltan las dimensiones")
    contexto_sin_dimensiones = {
        "nombre": "Juan",
        "apellido": "Perez",
        "telefono": "099123456",
        "producto": "isodec",
        "espesor": "100mm",
        "largo": 0,
        "ancho": 0
    }
    faltantes = obtener_datos_faltantes(contexto_sin_dimensiones)
    print(f"Datos faltantes: {faltantes}")
    print(f"Mensaje: {formatear_mensaje_faltantes(faltantes)}\n")
    
    # Ejemplo 5: Usando validar_datos_completos
    print("📋 Ejemplo 5: Usando validar_datos_completos")
    completo, mensaje = validar_datos_completos(contexto_sin_apellido)
    print(f"¿Datos completos?: {completo}")
    if mensaje:
        print(f"Mensaje: {mensaje}\n")
    
    # Ejemplo 6: Usando construir_contexto_validacion
    print("📋 Ejemplo 6: Construir contexto desde diccionarios separados")
    datos_cliente = {"nombre": "Maria", "apellido": "Rodriguez", "telefono": "098765432"}
    datos_producto = {"producto": "poliestireno", "espesor": "75mm", "largo": 8, "ancho": 4}
    contexto = construir_contexto_validacion(datos_cliente, datos_producto)
    completo, mensaje = validar_datos_completos(contexto)
    print(f"Contexto construido: {contexto}")
    print(f"¿Datos completos?: {completo}")
    if mensaje:
        print(f"Mensaje: {mensaje}")
    else:
        print("✅ Todos los datos están completos")
