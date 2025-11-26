#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chat Interactivo con Agente de Cotizaciones BMC Uruguay
Permite conversar en tiempo real con el agente virtual
"""

import os
import re
from decimal import Decimal

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    # Intentar cargar desde .env.local primero, luego .env
    if os.path.exists('.env.local'):
        load_dotenv('.env.local')
    elif os.path.exists('.env'):
        load_dotenv('.env')
    else:
        load_dotenv()  # Busca .env en la raíz
except ImportError:
    pass  # python-dotenv no es crítico, las variables pueden estar en el sistema

from sistema_cotizaciones import SistemaCotizacionesBMC, Cliente, EspecificacionCotizacion
from utils_cotizaciones import obtener_datos_faltantes, formatear_mensaje_faltantes, construir_contexto_validacion
from integracion_google_sheets import IntegracionGoogleSheets


class AgenteInteractivo:
    """Agente de cotizaciones interactivo"""
    
    def __init__(self):
        self.sistema = SistemaCotizacionesBMC()
        self.cargar_configuracion()
        self.conversacion_activa = False
        self.cliente_actual = None
        self.especificaciones_actuales = None
        self.paso_actual = 0
        self.datos_cliente = {}
        self.datos_especificaciones = {}
        
        # Inicializar integración con Google Sheets (opcional, puede funcionar sin IA)
        try:
            self.google_sheets = IntegracionGoogleSheets(ia_conversacional=None)
            # Intentar conectar
            self.google_sheets.conectar_google_sheets()
        except Exception as e:
            print(f"⚠️  No se pudo inicializar Google Sheets: {e}")
            self.google_sheets = None
    
    def cargar_configuracion(self):
        """Carga la configuración inicial"""
        self.sistema.actualizar_precio_producto("isodec", Decimal('150.00'))
        self.sistema.actualizar_precio_producto("poliestireno", Decimal('120.00'))
        self.sistema.actualizar_precio_producto("lana_roca", Decimal('140.00'))
        
        print("[AGENTE] Agente de Cotizaciones BMC Uruguay iniciado")
        print("[SISTEMA] Sistema cargado y listo para atenderte")
    
    def procesar_mensaje(self, mensaje: str):
        """Procesa el mensaje del usuario y responde"""
        mensaje_lower = mensaje.lower().strip()
        
        # Detectar saludos
        if any(palabra in mensaje_lower for palabra in ["hola", "buenos", "buenas", "hi", "hello"]):
            return self.saludar()
        
        # Detectar intención de cotizar
        elif any(palabra in mensaje_lower for palabra in ["cotizar", "precio", "costo", "cuanto", "cotizacion"]):
            return self.iniciar_cotizacion()
        
        # Detectar consulta sobre productos
        elif any(palabra in mensaje_lower for palabra in ["isodec", "poliestireno", "lana", "producto", "productos"]):
            return self.responder_consulta_producto(mensaje_lower)
        
        # Detectar despedida
        elif any(palabra in mensaje_lower for palabra in ["gracias", "chau", "adios", "bye", "hasta luego"]):
            return self.despedir()
        
        # Si estamos en proceso de cotización
        elif self.conversacion_activa:
            return self.procesar_datos_cotizacion(mensaje)
        
        # Respuesta general
        else:
            return self.responder_general()
    
    def saludar(self):
        """Saluda al usuario"""
        return ("¡Hola! 👋\n\n"
                "Soy tu agente de cotizaciones de **BMC Uruguay**.\n"
                "Estoy aquí para ayudarte con:\n"
                "• 🏠 Cotizar productos de aislamiento térmico\n"
                "• ℹ️ Información sobre nuestros productos\n"
                "• 💰 Consultas de precios\n\n"
                "¿En qué puedo ayudarte hoy?")
    
    def iniciar_cotizacion(self):
        """Inicia el proceso de cotización"""
        self.conversacion_activa = True
        self.paso_actual = 1
        self.datos_cliente = {}
        self.datos_especificaciones = {}
        
        return ("¡Perfecto! 🎯 Vamos a crear tu cotización.\n\n"
                "Te voy a hacer algunas preguntas para darte el precio exacto:\n\n"
                "**PASO 1 - DATOS PERSONALES**\n"
                "¿Cuál es tu nombre y apellido?")
    
    def responder_consulta_producto(self, mensaje):
        """Responde consultas sobre productos"""
        if "isodec" in mensaje:
            return self.informar_isodec()
        elif "poliestireno" in mensaje:
            return self.informar_poliestireno()
        elif "lana" in mensaje:
            return self.informar_lana_roca()
        else:
            return self.listar_productos()
    
    def informar_isodec(self):
        """Informa sobre Isodec"""
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
    
    def informar_poliestireno(self):
        """Informa sobre Poliestireno"""
        return ("🧱 **POLIESTIRENO EXPANDIDO**\n\n"
                "**Características principales:**\n"
                "✅ Aislante térmico básico\n"
                "✅ Bajo costo\n"
                "✅ Fácil manipulación\n"
                "✅ Ideal para proyectos básicos\n\n"
                "**Opciones disponibles:**\n"
                "📏 Espesores: 25mm, 50mm, 75mm, 100mm\n"
                "🎨 Colores: Blanco, Gris\n\n"
                "💰 **Precio base:** $120/m² (100mm)\n\n"
                "¿Te interesa cotizar Poliestireno?")
    
    def informar_lana_roca(self):
        """Informa sobre Lana de Roca"""
        return ("🪨 **LANA DE ROCA**\n\n"
                "**Características principales:**\n"
                "✅ Aislante térmico y acústico\n"
                "✅ Resistente al fuego\n"
                "✅ No tóxico\n"
                "✅ Excelente durabilidad\n\n"
                "**Opciones disponibles:**\n"
                "📏 Espesores: 50mm, 75mm, 100mm\n"
                "🎨 Colores: Blanco, Gris\n\n"
                "💰 **Precio base:** $140/m² (100mm)\n\n"
                "¿Te interesa cotizar Lana de Roca?")
    
    def listar_productos(self):
        """Lista todos los productos"""
        return ("📋 **NUESTROS PRODUCTOS DISPONIBLES:**\n\n"
                "1️⃣ **ISODEC** - Panel aislante con núcleo EPS\n"
                "   💰 Desde $150/m² | 📏 50-150mm\n\n"
                "2️⃣ **POLIESTIRENO** - Aislante básico\n"
                "   💰 Desde $120/m² | 📏 25-100mm\n\n"
                "3️⃣ **LANA DE ROCA** - Aislante térmico y acústico\n"
                "   💰 Desde $140/m² | 📏 50-100mm\n\n"
                "¿Cuál te interesa conocer más o cotizar?")
    
    def procesar_datos_cotizacion(self, mensaje):
        """Procesa los datos de cotización paso a paso"""
        if self.paso_actual == 1:  # Nombre y Apellido
            return self.procesar_nombre_apellido(mensaje)
        elif self.paso_actual == 2:  # Teléfono
            return self.procesar_telefono(mensaje)
        elif self.paso_actual == 3:  # Dirección
            return self.procesar_direccion(mensaje)
        elif self.paso_actual == 4:  # Producto
            return self.procesar_producto(mensaje)
        elif self.paso_actual == 5:  # Dimensiones
            return self.procesar_dimensiones(mensaje)
        elif self.paso_actual == 6:  # Espesor
            return self.procesar_espesor(mensaje)
        elif self.paso_actual == 7:  # Color
            return self.procesar_color(mensaje)
        elif self.paso_actual == 8:  # Terminaciones
            return self.procesar_terminaciones(mensaje)
        else:
            return self.finalizar_cotizacion()
    
    def procesar_nombre_apellido(self, mensaje):
        """Procesa el nombre y apellido del cliente"""
        # Intentar extraer nombre y apellido
        mensaje_limpio = mensaje.strip()
        partes = mensaje_limpio.split()
        
        if len(partes) >= 2:
            self.datos_cliente['nombre'] = partes[0]
            self.datos_cliente['apellido'] = " ".join(partes[1:])
            self.paso_actual = 2
            return (f"¡Hola {self.datos_cliente['nombre']} {self.datos_cliente['apellido']}! 👋\n\n"
                    "**PASO 2 - CONTACTO**\n"
                    "¿Cuál es tu número de teléfono?")
        else:
            # Solo tiene un nombre, pedir apellido
            self.datos_cliente['nombre'] = mensaje_limpio
            return "¿Y cuál es tu apellido?"
    
    def procesar_telefono(self, mensaje):
        """Procesa el teléfono del cliente"""
        telefono = re.sub(r'[^\d]', '', mensaje)  # Solo números
        if len(telefono) >= 8:
            self.datos_cliente['telefono'] = telefono
            self.paso_actual = 3
            return ("✅ Teléfono registrado\n\n"
                    "**PASO 3 - UBICACIÓN**\n"
                    "¿En qué ciudad o zona estás?")
        else:
            return "❌ Por favor, ingresa un número de teléfono válido (mínimo 8 dígitos)"
    
    def procesar_direccion(self, mensaje):
        """Procesa la dirección del cliente"""
        self.datos_cliente['direccion'] = mensaje.strip()
        self.paso_actual = 4
        return ("✅ Ubicación registrada\n\n"
                "**PASO 4 - PRODUCTO**\n"
                "¿Qué producto te interesa?\n"
                "• Isodec\n"
                "• Poliestireno\n"
                "• Lana de Roca")
    
    def procesar_producto(self, mensaje):
        """Procesa el producto seleccionado"""
        mensaje_lower = mensaje.lower()
        if "isodec" in mensaje_lower:
            producto = "isodec"
        elif "poliestireno" in mensaje_lower:
            producto = "poliestireno"
        elif "lana" in mensaje_lower:
            producto = "lana_roca"
        else:
            return "❌ Por favor, selecciona uno de los productos: Isodec, Poliestireno o Lana de Roca"
        
        self.datos_especificaciones['producto'] = producto
        self.paso_actual = 5
        return (f"✅ Producto seleccionado: {producto.upper()}\n\n"
                "**PASO 5 - DIMENSIONES**\n"
                "¿Cuáles son las dimensiones que necesitas?\n"
                "Ejemplo: 10m x 5m o 10 metros por 5 metros")
    
    def procesar_dimensiones(self, mensaje):
        """Procesa las dimensiones"""
        # Extraer números del mensaje
        numeros = re.findall(r'\d+(?:\.\d+)?', mensaje)
        if len(numeros) >= 2:
            try:
                largo = Decimal(numeros[0])
                ancho = Decimal(numeros[1])
                if largo > 0 and ancho > 0:
                    self.datos_especificaciones['largo'] = largo
                    self.datos_especificaciones['ancho'] = ancho
                    self.paso_actual = 6
                    return (f"✅ Dimensiones registradas: {largo}m x {ancho}m\n\n"
                            "**PASO 6 - ESPESOR**\n"
                            "¿Qué espesor necesitas?\n"
                            "• 50mm\n"
                            "• 75mm\n"
                            "• 100mm\n"
                            "• 125mm\n"
                            "• 150mm")
                else:
                    return "❌ Las dimensiones deben ser números positivos"
            except (ValueError, TypeError):
                return "❌ Por favor, ingresa las dimensiones en formato: largo x ancho (ej: 10 x 5)"
        else:
            return "❌ Por favor, ingresa las dimensiones en formato: largo x ancho (ej: 10 x 5)"
    
    def procesar_espesor(self, mensaje):
        """Procesa el espesor"""
        espesor = re.findall(r'\d+', mensaje)
        if espesor and espesor[0] in ['50', '75', '100', '125', '150']:
            self.datos_especificaciones['espesor'] = espesor[0] + 'mm'
            self.paso_actual = 7
            return (f"✅ Espesor registrado: {self.datos_especificaciones['espesor']}\n\n"
                    "**PASO 7 - COLOR**\n"
                    "¿Qué color prefieres?\n"
                    "• Blanco\n"
                    "• Gris\n"
                    "• Personalizado")
        else:
            return "❌ Por favor, selecciona un espesor válido: 50mm, 75mm, 100mm, 125mm o 150mm"
    
    def procesar_color(self, mensaje):
        """Procesa el color"""
        mensaje_lower = mensaje.lower()
        if "blanco" in mensaje_lower:
            color = "Blanco"
        elif "gris" in mensaje_lower:
            color = "Gris"
        elif "personalizado" in mensaje_lower:
            color = "Personalizado"
        else:
            return "❌ Por favor, selecciona un color: Blanco, Gris o Personalizado"
        
        self.datos_especificaciones['color'] = color
        self.paso_actual = 8
        return (f"✅ Color registrado: {color}\n\n"
                "**PASO 8 - TERMINACIONES**\n"
                "¿Qué tipo de terminaciones necesitas?\n"
                "• Gotero (básico)\n"
                "• Hormigón (premium)\n"
                "• Aluminio (premium)")
    
    def procesar_terminaciones(self, mensaje):
        """Procesa las terminaciones"""
        mensaje_lower = mensaje.lower()
        if "gotero" in mensaje_lower:
            terminacion = "Gotero"
        elif "hormigon" in mensaje_lower or "hormigón" in mensaje_lower:
            terminacion = "Hormigón"
        elif "aluminio" in mensaje_lower:
            terminacion = "Aluminio"
        else:
            return "❌ Por favor, selecciona una terminación: Gotero, Hormigón o Aluminio"
        
        self.datos_especificaciones['terminacion'] = terminacion
        self.paso_actual = 9
        return self.finalizar_cotizacion()
    
    def finalizar_cotizacion(self):
        """Finaliza la cotización y muestra el resultado"""
        try:
            # Construir contexto de validación con los datos capturados
            contexto_validacion = construir_contexto_validacion(
                self.datos_cliente,
                self.datos_especificaciones
            )
            
            # Validar que todos los datos obligatorios estén presentes
            datos_faltantes = obtener_datos_faltantes(contexto_validacion)
            
            if datos_faltantes:
                # Hay datos faltantes, solicitar al usuario
                mensaje = formatear_mensaje_faltantes(datos_faltantes)
                return f"❌ {mensaje}"
            
            # Todos los datos están completos, crear cotización
            # Combinar nombre y apellido para el campo nombre del cliente
            nombre_completo = self.datos_cliente.get('nombre', 'Cliente')
            apellido = self.datos_cliente.get('apellido', '')
            if apellido:
                nombre_completo = f"{nombre_completo} {apellido}"
            
            # Crear cliente
            self.cliente_actual = Cliente(
                nombre=nombre_completo,
                telefono=self.datos_cliente['telefono'],
                direccion=self.datos_cliente['direccion'],
                zona=self.datos_cliente['direccion']
            )
            
            # Crear especificaciones
            self.especificaciones_actuales = EspecificacionCotizacion(
                producto=self.datos_especificaciones['producto'],
                espesor=self.datos_especificaciones['espesor'],
                relleno="EPS",
                largo_metros=self.datos_especificaciones['largo'],
                ancho_metros=self.datos_especificaciones['ancho'],
                color=self.datos_especificaciones['color'],
                termina_front=self.datos_especificaciones['terminacion'],
                termina_sup=self.datos_especificaciones['terminacion'],
                termina_lat_1=self.datos_especificaciones['terminacion'],
                termina_lat_2=self.datos_especificaciones['terminacion'],
                anclajes="Incluido",
                traslado="Incluido"
            )
            
            # Crear cotización
            cotizacion = self.sistema.crear_cotizacion(
                cliente=self.cliente_actual,
                especificaciones=self.especificaciones_actuales,
                asignado_a="MA",
                observaciones="Cotización generada por chat interactivo"
            )
            
            # Calcular área
            area = self.datos_especificaciones['largo'] * self.datos_especificaciones['ancho']
            
            # Intentar guardar en Google Sheets
            mensaje_sheets = ""
            if self.google_sheets:
                try:
                    # Construir consulta para Google Sheets (dentro del try para manejar errores)
                    consulta_sheets = self.google_sheets.construir_consulta_cotizacion(
                        self.datos_cliente,
                        self.datos_especificaciones
                    )
                    
                    datos_sheets = {
                        'cliente': nombre_completo,
                        'telefono': self.datos_cliente['telefono'],
                        'direccion': self.datos_cliente['direccion'],
                        'consulta': consulta_sheets,
                        'origen': 'CH',  # CH = Chat Interactivo
                        'estado': 'Pendiente'
                    }
                    resultado_sheets = self.google_sheets.guardar_cotizacion_en_sheets(datos_sheets)
                    if resultado_sheets.get('exito'):
                        codigo_arg = resultado_sheets.get('codigo_arg', '')
                        mensaje_sheets = f"\n📊 **Guardado en Google Sheets:** Código {codigo_arg}"
                    else:
                        mensaje_sheets = "\n⚠️  No se pudo guardar en Google Sheets (modo simulado)"
                except Exception as e:
                    mensaje_sheets = f"\n⚠️  Error guardando en Google Sheets: {str(e)}"
            
            respuesta = ("🎉 **¡COTIZACIÓN LISTA!**\n\n"
                        f"📋 **ID:** {cotizacion.id}\n"
                        f"👤 **Cliente:** {cotizacion.cliente.nombre}\n"
                        f"🏠 **Producto:** {cotizacion.especificaciones.producto.upper()}\n"
                        f"📏 **Dimensiones:** {cotizacion.especificaciones.largo_metros}m x {cotizacion.especificaciones.ancho_metros}m\n"
                        f"📐 **Área total:** {area} m²\n"
                        f"📐 **Espesor:** {cotizacion.especificaciones.espesor}\n"
                        f"🎨 **Color:** {cotizacion.especificaciones.color}\n"
                        f"🔧 **Terminaciones:** {cotizacion.especificaciones.termina_front}\n\n"
                        f"💰 **PRECIO POR M²:** ${cotizacion.precio_metro_cuadrado}\n"
                        f"💰 **PRECIO TOTAL:** ${cotizacion.precio_total}\n\n"
                        "✅ **Incluye:**\n"
                        "• Material del producto\n"
                        "• Terminaciones\n"
                        "• Anclajes\n"
                        "• Traslado\n"
                        f"{mensaje_sheets}\n\n"
                        "¿Te parece bien esta cotización? ¿Necesitas algún ajuste?")
            
            # Resetear para nueva cotización
            self.conversacion_activa = False
            self.paso_actual = 0
            self.cliente_actual = None
            self.especificaciones_actuales = None
            self.datos_cliente = {}
            self.datos_especificaciones = {}
            
            return respuesta
            
        except Exception as e:
            return f"❌ **Error generando cotización:** {str(e)}\n\n¿Podrías intentar de nuevo?"
    
    def responder_general(self):
        """Responde a mensajes generales"""
        return ("🤔 No estoy seguro de cómo ayudarte con eso.\n\n"
                "Puedo ayudarte con:\n"
                "• 📋 Cotizar productos de aislamiento\n"
                "• ℹ️ Información sobre productos\n"
                "• 💰 Consultas de precios\n\n"
                "¿Qué te gustaría hacer?")
    
    def despedir(self):
        """Se despide del usuario"""
        return ("👋 ¡Gracias por contactar BMC Uruguay!\n\n"
                "Espero haber sido de ayuda con tu cotización.\n"
                "Si necesitas algo más, no dudes en contactarnos.\n\n"
                "🏢 **BMC Uruguay - Aislamientos Térmicos**\n"
                "📞 Tel: +598 XX XXX XXX\n"
                "🌐 Web: bmcuruguay.com.uy\n\n"
                "¡Que tengas un excelente día! 😊")


def main():
    """Función principal del chat interactivo"""
    print("="*70)
    print("🤖 CHAT INTERACTIVO - AGENTE DE COTIZACIONES BMC URUGUAY")
    print("="*70)
    print("Escribe 'salir' para terminar la conversación")
    print("="*70)
    
    agente = AgenteInteractivo()
    
    # Saludo inicial
    print(f"\n🤖 Agente: {agente.saludar()}")
    
    while True:
        try:
            # Obtener mensaje del usuario
            mensaje = input("\n👤 Tú: ").strip()
            
            # Verificar si quiere salir
            if mensaje.lower() in ['salir', 'exit', 'chau', 'adios', 'bye']:
                print(f"\n🤖 Agente: {agente.despedir()}")
                break
            
            # Procesar mensaje si no está vacío
            if mensaje:
                respuesta = agente.procesar_mensaje(mensaje)
                print(f"\n🤖 Agente: {respuesta}")
            
        except KeyboardInterrupt:
            print(f"\n\n🤖 Agente: {agente.despedir()}")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
