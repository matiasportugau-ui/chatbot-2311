#!/usr/bin/env python3
"""
Sistema de Cotizaciones BMC Uruguay - Script Principal
Integra todos los componentes del sistema de cotizaciones
"""

import json
import sys
from decimal import Decimal

from generador_plantillas import GeneradorPlantillas
from importar_datos_planilla import ImportadorPlanilla
from sistema_cotizaciones import Cliente, EspecificacionCotizacion, SistemaCotizacionesBMC


class SistemaCompletoBMC:
    """Sistema completo de cotizaciones BMC Uruguay"""

    def __init__(self):
        self.sistema_cotizaciones = SistemaCotizacionesBMC()
        self.importador = ImportadorPlanilla(self.sistema_cotizaciones)
        self.generador_plantillas = GeneradorPlantillas()
        self.cargar_configuracion()

    def cargar_configuracion(self):
        """Carga la configuración del sistema"""
        try:
            with open("matriz_precios.json", encoding="utf-8") as f:
                matriz_precios = json.load(f)

            # Cargar productos y precios
            for codigo_producto, datos_producto in matriz_precios["productos"].items():
                if "espesores_disponibles" in datos_producto:
                    # Usar el precio base del espesor más común (100mm)
                    precio_base = (
                        datos_producto["espesores_disponibles"]
                        .get("100mm", {})
                        .get("precio_base", 0)
                    )
                    self.sistema_cotizaciones.actualizar_precio_producto(
                        codigo_producto, Decimal(str(precio_base))
                    )

            print("✓ Configuración cargada correctamente")

        except FileNotFoundError:
            print("⚠ Archivo de configuración no encontrado, usando configuración por defecto")
        except Exception as e:
            print(f"⚠ Error cargando configuración: {e}")

    def crear_cotizacion_interactiva(self):
        """Crea una cotización de forma interactiva"""
        print("\n=== CREAR NUEVA COTIZACIÓN ===")

        # Datos del cliente
        print("\n--- DATOS DEL CLIENTE ---")
        nombre = input("Nombre del cliente: ").strip()
        telefono = input("Teléfono: ").strip()
        direccion = input("Dirección: ").strip()
        zona = input("Zona: ").strip()

        cliente = Cliente(nombre=nombre, telefono=telefono, direccion=direccion, zona=zona)

        # Especificaciones del producto
        print("\n--- ESPECIFICACIONES DEL PRODUCTO ---")
        print("Productos disponibles:")
        for codigo, producto in self.sistema_cotizaciones.productos.items():
            print(f"- {codigo}: {producto.nombre}")

        producto = input("Código del producto: ").strip().lower()

        if producto not in self.sistema_cotizaciones.productos:
            print("⚠ Producto no encontrado, usando Isodec por defecto")
            producto = "isodec"

        espesor = input("Espesor (50mm, 75mm, 100mm, 125mm, 150mm): ").strip()
        relleno = input("Relleno (EPS, Poliuretano, Lana de roca): ").strip()
        color = input("Color (Blanco, Gris, Personalizado): ").strip()

        print("\n--- DIMENSIONES ---")
        try:
            largo = Decimal(input("Largo en metros: ").strip())
            ancho = Decimal(input("Ancho en metros: ").strip())
        except (ValueError, TypeError):
            print("⚠ Valores inválidos, usando 10x5 metros por defecto")
            largo = Decimal("10")
            ancho = Decimal("5")

        print("\n--- TERMINACIONES (opcional) ---")
        termina_front = input("Terminación frontal (Gotero, Hormigón, Aluminio): ").strip()
        termina_sup = input("Terminación superior (Gotero, Hormigón, Aluminio): ").strip()
        termina_lat_1 = input("Terminación lateral 1 (Gotero, Hormigón, Aluminio): ").strip()
        termina_lat_2 = input("Terminación lateral 2 (Gotero, Hormigón, Aluminio): ").strip()

        print("\n--- SERVICIOS ---")
        anclajes = input("Anclajes (Incluido, No incluido): ").strip()
        traslado = input("Traslado (Incluido, No incluido): ").strip()

        print("\n--- INFORMACIÓN ADICIONAL ---")
        forma_contacto = input("Forma de contacto (WhatsApp, Email, Teléfono): ").strip()
        origen = input("Origen (WA, Web, Teléfono): ").strip()
        observaciones = input("Observaciones: ").strip()

        # Crear especificaciones
        especificaciones = EspecificacionCotizacion(
            producto=producto,
            espesor=espesor,
            relleno=relleno,
            largo_metros=largo,
            ancho_metros=ancho,
            color=color,
            termina_front=termina_front,
            termina_sup=termina_sup,
            termina_lat_1=termina_lat_1,
            termina_lat_2=termina_lat_2,
            anclajes=anclajes,
            traslado=traslado,
            forma=forma_contacto,
            origen=origen,
        )

        # Crear cotización
        cotizacion = self.sistema_cotizaciones.crear_cotizacion(
            cliente=cliente,
            especificaciones=especificaciones,
            asignado_a="MA",
            observaciones=observaciones,
        )

        print(f"\n✓ Cotización creada: {cotizacion.id}")
        return cotizacion

    def buscar_cotizaciones(self):
        """Busca cotizaciones existentes"""
        print("\n=== BUSCAR COTIZACIONES ===")

        print("1. Buscar por nombre del cliente")
        print("2. Buscar por teléfono")
        print("3. Buscar por fecha")
        print("4. Mostrar todas")

        opcion = input("\nSeleccione una opción (1-4): ").strip()

        if opcion == "1":
            nombre = input("Nombre del cliente: ").strip()
            resultados = self.sistema_cotizaciones.buscar_cotizaciones_por_cliente(nombre=nombre)
        elif opcion == "2":
            telefono = input("Teléfono: ").strip()
            resultados = self.sistema_cotizaciones.buscar_cotizaciones_por_cliente(
                telefono=telefono
            )
        elif opcion == "3":
            print("Formato de fecha: DD-MM-YYYY")
            fecha_str = input("Fecha de inicio: ").strip()
            # Implementar parsing de fecha
            resultados = []
        elif opcion == "4":
            resultados = self.sistema_cotizaciones.cotizaciones
        else:
            print("⚠ Opción inválida")
            return

        if not resultados:
            print("No se encontraron cotizaciones")
            return

        print(f"\nSe encontraron {len(resultados)} cotización(es):")
        for i, cotizacion in enumerate(resultados, 1):
            print(f"\n{i}. ID: {cotizacion.id}")
            print(f"   Cliente: {cotizacion.cliente.nombre}")
            print(f"   Fecha: {cotizacion.fecha.strftime('%d/%m/%Y %H:%M')}")
            print(f"   Estado: {cotizacion.estado}")
            print(f"   Precio: ${cotizacion.precio_total}")

    def generar_reporte(self, cotizacion_id: str):
        """Genera un reporte de cotización"""
        cotizacion = None
        for c in self.sistema_cotizaciones.cotizaciones:
            if c.id == cotizacion_id:
                cotizacion = c
                break

        if not cotizacion:
            print("⚠ Cotización no encontrada")
            return

        print("\n=== REPORTE DE COTIZACIÓN ===")
        print(self.sistema_cotizaciones.generar_reporte_cotizacion(cotizacion))

    def exportar_datos(self):
        """Exporta todos los datos del sistema"""
        print("\n=== EXPORTAR DATOS ===")

        # Exportar cotizaciones
        archivo_cotizaciones = "cotizaciones_exportadas.json"
        self.sistema_cotizaciones.exportar_cotizaciones_a_json(archivo_cotizaciones)
        print(f"✓ Cotizaciones exportadas a {archivo_cotizaciones}")

        # Exportar plantillas
        archivo_plantillas = "plantillas_exportadas.json"
        self.generador_plantillas.exportar_plantillas(archivo_plantillas)
        print(f"✓ Plantillas exportadas a {archivo_plantillas}")

    def mostrar_estadisticas(self):
        """Muestra estadísticas del sistema"""
        print("\n=== ESTADÍSTICAS DEL SISTEMA ===")

        total_cotizaciones = len(self.sistema_cotizaciones.cotizaciones)
        print(f"Total de cotizaciones: {total_cotizaciones}")

        if total_cotizaciones > 0:
            # Estadísticas por estado
            estados = {}
            for cotizacion in self.sistema_cotizaciones.cotizaciones:
                estado = cotizacion.estado
                estados[estado] = estados.get(estado, 0) + 1

            print("\nCotizaciones por estado:")
            for estado, cantidad in estados.items():
                print(f"  {estado}: {cantidad}")

            # Estadísticas por producto
            productos = {}
            for cotizacion in self.sistema_cotizaciones.cotizaciones:
                producto = cotizacion.especificaciones.producto
                productos[producto] = productos.get(producto, 0) + 1

            print("\nCotizaciones por producto:")
            for producto, cantidad in productos.items():
                print(f"  {producto}: {cantidad}")

            # Precio promedio
            precios = [
                float(c.precio_total)
                for c in self.sistema_cotizaciones.cotizaciones
                if c.precio_total > 0
            ]
            if precios:
                precio_promedio = sum(precios) / len(precios)
                print(f"\nPrecio promedio: ${precio_promedio:.2f}")

        print(f"\nProductos disponibles: {len(self.sistema_cotizaciones.productos)}")
        print(f"Plantillas disponibles: {len(self.generador_plantillas.plantillas)}")

    def menu_principal(self):
        """Menú principal del sistema"""
        while True:
            print("\n" + "=" * 50)
            print("SISTEMA DE COTIZACIONES BMC URUGUAY")
            print("=" * 50)
            print("1. Crear nueva cotización")
            print("2. Buscar cotizaciones")
            print("3. Generar reporte")
            print("4. Exportar datos")
            print("5. Mostrar estadísticas")
            print("6. Salir")

            opcion = input("\nSeleccione una opción (1-6): ").strip()

            if opcion == "1":
                try:
                    cotizacion = self.crear_cotizacion_interactiva()
                    print("\n¿Desea generar el reporte de esta cotización? (s/n): ", end="")
                    if input().strip().lower() == "s":
                        print(self.sistema_cotizaciones.generar_reporte_cotizacion(cotizacion))
                except Exception as e:
                    print(f"⚠ Error creando cotización: {e}")

            elif opcion == "2":
                self.buscar_cotizaciones()

            elif opcion == "3":
                cotizacion_id = input("ID de la cotización: ").strip()
                self.generar_reporte(cotizacion_id)

            elif opcion == "4":
                self.exportar_datos()

            elif opcion == "5":
                self.mostrar_estadisticas()

            elif opcion == "6":
                print("¡Hasta luego!")
                break

            else:
                print("⚠ Opción inválida")


def main():
    """Función principal"""
    print("Iniciando Sistema de Cotizaciones BMC Uruguay...")

    try:
        sistema = SistemaCompletoBMC()
        sistema.menu_principal()
    except KeyboardInterrupt:
        print("\n\nSistema interrumpido por el usuario")
    except Exception as e:
        print(f"\nError del sistema: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
