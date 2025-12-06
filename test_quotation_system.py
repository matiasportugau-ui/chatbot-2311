#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para validar el sistema de cotizaciones inteligente
Verifica que la validación y solicitud de datos faltantes funcione correctamente
"""

import sys
from sistema_cotizaciones import SistemaCotizacionesBMC, Cliente, EspecificacionCotizacion
from utils_cotizaciones import obtener_datos_faltantes, formatear_mensaje_faltantes, construir_contexto_validacion
from decimal import Decimal

def test_quotation_validation():
    """Prueba el sistema de validación de cotizaciones"""
    print("\n" + "="*60)
    print("🧪 PRUEBA: Sistema de Validación de Cotizaciones")
    print("="*60 + "\n")
    
    # Test 1: Contexto completo
    print("📋 Test 1: Contexto completo (debería pasar validación)")
    contexto_completo = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "telefono": "099123456",
        "producto": "isodec",
        "espesor": "100mm",
        "largo": 10,
        "ancho": 5
    }
    
    faltantes = obtener_datos_faltantes(contexto_completo)
    if not faltantes:
        print("✅ Test 1 PASADO: No hay datos faltantes")
    else:
        print(f"❌ Test 1 FALLIDO: Se encontraron datos faltantes: {faltantes}")
    
    # Test 2: Contexto incompleto
    print("\n📋 Test 2: Contexto incompleto (debería detectar faltantes)")
    contexto_incompleto = {
        "nombre": "Juan",
        "apellido": "",  # Faltante
        "telefono": "099123456",
        "producto": "isodec",
        "espesor": "",  # Faltante
        "largo": 10,
        "ancho": 0  # Faltante
    }
    
    faltantes = obtener_datos_faltantes(contexto_incompleto)
    if faltantes:
        print(f"✅ Test 2 PASADO: Detectó datos faltantes: {faltantes}")
        mensaje = formatear_mensaje_faltantes(faltantes)
        print(f"   Mensaje generado: {mensaje[:100]}...")
    else:
        print("❌ Test 2 FALLIDO: No detectó datos faltantes")
    
    # Test 3: Crear cotización válida
    print("\n📋 Test 3: Crear cotización válida")
    try:
        sistema = SistemaCotizacionesBMC()
        sistema.actualizar_precio_producto("isodec", Decimal("150.00"))
        
        cliente = Cliente(
            nombre="Juan",
            telefono="099123456",
            direccion="Av. 18 de Julio 1234",
            zona="Montevideo",
            email="juan@example.com"
        )
        
        especificaciones = EspecificacionCotizacion(
            producto="isodec",
            espesor="100mm",
            relleno="EPS",
            largo_metros=Decimal("10"),
            ancho_metros=Decimal("5"),
            color="Blanco"
        )
        
        cotizacion = sistema.crear_cotizacion(
            cliente=cliente,
            especificaciones=especificaciones,
            asignado_a="MA"
        )
        
        print(f"✅ Test 3 PASADO: Cotización creada")
        print(f"   ID: {cotizacion.id}")
        print(f"   Precio total: ${cotizacion.precio_total}")
        print(f"   Precio m²: ${cotizacion.precio_metro_cuadrado}")
        print(f"   Estado: {cotizacion.estado}")
        
    except Exception as e:
        print(f"❌ Test 3 FALLIDO: Error al crear cotización: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Validar mensaje de datos faltantes
    print("\n📋 Test 4: Mensaje de datos faltantes")
    faltantes_test = ["producto", "espesor", "largo", "ancho"]
    mensaje = formatear_mensaje_faltantes(faltantes_test)
    print(f"✅ Mensaje generado:")
    print(f"   {mensaje}")
    
    print("\n" + "="*60)
    print("✅ Pruebas completadas")
    print("="*60 + "\n")

def test_quotation_products():
    """Prueba los productos disponibles"""
    print("\n" + "="*60)
    print("🧪 PRUEBA: Productos Disponibles")
    print("="*60 + "\n")
    
    try:
        sistema = SistemaCotizacionesBMC()
        
        # Obtener productos
        productos = sistema.obtener_productos_disponibles()
        
        print(f"✅ Productos encontrados: {len(productos)}")
        for producto in productos[:5]:  # Mostrar primeros 5
            print(f"   - {producto.nombre} ({producto.codigo})")
            print(f"     Espesor: {producto.espesor}, Precio base: ${producto.precio_base}")
        
    except Exception as e:
        print(f"❌ Error al obtener productos: {e}")
        import traceback
        traceback.print_exc()

def test_complex_calculation():
    """Prueba cálculos con múltiples factores"""
    print("\n" + "="*60)
    print("🧪 PRUEBA: Cálculo Complejo de Cotizaciones")
    print("="*60 + "\n")
    
    sistema = SistemaCotizacionesBMC()
    # Precio base para Isodec: $100
    sistema.actualizar_precio_producto("isodec", Decimal("100.00"))
    
    try:
        # Caso 1: Factores que aumentan precio
        # Espesor 150mm -> factor 1.2
        # Color Personalizado -> factor 1.15
        # Terminación Hormigón -> +0.1
        print("📋 Test 1: Factores de aumento")
        
        especificaciones = EspecificacionCotizacion(
            producto="isodec",
            espesor="150mm",  # Factor 1.2
            relleno="EPS",
            largo_metros=Decimal("10"),
            ancho_metros=Decimal("1"), # 10 m2
            color="Personalizado", # Factor 1.15
            termina_front="Hormigón", # +0.1
            anclajes="Incluido", # 1.0
            traslado="Incluido" # 1.0
        )
        
        # Base: 100
        # Factor espesor: 1.2 -> 120
        # Factor color: 1.15 -> 120 * 1.15 = 138
        # Factor terminación: 1.0 + 0.1 = 1.1 -> 138 * 1.1 = 151.8
        
        # Cálculo esperado según código:
        # precio_metro_cuadrado * factor_espesor * factor_color * factor_terminaciones * factor_anclajes * factor_traslado
        # 100 * 1.2 * 1.15 * 1.1 * 1.0 * 1.0 = 151.8
        
        precio_total, precio_m2 = sistema.calcular_precio_cotizacion(especificaciones)
        
        expected_m2 = Decimal("100") * Decimal("1.2") * Decimal("1.15") * Decimal("1.1")
        
        print(f"   Precio m² calculado: ${precio_m2}")
        print(f"   Precio m² esperado:  ${expected_m2}")
        
        if abs(precio_m2 - expected_m2) < Decimal("0.01"):
            print("✅ Test 1 PASADO")
        else:
            print(f"❌ Test 1 FALLIDO: Diferencia de {abs(precio_m2 - expected_m2)}")

        # Caso 2: Factores de descuento
        # 50mm -> 0.8
        # Anclajes no incluido -> 0.95
        # Traslado no incluido -> 0.9
        print("\n📋 Test 2: Factores de descuento")
        
        especificaciones_desc = EspecificacionCotizacion(
            producto="isodec",
            espesor="50mm",  # Factor 0.8
            relleno="EPS",
            largo_metros=Decimal("10"),
            ancho_metros=Decimal("1"),
            color="Blanco", # 1.0
            anclajes="No incluido", # 0.95
            traslado="No incluido" # 0.9
        )
        
        # 100 * 0.8 * 1.0 * 1.0 (term default) * 0.95 * 0.9
        # 80 * 0.95 = 76
        # 76 * 0.9 = 68.4
        
        precio_total_desc, precio_m2_desc = sistema.calcular_precio_cotizacion(especificaciones_desc)
        
        expected_m2_desc = Decimal("100") * Decimal("0.8") * Decimal("0.95") * Decimal("0.9")
        
        print(f"   Precio m² calculado: ${precio_m2_desc}")
        print(f"   Precio m² esperado:  ${expected_m2_desc}")
        
        if abs(precio_m2_desc - expected_m2_desc) < Decimal("0.01"):
            print("✅ Test 2 PASADO")
        else:
             print(f"❌ Test 2 FALLIDO: Diferencia de {abs(precio_m2_desc - expected_m2_desc)}")
             
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        test_quotation_validation()
        test_quotation_products()
        test_complex_calculation()
        print("\n✅ Todas las pruebas completadas exitosamente!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

