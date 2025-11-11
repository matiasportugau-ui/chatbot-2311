#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Automático del Agente de Cotizaciones BMC Uruguay
Ejecuta una simulación completa sin necesidad de input del usuario
"""

import time
from decimal import Decimal
from sistema_cotizaciones import SistemaCotizacionesBMC, Cliente, EspecificacionCotizacion


def demo_conversacion_completa():
    """Demo de una conversación completa con el agente"""
    print("🎭 SIMULACIÓN DE CONVERSACIÓN CON AGENTE DE COTIZACIONES BMC URUGUAY")
    print("="*80)
    
    # Inicializar sistema
    sistema = SistemaCotizacionesBMC()
    sistema.actualizar_precio_producto("isodec", Decimal('150.00'))
    sistema.actualizar_precio_producto("poliestireno", Decimal('120.00'))
    sistema.actualizar_precio_producto("lana_roca", Decimal('140.00'))
    
    print("\n🤖 **AGENTE:** ¡Hola! Soy tu agente de cotizaciones de BMC Uruguay.")
    print("🏢 Estoy aquí para ayudarte a cotizar productos de aislamiento térmico.")
    print("📋 Tenemos Isodec, Poliestireno, Lana de Roca y más productos disponibles.")
    print("¿En qué puedo ayudarte hoy?")
    
    time.sleep(2)
    
    print("\n👤 **CLIENTE:** Hola, necesito cotizar algo para mi casa")
    
    time.sleep(1)
    
    print("\n🤖 **AGENTE:** ¡Perfecto! 🎯")
    print("Vamos a crear tu cotización paso a paso.")
    print("Primero, necesito algunos datos:")
    print("1️⃣ ¿Cuál es tu nombre?")
    print("2️⃣ ¿Qué producto te interesa? (Isodec, Poliestireno, Lana de Roca)")
    print("3️⃣ ¿Cuáles son las dimensiones? (largo x ancho en metros)")
    print("4️⃣ ¿Qué espesor necesitas? (50mm, 75mm, 100mm, 125mm, 150mm)")
    print("Puedes darme toda la información de una vez o paso a paso. 😊")
    
    time.sleep(2)
    
    print("\n👤 **CLIENTE:** Quiero cotizar Isodec para mi casa")
    
    time.sleep(1)
    
    print("\n🤖 **AGENTE:** 🏠 **ISODEC** - Panel Aislante Térmico")
    print("✅ **Características:**")
    print("• Núcleo de EPS (Poliestireno Expandido)")
    print("• Excelente aislamiento térmico")
    print("• Fácil instalación")
    print("• Disponible en varios espesores")
    print("📏 **Espesores disponibles:** 50mm, 75mm, 100mm, 125mm, 150mm")
    print("🎨 **Colores:** Blanco, Gris, Personalizado")
    print("💰 **Precio base:** $150/m² (100mm, Blanco)")
    print("¿Te interesa cotizar Isodec?")
    
    time.sleep(2)
    
    print("\n👤 **CLIENTE:** Sí, mi nombre es Gabriel, necesito 10 metros por 5 metros, 100mm, blanco")
    
    time.sleep(1)
    
    print("\n🤖 **AGENTE:** ✅ **Datos del cliente registrados**")
    print("👤 Nombre: Gabriel")
    print("📞 Teléfono: 099123456")
    print("📍 Dirección: Montevideo")
    print("Ahora necesito las especificaciones del producto:")
    print("• ¿Qué producto? (Isodec, Poliestireno, Lana de Roca)")
    print("• ¿Qué dimensiones? (ej: 10m x 5m)")
    print("• ¿Qué espesor? (50mm, 75mm, 100mm, 125mm, 150mm)")
    print("• ¿Qué color? (Blanco, Gris, Personalizado)")
    
    time.sleep(2)
    
    print("\n👤 **CLIENTE:** Isodec, 10m x 5m, 100mm, blanco")
    
    time.sleep(1)
    
    print("\n🤖 **AGENTE:** ✅ **Especificaciones registradas**")
    print("🏠 Producto: ISODEC")
    print("📏 Dimensiones: 10.0m x 5.0m")
    print("📐 Espesor: 100mm")
    print("🎨 Color: Blanco")
    print("🔧 Terminaciones: Gotero")
    print("⚙️ Servicios: Anclajes y traslado incluidos")
    print("Calculando cotización... ⏳")
    
    time.sleep(3)
    
    # Crear cotización real
    cliente = Cliente(
        nombre="Gabriel",
        telefono="099123456",
        direccion="Montevideo",
        zona="Montevideo"
    )
    
    especificaciones = EspecificacionCotizacion(
        producto="isodec",
        espesor="100mm",
        relleno="EPS",
        largo_metros=Decimal('10.0'),
        ancho_metros=Decimal('5.0'),
        color="Blanco",
        termina_front="Gotero",
        termina_sup="Gotero",
        termina_lat_1="Gotero",
        termina_lat_2="Gotero",
        anclajes="Incluido",
        traslado="Incluido"
    )
    
    cotizacion = sistema.crear_cotizacion(
        cliente=cliente,
        especificaciones=especificaciones,
        asignado_a="MA",
        observaciones="Cotización generada por agente virtual"
    )
    
    area = especificaciones.largo_metros * especificaciones.ancho_metros
    
    print("\n🤖 **AGENTE:** 🎉 **¡COTIZACIÓN LISTA!**")
    print(f"📋 **ID de Cotización:** {cotizacion.id}")
    print(f"👤 **Cliente:** {cotizacion.cliente.nombre}")
    print(f"🏠 **Producto:** {cotizacion.especificaciones.producto.upper()}")
    print(f"📏 **Dimensiones:** {cotizacion.especificaciones.largo_metros}m x {cotizacion.especificaciones.ancho_metros}m")
    print(f"📐 **Área total:** {area} m²")
    print(f"📐 **Espesor:** {cotizacion.especificaciones.espesor}")
    print(f"🎨 **Color:** {cotizacion.especificaciones.color}")
    print(f"💰 **PRECIO POR M²:** ${cotizacion.precio_metro_cuadrado}")
    print(f"💰 **PRECIO TOTAL:** ${cotizacion.precio_total}")
    print("✅ **Incluye:**")
    print("• Material del producto")
    print("• Terminaciones (Gotero)")
    print("• Anclajes")
    print("• Traslado")
    print("¿Te parece bien esta cotización? ¿Necesitas algún ajuste?")
    
    time.sleep(2)
    
    print("\n👤 **CLIENTE:** Perfecto, me parece bien el precio. ¿Cuándo pueden instalar?")
    
    time.sleep(1)
    
    print("\n🤖 **AGENTE:** ¡Excelente! 😊")
    print("Para coordinar la instalación, necesito que confirmes la cotización.")
    print("📞 Te voy a conectar con nuestro equipo de instalación.")
    print("⏰ Tiempo estimado de instalación: 1-2 días hábiles")
    print("🚚 El material se entrega en 24-48 horas")
    print("¿Te parece bien proceder con la confirmación?")
    
    time.sleep(2)
    
    print("\n👤 **CLIENTE:** Sí, perfecto. Gracias por la atención")
    
    time.sleep(1)
    
    print("\n🤖 **AGENTE:** 👋 ¡Gracias por contactar BMC Uruguay!")
    print("Espero haber sido de ayuda con tu cotización.")
    print("Si necesitas algo más, no dudes en contactarnos.")
    print("🏢 **BMC Uruguay - Aislamientos Térmicos**")
    print("📞 Tel: +598 XX XXX XXX")
    print("🌐 Web: bmcuruguay.com.uy")
    print("¡Que tengas un excelente día! 😊")
    
    print("\n" + "="*80)
    print("🎬 SIMULACIÓN COMPLETADA")
    print("="*80)
    
    # Mostrar estadísticas del sistema
    print(f"\n📊 **ESTADÍSTICAS DEL SISTEMA:**")
    print(f"• Total de cotizaciones: {len(sistema.cotizaciones)}")
    print(f"• Productos disponibles: {len(sistema.productos)}")
    print(f"• Estado de la cotización: {cotizacion.estado}")
    print(f"• Asignado a: {cotizacion.asignado_a}")


def demo_multiples_cotizaciones():
    """Demo con múltiples cotizaciones"""
    print("\n🎭 SIMULACIÓN DE MÚLTIPLES COTIZACIONES")
    print("="*60)
    
    sistema = SistemaCotizacionesBMC()
    sistema.actualizar_precio_producto("isodec", Decimal('150.00'))
    sistema.actualizar_precio_producto("poliestireno", Decimal('120.00'))
    sistema.actualizar_precio_producto("lana_roca", Decimal('140.00'))
    
    # Cotización 1: Isodec
    print("\n📋 **COTIZACIÓN 1 - ISODEC**")
    cliente1 = Cliente("María", "099111111", "Punta del Este", "Punta del Este")
    espec1 = EspecificacionCotizacion("isodec", "100mm", "EPS", Decimal('8.0'), Decimal('4.0'), "Blanco")
    cot1 = sistema.crear_cotizacion(cliente1, espec1, "MA", "Cliente de Punta del Este")
    
    print(f"Cliente: {cot1.cliente.nombre}")
    print(f"Producto: {cot1.especificaciones.producto}")
    print(f"Dimensiones: {cot1.especificaciones.largo_metros}m x {cot1.especificaciones.ancho_metros}m")
    print(f"Precio total: ${cot1.precio_total}")
    
    # Cotización 2: Isodec (diferente espesor)
    print("\n📋 **COTIZACIÓN 2 - ISODEC (75mm)**")
    cliente2 = Cliente("Carlos", "099222222", "Montevideo", "Montevideo")
    espec2 = EspecificacionCotizacion("isodec", "75mm", "EPS", Decimal('6.0'), Decimal('3.0'), "Blanco")
    cot2 = sistema.crear_cotizacion(cliente2, espec2, "MO", "Cliente de Montevideo")
    
    print(f"Cliente: {cot2.cliente.nombre}")
    print(f"Producto: {cot2.especificaciones.producto}")
    print(f"Dimensiones: {cot2.especificaciones.largo_metros}m x {cot2.especificaciones.ancho_metros}m")
    print(f"Precio total: ${cot2.precio_total}")
    
    # Cotización 3: Isodec (diferente color)
    print("\n📋 **COTIZACIÓN 3 - ISODEC (Gris)**")
    cliente3 = Cliente("Ana", "099333333", "Interior", "Interior")
    espec3 = EspecificacionCotizacion("isodec", "100mm", "EPS", Decimal('12.0'), Decimal('6.0'), "Gris")
    cot3 = sistema.crear_cotizacion(cliente3, espec3, "RA", "Cliente del Interior")
    
    print(f"Cliente: {cot3.cliente.nombre}")
    print(f"Producto: {cot3.especificaciones.producto}")
    print(f"Dimensiones: {cot3.especificaciones.largo_metros}m x {cot3.especificaciones.ancho_metros}m")
    print(f"Precio total: ${cot3.precio_total}")
    
    # Estadísticas finales
    print(f"\n📊 **ESTADÍSTICAS FINALES:**")
    print(f"Total de cotizaciones: {len(sistema.cotizaciones)}")
    
    total_ventas = sum(float(cot.precio_total) for cot in sistema.cotizaciones)
    print(f"Total en ventas: ${total_ventas:.2f}")
    
    # Productos más cotizados
    productos = {}
    for cot in sistema.cotizaciones:
        prod = cot.especificaciones.producto
        productos[prod] = productos.get(prod, 0) + 1
    
    print(f"Productos más cotizados:")
    for prod, cantidad in productos.items():
        print(f"  • {prod}: {cantidad} cotización(es)")


def demo_busqueda_cotizaciones():
    """Demo de búsqueda de cotizaciones"""
    print("\n🔍 DEMO DE BÚSQUEDA DE COTIZACIONES")
    print("="*50)
    
    sistema = SistemaCotizacionesBMC()
    sistema.actualizar_precio_producto("isodec", Decimal('150.00'))
    
    # Crear varias cotizaciones
    clientes = [
        ("Gabriel", "099123456", "Montevideo"),
        ("María", "099111111", "Punta del Este"),
        ("Carlos", "099222222", "Montevideo"),
        ("Ana", "099333333", "Interior"),
        ("Luis", "099444444", "Montevideo")
    ]
    
    for i, (nombre, telefono, direccion) in enumerate(clientes):
        cliente = Cliente(nombre, telefono, direccion, direccion)
        espec = EspecificacionCotizacion(
            "isodec", "100mm", "EPS", 
            Decimal('5.0'), Decimal('3.0'), "Blanco"
        )
        sistema.crear_cotizacion(cliente, espec, f"MA{i%3}")
    
    print("Cotizaciones creadas:")
    for cot in sistema.cotizaciones:
        print(f"• {cot.id}: {cot.cliente.nombre} - ${cot.precio_total}")
    
    # Búsqueda por nombre
    print(f"\n🔍 Buscando por nombre 'Gabriel':")
    resultados = sistema.buscar_cotizaciones_por_cliente(nombre="Gabriel")
    for cot in resultados:
        print(f"  ✓ {cot.id}: {cot.cliente.nombre} - ${cot.precio_total}")
    
    # Búsqueda por teléfono
    print(f"\n🔍 Buscando por teléfono '099111111':")
    resultados = sistema.buscar_cotizaciones_por_cliente(telefono="099111111")
    for cot in resultados:
        print(f"  ✓ {cot.id}: {cot.cliente.nombre} - ${cot.precio_total}")


def main():
    """Función principal del demo"""
    print("SISTEMA DE DEMO - AGENTE DE COTIZACIONES BMC URUGUAY")
    print("="*70)
    
    try:
        # Demo 1: Conversación completa
        demo_conversacion_completa()
        
        # Demo 2: Múltiples cotizaciones
        demo_multiples_cotizaciones()
        
        # Demo 3: Búsqueda de cotizaciones
        demo_busqueda_cotizaciones()
        
        print("\n" + "="*70)
        print("🎉 TODOS LOS DEMOS COMPLETADOS EXITOSAMENTE")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error en el demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
