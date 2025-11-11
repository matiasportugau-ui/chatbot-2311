#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IA Conversacional Integrada BMC Uruguay
Sistema de IA que aprende y evoluciona constantemente
"""

import json
import datetime
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal
import random
from base_conocimiento_dinamica import BaseConocimientoDinamica, InteraccionCliente
from motor_analisis_conversiones import MotorAnalisisConversiones
from sistema_cotizaciones import SistemaCotizacionesBMC, Cliente, EspecificacionCotizacion


@dataclass
class ContextoConversacion:
    """Contexto de una conversación en curso"""
    cliente_id: str
    sesion_id: str
    mensajes_intercambiados: List[Dict[str, Any]]
    intencion_actual: str
    entidades_extraidas: Dict[str, Any]
    estado_cotizacion: str
    datos_cliente: Dict[str, Any]
    datos_producto: Dict[str, Any]
    historial_interacciones: List[str]
    confianza_respuesta: float
    timestamp_inicio: datetime.datetime
    timestamp_ultima_actividad: datetime.datetime


@dataclass
class RespuestaIA:
    """Respuesta generada por la IA"""
    mensaje: str
    tipo_respuesta: str  # informativa, pregunta, cotizacion, seguimiento
    acciones_sugeridas: List[str]
    confianza: float
    fuentes_conocimiento: List[str]
    personalizacion: Dict[str, Any]
    timestamp: datetime.datetime


class IAConversacionalIntegrada:
    """IA Conversacional que aprende y evoluciona constantemente"""
    
    def __init__(self):
        self.base_conocimiento = BaseConocimientoDinamica()
        self.motor_analisis = MotorAnalisisConversiones(self.base_conocimiento)
        self.sistema_cotizaciones = SistemaCotizacionesBMC()
        self.conversaciones_activas = {}
        self.patrones_respuesta = {}
        self.entidades_reconocidas = {}
        self.cargar_configuracion_inicial()
    
    def cargar_configuracion_inicial(self):
        """Carga la configuración inicial de la IA"""
        # Configurar sistema de cotizaciones
        self.sistema_cotizaciones.actualizar_precio_producto("isodec", Decimal('150.00'))
        self.sistema_cotizaciones.actualizar_precio_producto("poliestireno", Decimal('120.00'))
        self.sistema_cotizaciones.actualizar_precio_producto("lana_roca", Decimal('140.00'))
        
        # Cargar patrones de respuesta iniciales
        self.patrones_respuesta = {
            "saludo": [
                "¡Hola! Soy tu asistente de cotizaciones de BMC Uruguay. ¿En qué puedo ayudarte?",
                "¡Buenos días! Estoy aquí para ayudarte con tus consultas de aislamiento térmico.",
                "¡Hola! ¿Te interesa cotizar algún producto de aislamiento térmico?"
            ],
            "despedida": [
                "¡Gracias por contactar BMC Uruguay! Que tengas un excelente día.",
                "Ha sido un placer ayudarte. ¡Hasta la próxima!",
                "Espero haber sido de ayuda. ¡Que tengas un gran día!"
            ],
            "consulta_producto": [
                "Te ayudo con información sobre nuestros productos de aislamiento térmico.",
                "Tenemos varios productos disponibles. ¿Cuál te interesa conocer?",
                "Perfecto, te explico las características de nuestros productos."
            ],
            "cotizacion": [
                "¡Excelente! Vamos a crear tu cotización paso a paso.",
                "Perfecto, necesito algunos datos para darte el precio exacto.",
                "Genial, te ayudo a cotizar el producto que necesitas."
            ]
        }
        
        # Cargar entidades reconocidas
        self.entidades_reconocidas = {
            "productos": ["isodec", "poliestireno", "lana de roca", "lana_roca"],
            "espesores": ["50mm", "75mm", "100mm", "125mm", "150mm"],
            "colores": ["blanco", "gris", "personalizado"],
            "aplicaciones": ["casa", "edificio", "comercial", "industrial", "residencial"],
            "objeciones": ["caro", "costoso", "no estoy seguro", "necesito pensarlo"],
            "intenciones": ["cotizar", "precio", "informacion", "caracteristicas", "instalacion"]
        }
    
    def procesar_mensaje(self, mensaje: str, cliente_id: str, sesion_id: str = None) -> RespuestaIA:
        """Procesa un mensaje del cliente y genera respuesta"""
        if not sesion_id:
            sesion_id = f"sesion_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Obtener o crear contexto de conversación
        contexto = self._obtener_contexto_conversacion(cliente_id, sesion_id)
        
        # Actualizar contexto con nuevo mensaje
        self._actualizar_contexto(contexto, mensaje)
        
        # Analizar mensaje
        intencion = self._analizar_intencion(mensaje)
        entidades = self._extraer_entidades(mensaje)
        
        # Generar respuesta
        respuesta = self._generar_respuesta_inteligente(mensaje, intencion, entidades, contexto)
        
        # Registrar interacción
        self._registrar_interaccion(mensaje, respuesta, contexto)
        
        # Actualizar conocimiento
        self._actualizar_conocimiento_conversacion(contexto, respuesta)
        
        return respuesta
    
    def _obtener_contexto_conversacion(self, cliente_id: str, sesion_id: str) -> ContextoConversacion:
        """Obtiene o crea el contexto de una conversación"""
        clave_contexto = f"{cliente_id}_{sesion_id}"
        
        if clave_contexto in self.conversaciones_activas:
            return self.conversaciones_activas[clave_contexto]
        
        # Crear nuevo contexto
        contexto = ContextoConversacion(
            cliente_id=cliente_id,
            sesion_id=sesion_id,
            mensajes_intercambiados=[],
            intencion_actual="",
            entidades_extraidas={},
            estado_cotizacion="inicial",
            datos_cliente={},
            datos_producto={},
            historial_interacciones=[],
            confianza_respuesta=0.0,
            timestamp_inicio=datetime.datetime.now(),
            timestamp_ultima_actividad=datetime.datetime.now()
        )
        
        self.conversaciones_activas[clave_contexto] = contexto
        return contexto
    
    def _actualizar_contexto(self, contexto: ContextoConversacion, mensaje: str):
        """Actualiza el contexto con un nuevo mensaje"""
        contexto.mensajes_intercambiados.append({
            "tipo": "cliente",
            "mensaje": mensaje,
            "timestamp": datetime.datetime.now().isoformat()
        })
        contexto.timestamp_ultima_actividad = datetime.datetime.now()
    
    def _analizar_intencion(self, mensaje: str) -> str:
        """Analiza la intención del mensaje del cliente"""
        mensaje_lower = mensaje.lower()
        
        # Patrones de intención
        patrones_intencion = {
            "saludo": ["hola", "buenos", "buenas", "hi", "hello"],
            "despedida": ["gracias", "chau", "adios", "bye", "hasta luego"],
            "cotizacion": ["cotizar", "precio", "costo", "cuanto", "presupuesto"],
            "informacion": ["informacion", "caracteristicas", "especificaciones", "que es"],
            "producto": ["isodec", "poliestireno", "lana", "producto"],
            "instalacion": ["instalar", "instalacion", "montaje", "colocacion"],
            "servicio": ["servicio", "garantia", "soporte", "atención"],
            "objecion": ["caro", "costoso", "no estoy seguro", "dudar"]
        }
        
        # Calcular puntuación para cada intención
        puntuaciones = {}
        for intencion, palabras in patrones_intencion.items():
            puntuacion = sum(1 for palabra in palabras if palabra in mensaje_lower)
            puntuaciones[intencion] = puntuacion
        
        # Retornar intención con mayor puntuación
        if puntuaciones:
            intencion_principal = max(puntuaciones, key=puntuaciones.get)
            if puntuaciones[intencion_principal] > 0:
                return intencion_principal
        
        return "general"
    
    def _extraer_entidades(self, mensaje: str) -> Dict[str, Any]:
        """Extrae entidades del mensaje"""
        mensaje_lower = mensaje.lower()
        entidades = {}
        
        # Extraer productos
        productos_encontrados = []
        for producto in self.entidades_reconocidas["productos"]:
            if producto in mensaje_lower:
                productos_encontrados.append(producto)
        if productos_encontrados:
            entidades["productos"] = productos_encontrados
        
        # Extraer espesores
        espesores_encontrados = []
        for espesor in self.entidades_reconocidas["espesores"]:
            if espesor in mensaje_lower:
                espesores_encontrados.append(espesor)
        if espesores_encontrados:
            entidades["espesores"] = espesores_encontrados
        
        # Extraer colores
        colores_encontrados = []
        for color in self.entidades_reconocidas["colores"]:
            if color in mensaje_lower:
                colores_encontrados.append(color)
        if colores_encontrados:
            entidades["colores"] = colores_encontrados
        
        # Extraer dimensiones
        dimensiones = self._extraer_dimensiones(mensaje)
        if dimensiones:
            entidades["dimensiones"] = dimensiones
        
        # Extraer números de teléfono
        telefono = self._extraer_telefono(mensaje)
        if telefono:
            entidades["telefono"] = telefono
        
        return entidades
    
    def _extraer_dimensiones(self, mensaje: str) -> Optional[Dict[str, float]]:
        """Extrae dimensiones del mensaje"""
        # Patrones para dimensiones
        patrones = [
            r'(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*metros?\s*[x×]\s*(\d+(?:\.\d+)?)\s*metros?',
            r'(\d+(?:\.\d+)?)\s*m\s*[x×]\s*(\d+(?:\.\d+)?)\s*m'
        ]
        
        for patron in patrones:
            match = re.search(patron, mensaje, re.IGNORECASE)
            if match:
                try:
                    largo = float(match.group(1))
                    ancho = float(match.group(2))
                    return {"largo": largo, "ancho": ancho}
                except ValueError:
                    continue
        
        return None
    
    def _extraer_telefono(self, mensaje: str) -> Optional[str]:
        """Extrae número de teléfono del mensaje"""
        patron = r'(\+?598\s?)?(\d{2,3}\s?\d{3}\s?\d{3})'
        match = re.search(patron, mensaje)
        if match:
            return match.group(0).replace(' ', '')
        return None
    
    def _generar_respuesta_inteligente(self, mensaje: str, intencion: str, entidades: Dict[str, Any], contexto: ContextoConversacion) -> RespuestaIA:
        """Genera respuesta inteligente basada en el análisis"""
        # Buscar en base de conocimiento
        respuesta_conocimiento = self.base_conocimiento.obtener_respuesta_inteligente(mensaje, contexto.datos_cliente)
        
        if respuesta_conocimiento and len(respuesta_conocimiento) > 50:
            # Usar respuesta de la base de conocimiento
            return self._crear_respuesta(respuesta_conocimiento, "informativa", 0.8, ["base_conocimiento"])
        
        # Generar respuesta basada en intención
        if intencion == "saludo":
            return self._manejar_saludo(contexto)
        elif intencion == "despedida":
            return self._manejar_despedida(contexto)
        elif intencion == "cotizacion":
            return self._manejar_cotizacion(entidades, contexto)
        elif intencion == "informacion":
            return self._manejar_informacion(entidades, contexto)
        elif intencion == "producto":
            return self._manejar_consulta_producto(entidades, contexto)
        elif intencion == "objecion":
            return self._manejar_objecion(mensaje, contexto)
        else:
            return self._manejar_consulta_general(mensaje, contexto)
    
    def _manejar_saludo(self, contexto: ContextoConversacion) -> RespuestaIA:
        """Maneja saludos del cliente"""
        saludos = self.patrones_respuesta["saludo"]
        mensaje = random.choice(saludos)
        
        return self._crear_respuesta(
            mensaje, "informativa", 0.9, ["patrones_respuesta"]
        )
    
    def _manejar_despedida(self, contexto: ContextoConversacion) -> RespuestaIA:
        """Maneja despedidas del cliente"""
        despedidas = self.patrones_respuesta["despedida"]
        mensaje = random.choice(despedidas)
        
        return self._crear_respuesta(
            mensaje, "despedida", 0.9, ["patrones_respuesta"]
        )
    
    def _manejar_cotizacion(self, entidades: Dict[str, Any], contexto: ContextoConversacion) -> RespuestaIA:
        """Maneja solicitudes de cotización"""
        if contexto.estado_cotizacion == "inicial":
            contexto.estado_cotizacion = "recopilando_datos"
            mensaje = ("¡Perfecto! Vamos a crear tu cotización paso a paso.\n\n"
                      "Necesito algunos datos:\n"
                      "1️⃣ ¿Cuál es tu nombre?\n"
                      "2️⃣ ¿Qué producto te interesa? (Isodec, Poliestireno, Lana de Roca)\n"
                      "3️⃣ ¿Cuáles son las dimensiones? (largo x ancho en metros)\n"
                      "4️⃣ ¿Qué espesor necesitas? (50mm, 75mm, 100mm, 125mm, 150mm)")
            
            return self._crear_respuesta(
                mensaje, "pregunta", 0.9, ["sistema_cotizaciones"]
            )
        
        elif contexto.estado_cotizacion == "recopilando_datos":
            # Procesar datos de cotización
            if "productos" in entidades:
                contexto.datos_producto["producto"] = entidades["productos"][0]
            
            if "dimensiones" in entidades:
                contexto.datos_producto["largo"] = entidades["dimensiones"]["largo"]
                contexto.datos_producto["ancho"] = entidades["dimensiones"]["ancho"]
            
            if "espesores" in entidades:
                contexto.datos_producto["espesor"] = entidades["espesores"][0]
            
            # Verificar si tenemos datos suficientes
            if (contexto.datos_producto.get("producto") and 
                contexto.datos_producto.get("largo") and 
                contexto.datos_producto.get("ancho")):
                
                # Crear cotización
                cotizacion = self._crear_cotizacion(contexto)
                if cotizacion:
                    contexto.estado_cotizacion = "cotizacion_completada"
                    mensaje = self._formatear_cotizacion(cotizacion)
                    return self._crear_respuesta(
                        mensaje, "cotizacion", 0.95, ["sistema_cotizaciones"]
                    )
            
            # Solicitar datos faltantes
            datos_faltantes = []
            if not contexto.datos_producto.get("producto"):
                datos_faltantes.append("producto")
            if not contexto.datos_producto.get("largo") or not contexto.datos_producto.get("ancho"):
                datos_faltantes.append("dimensiones")
            if not contexto.datos_producto.get("espesor"):
                datos_faltantes.append("espesor")
            
            mensaje = f"Necesito que me proporciones: {', '.join(datos_faltantes)}"
            return self._crear_respuesta(
                mensaje, "pregunta", 0.8, ["sistema_cotizaciones"]
            )
        
        return self._crear_respuesta(
            "¿En qué más puedo ayudarte?", "pregunta", 0.7, ["general"]
        )
    
    def _manejar_informacion(self, entidades: Dict[str, Any], contexto: ContextoConversacion) -> RespuestaIA:
        """Maneja solicitudes de información"""
        if "productos" in entidades:
            producto = entidades["productos"][0]
            mensaje = self._obtener_informacion_producto(producto)
        else:
            mensaje = ("Tenemos varios productos de aislamiento térmico:\n\n"
                      "🏠 **ISODEC** - Panel aislante con núcleo EPS\n"
                      "🧱 **POLIESTIRENO** - Aislante básico\n"
                      "🪨 **LANA DE ROCA** - Aislante térmico y acústico\n\n"
                      "¿Sobre cuál te gustaría saber más?")
        
        return self._crear_respuesta(
            mensaje, "informativa", 0.9, ["base_conocimiento"]
        )
    
    def _manejar_consulta_producto(self, entidades: Dict[str, Any], contexto: ContextoConversacion) -> RespuestaIA:
        """Maneja consultas específicas sobre productos"""
        if "productos" in entidades:
            producto = entidades["productos"][0]
            mensaje = self._obtener_informacion_producto(producto)
        else:
            mensaje = "¿Sobre qué producto específico te gustaría información?"
        
        return self._crear_respuesta(
            mensaje, "informativa", 0.8, ["base_conocimiento"]
        )
    
    def _manejar_objecion(self, mensaje: str, contexto: ContextoConversacion) -> RespuestaIA:
        """Maneja objeciones del cliente"""
        mensaje_lower = mensaje.lower()
        
        if "caro" in mensaje_lower or "costoso" in mensaje_lower:
            respuesta = ("Entiendo tu preocupación por el precio. Te explico el valor a largo plazo:\n\n"
                        "✅ Ahorro energético del 30-40%\n"
                        "✅ Durabilidad superior a 20 años\n"
                        "✅ Incluye instalación y garantía\n"
                        "✅ Retorno de inversión en 3-5 años\n\n"
                        "¿Te gustaría que te muestre un cálculo de ahorro específico?")
        elif "no estoy seguro" in mensaje_lower:
            respuesta = ("Es normal tener dudas en una inversión importante. Te puedo ayudar:\n\n"
                        "📋 Enviarte información detallada\n"
                        "📞 Conectarte con nuestro técnico\n"
                        "🏠 Mostrarte casos similares exitosos\n\n"
                        "¿Qué te ayudaría a decidir?")
        else:
            respuesta = "Entiendo tu preocupación. ¿Podrías contarme más específicamente qué te preocupa?"
        
        return self._crear_respuesta(
            respuesta, "informativa", 0.8, ["base_conocimiento", "objeciones"]
        )
    
    def _manejar_consulta_general(self, mensaje: str, contexto: ContextoConversacion) -> RespuestaIA:
        """Maneja consultas generales"""
        mensaje = ("Puedo ayudarte con:\n\n"
                  "🏠 Información sobre productos de aislamiento\n"
                  "💰 Cotizaciones personalizadas\n"
                  "📋 Especificaciones técnicas\n"
                  "🔧 Consultas sobre instalación\n\n"
                  "¿En qué te gustaría que te ayude?")
        
        return self._crear_respuesta(
            mensaje, "informativa", 0.7, ["general"]
        )
    
    def _obtener_informacion_producto(self, producto: str) -> str:
        """Obtiene información detallada de un producto"""
        if producto == "isodec":
            return ("🏠 **ISODEC - Panel Aislante Térmico**\n\n"
                   "**Características principales:**\n"
                   "✅ Núcleo de EPS (Poliestireno Expandido)\n"
                   "✅ Excelente aislamiento térmico\n"
                   "✅ Fácil instalación\n"
                   "✅ Durabilidad superior\n\n"
                   "**Opciones disponibles:**\n"
                   "📏 Espesores: 50mm, 75mm, 100mm, 125mm, 150mm\n"
                   "🎨 Colores: Blanco, Gris, Personalizado\n"
                   "🔧 Terminaciones: Gotero, Hormigón, Aluminio\n\n"
                   "💰 **Precio base:** $150/m² (100mm, Blanco)\n\n"
                   "¿Te interesa cotizar Isodec?")
        elif producto == "poliestireno":
            return ("🧱 **POLIESTIRENO EXPANDIDO**\n\n"
                   "**Características principales:**\n"
                   "✅ Aislante térmico básico\n"
                   "✅ Bajo costo\n"
                   "✅ Fácil manipulación\n"
                   "✅ Ideal para proyectos básicos\n\n"
                   "💰 **Precio base:** $120/m² (100mm)\n\n"
                   "¿Te interesa cotizar Poliestireno?")
        elif producto in ["lana", "lana_roca"]:
            return ("🪨 **LANA DE ROCA**\n\n"
                   "**Características principales:**\n"
                   "✅ Aislante térmico y acústico\n"
                   "✅ Resistente al fuego\n"
                   "✅ No tóxico\n"
                   "✅ Excelente durabilidad\n\n"
                   "💰 **Precio base:** $140/m² (100mm)\n\n"
                   "¿Te interesa cotizar Lana de Roca?")
        else:
            return "Producto no reconocido. ¿Podrías especificar cuál te interesa?"
    
    def _crear_cotizacion(self, contexto: ContextoConversacion):
        """Crea una cotización basada en los datos del contexto"""
        try:
            # Crear cliente
            cliente = Cliente(
                nombre=contexto.datos_cliente.get("nombre", "Cliente"),
                telefono=contexto.datos_cliente.get("telefono", ""),
                direccion=contexto.datos_cliente.get("direccion", ""),
                zona=contexto.datos_cliente.get("zona", "")
            )
            
            # Crear especificaciones
            especificaciones = EspecificacionCotizacion(
                producto=contexto.datos_producto.get("producto", "isodec"),
                espesor=contexto.datos_producto.get("espesor", "100mm"),
                relleno="EPS",
                largo_metros=Decimal(str(contexto.datos_producto.get("largo", 5))),
                ancho_metros=Decimal(str(contexto.datos_producto.get("ancho", 3))),
                color=contexto.datos_producto.get("color", "Blanco"),
                termina_front="Gotero",
                termina_sup="Gotero",
                termina_lat_1="Gotero",
                termina_lat_2="Gotero",
                anclajes="Incluido",
                traslado="Incluido"
            )
            
            # Crear cotización
            cotizacion = self.sistema_cotizaciones.crear_cotizacion(
                cliente=cliente,
                especificaciones=especificaciones,
                asignado_a="IA",
                observaciones="Cotización generada por IA conversacional"
            )
            
            return cotizacion
            
        except Exception as e:
            print(f"Error creando cotización: {e}")
            return None
    
    def _formatear_cotizacion(self, cotizacion) -> str:
        """Formatea una cotización para mostrar al cliente"""
        area = cotizacion.especificaciones.largo_metros * cotizacion.especificaciones.ancho_metros
        
        return (f"🎉 **¡COTIZACIÓN LISTA!**\n\n"
                f"📋 **ID:** {cotizacion.id}\n"
                f"🏠 **Producto:** {cotizacion.especificaciones.producto.upper()}\n"
                f"📏 **Dimensiones:** {cotizacion.especificaciones.largo_metros}m x {cotizacion.especificaciones.ancho_metros}m\n"
                f"📐 **Área total:** {area} m²\n"
                f"📐 **Espesor:** {cotizacion.especificaciones.espesor}\n"
                f"🎨 **Color:** {cotizacion.especificaciones.color}\n\n"
                f"💰 **PRECIO POR M²:** ${cotizacion.precio_metro_cuadrado}\n"
                f"💰 **PRECIO TOTAL:** ${cotizacion.precio_total}\n\n"
                f"✅ **Incluye:** Material, terminaciones, anclajes y traslado\n\n"
                f"¿Te parece bien esta cotización? ¿Necesitas algún ajuste?")
    
    def _crear_respuesta(self, mensaje: str, tipo: str, confianza: float, fuentes: List[str]) -> RespuestaIA:
        """Crea una respuesta estructurada"""
        return RespuestaIA(
            mensaje=mensaje,
            tipo_respuesta=tipo,
            acciones_sugeridas=[],
            confianza=confianza,
            fuentes_conocimiento=fuentes,
            personalizacion={},
            timestamp=datetime.datetime.now()
        )
    
    def _registrar_interaccion(self, mensaje_cliente: str, respuesta: RespuestaIA, contexto: ContextoConversacion):
        """Registra la interacción en la base de conocimiento"""
        interaccion = InteraccionCliente(
            id=f"ia_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.datetime.now(),
            cliente_id=contexto.cliente_id,
            tipo_interaccion="consulta_ia",
            mensaje_cliente=mensaje_cliente,
            respuesta_agente=respuesta.mensaje,
            contexto=contexto.datos_cliente,
            resultado="exitoso" if respuesta.confianza > 0.7 else "pendiente",
            satisfaccion_cliente=None
        )
        
        self.base_conocimiento.registrar_interaccion(interaccion)
    
    def _actualizar_conocimiento_conversacion(self, contexto: ContextoConversacion, respuesta: RespuestaIA):
        """Actualiza el conocimiento basado en la conversación"""
        # Actualizar patrones de respuesta si la respuesta fue efectiva
        if respuesta.confianza > 0.8:
            tipo_respuesta = respuesta.tipo_respuesta
            if tipo_respuesta not in self.patrones_respuesta:
                self.patrones_respuesta[tipo_respuesta] = []
            
            if respuesta.mensaje not in self.patrones_respuesta[tipo_respuesta]:
                self.patrones_respuesta[tipo_respuesta].append(respuesta.mensaje)
    
    def exportar_conocimiento_ia(self, archivo: str):
        """Exporta todo el conocimiento de la IA"""
        conocimiento_ia = {
            "patrones_respuesta": self.patrones_respuesta,
            "entidades_reconocidas": self.entidades_reconocidas,
            "conversaciones_activas": {
                k: {
                    "cliente_id": v.cliente_id,
                    "sesion_id": v.sesion_id,
                    "estado_cotizacion": v.estado_cotizacion,
                    "timestamp_inicio": v.timestamp_inicio.isoformat(),
                    "timestamp_ultima_actividad": v.timestamp_ultima_actividad.isoformat()
                } for k, v in self.conversaciones_activas.items()
            },
            "fecha_exportacion": datetime.datetime.now().isoformat()
        }
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(conocimiento_ia, f, ensure_ascii=False, indent=2)


def main():
    """Función principal para demostrar la IA conversacional"""
    print("IA Conversacional Integrada BMC Uruguay")
    print("=" * 50)
    
    # Crear IA
    ia = IAConversacionalIntegrada()
    
    # Simular conversación
    mensajes_simulados = [
        "Hola, necesito información sobre Isodec",
        "Quiero cotizar para mi casa, 10 metros por 5 metros",
        "100mm, blanco",
        "Perfecto, me parece bien el precio"
    ]
    
    cliente_id = "cliente_demo"
    
    for mensaje in mensajes_simulados:
        print(f"\n👤 Cliente: {mensaje}")
        respuesta = ia.procesar_mensaje(mensaje, cliente_id)
        print(f"🤖 IA: {respuesta.mensaje}")
        print(f"   Confianza: {respuesta.confianza:.2f}")
        print(f"   Fuentes: {', '.join(respuesta.fuentes_conocimiento)}")
    
    # Exportar conocimiento
    ia.exportar_conocimiento_ia("ia_conversacional.json")
    print("\nConocimiento de IA exportado a ia_conversacional.json")


if __name__ == "__main__":
    main()
