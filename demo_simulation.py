#!/usr/bin/env python3
"""
Simulación de Chatbot de Cotizaciones (Modo Demo)
Este script simula una conversación completa entre un usuario y el agente
utilizando la lógica interna del sistema, sin depender de APIs externas.
"""
import sys
import time
from sistema_cotizaciones import SistemaCotizacionesBMC, Cliente, EspecificacionCotizacion
from utils_cotizaciones import obtener_datos_faltantes, formatear_mensaje_faltantes

class DemoChatbot:
    def __init__(self):
        self.sistema = SistemaCotizacionesBMC()
        # Configurar precios
        self.sistema.actualizar_precio_producto("isodec", 150)
        self.sistema.actualizar_precio_producto("poliestireno", 120)
        self.sistema.actualizar_precio_producto("lana_roca", 140)
        
        self.datos_cliente = {}
        self.datos_producto = {}
        
    def print_agent(self, msg):
        print(f"\n🤖 AGENTE: {msg}")
        time.sleep(1)

    def print_user(self, msg):
        print(f"\n👤 USUARIO: {msg}")
        time.sleep(1)

    def run_simulation(self):
        print("="*60)
        print(" INICIANDO SIMULACIÓN DE CHAT DE COTIZACIONES")
        print("="*60)

        # 1. Saludo
        self.print_user("Hola, quisiera cotizar")
        self.print_agent("¡Hola! 👋 Soy tu asistente de BMC Uruguay. Para cotizar, necesito algunos datos. Primero, ¿cuál es tu nombre y apellido?")
        
        # 2. Nombre
        self.print_user("Juan Pérez")
        self.datos_cliente['nombre'] = "Juan"
        self.datos_cliente['apellido'] = "Pérez"
        self.print_agent(f"Gracias Juan. ¿Me podrías dar un número de teléfono para contactarte?")

        # 3. Telefono
        self.print_user("099123456")
        self.datos_cliente['telefono'] = "099123456"
        self.print_agent("¡Perfecto! ¿Qué producto te interesa? Trabajamos con Isodec, Poliestireno y Lana de Roca.")

        # 4. Producto
        self.print_user("Me interesa el Isodec")
        self.datos_producto['producto'] = 'isodec'
        self.print_agent("Excelente elección. El Isodec es un panel aislante con núcleo EPS. ¿Qué espesor necesitas? (50mm, 75mm, 100mm, 125mm, 150mm)")

        # 5. Espesor
        self.print_user("100mm")
        self.datos_producto['espesor'] = '100mm'
        self.print_agent("Bien, 100mm. Ahora necesito las dimensiones. ¿Cuál es el largo y ancho en metros?")

        # 6. Dimensiones
        self.print_user("Serían 10 metros de largo y 5 de ancho")
        self.datos_producto['largo'] = 10
        self.datos_producto['ancho'] = 5
        self.print_agent("Entendido, 50 m². ¿Qué color prefieres? (Blanco, Gris, Personalizado)")

        # 7. Color
        self.print_user("Blanco")
        self.datos_producto['color'] = 'Blanco'
        self.print_agent("¿Qué terminación necesitas? (Gotero, Hormigón, Aluminio)")
        
        # 8. Terminaciones
        self.print_user("Gotero")
        self.datos_producto['terminacion'] = 'Gotero'
        
        # Generar cotización
        self.print_agent("¡Perfecto! Generando tu cotización...")
        time.sleep(1)
        
        # Lógica real
        try:
            cliente = Cliente(
                nombre=f"{self.datos_cliente['nombre']} {self.datos_cliente['apellido']}",
                telefono=self.datos_cliente['telefono'],
                direccion="Montevideo (Simulado)"
            )
            
            specs = EspecificacionCotizacion(
                producto=self.datos_producto['producto'],
                espesor=self.datos_producto['espesor'],
                relleno="EPS",
                largo_metros=self.datos_producto['largo'],
                ancho_metros=self.datos_producto['ancho'],
                color=self.datos_producto['color'],
                termina_front=self.datos_producto['terminacion'],
                termina_sup="Gotero",
                termina_lat_1="Gotero",
                termina_lat_2="Gotero",
                anclajes="Incluido",
                traslado="Incluido"
            )
            
            cotizacion = self.sistema.crear_cotizacion(cliente, specs, "Simulación")
            
            reporte = self.sistema.generar_reporte_cotizacion(cotizacion)
            print("\n" + "-"*40)
            print(reporte)
            print("-" * 40)
            
            self.print_agent("¿Te sirve esta cotización?")
            self.print_user("Sí, está perfecta. Gracias.")
            self.print_agent("¡Excelente! Un asesor se pondrá en contacto contigo pronto. ¡Hasta luego!")

        except Exception as e:
            print(f"Error en simulación: {e}")

if __name__ == "__main__":
    sim = DemoChatbot()
    sim.run_simulation()
