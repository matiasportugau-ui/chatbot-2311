#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulación de Conversación con Agente de Cotizaciones BMC Uruguay
Demuestra cómo un agente usaría el sistema en una conversación real
"""

import time
from decimal import Decimal
from sistema_cotizaciones import SistemaCotizacionesBMC, Cliente, EspecificacionCotizacion


class AgenteCotizaciones:
    """Simulación de agente de cotizaciones con el sistema"""
    
    def __init__(self):
        self.sistema = SistemaCotizacionesBMC()
        self.cargar_configuracion_inicial()
        self.conversacion_activa = False
        self.cliente_actual = None
        self.especificaciones_actuales = None
    
    def cargar_configuracion_inicial(self):
        """Carga la configuración inicial del sistema"""
        # Configurar precios base
        self.sistema.actualizar_precio_producto("isodec", Decimal('150.00'))
        self.sistema.actualizar_precio_producto("poliestireno", Decimal('120.00'))
        self.sistema.actualizar_precio_producto("lana_roca", Decimal('140.00'))
        
        print("🤖 Agente de Cotizaciones BMC Uruguay iniciado")
        print("📋 Sistema de cotizaciones cargado y listo")
    
    def saludar_cliente(self):
        """Saluda al cliente y presenta el servicio"""
        print("\n" + "="*60)
        print("🏢 BMC URUGUAY - AISLAMIENTOS TÉRMICOS")
        print("="*60)
        print("¡Hola! Soy tu agente de cotizaciones.")
        print("Estoy aquí para ayudarte a cotizar productos de aislamiento térmico.")
        print("Tenemos Isodec, Poliestireno, Lana de Roca y más productos disponibles.")
        print("¿En qué puedo ayudarte hoy?")
        print("="*60)
    
    def procesar_mensaje_cliente(self, mensaje: str):
        """Procesa el mensaje del cliente y responde apropiadamente"""
        mensaje_lower = mensaje.lower()
        
        # Detectar intención del cliente
        if any(palabra in mensaje_lower for palabra in ["hola", "buenos", "buenas"]):
            return self.responder_saludo()
        elif any(palabra in mensaje_lower for palabra in ["cotizar", "precio", "costo", "cuanto"]):
            return self.iniciar_cotizacion()
        elif any(palabra in mensaje_lower for palabra in ["isodec", "poliestireno", "lana"]):
            return self.procesar_consulta_producto(mensaje)
        elif any(palabra in mensaje_lower for palabra in ["gracias", "chau", "adios"]):
            return self.despedir_cliente()
        elif self.conversacion_activa:
            return self.procesar_datos_cotizacion(mensaje)
        else:
            return self.responder_general()
    
    def responder_saludo(self):
        """Responde a saludos del cliente"""
        return ("¡Hola! 👋\n"
                "Soy tu agente de cotizaciones de BMC Uruguay.\n"
                "¿Te gustaría cotizar algún producto de aislamiento térmico?\n"
                "Tenemos Isodec, Poliestireno Expandido y Lana de Roca disponibles.")
    
    def iniciar_cotizacion(self):
        """Inicia el proceso de cotización"""
        self.conversacion_activa = True
        return ("¡Perfecto! 🎯\n"
                "Vamos a crear tu cotización paso a paso.\n\n"
                "Primero, necesito algunos datos:\n"
                "1️⃣ ¿Cuál es tu nombre?\n"
                "2️⃣ ¿Qué producto te interesa? (Isodec, Poliestireno, Lana de Roca)\n"
                "3️⃣ ¿Cuáles son las dimensiones? (largo x ancho en metros)\n"
                "4️⃣ ¿Qué espesor necesitas? (50mm, 75mm, 100mm, 125mm, 150mm)\n\n"
                "Puedes darme toda la información de una vez o paso a paso. 😊")
    
    def procesar_consulta_producto(self, mensaje: str):
        """Procesa consultas específicas sobre productos"""
        if "isodec" in mensaje.lower():
            return self.informar_isodec()
        elif "poliestireno" in mensaje.lower():
            return self.informar_poliestireno()
        elif "lana" in mensaje.lower():
            return self.informar_lana_roca()
        else:
            return self.listar_productos()
    
    def informar_isodec(self):
        """Informa sobre Isodec"""
        return ("🏠 **ISODEC** - Panel Aislante Térmico\n\n"
                "✅ **Características:**\n"
                "• Núcleo de EPS (Poliestireno Expandido)\n"
                "• Excelente aislamiento térmico\n"
                "• Fácil instalación\n"
                "• Disponible en varios espesores\n\n"
                "📏 **Espesores disponibles:** 50mm, 75mm, 100mm, 125mm, 150mm\n"
                "🎨 **Colores:** Blanco, Gris, Personalizado\n"
                "💰 **Precio base:** $150/m² (100mm, Blanco)\n\n"
                "¿Te interesa cotizar Isodec?")
    
    def informar_poliestireno(self):
        """Informa sobre Poliestireno"""
        return ("🧱 **POLIESTIRENO EXPANDIDO**\n\n"
                "✅ **Características:**\n"
                "• Aislante térmico de poliestireno\n"
                "• Bajo costo\n"
                "• Fácil manipulación\n"
                "• Ideal para proyectos básicos\n\n"
                "📏 **Espesores disponibles:** 25mm, 50mm, 75mm, 100mm\n"
                "💰 **Precio base:** $120/m² (100mm)\n\n"
                "¿Te interesa cotizar Poliestireno?")
    
    def informar_lana_roca(self):
        """Informa sobre Lana de Roca"""
        return ("🪨 **LANA DE ROCA**\n\n"
                "✅ **Características:**\n"
                "• Aislante térmico y acústico\n"
                "• Resistente al fuego\n"
                "• No tóxico\n"
                "• Excelente durabilidad\n\n"
                "📏 **Espesores disponibles:** 50mm, 75mm, 100mm\n"
                "💰 **Precio base:** $140/m² (100mm)\n\n"
                "¿Te interesa cotizar Lana de Roca?")
    
    def listar_productos(self):
        """Lista todos los productos disponibles"""
        return ("📋 **PRODUCTOS DISPONIBLES:**\n\n"
                "1️⃣ **ISODEC** - Panel aislante con núcleo EPS\n"
                "   Precio: $150/m² | Espesores: 50-150mm\n\n"
                "2️⃣ **POLIESTIRENO** - Aislante básico\n"
                "   Precio: $120/m² | Espesores: 25-100mm\n\n"
                "3️⃣ **LANA DE ROCA** - Aislante térmico y acústico\n"
                "   Precio: $140/m² | Espesores: 50-100mm\n\n"
                "¿Cuál te interesa cotizar?")
    
    def procesar_datos_cotizacion(self, mensaje: str):
        """Procesa los datos de cotización del cliente"""
        # Simular procesamiento de datos del cliente
        if not self.cliente_actual:
            return self.procesar_datos_cliente(mensaje)
        elif not self.especificaciones_actuales:
            return self.procesar_especificaciones(mensaje)
        else:
            return self.finalizar_cotizacion()
    
    def procesar_datos_cliente(self, mensaje: str):
        """Procesa datos del cliente"""
        # Simular extracción de datos del mensaje
        nombre = "Cliente"  # En un sistema real, se extraería del mensaje
        telefono = "099123456"
        direccion = "Montevideo"
        
        self.cliente_actual = Cliente(
            nombre=nombre,
            telefono=telefono,
            direccion=direccion,
            zona="Montevideo"
        )
        
        return ("✅ **Datos del cliente registrados**\n\n"
                f"👤 Nombre: {nombre}\n"
                f"📞 Teléfono: {telefono}\n"
                f"📍 Dirección: {direccion}\n\n"
                "Ahora necesito las especificaciones del producto:\n"
                "• ¿Qué producto? (Isodec, Poliestireno, Lana de Roca)\n"
                "• ¿Qué dimensiones? (ej: 10m x 5m)\n"
                "• ¿Qué espesor? (50mm, 75mm, 100mm, 125mm, 150mm)\n"
                "• ¿Qué color? (Blanco, Gris, Personalizado)")
    
    def procesar_especificaciones(self, mensaje: str):
        """Procesa especificaciones del producto"""
        # Simular extracción de especificaciones
        producto = "isodec"
        espesor = "100mm"
        largo = Decimal('10.0')
        ancho = Decimal('5.0')
        color = "Blanco"
        
        self.especificaciones_actuales = EspecificacionCotizacion(
            producto=producto,
            espesor=espesor,
            relleno="EPS",
            largo_metros=largo,
            ancho_metros=ancho,
            color=color,
            termina_front="Gotero",
            termina_sup="Gotero",
            termina_lat_1="Gotero",
            termina_lat_2="Gotero",
            anclajes="Incluido",
            traslado="Incluido"
        )
        
        return ("✅ **Especificaciones registradas**\n\n"
                f"🏠 Producto: {producto.upper()}\n"
                f"📏 Dimensiones: {largo}m x {ancho}m\n"
                f"📐 Espesor: {espesor}\n"
                f"🎨 Color: {color}\n"
                f"🔧 Terminaciones: Gotero\n"
                f"⚙️ Servicios: Anclajes y traslado incluidos\n\n"
                "Calculando cotización... ⏳")
    
    def finalizar_cotizacion(self):
        """Finaliza la cotización y muestra el resultado"""
        try:
            # Crear cotización
            cotizacion = self.sistema.crear_cotizacion(
                cliente=self.cliente_actual,
                especificaciones=self.especificaciones_actuales,
                asignado_a="MA",
                observaciones="Cotización generada por agente virtual"
            )
            
            # Calcular área
            area = (self.especificaciones_actuales.largo_metros * 
                   self.especificaciones_actuales.ancho_metros)
            
            respuesta = ("🎉 **¡COTIZACIÓN LISTA!**\n\n"
                        f"📋 **ID de Cotización:** {cotizacion.id}\n"
                        f"👤 **Cliente:** {cotizacion.cliente.nombre}\n"
                        f"🏠 **Producto:** {cotizacion.especificaciones.producto.upper()}\n"
                        f"📏 **Dimensiones:** {cotizacion.especificaciones.largo_metros}m x {cotizacion.especificaciones.ancho_metros}m\n"
                        f"📐 **Área total:** {area} m²\n"
                        f"📐 **Espesor:** {cotizacion.especificaciones.espesor}\n"
                        f"🎨 **Color:** {cotizacion.especificaciones.color}\n\n"
                        f"💰 **PRECIO POR M²:** ${cotizacion.precio_metro_cuadrado}\n"
                        f"💰 **PRECIO TOTAL:** ${cotizacion.precio_total}\n\n"
                        "✅ **Incluye:**\n"
                        "• Material del producto\n"
                        "• Terminaciones (Gotero)\n"
                        "• Anclajes\n"
                        "• Traslado\n\n"
                        "¿Te parece bien esta cotización? ¿Necesitas algún ajuste?")
            
            # Resetear para nueva cotización
            self.conversacion_activa = False
            self.cliente_actual = None
            self.especificaciones_actuales = None
            
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
    
    def despedir_cliente(self):
        """Se despide del cliente"""
        return ("👋 ¡Gracias por contactar BMC Uruguay!\n\n"
                "Espero haber sido de ayuda con tu cotización.\n"
                "Si necesitas algo más, no dudes en contactarnos.\n\n"
                "🏢 **BMC Uruguay - Aislamientos Térmicos**\n"
                "📞 Tel: +598 XX XXX XXX\n"
                "🌐 Web: bmcuruguay.com.uy\n\n"
                "¡Que tengas un excelente día! 😊")


def simular_conversacion():
    """Simula una conversación completa con el agente"""
    agente = AgenteCotizaciones()
    
    print("🎭 SIMULACIÓN DE CONVERSACIÓN CON AGENTE DE COTIZACIONES")
    print("="*70)
    
    # Saludo inicial
    agente.saludar_cliente()
    
    # Simular conversación
    mensajes_cliente = [
        "Hola, necesito cotizar algo",
        "Quiero cotizar Isodec para mi casa",
        "Gabriel, 10 metros por 5 metros, 100mm, blanco",
        "Perfecto, me parece bien el precio",
        "Gracias, hasta luego"
    ]
    
    for i, mensaje in enumerate(mensajes_cliente, 1):
        print(f"\n👤 **CLIENTE:** {mensaje}")
        time.sleep(1)  # Simular tiempo de procesamiento
        
        respuesta = agente.procesar_mensaje_cliente(mensaje)
        print(f"\n🤖 **AGENTE:** {respuesta}")
        
        if i < len(mensajes_cliente):
            print("\n" + "-"*50)
            time.sleep(2)  # Pausa entre mensajes
    
    print("\n" + "="*70)
    print("🎬 SIMULACIÓN COMPLETADA")


def demo_interactivo():
    """Demo interactivo donde el usuario puede chatear con el agente"""
    agente = AgenteCotizaciones()
    agente.saludar_cliente()
    
    print("\n💬 **MODO INTERACTIVO**")
    print("Escribe 'salir' para terminar la conversación")
    print("-"*50)
    
    while True:
        try:
            mensaje = input("\n👤 Tú: ").strip()
            
            if mensaje.lower() in ['salir', 'exit', 'chau', 'adios']:
                print(f"\n🤖 Agente: {agente.despedir_cliente()}")
                break
            
            if mensaje:
                respuesta = agente.procesar_mensaje_cliente(mensaje)
                print(f"\n🤖 Agente: {respuesta}")
            
        except KeyboardInterrupt:
            print(f"\n\n🤖 Agente: {agente.despedir_cliente()}")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """Función principal"""
    print("SISTEMA DE SIMULACIÓN DE AGENTE DE COTIZACIONES")
    print("="*60)
    print("1. Simulación automática")
    print("2. Demo interactivo")
    print("3. Salir")
    
    while True:
        try:
            opcion = input("\nSelecciona una opción (1-3): ").strip()
            
            if opcion == "1":
                simular_conversacion()
                break
            elif opcion == "2":
                demo_interactivo()
                break
            elif opcion == "3":
                print("¡Hasta luego!")
                break
            else:
                print("⚠ Opción inválida. Selecciona 1, 2 o 3.")
                
        except KeyboardInterrupt:
            print("\n\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

