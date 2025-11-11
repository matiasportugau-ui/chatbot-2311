#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de integración con n8n para Sistema de Cotizaciones BMC
Recibe JSON desde stdin y retorna JSON a stdout
"""

import sys
import json
import datetime
from decimal import Decimal
from typing import Dict, Any, Optional

# Importar módulos del sistema
try:
    from ia_conversacional_integrada import IAConversacionalIntegrada
    from sistema_cotizaciones import SistemaCotizacionesBMC, Cliente, EspecificacionCotizacion
    from base_conocimiento_dinamica import InteraccionCliente
    from motor_analisis_conversiones import MotorAnalisisConversiones
except ImportError as e:
    print(json.dumps({
        "error": f"Error importando módulos del sistema: {str(e)}",
        "success": False
    }))
    sys.exit(1)


def json_serializer(obj):
    """Serializador custom para objetos no-JSON nativos"""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)


def procesar_mensaje(data: Dict[str, Any]) -> Dict[str, Any]:
    """Procesar mensaje conversacional con IA"""
    try:
        ia = IAConversacionalIntegrada()
        
        mensaje = data.get('mensaje', '')
        telefono = data.get('telefono')
        sesion_id = data.get('sesion_id')
        
        if not mensaje:
            return {"error": "Mensaje requerido", "success": False}
        
        # Procesar mensaje con IA conversacional
        respuesta = ia.procesar_mensaje_usuario(
            mensaje=mensaje,
            telefono_cliente=telefono or "default",
            sesion_id=sesion_id
        )
        
        # Convertir respuesta a formato compatible
        if isinstance(respuesta, dict):
            # Ya está en formato correcto
            pass
        else:
            # Convertir RespuestaIA a dict
            respuesta = {
                "mensaje": respuesta.mensaje,
                "tipo": respuesta.tipo_respuesta,
                "acciones": respuesta.acciones_sugeridas,
                "confianza": respuesta.confianza,
                "necesita_datos": [],
                "sesion_id": sesion_id,
                "timestamp": respuesta.timestamp.isoformat()
            }
        
        return {
            "success": True,
            "data": respuesta,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": f"Error procesando mensaje: {str(e)}",
            "success": False
        }


def crear_cotizacion(data: Dict[str, Any]) -> Dict[str, Any]:
    """Crear nueva cotización"""
    try:
        sistema = SistemaCotizacionesBMC()
        
        # Extraer datos del cliente
        cliente_data = data.get('cliente', {})
        cliente = Cliente(
            nombre=cliente_data.get('nombre', 'Cliente'),
            telefono=cliente_data.get('telefono', ''),
            direccion=cliente_data.get('direccion', ''),
            zona=cliente_data.get('zona', 'Montevideo'),
            email=cliente_data.get('email', '')
        )
        
        # Extraer especificaciones
        espec_data = data.get('especificaciones', {})
        especificaciones = EspecificacionCotizacion(
            producto=espec_data.get('producto', ''),
            espesor=espec_data.get('espesor', ''),
            relleno=espec_data.get('relleno', 'EPS'),
            largo_metros=Decimal(str(espec_data.get('largo_metros', 0))),
            ancho_metros=Decimal(str(espec_data.get('ancho_metros', 0))),
            color=espec_data.get('color', 'Blanco'),
            termina_front=espec_data.get('termina_front', ''),
            termina_sup=espec_data.get('termina_sup', ''),
            termina_lat_1=espec_data.get('termina_lat_1', ''),
            termina_lat_2=espec_data.get('termina_lat_2', ''),
            anclajes=espec_data.get('anclajes', ''),
            traslado=espec_data.get('traslado', ''),
            direccion=espec_data.get('direccion', ''),
            forma=espec_data.get('forma', ''),
            origen=espec_data.get('origen', 'WA')
        )
        
        asignado_a = data.get('asignado_a', 'MA')
        observaciones = data.get('observaciones', '')
        
        # Crear cotización
        cotizacion = sistema.crear_cotizacion(
            cliente=cliente,
            especificaciones=especificaciones,
            asignado_a=asignado_a,
            observaciones=observaciones
        )
        
        return {
            "success": True,
            "data": {
                "id": cotizacion.id,
                "cliente": cotizacion.cliente.nombre,
                "telefono": cotizacion.cliente.telefono,
                "producto": cotizacion.especificaciones.producto,
                "precio_total": float(cotizacion.precio_total),
                "precio_m2": float(cotizacion.precio_metro_cuadrado),
                "estado": cotizacion.estado,
                "fecha": cotizacion.fecha.isoformat()
            }
        }
    except Exception as e:
        return {
            "error": f"Error creando cotización: {str(e)}",
            "success": False
        }


def obtener_insights() -> Dict[str, Any]:
    """Obtener insights de la base de conocimiento"""
    try:
        ia = IAConversacionalIntegrada()
        insights = ia.base_conocimiento.generar_insights()
        
        return {
            "success": True,
            "data": {
                "total_interacciones": insights.get('total_interacciones', 0),
                "patrones_exitosos": insights.get('patrones_exitosos', []),
                "productos_populares": insights.get('productos_populares', []),
                "tendencias": insights.get('tendencias', [])
            }
        }
    except Exception as e:
        return {
            "error": f"Error obteniendo insights: {str(e)}",
            "success": False
        }


def analisis_conversiones() -> Dict[str, Any]:
    """Obtener análisis de conversiones"""
    try:
        ia = IAConversacionalIntegrada()
        analisis = ia.motor_analisis.generar_reporte_completo()
        
        return {
            "success": True,
            "data": analisis
        }
    except Exception as e:
        return {
            "error": f"Error en análisis de conversiones: {str(e)}",
            "success": False
        }


def listar_cotizaciones(data: Dict[str, Any]) -> Dict[str, Any]:
    """Listar cotizaciones con filtros opcionales"""
    try:
        sistema = SistemaCotizacionesBMC()
        estado = data.get('estado')
        limite = data.get('limite', 50)
        
        cotizaciones = []
        for cot_id, cot in list(sistema.cotizaciones.items())[:limite]:
            if estado is None or cot.estado == estado:
                cotizaciones.append({
                    "id": cot.id,
                    "cliente": cot.cliente.nombre,
                    "telefono": cot.cliente.telefono,
                    "producto": cot.especificaciones.producto,
                    "precio_total": float(cot.precio_total),
                    "estado": cot.estado,
                    "fecha": cot.fecha.isoformat()
                })
        
        return {
            "success": True,
            "data": cotizaciones,
            "count": len(cotizaciones)
        }
    except Exception as e:
        return {
            "error": f"Error listando cotizaciones: {str(e)}",
            "success": False
        }


def obtener_productos() -> Dict[str, Any]:
    """Obtener lista de productos disponibles"""
    try:
        sistema = SistemaCotizacionesBMC()
        
        productos = []
        for codigo, producto in sistema.productos.items():
            productos.append({
                "codigo": codigo,
                "nombre": producto.nombre,
                "espesor": producto.espesor,
                "relleno": producto.relleno,
                "color": producto.color,
                "precio_base": float(producto.precio_base),
                "link_web": producto.link_web
            })
        
        return {
            "success": True,
            "data": productos,
            "count": len(productos)
        }
    except Exception as e:
        return {
            "error": f"Error obteniendo productos: {str(e)}",
            "success": False
        }


def main():
    """Función principal que procesa el input de n8n"""
    try:
        # Leer JSON desde stdin
        input_data = json.loads(sys.stdin.read())
        
        # Obtener acción
        action = input_data.get('action', '')
        
        # Procesar según la acción
        if action == 'procesar_mensaje':
            resultado = procesar_mensaje(input_data)
        elif action == 'crear_cotizacion':
            resultado = crear_cotizacion(input_data)
        elif action == 'obtener_insights':
            resultado = obtener_insights()
        elif action == 'analisis_conversiones':
            resultado = analisis_conversiones()
        elif action == 'listar_cotizaciones':
            resultado = listar_cotizaciones(input_data)
        elif action == 'obtener_productos':
            resultado = obtener_productos()
        elif action == 'health_check':
            resultado = {
                "success": True,
                "status": "healthy",
                "timestamp": datetime.datetime.now().isoformat()
            }
        else:
            resultado = {
                "error": f"Acción '{action}' no válida",
                "success": False,
                "acciones_disponibles": [
                    "procesar_mensaje",
                    "crear_cotizacion",
                    "obtener_insights",
                    "analisis_conversiones",
                    "listar_cotizaciones",
                    "obtener_productos",
                    "health_check"
                ]
            }
        
        # Retornar JSON a n8n
        print(json.dumps(resultado, ensure_ascii=False, default=json_serializer))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            "error": f"JSON inválido en input: {str(e)}",
            "success": False
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": f"Error general: {str(e)}",
            "success": False
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()

