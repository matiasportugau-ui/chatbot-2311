#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Plantillas de Cotización BMC Uruguay
Crea plantillas personalizadas para diferentes tipos de cotizaciones
"""

import json
from typing import Dict, List
from decimal import Decimal
from sistema_cotizaciones import Cotizacion

class GeneradorPlantillas:
    """Generador de plantillas de cotización"""
    
    def __init__(self):
        self.plantillas = {}
        self.cargar_plantillas_base()
    
    def cargar_plantillas_base(self):
        """Carga las plantillas base del sistema"""
        
        # Plantilla para Isodec
        self.plantillas['isodec_estandar'] = {
            'nombre': 'Isodec - Cotización Estándar',
            'producto_base': 'isodec',
            'campos_requeridos': [
                'cliente.nombre',
                'cliente.telefono',
                'cliente.direccion',
                'especificaciones.largo_metros',
                'especificaciones.ancho_metros',
                'especificaciones.espesor',
                'especificaciones.color'
            ],
            'campos_opcionales': [
                'especificaciones.termina_front',
                'especificaciones.termina_sup',
                'especificaciones.termina_lat_1',
                'especificaciones.termina_lat_2',
                'especificaciones.anclajes',
                'especificaciones.traslado'
            ],
            'formulas': {
                'area_total': 'largo_metros * ancho_metros',
                'precio_base': 'precio_metro_cuadrado * area_total',
                'factor_espesor': 'self._calcular_factor_espesor(espesor)',
                'factor_color': 'self._calcular_factor_color(color)',
                'factor_terminaciones': 'self._calcular_factor_terminaciones(termina_front, termina_sup, termina_lat_1, termina_lat_2)',
                'precio_final': 'precio_base * factor_espesor * factor_color * factor_terminaciones'
            },
            'template_html': self._generar_template_html_isodec(),
            'template_pdf': self._generar_template_pdf_isodec()
        }
        
        # Plantilla para cotización rápida
        self.plantillas['cotizacion_rapida'] = {
            'nombre': 'Cotización Rápida',
            'producto_base': 'cualquiera',
            'campos_requeridos': [
                'cliente.nombre',
                'cliente.telefono',
                'especificaciones.largo_metros',
                'especificaciones.ancho_metros'
            ],
            'campos_opcionales': [
                'especificaciones.producto',
                'especificaciones.espesor',
                'especificaciones.color'
            ],
            'formulas': {
                'area_total': 'largo_metros * ancho_metros',
                'precio_estimado': 'area_total * 150'  # Precio estimado por m²
            },
            'template_html': self._generar_template_html_rapida(),
            'template_pdf': self._generar_template_pdf_rapida()
        }
        
        # Plantilla para cotización detallada
        self.plantillas['cotizacion_detallada'] = {
            'nombre': 'Cotización Detallada',
            'producto_base': 'cualquiera',
            'campos_requeridos': [
                'cliente.nombre',
                'cliente.telefono',
                'cliente.direccion',
                'cliente.zona',
                'especificaciones.producto',
                'especificaciones.largo_metros',
                'especificaciones.ancho_metros',
                'especificaciones.espesor',
                'especificaciones.relleno',
                'especificaciones.color'
            ],
            'campos_opcionales': [
                'especificaciones.termina_front',
                'especificaciones.termina_sup',
                'especificaciones.termina_lat_1',
                'especificaciones.termina_lat_2',
                'especificaciones.anclajes',
                'especificaciones.traslado',
                'especificaciones.direccion',
                'especificaciones.forma',
                'especificaciones.origen'
            ],
            'formulas': {
                'area_total': 'largo_metros * ancho_metros',
                'perimetro': '2 * (largo_metros + ancho_metros)',
                'precio_base': 'precio_metro_cuadrado * area_total',
                'costo_terminaciones': 'perimetro * precio_terminacion_metro_lineal',
                'costo_servicios': 'costo_anclajes + costo_traslado',
                'subtotal': 'precio_base + costo_terminaciones + costo_servicios',
                'iva': 'subtotal * 0.22',
                'total': 'subtotal + iva'
            },
            'template_html': self._generar_template_html_detallada(),
            'template_pdf': self._generar_template_pdf_detallada()
        }
    
    def _generar_template_html_isodec(self) -> str:
        """Genera template HTML para Isodec"""
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cotización Isodec - BMC Uruguay</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
        .content { margin: 20px 0; }
        .section { margin: 20px 0; border: 1px solid #ddd; padding: 15px; }
        .section h3 { color: #2c3e50; margin-top: 0; }
        .row { display: flex; justify-content: space-between; margin: 10px 0; }
        .label { font-weight: bold; }
        .value { color: #666; }
        .total { background-color: #f8f9fa; padding: 15px; font-size: 18px; font-weight: bold; }
        .footer { text-align: center; margin-top: 30px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>BMC URUGUAY</h1>
        <h2>COTIZACIÓN ISODEC</h2>
        <p>ID: {{cotizacion.id}} | Fecha: {{cotizacion.fecha}}</p>
    </div>
    
    <div class="content">
        <div class="section">
            <h3>DATOS DEL CLIENTE</h3>
            <div class="row">
                <span class="label">Nombre:</span>
                <span class="value">{{cotizacion.cliente.nombre}}</span>
            </div>
            <div class="row">
                <span class="label">Teléfono:</span>
                <span class="value">{{cotizacion.cliente.telefono}}</span>
            </div>
            <div class="row">
                <span class="label">Dirección:</span>
                <span class="value">{{cotizacion.cliente.direccion}}</span>
            </div>
        </div>
        
        <div class="section">
            <h3>ESPECIFICACIONES DEL PRODUCTO</h3>
            <div class="row">
                <span class="label">Producto:</span>
                <span class="value">{{cotizacion.especificaciones.producto}}</span>
            </div>
            <div class="row">
                <span class="label">Espesor:</span>
                <span class="value">{{cotizacion.especificaciones.espesor}}</span>
            </div>
            <div class="row">
                <span class="label">Relleno:</span>
                <span class="value">{{cotizacion.especificaciones.relleno}}</span>
            </div>
            <div class="row">
                <span class="label">Color:</span>
                <span class="value">{{cotizacion.especificaciones.color}}</span>
            </div>
        </div>
        
        <div class="section">
            <h3>DIMENSIONES</h3>
            <div class="row">
                <span class="label">Largo:</span>
                <span class="value">{{cotizacion.especificaciones.largo_metros}} m</span>
            </div>
            <div class="row">
                <span class="label">Ancho:</span>
                <span class="value">{{cotizacion.especificaciones.ancho_metros}} m</span>
            </div>
            <div class="row">
                <span class="label">Área total:</span>
                <span class="value">{{area_total}} m²</span>
            </div>
        </div>
        
        <div class="section">
            <h3>TERMINACIONES</h3>
            <div class="row">
                <span class="label">Frontal:</span>
                <span class="value">{{cotizacion.especificaciones.termina_front}}</span>
            </div>
            <div class="row">
                <span class="label">Superior:</span>
                <span class="value">{{cotizacion.especificaciones.termina_sup}}</span>
            </div>
            <div class="row">
                <span class="label">Lateral 1:</span>
                <span class="value">{{cotizacion.especificaciones.termina_lat_1}}</span>
            </div>
            <div class="row">
                <span class="label">Lateral 2:</span>
                <span class="value">{{cotizacion.especificaciones.termina_lat_2}}</span>
            </div>
        </div>
        
        <div class="section">
            <h3>SERVICIOS</h3>
            <div class="row">
                <span class="label">Anclajes:</span>
                <span class="value">{{cotizacion.especificaciones.anclajes}}</span>
            </div>
            <div class="row">
                <span class="label">Traslado:</span>
                <span class="value">{{cotizacion.especificaciones.traslado}}</span>
            </div>
        </div>
        
        <div class="section total">
            <h3>PRECIOS</h3>
            <div class="row">
                <span class="label">Precio por m²:</span>
                <span class="value">${{cotizacion.precio_metro_cuadrado}}</span>
            </div>
            <div class="row">
                <span class="label">Precio total:</span>
                <span class="value">${{cotizacion.precio_total}}</span>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>BMC Uruguay - Aislamientos Térmicos</p>
        <p>Tel: +598 XX XXX XXX | Email: info@bmcuruguay.com.uy</p>
        <p>Web: <a href="https://bmcuruguay.com.uy">bmcuruguay.com.uy</a></p>
    </div>
</body>
</html>
        """
    
    def _generar_template_html_rapida(self) -> str:
        """Genera template HTML para cotización rápida"""
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cotización Rápida - BMC Uruguay</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #3498db; color: white; padding: 20px; text-align: center; }
        .content { margin: 20px 0; }
        .section { margin: 20px 0; border: 1px solid #ddd; padding: 15px; }
        .section h3 { color: #3498db; margin-top: 0; }
        .row { display: flex; justify-content: space-between; margin: 10px 0; }
        .label { font-weight: bold; }
        .value { color: #666; }
        .total { background-color: #f8f9fa; padding: 15px; font-size: 18px; font-weight: bold; }
        .footer { text-align: center; margin-top: 30px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>BMC URUGUAY</h1>
        <h2>COTIZACIÓN RÁPIDA</h2>
        <p>ID: {{cotizacion.id}} | Fecha: {{cotizacion.fecha}}</p>
    </div>
    
    <div class="content">
        <div class="section">
            <h3>CLIENTE</h3>
            <div class="row">
                <span class="label">Nombre:</span>
                <span class="value">{{cotizacion.cliente.nombre}}</span>
            </div>
            <div class="row">
                <span class="label">Teléfono:</span>
                <span class="value">{{cotizacion.cliente.telefono}}</span>
            </div>
        </div>
        
        <div class="section">
            <h3>DIMENSIONES</h3>
            <div class="row">
                <span class="label">Largo:</span>
                <span class="value">{{cotizacion.especificaciones.largo_metros}} m</span>
            </div>
            <div class="row">
                <span class="label">Ancho:</span>
                <span class="value">{{cotizacion.especificaciones.ancho_metros}} m</span>
            </div>
            <div class="row">
                <span class="label">Área total:</span>
                <span class="value">{{area_total}} m²</span>
            </div>
        </div>
        
        <div class="section total">
            <h3>PRECIO ESTIMADO</h3>
            <div class="row">
                <span class="label">Precio estimado:</span>
                <span class="value">${{precio_estimado}}</span>
            </div>
            <p><em>* Precio estimado. Para cotización exacta, contactar con nuestros asesores.</em></p>
        </div>
    </div>
    
    <div class="footer">
        <p>BMC Uruguay - Aislamientos Térmicos</p>
        <p>Tel: +598 XX XXX XXX | Email: info@bmcuruguay.com.uy</p>
    </div>
</body>
</html>
        """
    
    def _generar_template_html_detallada(self) -> str:
        """Genera template HTML para cotización detallada"""
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cotización Detallada - BMC Uruguay</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #e74c3c; color: white; padding: 20px; text-align: center; }
        .content { margin: 20px 0; }
        .section { margin: 20px 0; border: 1px solid #ddd; padding: 15px; }
        .section h3 { color: #e74c3c; margin-top: 0; }
        .row { display: flex; justify-content: space-between; margin: 10px 0; }
        .label { font-weight: bold; }
        .value { color: #666; }
        .total { background-color: #f8f9fa; padding: 15px; font-size: 18px; font-weight: bold; }
        .footer { text-align: center; margin-top: 30px; color: #666; }
        .desglose { background-color: #f8f9fa; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>BMC URUGUAY</h1>
        <h2>COTIZACIÓN DETALLADA</h2>
        <p>ID: {{cotizacion.id}} | Fecha: {{cotizacion.fecha}}</p>
    </div>
    
    <div class="content">
        <div class="section">
            <h3>DATOS DEL CLIENTE</h3>
            <div class="row">
                <span class="label">Nombre:</span>
                <span class="value">{{cotizacion.cliente.nombre}}</span>
            </div>
            <div class="row">
                <span class="label">Teléfono:</span>
                <span class="value">{{cotizacion.cliente.telefono}}</span>
            </div>
            <div class="row">
                <span class="label">Dirección:</span>
                <span class="value">{{cotizacion.cliente.direccion}}</span>
            </div>
            <div class="row">
                <span class="label">Zona:</span>
                <span class="value">{{cotizacion.cliente.zona}}</span>
            </div>
        </div>
        
        <div class="section">
            <h3>ESPECIFICACIONES TÉCNICAS</h3>
            <div class="row">
                <span class="label">Producto:</span>
                <span class="value">{{cotizacion.especificaciones.producto}}</span>
            </div>
            <div class="row">
                <span class="label">Espesor:</span>
                <span class="value">{{cotizacion.especificaciones.espesor}}</span>
            </div>
            <div class="row">
                <span class="label">Relleno:</span>
                <span class="value">{{cotizacion.especificaciones.relleno}}</span>
            </div>
            <div class="row">
                <span class="label">Color:</span>
                <span class="value">{{cotizacion.especificaciones.color}}</span>
            </div>
        </div>
        
        <div class="section">
            <h3>DIMENSIONES Y CÁLCULOS</h3>
            <div class="row">
                <span class="label">Largo:</span>
                <span class="value">{{cotizacion.especificaciones.largo_metros}} m</span>
            </div>
            <div class="row">
                <span class="label">Ancho:</span>
                <span class="value">{{cotizacion.especificaciones.ancho_metros}} m</span>
            </div>
            <div class="row">
                <span class="label">Área total:</span>
                <span class="value">{{area_total}} m²</span>
            </div>
            <div class="row">
                <span class="label">Perímetro:</span>
                <span class="value">{{perimetro}} m</span>
            </div>
        </div>
        
        <div class="section">
            <h3>DESGLOSE DE PRECIOS</h3>
            <div class="desglose">
                <div class="row">
                    <span class="label">Precio base ({{area_total}} m² × ${{precio_metro_cuadrado}}):</span>
                    <span class="value">${{precio_base}}</span>
                </div>
                <div class="row">
                    <span class="label">Terminaciones ({{perimetro}} m × ${{precio_terminacion_metro_lineal}}):</span>
                    <span class="value">${{costo_terminaciones}}</span>
                </div>
                <div class="row">
                    <span class="label">Anclajes:</span>
                    <span class="value">${{costo_anclajes}}</span>
                </div>
                <div class="row">
                    <span class="label">Traslado:</span>
                    <span class="value">${{costo_traslado}}</span>
                </div>
                <div class="row">
                    <span class="label">Subtotal:</span>
                    <span class="value">${{subtotal}}</span>
                </div>
                <div class="row">
                    <span class="label">IVA (22%):</span>
                    <span class="value">${{iva}}</span>
                </div>
            </div>
        </div>
        
        <div class="section total">
            <h3>TOTAL</h3>
            <div class="row">
                <span class="label">Precio total:</span>
                <span class="value">${{total}}</span>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>BMC Uruguay - Aislamientos Térmicos</p>
        <p>Tel: +598 XX XXX XXX | Email: info@bmcuruguay.com.uy</p>
        <p>Web: <a href="https://bmcuruguay.com.uy">bmcuruguay.com.uy</a></p>
    </div>
</body>
</html>
        """
    
    def _generar_template_pdf_isodec(self) -> str:
        """Genera template PDF para Isodec"""
        return "Template PDF para Isodec (implementar con reportlab)"
    
    def _generar_template_pdf_rapida(self) -> str:
        """Genera template PDF para cotización rápida"""
        return "Template PDF para cotización rápida (implementar con reportlab)"
    
    def _generar_template_pdf_detallada(self) -> str:
        """Genera template PDF para cotización detallada"""
        return "Template PDF para cotización detallada (implementar con reportlab)"
    
    def obtener_plantilla(self, nombre_plantilla: str) -> Dict:
        """Obtiene una plantilla por nombre"""
        return self.plantillas.get(nombre_plantilla, {})
    
    def listar_plantillas(self) -> List[str]:
        """Lista todas las plantillas disponibles"""
        return list(self.plantillas.keys())
    
    def crear_plantilla_personalizada(self, nombre: str, configuracion: Dict):
        """Crea una plantilla personalizada"""
        self.plantillas[nombre] = configuracion
    
    def exportar_plantillas(self, archivo: str):
        """Exporta todas las plantillas a un archivo JSON"""
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(self.plantillas, f, ensure_ascii=False, indent=2)
    
    def importar_plantillas(self, archivo: str):
        """Importa plantillas desde un archivo JSON"""
        with open(archivo, 'r', encoding='utf-8') as f:
            self.plantillas = json.load(f)

def main():
    """Función principal para demostrar el generador de plantillas"""
    generador = GeneradorPlantillas()
    
    print("Plantillas disponibles:")
    for plantilla in generador.listar_plantillas():
        print(f"- {plantilla}")
    
    # Exportar plantillas
    generador.exportar_plantillas('plantillas_cotizacion.json')
    print("\nPlantillas exportadas a 'plantillas_cotizacion.json'")

if __name__ == "__main__":
    main()
