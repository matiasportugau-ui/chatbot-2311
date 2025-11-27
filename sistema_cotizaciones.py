#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Cotizaciones BMC Uruguay
Desarrollado para automatizar el proceso de cotización basado en plantillas
y matrices de precios
"""

import json
import datetime
from typing import List, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP

@dataclass
class Cliente:
    """Estructura para datos del cliente"""
    nombre: str
    telefono: str
    direccion: str
    zona: str = ""
    email: str = ""


@dataclass
class Producto:
    """Estructura para productos disponibles"""
    codigo: str
    nombre: str
    espesor: str
    relleno: str
    color: str
    precio_base: Decimal
    link_web: str = ""
    terminaciones_disponibles: List[str] = None
    anclajes_incluidos: bool = False
    traslado_incluido: bool = False


@dataclass
class EspecificacionCotizacion:
    """Especificaciones técnicas para la cotización"""
    producto: str
    espesor: str
    relleno: str
    largo_metros: Decimal
    ancho_metros: Decimal
    color: str
    termina_front: str = ""
    termina_sup: str = ""
    termina_lat_1: str = ""
    termina_lat_2: str = ""
    anclajes: str = ""
    traslado: str = ""
    direccion: str = ""
    forma: str = ""
    origen: str = ""


@dataclass
class Cotizacion:
    """Estructura completa de cotización"""
    id: str
    cliente: Cliente
    especificaciones: EspecificacionCotizacion
    fecha: datetime.datetime
    estado: str
    asignado_a: str
    precio_total: Decimal = Decimal('0')
    precio_metro_cuadrado: Decimal = Decimal('0')
    observaciones: str = ""

class SistemaCotizacionesBMC:
    """Sistema principal de cotizaciones BMC Uruguay"""
    
    def __init__(self):
        self.productos = {}
        self.cotizaciones = []
        self.plantillas = {}
        self.matriz_precios = {}
        self.cargar_datos_iniciales()
    
    def cargar_datos_iniciales(self):
        """Carga los datos iniciales del sistema"""
        # Productos base identificados en la planilla
        self.productos = {
            "isodec": Producto(
                codigo="isodec",
                nombre="Isodec",
                espesor="100mm",
                relleno="EPS",
                color="Blanco",
                precio_base=Decimal('0'),  # Se actualizará con matriz de precios
                link_web="https://bmcuruguay.com.uy/productos/isodec",
                terminaciones_disponibles=["Gotero", "Hormigón"],
                anclajes_incluidos=True,
                traslado_incluido=False
            ),
            "poliestireno": Producto(
                codigo="poliestireno",
                nombre="Poliestireno Expandido",
                espesor="75mm",
                relleno="EPS",
                color="Blanco",
                precio_base=Decimal('0'),
                link_web="https://bmcuruguay.com.uy/productos/poliestireno",
                terminaciones_disponibles=["Gotero"],
                anclajes_incluidos=False,
                traslado_incluido=False
            ),
            "lana_roca": Producto(
                codigo="lana_roca",
                nombre="Lana de Roca",
                espesor="50mm",
                relleno="Lana de roca",
                color="Blanco",
                precio_base=Decimal('0'),
                link_web="https://bmcuruguay.com.uy/productos/lana-de-roca",
                terminaciones_disponibles=["Hormigón", "Aluminio"],
                anclajes_incluidos=False,
                traslado_incluido=False
            )
        }
        
        # Estados del sistema basados en la planilla
        self.estados = ["Pendiente", "Asignado", "Enviado", "Listo", "Confirmado"]
        
        # Asignaciones del sistema
        self.asignaciones = ["MA", "MO", "RA", "SPRT", "Ref."]
    
    def agregar_producto(self, producto: Producto):
        """Agrega un nuevo producto al sistema"""
        self.productos[producto.codigo] = producto
    
    def actualizar_precio_producto(self, codigo: str, precio: Decimal):
        """Actualiza el precio de un producto"""
        if codigo in self.productos:
            self.productos[codigo].precio_base = precio
    
    def calcular_precio_cotizacion(self, especificaciones: EspecificacionCotizacion) -> Tuple[Decimal, Decimal]:
        """
        Calcula el precio de una cotización basado en las especificaciones
        Retorna: (precio_total, precio_metro_cuadrado)
        """
        if especificaciones.producto not in self.productos:
            raise ValueError(f"Producto {especificaciones.producto} no encontrado")
        
        producto = self.productos[especificaciones.producto]
        
        # Calcular área en metros cuadrados
        area_metros_cuadrados = especificaciones.largo_metros * especificaciones.ancho_metros
        
        # Precio base por metro cuadrado
        precio_metro_cuadrado = producto.precio_base
        
        # Aplicar factores de ajuste según especificaciones
        factor_espesor = self._calcular_factor_espesor(especificaciones.espesor)
        factor_color = self._calcular_factor_color(especificaciones.color)
        factor_terminaciones = self._calcular_factor_terminaciones(
            especificaciones.termina_front,
            especificaciones.termina_sup,
            especificaciones.termina_lat_1,
            especificaciones.termina_lat_2
        )
        factor_anclajes = self._calcular_factor_anclajes(especificaciones.anclajes)
        factor_traslado = self._calcular_factor_traslado(especificaciones.traslado)
        
        # Calcular precio final
        precio_metro_cuadrado_ajustado = (
            precio_metro_cuadrado * 
            factor_espesor * 
            factor_color * 
            factor_terminaciones * 
            factor_anclajes * 
            factor_traslado
        )
        
        precio_total = precio_metro_cuadrado_ajustado * area_metros_cuadrados
        
        return precio_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), precio_metro_cuadrado_ajustado
    
    def _calcular_factor_espesor(self, espesor: str) -> Decimal:
        """Calcula factor de ajuste por espesor"""
        factores_espesor = {
            "50mm": Decimal('0.8'),
            "75mm": Decimal('0.9'),
            "100mm": Decimal('1.0'),
            "125mm": Decimal('1.1'),
            "150mm": Decimal('1.2')
        }
        return factores_espesor.get(espesor, Decimal('1.0'))
    
    def _calcular_factor_color(self, color: str) -> Decimal:
        """Calcula factor de ajuste por color"""
        factores_color = {
            "Blanco": Decimal('1.0'),
            "Gris": Decimal('1.05'),
            "Personalizado": Decimal('1.15')
        }
        return factores_color.get(color, Decimal('1.0'))
    
    def _calcular_factor_terminaciones(self, front: str, sup: str, lat1: str, lat2: str) -> Decimal:
        """Calcula factor de ajuste por terminaciones"""
        factor = Decimal('1.0')
        
        terminaciones = [front, sup, lat1, lat2]
        for term in terminaciones:
            if term == "Gotero":
                factor += Decimal('0.05')
            elif term == "Hormigón":
                factor += Decimal('0.1')
        
        return factor
    
    def _calcular_factor_anclajes(self, anclajes: str) -> Decimal:
        """Calcula factor de ajuste por anclajes"""
        if anclajes.lower() == "incluido":
            return Decimal('1.0')
        elif anclajes.lower() == "no incluido":
            return Decimal('0.95')
        return Decimal('1.0')
    
    def _calcular_factor_traslado(self, traslado: str) -> Decimal:
        """Calcula factor de ajuste por traslado"""
        if traslado.lower() == "incluido":
            return Decimal('1.0')
        elif traslado.lower() == "no incluido":
            return Decimal('0.9')
        return Decimal('1.0')
    
    def crear_cotizacion(self, cliente: Cliente, especificaciones: EspecificacionCotizacion, 
                        asignado_a: str = "", observaciones: str = "") -> Cotizacion:
        """Crea una nueva cotización"""
        
        # Generar ID único
        id_cotizacion = f"COT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calcular precios
        precio_total, precio_metro_cuadrado = self.calcular_precio_cotizacion(especificaciones)
        
        # Crear cotización
        cotizacion = Cotizacion(
            id=id_cotizacion,
            cliente=cliente,
            especificaciones=especificaciones,
            fecha=datetime.datetime.now(),
            estado="Pendiente",
            asignado_a=asignado_a,
            precio_total=precio_total,
            precio_metro_cuadrado=precio_metro_cuadrado,
            observaciones=observaciones
        )
        
        self.cotizaciones.append(cotizacion)
        return cotizacion
    
    def buscar_cotizaciones_por_cliente(self, nombre: str = "", telefono: str = "") -> List[Cotizacion]:
        """Busca cotizaciones por nombre o teléfono del cliente"""
        resultados = []
        
        for cotizacion in self.cotizaciones:
            if (nombre and nombre.lower() in cotizacion.cliente.nombre.lower()) or \
               (telefono and telefono in cotizacion.cliente.telefono):
                resultados.append(cotizacion)
        
        return resultados
    
    def buscar_cotizaciones_por_fecha(self, fecha_inicio: datetime.datetime, 
                                    fecha_fin: datetime.datetime) -> List[Cotizacion]:
        """Busca cotizaciones por rango de fechas"""
        resultados = []
        
        for cotizacion in self.cotizaciones:
            if fecha_inicio <= cotizacion.fecha <= fecha_fin:
                resultados.append(cotizacion)
        
        return resultados
    
    def actualizar_estado_cotizacion(self, id_cotizacion: str, nuevo_estado: str):
        """Actualiza el estado de una cotización"""
        for cotizacion in self.cotizaciones:
            if cotizacion.id == id_cotizacion:
                cotizacion.estado = nuevo_estado
                break
    
    def generar_reporte_cotizacion(self, cotizacion: Cotizacion) -> str:
        """Genera un reporte detallado de la cotización"""
        reporte = f"""
=== COTIZACIÓN BMC URUGUAY ===
ID: {cotizacion.id}
Fecha: {cotizacion.fecha.strftime('%d/%m/%Y %H:%M')}
Estado: {cotizacion.estado}
Asignado a: {cotizacion.asignado_a}

CLIENTE:
Nombre: {cotizacion.cliente.nombre}
Teléfono: {cotizacion.cliente.telefono}
Dirección: {cotizacion.cliente.direccion}
Zona: {cotizacion.cliente.zona}

PRODUCTO:
Código: {cotizacion.especificaciones.producto}
Espesor: {cotizacion.especificaciones.espesor}
Relleno: {cotizacion.especificaciones.relleno}
Color: {cotizacion.especificaciones.color}

DIMENSIONES:
Largo: {cotizacion.especificaciones.largo_metros} m
Ancho: {cotizacion.especificaciones.ancho_metros} m
Área total: {cotizacion.especificaciones.largo_metros * cotizacion.especificaciones.ancho_metros} m²

TERMINACIONES:
Frontal: {cotizacion.especificaciones.termina_front}
Superior: {cotizacion.especificaciones.termina_sup}
Lateral 1: {cotizacion.especificaciones.termina_lat_1}
Lateral 2: {cotizacion.especificaciones.termina_lat_2}

SERVICIOS:
Anclajes: {cotizacion.especificaciones.anclajes}
Traslado: {cotizacion.especificaciones.traslado}

PRECIOS:
Precio por m²: ${cotizacion.precio_metro_cuadrado}
Precio total: ${cotizacion.precio_total}

OBSERVACIONES:
{cotizacion.observaciones}
"""
        return reporte
    
    def exportar_cotizaciones_a_json(self, archivo: str):
        """Exporta todas las cotizaciones a un archivo JSON"""
        datos = []
        for cotizacion in self.cotizaciones:
            datos.append({
                'id': cotizacion.id,
                'cliente': asdict(cotizacion.cliente),
                'especificaciones': asdict(cotizacion.especificaciones),
                'fecha': cotizacion.fecha.isoformat(),
                'estado': cotizacion.estado,
                'asignado_a': cotizacion.asignado_a,
                'precio_total': float(cotizacion.precio_total),
                'precio_metro_cuadrado': float(cotizacion.precio_metro_cuadrado),
                'observaciones': cotizacion.observaciones
            })
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    
    def importar_cotizaciones_desde_json(self, archivo: str):
        """Importa cotizaciones desde un archivo JSON"""
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        for item in datos:
            cliente = Cliente(**item['cliente'])
            especificaciones = EspecificacionCotizacion(**item['especificaciones'])
            
            cotizacion = Cotizacion(
                id=item['id'],
                cliente=cliente,
                especificaciones=especificaciones,
                fecha=datetime.datetime.fromisoformat(item['fecha']),
                estado=item['estado'],
                asignado_a=item['asignado_a'],
                precio_total=Decimal(str(item['precio_total'])),
                precio_metro_cuadrado=Decimal(str(item['precio_metro_cuadrado'])),
                observaciones=item['observaciones']
            )
            
            self.cotizaciones.append(cotizacion)

def main():
    """Función principal para demostrar el uso del sistema"""
    sistema = SistemaCotizacionesBMC()
    
    # Configurar precios base (estos deberían venir de la matriz de precios)
    sistema.actualizar_precio_producto("isodec", Decimal('150.00'))
    
    # Ejemplo de creación de cotización
    cliente_ejemplo = Cliente(
        nombre="Gabriel",
        telefono="94 807 926",
        direccion="Cancha de Punta del Este",
        zona="Punta del Este"
    )
    
    especificaciones_ejemplo = EspecificacionCotizacion(
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
        traslado="Incluido",
        direccion="Punta del Este",
        forma="WhatsApp",
        origen="WA"
    )
    
    cotizacion = sistema.crear_cotizacion(
        cliente=cliente_ejemplo,
        especificaciones=especificaciones_ejemplo,
        asignado_a="MA",
        observaciones="Cliente interesado en instalación rápida"
    )
    
    print(sistema.generar_reporte_cotizacion(cotizacion))
    
    # Exportar cotizaciones
    sistema.exportar_cotizaciones_a_json("cotizaciones_bmc.json")

if __name__ == "__main__":
    main()
