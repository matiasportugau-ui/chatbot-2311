#!/usr/bin/env python3
"""
IA Conversacional Integrada BMC Uruguay
Sistema de IA que aprende y evoluciona constantemente
"""

import datetime
import json
import os
import random
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not available, will use system environment variables
from base_conocimiento_dinamica import BaseConocimientoDinamica, InteraccionCliente
from motor_analisis_conversiones import MotorAnalisisConversiones
from sistema_cotizaciones import (
    Cliente,
    EspecificacionCotizacion,
    SistemaCotizacionesBMC,
)
from utils_cotizaciones import (
    construir_contexto_validacion,
    formatear_mensaje_faltantes,
    obtener_datos_faltantes,
)

# Unified Model Integrator
try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False
    print("Warning: Model integrator not available. Using pattern matching only.")

# OpenAI integration (fallback)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class ContextoConversacion:
    """Contexto de una conversación en curso"""

    cliente_id: str
    sesion_id: str
    mensajes_intercambiados: list[dict[str, Any]]
    intencion_actual: str
    entidades_extraidas: dict[str, Any]
    estado_cotizacion: str
    datos_cliente: dict[str, Any]
    datos_producto: dict[str, Any]
    historial_interacciones: list[str]
    confianza_respuesta: float
    timestamp_inicio: datetime.datetime
    timestamp_ultima_actividad: datetime.datetime


@dataclass
class RespuestaIA:
    """Respuesta generada por la IA"""

    mensaje: str
    tipo_respuesta: str  # informativa, pregunta, cotizacion, seguimiento
    acciones_sugeridas: list[str]
    confianza: float
    fuentes_conocimiento: list[str]
    personalizacion: dict[str, Any]
    timestamp: datetime.datetime


class IAConversacionalIntegrada:
    """IA Conversacional que aprende y evoluciona constantemente"""

    # Memory limits to prevent unbounded growth
    MAX_CONVERSATIONS = 100  # Maximum number of active conversations to keep in memory
    MAX_MESSAGES_PER_CONVERSATION = 50  # Maximum messages per conversation
    CONVERSATION_TIMEOUT_HOURS = 24  # Remove conversations inactive for this many hours

    def __init__(self):
        self.base_conocimiento = BaseConocimientoDinamica()
        self.motor_analisis = MotorAnalisisConversiones(self.base_conocimiento)
        self.sistema_cotizaciones = SistemaCotizacionesBMC()
        self.conversaciones_activas = {}
        self.patrones_respuesta = {}
        self.entidades_reconocidas = {}

        # Shared context service for multi-agent system
        try:
            import sys
            from pathlib import Path

            python_scripts_path = Path(__file__).parent / "python-scripts"
            if str(python_scripts_path) not in sys.path:
                sys.path.insert(0, str(python_scripts_path))
            from shared_context_service import get_shared_context_service

            self.shared_context_service = get_shared_context_service()
            self.use_shared_context = True
        except Exception as e:
            self.shared_context_service = None
            self.use_shared_context = False
            print(f"Warning: Shared context service not available: {e}")

        # Unified Model Integrator configuration
        self.use_ai = False
        self.model_integrator = None
        self.openai_client = None  # Fallback
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # Try to initialize unified model integrator first
        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.model_integrator = get_model_integrator()
                # Check if any models are available
                available_models = self.model_integrator.list_available_models()
                if available_models:
                    self.use_ai = True
                    print(f"✅ Model integrator enabled with {len(available_models)} models")
                    for model in available_models:
                        if model['enabled']:
                            print(f"   - {model['provider']}: {model['model_name']}")
                else:
                    print("⚠️ No models configured in model integrator")
            except Exception as e:
                print(f"⚠️ Error initializing model integrator: {e}")
                self.use_ai = False
        
        # Fallback to OpenAI if integrator not available
        if not self.use_ai and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    self.openai_client = OpenAI(api_key=api_key)
                    self.use_ai = True
                    print("✅ OpenAI integration enabled (fallback mode)")
                except Exception as e:
                    print(f"⚠️ Error initializing OpenAI: {e}")
                    self.use_ai = False
            else:
                print("⚠️ No API keys configured, using pattern matching only")
        elif not self.use_ai:
            print("⚠️ No AI models available, using pattern matching only")

        self.cargar_configuracion_inicial()

    def cargar_configuracion_inicial(self):
        """Carga la configuración inicial de la IA"""
        # Configurar sistema de cotizaciones
        self.sistema_cotizaciones.actualizar_precio_producto("isodec", Decimal("150.00"))
        self.sistema_cotizaciones.actualizar_precio_producto("poliestireno", Decimal("120.00"))
        self.sistema_cotizaciones.actualizar_precio_producto("lana_roca", Decimal("140.00"))

        # Cargar patrones de respuesta iniciales
        self.patrones_respuesta = {
            "saludo": [
                "¡Hola! Soy tu asistente de cotizaciones de BMC Uruguay. ¿En qué puedo ayudarte?",
                "¡Buenos días! Estoy aquí para ayudarte con tus consultas de aislamiento térmico.",
                "¡Hola! ¿Te interesa cotizar algún producto de aislamiento térmico?",
            ],
            "despedida": [
                "¡Gracias por contactar BMC Uruguay! Que tengas un excelente día.",
                "Ha sido un placer ayudarte. ¡Hasta la próxima!",
                "Espero haber sido de ayuda. ¡Que tengas un gran día!",
            ],
            "consulta_producto": [
                "Te ayudo con información sobre nuestros productos de aislamiento térmico.",
                "Tenemos varios productos disponibles. ¿Cuál te interesa conocer?",
                "Perfecto, te explico las características de nuestros productos.",
            ],
            "cotizacion": [
                "¡Excelente! Vamos a crear tu cotización paso a paso.",
                "Perfecto, necesito algunos datos para darte el precio exacto.",
                "Genial, te ayudo a cotizar el producto que necesitas.",
            ],
        }

        # Cargar entidades reconocidas
        self.entidades_reconocidas = {
            "productos": ["isodec", "poliestireno", "lana de roca", "lana_roca"],
            "espesores": ["50mm", "75mm", "100mm", "125mm", "150mm"],
            "colores": ["blanco", "gris", "personalizado"],
            "aplicaciones": [
                "casa",
                "edificio",
                "comercial",
                "industrial",
                "residencial",
            ],
            "objeciones": ["caro", "costoso", "no estoy seguro", "necesito pensarlo"],
            "intenciones": [
                "cotizar",
                "precio",
                "informacion",
                "caracteristicas",
                "instalacion",
            ],
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

        # Save to shared context service
        if self.use_shared_context and self.shared_context_service and contexto.sesion_id:
            try:
                # Add assistant message
                self.shared_context_service.add_message(
                    contexto.sesion_id,
                    respuesta.mensaje,
                    "assistant",
                    {
                        "intent": intencion,
                        "entities": entidades,
                        "confidence": respuesta.confianza,
                    },
                )
                # Save full context
                context_dict = {
                    "user_phone": contexto.cliente_id,
                    "cliente_id": contexto.cliente_id,
                    "intent": contexto.intencion_actual,
                    "entities": contexto.entidades_extraidas,
                    "quote_state": {
                        "estado": contexto.estado_cotizacion,
                        "datos_cliente": contexto.datos_cliente,
                        "datos_producto": contexto.datos_producto,
                    },
                    "messages": [
                        {
                            "role": msg.get("tipo") == "cliente" and "user" or "assistant",
                            "content": msg.get("mensaje", ""),
                            "timestamp": msg.get("timestamp", datetime.datetime.now()),
                        }
                        for msg in contexto.mensajes_intercambiados
                    ],
                }
                self.shared_context_service.save_context(contexto.sesion_id, context_dict)
            except Exception as e:
                print(f"Warning: Failed to save context to shared service: {e}")

        return respuesta

    def _obtener_contexto_conversacion(
        self, cliente_id: str, sesion_id: str
    ) -> ContextoConversacion:
        """Obtiene o crea el contexto de una conversación"""
        clave_contexto = f"{cliente_id}_{sesion_id}"

        # Try to load from shared context service first
        if self.use_shared_context and self.shared_context_service and sesion_id:
            try:
                shared_context = self.shared_context_service.get_context(sesion_id, cliente_id)
                if shared_context:
                    # Convert shared context to ContextoConversacion
                    contexto = ContextoConversacion(
                        cliente_id=cliente_id,
                        sesion_id=sesion_id,
                        mensajes_intercambiados=[
                            {
                                "tipo": msg.get("role") == "user" and "cliente" or "asistente",
                                "mensaje": msg.get("content", ""),
                                "timestamp": msg.get("timestamp", datetime.datetime.now()),
                            }
                            for msg in shared_context.get("messages", [])
                        ],
                        intencion_actual=shared_context.get("intent", "general"),
                        entidades_extraidas=shared_context.get("entities", {}),
                        estado_cotizacion=shared_context.get("quote_state", {}).get(
                            "estado", "inicial"
                        ),
                        datos_cliente=shared_context.get("quote_state", {}).get(
                            "datos_cliente", {}
                        ),
                        datos_producto=shared_context.get("quote_state", {}).get(
                            "datos_producto", {}
                        ),
                        historial_interacciones=[],
                        confianza_respuesta=0.8,
                        timestamp_inicio=datetime.datetime.now(),
                        timestamp_ultima_actividad=datetime.datetime.now(),
                    )
                    # Store in active conversations for backward compatibility
                    self.conversaciones_activas[clave_contexto] = contexto
                    return contexto
            except Exception as e:
                print(f"Warning: Failed to load context from shared service: {e}")

        # Fallback to in-memory
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
            timestamp_ultima_actividad=datetime.datetime.now(),
        )

        self.conversaciones_activas[clave_contexto] = contexto
        
        # Periodically cleanup old conversations to prevent memory growth
        if len(self.conversaciones_activas) > self.MAX_CONVERSATIONS:
            self._limpiar_conversaciones_antiguas()
        
        return contexto

    def _limpiar_conversaciones_antiguas(self):
        """Remove old or inactive conversations to free memory"""
        if not self.conversaciones_activas:
            return
        
        now = datetime.datetime.now()
        timeout_delta = datetime.timedelta(hours=self.CONVERSATION_TIMEOUT_HOURS)
        
        # Remove conversations that are inactive for too long
        keys_to_remove = []
        for clave, contexto in self.conversaciones_activas.items():
            time_since_activity = now - contexto.timestamp_ultima_actividad
            if time_since_activity > timeout_delta:
                keys_to_remove.append(clave)
        
        # Remove old conversations
        for clave in keys_to_remove:
            del self.conversaciones_activas[clave]
        
        # If still over limit, remove oldest conversations
        if len(self.conversaciones_activas) > self.MAX_CONVERSATIONS:
            # Sort by last activity time and remove oldest
            sorted_conversations = sorted(
                self.conversaciones_activas.items(),
                key=lambda x: x[1].timestamp_ultima_actividad
            )
            # Remove oldest conversations
            num_to_remove = len(self.conversaciones_activas) - self.MAX_CONVERSATIONS
            for clave, _ in sorted_conversations[:num_to_remove]:
                del self.conversaciones_activas[clave]
        
        if keys_to_remove or len(self.conversaciones_activas) > self.MAX_CONVERSATIONS:
            # Use print if logger not available
            try:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Cleaned up {len(keys_to_remove)} old conversations. Active: {len(self.conversaciones_activas)}")
            except:
                print(f"Cleaned up {len(keys_to_remove)} old conversations. Active: {len(self.conversaciones_activas)}")

    def _actualizar_contexto(self, contexto: ContextoConversacion, mensaje: str):
        """Actualiza el contexto con un nuevo mensaje"""
        contexto.mensajes_intercambiados.append(
            {
                "tipo": "cliente",
                "mensaje": mensaje,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )
        # Limit message history to prevent unbounded memory growth
        if len(contexto.mensajes_intercambiados) > self.MAX_MESSAGES_PER_CONVERSATION:
            # Keep only the most recent messages
            contexto.mensajes_intercambiados = contexto.mensajes_intercambiados[-self.MAX_MESSAGES_PER_CONVERSATION:]
        contexto.timestamp_ultima_actividad = datetime.datetime.now()


    def _analizar_intencion(self, mensaje: str) -> tuple[str, float]:
        """Analiza la intención del mensaje del cliente con confidence scoring

        Returns:
            Tuple[str, float]: (intent, confidence_score)
        """

        mensaje_lower = mensaje.lower()

        # Patrones de intención
        patrones_intencion = {
            "saludo": ["hola", "buenos", "buenas", "hi", "hello"],
            "despedida": ["gracias", "chau", "adios", "bye", "hasta luego"],
            "cotizacion": ["cotizar", "precio", "costo", "cuanto", "presupuesto"],
            "informacion": [
                "informacion",
                "información",
                "caracteristicas",
                "especificaciones",
                "que es",
                "necesito",
                "sobre",
                "acerca",
                "techos",
                "techo",
                "aislamiento",
            ],
            "producto": ["isodec", "poliestireno", "lana", "producto", "productos"],
            "instalacion": ["instalar", "instalacion", "montaje", "colocacion"],
            "servicio": ["servicio", "garantia", "soporte", "atención"],
            "objecion": ["caro", "costoso", "no estoy seguro", "dudar"],
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


    def _extraer_entidades(self, mensaje: str) -> dict[str, Any]:
        """Extrae entidades del mensaje con matching mejorado"""

        mensaje_lower = mensaje.lower()
        entidades = {}

        # Extraer productos
        productos_encontrados = []
        for producto in self.entidades_reconocidas["productos"]:
            if producto in mensaje_lower:
                productos_encontrados.append(producto)
        if productos_encontrados:

            entidades["productos"] = list(set(productos_encontrados))  # Remove duplicates


        # Extraer espesores
        espesores_encontrados = []
        for espesor in self.entidades_reconocidas["espesores"]:
            if espesor in mensaje_lower:
                espesores_encontrados.append(espesor)
        if espesores_encontrados:

            entidades["espesores"] = list(set(espesores_encontrados))  # Remove duplicates


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

        # Extraer nombre y apellido
        nombre_apellido = self._extraer_nombre_apellido(mensaje)
        if nombre_apellido:
            entidades["nombre"] = nombre_apellido["nombre"]
            entidades["apellido"] = nombre_apellido["apellido"]

        return entidades

    def _extraer_dimensiones(self, mensaje: str) -> dict[str, float] | None:
        """Extrae dimensiones del mensaje"""
        # Patrones para dimensiones
        patrones = [
            r"(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*metros?\s*[x×]\s*(\d+(?:\.\d+)?)\s*metros?",
            r"(\d+(?:\.\d+)?)\s*m\s*[x×]\s*(\d+(?:\.\d+)?)\s*m",
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

    def _extraer_telefono(self, mensaje: str) -> str | None:
        """Extrae número de teléfono del mensaje"""
        patron = r"(\+?598\s?)?(\d{2,3}\s?\d{3}\s?\d{3})"
        match = re.search(patron, mensaje)
        if match:
            return match.group(0).replace(" ", "")
        return None

    def _extraer_nombre_apellido(self, mensaje: str) -> dict[str, str] | None:
        """Extrae nombre y apellido del mensaje"""
        # Buscar patrones comunes de presentación
        # Ejemplos: "Me llamo Juan Perez", "Soy Maria Rodriguez", "Juan Perez"

        # Patrón: "me llamo/soy + nombre apellido"
        patron_presentacion = r"(?:me llamo|soy|mi nombre es)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)"
        match = re.search(patron_presentacion, mensaje, re.IGNORECASE)

        if match:
            nombre_completo = match.group(1).strip()
            partes = nombre_completo.split()
            if len(partes) >= 2:
                return {"nombre": partes[0], "apellido": " ".join(partes[1:])}

        # Patrón: dos palabras capitalizadas consecutivas (sin palabras clave antes)
        # Solo si no hay otras palabras clave en el mensaje
        mensaje_limpio = mensaje.strip()
        palabras_clave = [
            "producto",
            "isodec",
            "poliestireno",
            "lana",
            "metro",
            "espesor",
            "precio",
        ]

        if not any(palabra in mensaje.lower() for palabra in palabras_clave):
            patron_nombre_simple = r"^([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)$"
            match = re.match(patron_nombre_simple, mensaje_limpio)

            if match:
                return {"nombre": match.group(1), "apellido": match.group(2)}

        return None

    def _generar_respuesta_inteligente(
        self,
        mensaje: str,
        intencion: str,
        entidades: dict[str, Any],
        contexto: ContextoConversacion,
    ) -> RespuestaIA:
        """Genera respuesta inteligente basada en el análisis"""
        # Primero, intentar generar respuesta basada en intención detectada
        # Solo usar base de conocimiento si no hay intención clara o si la intención es "general"

        # Respuestas genéricas que debemos ignorar de la base de conocimiento
        respuestas_genericas = [
            "gracias por tu consulta",
            "te ayudo con la información",
            "puedo ayudarte con",
        ]

        # Si hay una intención específica detectada, usarla primero
        if intencion != "general":
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

        # Si intención es "general", buscar en base de conocimiento
        # pero solo si la respuesta no es genérica
        respuesta_conocimiento = self.base_conocimiento.obtener_respuesta_inteligente(
            mensaje, contexto.datos_cliente
        )

        if respuesta_conocimiento and len(respuesta_conocimiento) > 50:
            # Verificar si la respuesta es genérica
            respuesta_lower = respuesta_conocimiento.lower()
            es_generica = any(generica in respuesta_lower for generica in respuestas_genericas)

            if not es_generica:
                # Usar respuesta de la base de conocimiento si no es genérica
                return self._crear_respuesta(
                    respuesta_conocimiento, "informativa", 0.8, ["base_conocimiento"]
                )

        # Si llegamos aquí, usar respuesta general
        return self._manejar_consulta_general(mensaje, contexto)

    def _manejar_saludo(self, contexto: ContextoConversacion) -> RespuestaIA:
        """Maneja saludos del cliente"""
        saludos = self.patrones_respuesta["saludo"]
        mensaje = random.choice(saludos)

        return self._crear_respuesta(mensaje, "informativa", 0.9, ["patrones_respuesta"])

    def _manejar_despedida(self, contexto: ContextoConversacion) -> RespuestaIA:
        """Maneja despedidas del cliente"""
        despedidas = self.patrones_respuesta["despedida"]
        mensaje = random.choice(despedidas)

        return self._crear_respuesta(mensaje, "despedida", 0.9, ["patrones_respuesta"])

    def _manejar_cotizacion(
        self, entidades: dict[str, Any], contexto: ContextoConversacion
    ) -> RespuestaIA:
        """Maneja solicitudes de cotización"""
        if contexto.estado_cotizacion == "inicial":
            contexto.estado_cotizacion = "recopilando_datos"
            mensaje = (
                "¡Perfecto! Vamos a crear tu cotización paso a paso.\n\n"
                "Necesito algunos datos:\n"
                "1️⃣ ¿Cuál es tu nombre y apellido?\n"
                "2️⃣ ¿Cuál es tu teléfono?\n"
                "3️⃣ ¿Qué producto te interesa? (Isodec, Poliestireno, Lana de Roca)\n"
                "4️⃣ ¿Cuáles son las dimensiones? (largo x ancho en metros)\n"
                "5️⃣ ¿Qué espesor necesitas? (50mm, 75mm, 100mm, 125mm, 150mm)"
            )

            return self._crear_respuesta(mensaje, "pregunta", 0.9, ["sistema_cotizaciones"])

        elif contexto.estado_cotizacion == "recopilando_datos":
            # Actualizar datos del cliente con entidades extraídas
            if "nombre" in entidades:
                contexto.datos_cliente["nombre"] = entidades["nombre"]

            if "apellido" in entidades:
                contexto.datos_cliente["apellido"] = entidades["apellido"]

            if "telefono" in entidades:
                contexto.datos_cliente["telefono"] = entidades["telefono"]

            # Actualizar datos del producto con entidades extraídas
            if "productos" in entidades:
                contexto.datos_producto["producto"] = entidades["productos"][0]

            if "dimensiones" in entidades:
                contexto.datos_producto["largo"] = entidades["dimensiones"]["largo"]
                contexto.datos_producto["ancho"] = entidades["dimensiones"]["ancho"]

            if "espesores" in entidades:
                contexto.datos_producto["espesor"] = entidades["espesores"][0]

            # Construir contexto de validación unificado
            contexto_validacion = construir_contexto_validacion(
                contexto.datos_cliente, contexto.datos_producto
            )

            # Usar validación centralizada para verificar datos faltantes
            datos_faltantes = obtener_datos_faltantes(contexto_validacion)

            if datos_faltantes:
                # Hay datos faltantes, solicitar al cliente
                mensaje = formatear_mensaje_faltantes(datos_faltantes)
                return self._crear_respuesta(mensaje, "pregunta", 0.8, ["sistema_cotizaciones"])

            # Todos los datos están completos, crear cotización
            cotizacion = self._crear_cotizacion(contexto)
            if cotizacion:
                contexto.estado_cotizacion = "cotizacion_completada"
                mensaje = self._formatear_cotizacion(cotizacion)
                return self._crear_respuesta(mensaje, "cotizacion", 0.95, ["sistema_cotizaciones"])
            else:
                # Error al crear cotización
                return self._crear_respuesta(
                    "Hubo un error al generar la cotización. ¿Podrías verificar los datos?",
                    "pregunta",
                    0.5,
                    ["sistema_cotizaciones"],
                )

        return self._crear_respuesta("¿En qué más puedo ayudarte?", "pregunta", 0.7, ["general"])

    def _manejar_informacion(
        self, entidades: dict[str, Any], contexto: ContextoConversacion
    ) -> RespuestaIA:
        """Maneja solicitudes de información"""
        if "productos" in entidades:
            producto = entidades["productos"][0]
            mensaje = self._obtener_informacion_producto(producto)
        else:
            mensaje = (
                "Tenemos varios productos de aislamiento térmico:\n\n"
                "🏠 **ISODEC** - Panel aislante con núcleo EPS\n"
                "🧱 **POLIESTIRENO** - Aislante básico\n"
                "🪨 **LANA DE ROCA** - Aislante térmico y acústico\n\n"
                "¿Sobre cuál te gustaría saber más?"
            )

        return self._crear_respuesta(mensaje, "informativa", 0.9, ["base_conocimiento"])

    def _manejar_consulta_producto(
        self, entidades: dict[str, Any], contexto: ContextoConversacion
    ) -> RespuestaIA:
        """Maneja consultas específicas sobre productos"""
        if "productos" in entidades:
            producto = entidades["productos"][0]
            mensaje = self._obtener_informacion_producto(producto)
        else:
            mensaje = "¿Sobre qué producto específico te gustaría información?"

        return self._crear_respuesta(mensaje, "informativa", 0.8, ["base_conocimiento"])

    def _manejar_objecion(self, mensaje: str, contexto: ContextoConversacion) -> RespuestaIA:
        """Maneja objeciones del cliente"""
        mensaje_lower = mensaje.lower()

        if "caro" in mensaje_lower or "costoso" in mensaje_lower:
            respuesta = (
                "Entiendo tu preocupación por el precio. Te explico el valor a largo plazo:\n\n"
                "✅ Ahorro energético del 30-40%\n"
                "✅ Durabilidad superior a 20 años\n"
                "✅ Incluye instalación y garantía\n"
                "✅ Retorno de inversión en 3-5 años\n\n"
                "¿Te gustaría que te muestre un cálculo de ahorro específico?"
            )
        elif "no estoy seguro" in mensaje_lower:
            respuesta = (
                "Es normal tener dudas en una inversión importante. Te puedo ayudar:\n\n"
                "📋 Enviarte información detallada\n"
                "📞 Conectarte con nuestro técnico\n"
                "🏠 Mostrarte casos similares exitosos\n\n"
                "¿Qué te ayudaría a decidir?"
            )
        else:
            respuesta = (
                "Entiendo tu preocupación. ¿Podrías contarme más específicamente qué te preocupa?"
            )

        return self._crear_respuesta(
            respuesta, "informativa", 0.8, ["base_conocimiento", "objeciones"]
        )

    def _manejar_consulta_general(
        self, mensaje: str, contexto: ContextoConversacion
    ) -> RespuestaIA:
        """Maneja consultas generales"""
        mensaje = (
            "Puedo ayudarte con:\n\n"
            "🏠 Información sobre productos de aislamiento\n"
            "💰 Cotizaciones personalizadas\n"
            "📋 Especificaciones técnicas\n"
            "🔧 Consultas sobre instalación\n\n"
            "¿En qué te gustaría que te ayude?"
        )

        return self._crear_respuesta(mensaje, "informativa", 0.7, ["general"])

    def _obtener_informacion_producto(self, producto: str) -> str:
        """Obtiene información detallada de un producto"""
        if producto == "isodec":
            return (
                "🏠 **ISODEC - Panel Aislante Térmico**\n\n"
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
                "¿Te interesa cotizar Isodec?"
            )
        elif producto == "poliestireno":
            return (
                "🧱 **POLIESTIRENO EXPANDIDO**\n\n"
                "**Características principales:**\n"
                "✅ Aislante térmico básico\n"
                "✅ Bajo costo\n"
                "✅ Fácil manipulación\n"
                "✅ Ideal para proyectos básicos\n\n"
                "💰 **Precio base:** $120/m² (100mm)\n\n"
                "¿Te interesa cotizar Poliestireno?"
            )
        elif producto in ["lana", "lana_roca"]:
            return (
                "🪨 **LANA DE ROCA**\n\n"
                "**Características principales:**\n"
                "✅ Aislante térmico y acústico\n"
                "✅ Resistente al fuego\n"
                "✅ No tóxico\n"
                "✅ Excelente durabilidad\n\n"
                "💰 **Precio base:** $140/m² (100mm)\n\n"
                "¿Te interesa cotizar Lana de Roca?"
            )
        else:
            return "Producto no reconocido. ¿Podrías especificar cuál te interesa?"

    def _crear_cotizacion(self, contexto: ContextoConversacion):
        """Crea una cotización basada en los datos del contexto"""
        try:
            # Combinar nombre y apellido para el campo nombre del cliente
            nombre_completo = contexto.datos_cliente.get("nombre", "Cliente")
            apellido = contexto.datos_cliente.get("apellido", "")
            if apellido:
                nombre_completo = f"{nombre_completo} {apellido}"

            # Crear cliente
            cliente = Cliente(
                nombre=nombre_completo,
                telefono=contexto.datos_cliente.get("telefono", ""),
                direccion=contexto.datos_cliente.get("direccion", ""),
                zona=contexto.datos_cliente.get("zona", ""),
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
                traslado="Incluido",
            )

            # Crear cotización
            cotizacion = self.sistema_cotizaciones.crear_cotizacion(
                cliente=cliente,
                especificaciones=especificaciones,
                asignado_a="IA",
                observaciones="Cotización generada por IA conversacional",
            )

            return cotizacion

        except Exception as e:
            print(f"Error creando cotización: {e}")
            return None

    def _formatear_cotizacion(self, cotizacion) -> str:
        """Formatea una cotización para mostrar al cliente"""
        area = cotizacion.especificaciones.largo_metros * cotizacion.especificaciones.ancho_metros

        return (
            f"🎉 **¡COTIZACIÓN LISTA!**\n\n"
            f"📋 **ID:** {cotizacion.id}\n"
            f"🏠 **Producto:** {cotizacion.especificaciones.producto.upper()}\n"
            f"📏 **Dimensiones:** {cotizacion.especificaciones.largo_metros}m x {cotizacion.especificaciones.ancho_metros}m\n"
            f"📐 **Área total:** {area} m²\n"
            f"📐 **Espesor:** {cotizacion.especificaciones.espesor}\n"
            f"🎨 **Color:** {cotizacion.especificaciones.color}\n\n"
            f"💰 **PRECIO POR M²:** ${cotizacion.precio_metro_cuadrado}\n"
            f"💰 **PRECIO TOTAL:** ${cotizacion.precio_total}\n\n"
            f"✅ **Incluye:** Material, terminaciones, anclajes y traslado\n\n"
            f"¿Te parece bien esta cotización? ¿Necesitas algún ajuste?"
        )

    def _crear_respuesta(
        self, mensaje: str, tipo: str, confianza: float, fuentes: list[str]
    ) -> RespuestaIA:
        """Crea una respuesta estructurada"""
        return RespuestaIA(
            mensaje=mensaje,
            tipo_respuesta=tipo,
            acciones_sugeridas=[],
            confianza=confianza,
            fuentes_conocimiento=fuentes,
            personalizacion={},
            timestamp=datetime.datetime.now(),
        )

    def _registrar_interaccion(
        self,
        mensaje_cliente: str,
        respuesta: RespuestaIA,
        contexto: ContextoConversacion,
    ):
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
            satisfaccion_cliente=None,
        )

        self.base_conocimiento.registrar_interaccion(interaccion)

    def _actualizar_conocimiento_conversacion(
        self, contexto: ContextoConversacion, respuesta: RespuestaIA
    ):
        """Actualiza el conocimiento basado en la conversación"""
        # Actualizar patrones de respuesta si la respuesta fue efectiva
        if respuesta.confianza > 0.8:
            tipo_respuesta = respuesta.tipo_respuesta
            if tipo_respuesta not in self.patrones_respuesta:
                self.patrones_respuesta[tipo_respuesta] = []

            if respuesta.mensaje not in self.patrones_respuesta[tipo_respuesta]:
                self.patrones_respuesta[tipo_respuesta].append(respuesta.mensaje)

    def procesar_mensaje_usuario(

        self, mensaje: str, telefono_cliente: str, sesion_id: str = None
    ) -> dict[str, Any]:

        """
        Procesa mensaje del usuario usando IA para respuestas naturales y contextuales.
        Siempre usa OpenAI cuando está disponible para generar respuestas fluidas e inteligentes.
        Retorna diccionario compatible con API
        
        Args:
            mensaje: Mensaje del usuario
            telefono_cliente: Teléfono del cliente
            sesion_id: ID de sesión (opcional)
            request_id: Request ID para tracking (opcional)
            client_request_id: Client request ID para tracking (opcional)
        """
        if not sesion_id:
            sesion_id = f"sesion_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"


        # Siempre usar OpenAI si está disponible para respuestas naturales y contextuales

        if self.use_ai and self.openai_client:
            try:
                return self._procesar_con_openai(
                    mensaje, telefono_cliente, sesion_id,
                    request_id=request_id, client_request_id=client_request_id
                )
            except Exception as e:
                print(f"⚠️ Error con OpenAI, usando pattern matching: {e}")
                # Fallback a pattern matching solo si OpenAI falla
                return self._procesar_mensaje_patrones(mensaje, telefono_cliente, sesion_id)
        else:
            # Si no hay IA, usar pattern matching
            return self._procesar_mensaje_patrones(mensaje, telefono_cliente, sesion_id)

    def _procesar_con_openai(

        self, mensaje: str, telefono_cliente: str, sesion_id: str
    ) -> dict[str, Any]:
        """Procesa mensaje usando OpenAI"""

        # Obtener contexto
        contexto = self._obtener_contexto_conversacion(telefono_cliente, sesion_id)

        # Obtener historial reciente
        historial = (
            contexto.mensajes_intercambiados[-5:]
            if len(contexto.mensajes_intercambiados) > 5
            else contexto.mensajes_intercambiados
        )

        # Obtener información de productos y precios para enriquecer el contexto
        info_productos = self._obtener_info_productos_para_prompt()
        estado_cotizacion = self._obtener_estado_cotizacion_para_prompt(contexto)

        # Construir historial de conversación para OpenAI
        messages = [
            {
                "role": "system",
                "content": f"""Eres Superchapita, un asistente experto en ventas de productos de construcción de BMC Uruguay.                                   
Tu trabajo es ayudar a los clientes con:
1. Información sobre productos de aislamiento térmico (Isodec, Poliestireno, Lana de Roca)                                                                      
2. Cotizaciones personalizadas
3. Consultas técnicas
4. Seguimiento de pedidos

{info_productos}

{estado_cotizacion}

INSTRUCCIONES CRÍTICAS PARA CONVERSACIÓN NATURAL:
- Responde de forma FLUIDA, NATURAL y CONVERSACIONAL en español de Uruguay
- NUNCA repitas información que ya compartiste en mensajes anteriores
- Si ya saludaste al cliente, NO vuelvas a presentarte ni a explicar tus capacidades
- Varía tus respuestas - no uses siempre las mismas frases
- Sé CONCISO - responde directamente a lo que el cliente pregunta
- Si el cliente dice "hola" por segunda vez, responde brevemente como en una conversación real
- Si el cliente solicita una cotización, pide los datos necesarios: producto, dimensiones (largo x ancho), espesor, color
- Usa emojis moderadamente (1-2 por mensaje máximo)
- Mantén el tono profesional pero amigable
- Adapta tu respuesta al contexto de la conversación - lee el historial antes de responder

IMPORTANTE: Debes responder SIEMPRE en formato JSON con esta estructura exacta:
{{
  "mensaje": "tu respuesta al cliente aquí",
  "tipo": "cotizacion|informacion|pregunta|seguimiento|general",
  "acciones": ["accion1", "accion2"],
  "confianza": 0.95,
  "necesita_datos": ["dato1", "dato2"]
}}

El campo "tipo" debe ser uno de: cotizacion, informacion, pregunta, seguimiento, general.                                                                       
El campo "confianza" debe ser un número entre 0.0 y 1.0.
El campo "necesita_datos" debe ser una lista de datos que faltan para completar una cotización (ej: ["producto", "dimensiones", "espesor"]).""",
            }
        ]

        # Agregar historial
        for msg in historial:
            if msg["tipo"] == "cliente":
                messages.append({"role": "user", "content": msg["mensaje"]})
            else:
                messages.append({"role": "assistant", "content": msg["mensaje"]})

        # Agregar mensaje actual
        messages.append({"role": "user", "content": mensaje})


        # Llamar a OpenAI con temperatura más alta para respuestas más variadas y naturales
        response = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            temperature=0.85,  # Aumentado de 0.7 a 0.85 para respuestas más variadas y naturales
            response_format={"type": "json_object"},
        )

        # Parsear respuesta
        resultado = json.loads(response.choices[0].message.content)


        # Actualizar contexto
        self._actualizar_contexto(contexto, mensaje)
        contexto.mensajes_intercambiados.append(
            {
                "tipo": "ia",
                "mensaje": resultado.get("mensaje", ""),
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )
        # Limit message history after adding assistant message
        if len(contexto.mensajes_intercambiados) > self.MAX_MESSAGES_PER_CONVERSATION:
            contexto.mensajes_intercambiados = contexto.mensajes_intercambiados[-self.MAX_MESSAGES_PER_CONVERSATION:]

        # Crear respuesta estructurada
        fuente = ["model_integrator"] if self.model_integrator else ["openai"]
        respuesta_ia = self._crear_respuesta(
            resultado.get("mensaje", ""),
            resultado.get("tipo", "general"),
            float(resultado.get("confianza", 0.8)),
            fuente,
        )

        # Registrar interacción
        self._registrar_interaccion(mensaje, respuesta_ia, contexto)

        # Retornar formato API
        return {
            "mensaje": resultado.get("mensaje", ""),
            "tipo": resultado.get("tipo", "general"),
            "acciones": resultado.get("acciones", []),
            "confianza": float(resultado.get("confianza", 0.8)),
            "necesita_datos": resultado.get("necesita_datos", []),
            "sesion_id": sesion_id,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def _obtener_info_productos_para_prompt(self) -> str:
        """Obtiene información de productos para enriquecer el prompt de OpenAI"""
        productos_info = []

        # Obtener precios actuales
        precios = {
            "isodec": self.sistema_cotizaciones.obtener_precio_producto("isodec"),
            "poliestireno": self.sistema_cotizaciones.obtener_precio_producto("poliestireno"),
            "lana_roca": self.sistema_cotizaciones.obtener_precio_producto("lana_roca"),
        }

        productos_info.append("PRODUCTOS DISPONIBLES:")
        productos_info.append("1. ISODEC - Panel aislante con núcleo EPS")
        productos_info.append(f"   Precio base: ${precios.get('isodec', 150):.2f} por m²")
        productos_info.append(
            "   Características: Excelente aislamiento térmico, fácil instalación"
        )

        productos_info.append("2. POLIESTIRENO - Aislante básico")
        productos_info.append(f"   Precio base: ${precios.get('poliestireno', 120):.2f} por m²")
        productos_info.append("   Características: Aislante económico y eficiente")

        productos_info.append("3. LANA DE ROCA - Aislante térmico y acústico")
        productos_info.append(f"   Precio base: ${precios.get('lana_roca', 140):.2f} por m²")
        productos_info.append("   Características: Aislamiento térmico y acústico superior")

        productos_info.append("\nESPESORES DISPONIBLES: 50mm, 75mm, 100mm, 125mm, 150mm")
        productos_info.append("COLORES DISPONIBLES: Blanco, Gris, Beige")

        return "\n".join(productos_info)

    def _obtener_estado_cotizacion_para_prompt(self, contexto: ContextoConversacion) -> str:
        """Obtiene el estado actual de cotización para enriquecer el prompt"""
        if contexto.estado_cotizacion == "inicial":
            return ""

        estado_info = [f"ESTADO ACTUAL DE LA COTIZACIÓN: {contexto.estado_cotizacion.upper()}"]

        if contexto.datos_cliente:
            estado_info.append(
                f"Datos del cliente: {json.dumps(contexto.datos_cliente, ensure_ascii=False)}"
            )

        if contexto.datos_producto:
            estado_info.append(
                f"Datos del producto: {json.dumps(contexto.datos_producto, ensure_ascii=False)}"
            )

        if contexto.estado_cotizacion == "recopilando_datos":
            datos_faltantes = []
            if not contexto.datos_producto.get("producto"):
                datos_faltantes.append("producto")
            if not contexto.datos_producto.get("largo") or not contexto.datos_producto.get("ancho"):
                datos_faltantes.append("dimensiones")
            if not contexto.datos_producto.get("espesor"):
                datos_faltantes.append("espesor")

            if datos_faltantes:
                estado_info.append(f"DATOS FALTANTES: {', '.join(datos_faltantes)}")

        return "\n".join(estado_info) if len(estado_info) > 1 else ""

    def _procesar_mensaje_patrones(
        self, mensaje: str, telefono_cliente: str, sesion_id: str
    ) -> dict[str, Any]:
        """Procesa mensaje usando pattern matching (fallback)"""
        respuesta = self.procesar_mensaje(mensaje, telefono_cliente, sesion_id)

        # Convertir RespuestaIA a formato API
        return {
            "mensaje": respuesta.mensaje,
            "tipo": respuesta.tipo_respuesta,
            "acciones": respuesta.acciones_sugeridas,
            "confianza": respuesta.confianza,
            "necesita_datos": [],
            "sesion_id": sesion_id,
            "timestamp": respuesta.timestamp.isoformat(),
        }

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
                    "timestamp_ultima_actividad": v.timestamp_ultima_actividad.isoformat(),
                }
                for k, v in self.conversaciones_activas.items()
            },
            "fecha_exportacion": datetime.datetime.now().isoformat(),
        }

        with open(archivo, "w", encoding="utf-8") as f:
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
        "Perfecto, me parece bien el precio",
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
