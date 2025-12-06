#!/usr/bin/env python3
"""
Demo del Sistema de Cotizaciones BMC Uruguay
Demuestra las funcionalidades principales del sistema
"""

from decimal import Decimal

from sistema_cotizaciones import Cliente, EspecificacionCotizacion, SistemaCotizacionesBMC


def demo_cotizacion_isodec():
    """Demo de cotización Isodec"""
    print("=== DEMO: COTIZACIÓN ISODEC ===")

    # Crear sistema
    sistema = SistemaCotizacionesBMC()

    # Configurar precio base
    sistema.actualizar_precio_producto("isodec", Decimal("150.00"))

    # Crear cliente
    cliente = Cliente(
        nombre="Gabriel",
        telefono="94 807 926",
        direccion="Cancha de Punta del Este",
        zona="Punta del Este",
    )

    # Crear especificaciones
    especificaciones = EspecificacionCotizacion(
        producto="isodec",
        espesor="100mm",
        relleno="EPS",
        largo_metros=Decimal("10.0"),
        ancho_metros=Decimal("5.0"),
        color="Blanco",
        termina_front="Gotero",
        termina_sup="Gotero",
        termina_lat_1="Gotero",
        termina_lat_2="Gotero",
        anclajes="Incluido",
        traslado="Incluido",
        direccion="Punta del Este",
        forma="WhatsApp",
        origen="WA",
    )

    # Crear cotización
    cotizacion = sistema.crear_cotizacion(
        cliente=cliente,
        especificaciones=especificaciones,
        asignado_a="MA",
        observaciones="Cliente interesado en instalación rápida",
    )

    # Mostrar resultado
    print(sistema.generar_reporte_cotizacion(cotizacion))

    return cotizacion


def demo_cotizacion_rapida():
    """Demo de cotización rápida"""
    print("\n=== DEMO: COTIZACIÓN RÁPIDA ===")

    sistema = SistemaCotizacionesBMC()
    sistema.actualizar_precio_producto("isodec", Decimal("150.00"))

    cliente = Cliente(
        nombre="Luis Enrique", telefono="59891438873", direccion="Montevideo", zona="Montevideo"
    )

    especificaciones = EspecificacionCotizacion(
        producto="isodec",
        espesor="75mm",
        relleno="EPS",
        largo_metros=Decimal("8.0"),
        ancho_metros=Decimal("4.0"),
        color="Blanco",
    )

    cotizacion = sistema.crear_cotizacion(
        cliente=cliente, especificaciones=especificaciones, asignado_a="MO"
    )

    print(sistema.generar_reporte_cotizacion(cotizacion))

    return cotizacion


def demo_busqueda_cotizaciones():
    """Demo de búsqueda de cotizaciones"""
    print("\n=== DEMO: BÚSQUEDA DE COTIZACIONES ===")

    sistema = SistemaCotizacionesBMC()
    sistema.actualizar_precio_producto("isodec", Decimal("150.00"))

    # Crear varias cotizaciones
    clientes = [
        ("Gabriel", "94 807 926", "Punta del Este"),
        ("Luis Enrique", "59891438873", "Montevideo"),
        ("Martín Pé", "5493416669226", "Buenos Aires"),
        ("Angel Martinez", "59891262521", "Montevideo"),
    ]

    for i, (nombre, telefono, direccion) in enumerate(clientes):
        cliente = Cliente(nombre=nombre, telefono=telefono, direccion=direccion, zona=direccion)

        especificaciones = EspecificacionCotizacion(
            producto="isodec",
            espesor="100mm",
            relleno="EPS",
            largo_metros=Decimal("5.0"),
            ancho_metros=Decimal("3.0"),
            color="Blanco",
        )

        sistema.crear_cotizacion(
            cliente=cliente,
            especificaciones=especificaciones,
            asignado_a=["MA", "MO", "RA", "SPRT"][i % 4],
        )

    # Buscar por nombre
    print("Buscando por nombre 'Gabriel':")
    resultados = sistema.buscar_cotizaciones_por_cliente(nombre="Gabriel")
    for cotizacion in resultados:
        print(f"- {cotizacion.id}: {cotizacion.cliente.nombre}")

    # Buscar por teléfono
    print("\nBuscando por teléfono '59891438873':")
    resultados = sistema.buscar_cotizaciones_por_cliente(telefono="59891438873")
    for cotizacion in resultados:
        print(f"- {cotizacion.id}: {cotizacion.cliente.nombre}")

    print(f"\nTotal de cotizaciones: {len(sistema.cotizaciones)}")


def demo_exportacion():
    """Demo de exportación de datos"""
    print("\n=== DEMO: EXPORTACIÓN DE DATOS ===")

    sistema = SistemaCotizacionesBMC()
    sistema.actualizar_precio_producto("isodec", Decimal("150.00"))

    # Crear cotización de ejemplo
    cliente = Cliente(
        nombre="Cliente Demo", telefono="099123456", direccion="Dirección Demo", zona="Montevideo"
    )

    especificaciones = EspecificacionCotizacion(
        producto="isodec",
        espesor="100mm",
        relleno="EPS",
        largo_metros=Decimal("10.0"),
        ancho_metros=Decimal("5.0"),
        color="Blanco",
    )

    cotizacion = sistema.crear_cotizacion(
        cliente=cliente, especificaciones=especificaciones, asignado_a="MA"
    )

    # Exportar
    archivo = "demo_cotizaciones.json"
    sistema.exportar_cotizaciones_a_json(archivo)
    print(f"Cotizaciones exportadas a {archivo}")


def demo_estadisticas():
    """Demo de estadísticas del sistema"""
    print("\n=== DEMO: ESTADÍSTICAS ===")

    sistema = SistemaCotizacionesBMC()
    sistema.actualizar_precio_producto("isodec", Decimal("150.00"))

    # Crear cotizaciones de ejemplo
    productos = ["isodec", "isodec", "poliestireno", "lana_roca"]
    estados = ["Pendiente", "Enviado", "Listo", "Confirmado"]

    for i in range(4):
        cliente = Cliente(
            nombre=f"Cliente {i + 1}",
            telefono=f"099{i:07d}",
            direccion=f"Dirección {i + 1}",
            zona="Montevideo",
        )

        especificaciones = EspecificacionCotizacion(
            producto=productos[i],
            espesor="100mm",
            relleno="EPS",
            largo_metros=Decimal("5.0"),
            ancho_metros=Decimal("3.0"),
            color="Blanco",
        )

        cotizacion = sistema.crear_cotizacion(
            cliente=cliente, especificaciones=especificaciones, asignado_a="MA"
        )
        cotizacion.estado = estados[i]

    # Mostrar estadísticas
    print(f"Total de cotizaciones: {len(sistema.cotizaciones)}")

    # Estadísticas por estado
    estados_count = {}
    for cotizacion in sistema.cotizaciones:
        estado = cotizacion.estado
        estados_count[estado] = estados_count.get(estado, 0) + 1

    print("\nCotizaciones por estado:")
    for estado, cantidad in estados_count.items():
        print(f"  {estado}: {cantidad}")

    # Estadísticas por producto
    productos_count = {}
    for cotizacion in sistema.cotizaciones:
        producto = cotizacion.especificaciones.producto
        productos_count[producto] = productos_count.get(producto, 0) + 1

    print("\nCotizaciones por producto:")
    for producto, cantidad in productos_count.items():
        print(f"  {producto}: {cantidad}")


def main():
    """Función principal del demo"""
    print("SISTEMA DE COTIZACIONES BMC URUGUAY - DEMO")
    print("=" * 50)

    try:
        # Ejecutar demos
        demo_cotizacion_isodec()
        demo_cotizacion_rapida()
        demo_busqueda_cotizaciones()
        demo_exportacion()
        demo_estadisticas()

        print("\n" + "=" * 50)
        print("DEMO COMPLETADO EXITOSAMENTE")
        print("=" * 50)

    except Exception as e:
        print(f"\nError en el demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
