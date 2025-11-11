#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importador de datos desde Google Sheets - Administrador de Cotizaciones II
Convierte los datos de la planilla en formato CSV a cotizaciones del sistema
"""

import csv
import json
import datetime
from decimal import Decimal
from sistema_cotizaciones import SistemaCotizacionesBMC, Cliente, EspecificacionCotizacion, Cotizacion

class ImportadorPlanilla:
    """Importador de datos desde la planilla de Google Sheets"""
    
    def __init__(self, sistema_cotizaciones: SistemaCotizacionesBMC):
        self.sistema = sistema_cotizaciones
    
    def procesar_datos_planilla(self, datos_planilla: list) -> list:
        """
        Procesa los datos de la planilla y los convierte en cotizaciones
        
        Args:
            datos_planilla: Lista de diccionarios con los datos de la planilla
            
        Returns:
            Lista de cotizaciones procesadas
        """
        cotizaciones_procesadas = []
        
        for i, fila in enumerate(datos_planilla):
            try:
                # Saltar filas vacías o de encabezado
                if not fila.get('Cliente') or fila.get('Cliente').strip() == '':
                    continue
                
                # Crear cliente
                cliente = Cliente(
                    nombre=fila.get('Cliente', '').strip(),
                    telefono=fila.get('Telefono-Contacto', '').strip(),
                    direccion=fila.get('Direccion / Zona', '').strip(),
                    zona=fila.get('Direccion / Zona', '').strip()
                )
                
                # Crear especificaciones
                especificaciones = EspecificacionCotizacion(
                    producto=fila.get('Producto', '').strip(),
                    espesor=fila.get('Espesor', '').strip(),
                    relleno=fila.get('Relleno', '').strip(),
                    largo_metros=self._convertir_a_decimal(fila.get('Largo (M)', '0')),
                    ancho_metros=self._convertir_a_decimal(fila.get('Ancho (M)', '0')),
                    color=fila.get('Color', '').strip(),
                    termina_front=fila.get('TerminaFront', '').strip(),
                    termina_sup=fila.get('TerminaSup', '').strip(),
                    termina_lat_1=fila.get('Termina Lat. 1', '').strip(),
                    termina_lat_2=fila.get('Termina Lat. 2', '').strip(),
                    anclajes=fila.get('Anclajes a', '').strip(),
                    traslado=fila.get('Traslado', '').strip(),
                    direccion=fila.get('Dirección', '').strip(),
                    forma=fila.get('Forma', '').strip(),
                    origen=fila.get('Origen', '').strip()
                )
                
                # Crear cotización
                cotizacion = Cotizacion(
                    id=f"COT-IMPORT-{i+1:04d}",
                    cliente=cliente,
                    especificaciones=especificaciones,
                    fecha=self._parsear_fecha(fila.get('Fecha', '')),
                    estado=fila.get('Estado', 'Pendiente'),
                    asignado_a=fila.get('Asig.', ''),
                    observaciones=fila.get('NOTAS', '')
                )
                
                # Calcular precios si es posible
                try:
                    precio_total, precio_metro_cuadrado = self.sistema.calcular_precio_cotizacion(especificaciones)
                    cotizacion.precio_total = precio_total
                    cotizacion.precio_metro_cuadrado = precio_metro_cuadrado
                except Exception as e:
                    print(f"Error calculando precios para fila {i+1}: {e}")
                    cotizacion.precio_total = Decimal('0')
                    cotizacion.precio_metro_cuadrado = Decimal('0')
                
                cotizaciones_procesadas.append(cotizacion)
                
            except Exception as e:
                print(f"Error procesando fila {i+1}: {e}")
                continue
        
        return cotizaciones_procesadas
    
    def _convertir_a_decimal(self, valor: str) -> Decimal:
        """Convierte un string a Decimal, manejando valores vacíos"""
        if not valor or valor.strip() == '':
            return Decimal('0')
        
        # Limpiar el valor
        valor_limpio = valor.strip().replace(',', '.')
        
        try:
            return Decimal(valor_limpio)
        except:
            return Decimal('0')
    
    def _parsear_fecha(self, fecha_str: str) -> datetime.datetime:
        """Parsea una fecha desde string"""
        if not fecha_str or fecha_str.strip() == '':
            return datetime.datetime.now()
        
        # Intentar diferentes formatos de fecha
        formatos_fecha = [
            '%d-%m',
            '%d/%m/%Y',
            '%Y-%m-%d',
            '%d-%m-%Y'
        ]
        
        for formato in formatos_fecha:
            try:
                if formato == '%d-%m':
                    # Agregar año actual si solo hay día y mes
                    fecha_parsed = datetime.datetime.strptime(fecha_str.strip(), formato)
                    return fecha_parsed.replace(year=datetime.datetime.now().year)
                else:
                    return datetime.datetime.strptime(fecha_str.strip(), formato)
            except:
                continue
        
        # Si no se puede parsear, usar fecha actual
        return datetime.datetime.now()
    
    def importar_desde_csv(self, archivo_csv: str) -> list:
        """Importa datos desde un archivo CSV"""
        cotizaciones = []
        
        with open(archivo_csv, 'r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)
            datos_planilla = list(lector)
        
        return self.procesar_datos_planilla(datos_planilla)
    
    def exportar_cotizaciones_importadas(self, cotizaciones: list, archivo_salida: str):
        """Exporta las cotizaciones importadas a un archivo JSON"""
        datos_exportar = []
        
        for cotizacion in cotizaciones:
            datos_exportar.append({
                'id': cotizacion.id,
                'cliente': {
                    'nombre': cotizacion.cliente.nombre,
                    'telefono': cotizacion.cliente.telefono,
                    'direccion': cotizacion.cliente.direccion,
                    'zona': cotizacion.cliente.zona
                },
                'especificaciones': {
                    'producto': cotizacion.especificaciones.producto,
                    'espesor': cotizacion.especificaciones.espesor,
                    'relleno': cotizacion.especificaciones.relleno,
                    'largo_metros': float(cotizacion.especificaciones.largo_metros),
                    'ancho_metros': float(cotizacion.especificaciones.ancho_metros),
                    'color': cotizacion.especificaciones.color,
                    'termina_front': cotizacion.especificaciones.termina_front,
                    'termina_sup': cotizacion.especificaciones.termina_sup,
                    'termina_lat_1': cotizacion.especificaciones.termina_lat_1,
                    'termina_lat_2': cotizacion.especificaciones.termina_lat_2,
                    'anclajes': cotizacion.especificaciones.anclajes,
                    'traslado': cotizacion.especificaciones.traslado,
                    'direccion': cotizacion.especificaciones.direccion,
                    'forma': cotizacion.especificaciones.forma,
                    'origen': cotizacion.especificaciones.origen
                },
                'fecha': cotizacion.fecha.isoformat(),
                'estado': cotizacion.estado,
                'asignado_a': cotizacion.asignado_a,
                'precio_total': float(cotizacion.precio_total),
                'precio_metro_cuadrado': float(cotizacion.precio_metro_cuadrado),
                'observaciones': cotizacion.observaciones
            })
        
        with open(archivo_salida, 'w', encoding='utf-8') as archivo:
            json.dump(datos_exportar, archivo, ensure_ascii=False, indent=2)

def main():
    """Función principal para importar datos"""
    # Crear sistema de cotizaciones
    sistema = SistemaCotizacionesBMC()
    
    # Cargar matriz de precios
    with open('matriz_precios.json', 'r', encoding='utf-8') as f:
        matriz_precios = json.load(f)
    
    # Actualizar precios en el sistema
    for codigo_producto, datos_producto in matriz_precios['productos'].items():
        if 'espesores_disponibles' in datos_producto:
            # Usar el precio base del espesor más común (100mm)
            precio_base = datos_producto['espesores_disponibles'].get('100mm', {}).get('precio_base', 0)
            sistema.actualizar_precio_producto(codigo_producto, Decimal(str(precio_base)))
    
    # Crear importador
    importador = ImportadorPlanilla(sistema)
    
    # Datos de ejemplo basados en la planilla de Google Sheets
    datos_ejemplo = [
        {
            'Asig.': 'MA',
            'Estado': 'Enviado',
            'Fecha': '29-09',
            'Cliente': 'Gabriel',
            'Orig.': 'WA',
            'Telefono-Contacto': '94 807 926',
            'Direccion / Zona': 'Cancha de Punta del Este',
            'Consulta': 'No',
            'Producto': 'Isodec',
            'Espesor': '100 mm',
            'Relleno': 'EPS',
            'Color': 'Blanco',
            'TerminaFront': 'Gotero',
            'TerminaSup': 'Gotero',
            'Termina Lat. 1': 'Gotero',
            'Termina Lat. 2': 'Gotero',
            'Anclajes a': 'Incluido',
            'Traslado': 'Incluido',
            'Dirección': 'Maldonado',
            'Forma': 'Estandar',
            'Origen': 'WA',
            'NOTAS': 'Cliente interesado en instalación rápida'
        }
    ]
    
    # Procesar datos
    cotizaciones_importadas = importador.procesar_datos_planilla(datos_ejemplo)
    
    # Agregar al sistema
    for cotizacion in cotizaciones_importadas:
        sistema.cotizaciones.append(cotizacion)
    
    # Exportar resultados
    importador.exportar_cotizaciones_importadas(cotizaciones_importadas, 'cotizaciones_importadas.json')
    
    # Generar reportes
    for cotizacion in cotizaciones_importadas:
        print(sistema.generar_reporte_cotizacion(cotizacion))
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
