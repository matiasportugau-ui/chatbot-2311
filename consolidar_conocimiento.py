#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Consolidación de Conocimiento
Consolida todos los archivos JSON de conocimiento en un único archivo
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Any, Set
from collections import defaultdict


class ConsolidadorConocimiento:
    """Consolida conocimiento de múltiples archivos"""
    
    def __init__(self):
        self.conocimiento_consolidado = {
            "interacciones": [],
            "patrones_venta": [],
            "conocimiento_productos": {},
            "metricas_evolucion": {},
            "insights_automaticos": [],
            "fecha_consolidacion": datetime.now().isoformat(),
            "archivos_consolidados": []
        }
        
        self.interacciones_unicas = {}  # id -> interaccion
        self.patrones_unicos = {}  # id -> patron
        self.productos_consolidados = defaultdict(dict)
    
    def encontrar_archivos(self) -> List[str]:
        """Encuentra todos los archivos de conocimiento"""
        patrones = [
            "*conocimiento*.json",
            "*base_conocimiento*.json"
        ]
        
        archivos = []
        for patron in patrones:
            archivos.extend(glob.glob(patron))
        
        # Filtrar archivos de configuración
        archivos_filtrados = []
        for archivo in archivos:
            nombre = os.path.basename(archivo).lower()
            if not any(excluir in nombre for excluir in ['config', 'result', 'test', 'reporte']):
                archivos_filtrados.append(archivo)
        
        return sorted(set(archivos_filtrados))
    
    def cargar_archivo(self, ruta_archivo: str) -> Dict[str, Any]:
        """Carga un archivo de conocimiento"""
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error cargando {ruta_archivo}: {e}")
            return {}
    
    def consolidar_interacciones(self, interacciones: List[Dict[str, Any]], archivo_origen: str):
        """Consolida interacciones evitando duplicados"""
        for inter in interacciones:
            if not isinstance(inter, dict):
                continue
            
            inter_id = inter.get("id")
            if not inter_id:
                # Generar ID único basado en contenido
                contenido = f"{inter.get('mensaje_cliente', '')}{inter.get('timestamp', '')}"
                inter_id = f"consolidated_{hash(contenido)}"
                inter["id"] = inter_id
            
            # Si ya existe, mantener el más reciente
            if inter_id in self.interacciones_unicas:
                existente = self.interacciones_unicas[inter_id]
                timestamp_existente = existente.get("timestamp", "")
                timestamp_nuevo = inter.get("timestamp", "")
                
                if timestamp_nuevo > timestamp_existente:
                    inter["archivo_origen"] = archivo_origen
                    self.interacciones_unicas[inter_id] = inter
            else:
                inter["archivo_origen"] = archivo_origen
                self.interacciones_unicas[inter_id] = inter
    
    def consolidar_patrones(self, patrones: List[Dict[str, Any]], archivo_origen: str):
        """Consolida patrones de venta evitando duplicados"""
        for patron in patrones:
            if not isinstance(patron, dict):
                continue
            
            patron_id = patron.get("id")
            if not patron_id:
                # Generar ID único basado en nombre
                nombre = patron.get("nombre", "")
                patron_id = f"patron_{hash(nombre)}"
                patron["id"] = patron_id
            
            # Si ya existe, combinar información
            if patron_id in self.patrones_unicos:
                existente = self.patrones_unicos[patron_id]
                # Actualizar frecuencia sumando
                existente["frecuencia"] = existente.get("frecuencia", 0) + patron.get("frecuencia", 0)
                # Actualizar fecha si es más reciente
                fecha_existente = existente.get("fecha_ultima_actualizacion", "")
                fecha_nuevo = patron.get("fecha_ultima_actualizacion", "")
                if fecha_nuevo > fecha_existente:
                    existente["fecha_ultima_actualizacion"] = fecha_nuevo
                    # Actualizar otros campos si son más recientes
                    for key in ["descripcion", "estrategia_recomendada", "factores_clave"]:
                        if key in patron and patron[key]:
                            existente[key] = patron[key]
            else:
                patron["archivo_origen"] = archivo_origen
                self.patrones_unicos[patron_id] = patron
    
    def consolidar_productos(self, productos: Dict[str, Any], archivo_origen: str):
        """Consolida conocimiento de productos"""
        for producto_id, conocimiento in productos.items():
            if not isinstance(conocimiento, dict):
                continue
            
            # Combinar características
            if "caracteristicas_aprendidas" in conocimiento:
                if producto_id not in self.productos_consolidados:
                    self.productos_consolidados[producto_id] = conocimiento.copy()
                else:
                    # Combinar características aprendidas
                    existente = self.productos_consolidados[producto_id]
                    aprendidas_existente = existente.get("caracteristicas_aprendidas", {})
                    aprendidas_nuevo = conocimiento.get("caracteristicas_aprendidas", {})
                    aprendidas_existente.update(aprendidas_nuevo)
                    existente["caracteristicas_aprendidas"] = aprendidas_existente
            
            # Combinar objeciones comunes
            if "objeciones_comunes" in conocimiento:
                if producto_id not in self.productos_consolidados:
                    self.productos_consolidados[producto_id] = conocimiento.copy()
                else:
                    existente = self.productos_consolidados[producto_id]
                    objeciones_existente = set(existente.get("objeciones_comunes", []))
                    objeciones_nuevo = set(conocimiento.get("objeciones_comunes", []))
                    existente["objeciones_comunes"] = list(objeciones_existente | objeciones_nuevo)
            
            # Combinar respuestas efectivas
            if "respuestas_efectivas" in conocimiento:
                if producto_id not in self.productos_consolidados:
                    self.productos_consolidados[producto_id] = conocimiento.copy()
                else:
                    existente = self.productos_consolidados[producto_id]
                    respuestas_existente = set(existente.get("respuestas_efectivas", []))
                    respuestas_nuevo = set(conocimiento.get("respuestas_efectivas", []))
                    existente["respuestas_efectivas"] = list(respuestas_existente | respuestas_nuevo)
            
            # Si no existe, agregarlo
            if producto_id not in self.productos_consolidados:
                conocimiento["archivo_origen"] = archivo_origen
                self.productos_consolidados[producto_id] = conocimiento
    
    def consolidar_insights(self, insights: List[Any], archivo_origen: str):
        """Consolida insights automáticos"""
        for insight in insights:
            if isinstance(insight, dict):
                insight["archivo_origen"] = archivo_origen
            self.conocimiento_consolidado["insights_automaticos"].append(insight)
    
    def consolidar_todos(self) -> Dict[str, Any]:
        """Consolida todos los archivos de conocimiento"""
        archivos = self.encontrar_archivos()
        
        if not archivos:
            print("⚠️  No se encontraron archivos de conocimiento para consolidar")
            return self.conocimiento_consolidado
        
        print(f"📚 Consolidando {len(archivos)} archivos de conocimiento...")
        
        for archivo in archivos:
            print(f"  Procesando: {os.path.basename(archivo)}")
            datos = self.cargar_archivo(archivo)
            
            if not datos:
                continue
            
            self.conocimiento_consolidado["archivos_consolidados"].append(archivo)
            
            # Consolidar interacciones
            if "interacciones" in datos:
                self.consolidar_interacciones(datos["interacciones"], archivo)
            
            # Consolidar patrones
            if "patrones_venta" in datos:
                self.consolidar_patrones(datos["patrones_venta"], archivo)
            
            # Consolidar productos
            if "conocimiento_productos" in datos:
                self.consolidar_productos(datos["conocimiento_productos"], archivo)
            
            # Consolidar insights
            if "insights_automaticos" in datos:
                self.consolidar_insights(datos["insights_automaticos"], archivo)
            
            # Consolidar métricas (usar las más recientes)
            if "metricas_evolucion" in datos:
                fecha_actual = self.conocimiento_consolidado.get("metricas_evolucion", {}).get("fecha_actualizacion", "")
                fecha_nuevo = datos.get("fecha_exportacion", "")
                if fecha_nuevo > fecha_actual:
                    self.conocimiento_consolidado["metricas_evolucion"] = datos["metricas_evolucion"]
        
        # Agregar datos consolidados al resultado final
        self.conocimiento_consolidado["interacciones"] = list(self.interacciones_unicas.values())
        self.conocimiento_consolidado["patrones_venta"] = list(self.patrones_unicos.values())
        self.conocimiento_consolidado["conocimiento_productos"] = dict(self.productos_consolidados)
        
        return self.conocimiento_consolidado
    
    def validar_integridad(self) -> Dict[str, Any]:
        """Valida la integridad de los datos consolidados"""
        validacion = {
            "valido": True,
            "errores": [],
            "advertencias": [],
            "estadisticas": {}
        }
        
        # Validar interacciones
        interacciones = self.conocimiento_consolidado.get("interacciones", [])
        validacion["estadisticas"]["total_interacciones"] = len(interacciones)
        
        interacciones_sin_id = [i for i in interacciones if not i.get("id")]
        if interacciones_sin_id:
            validacion["advertencias"].append(f"{len(interacciones_sin_id)} interacciones sin ID")
        
        # Validar patrones
        patrones = self.conocimiento_consolidado.get("patrones_venta", [])
        validacion["estadisticas"]["total_patrones"] = len(patrones)
        
        # Validar productos
        productos = self.conocimiento_consolidado.get("conocimiento_productos", {})
        validacion["estadisticas"]["total_productos"] = len(productos)
        
        return validacion
    
    def guardar(self, archivo_salida: str = "conocimiento_consolidado.json"):
        """Guarda el conocimiento consolidado"""
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(self.conocimiento_consolidado, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ Conocimiento consolidado guardado en: {archivo_salida}")


def main():
    """Función principal"""
    print("🔄 Iniciando consolidación de conocimiento...")
    print("")
    
    consolidador = ConsolidadorConocimiento()
    consolidador.consolidar_todos()
    
    # Validar
    validacion = consolidador.validar_integridad()
    
    print("\n📊 Estadísticas de consolidación:")
    print(f"  Interacciones: {validacion['estadisticas']['total_interacciones']}")
    print(f"  Patrones de venta: {validacion['estadisticas']['total_patrones']}")
    print(f"  Productos: {validacion['estadisticas']['total_productos']}")
    print(f"  Archivos consolidados: {len(consolidador.conocimiento_consolidado['archivos_consolidados'])}")
    
    if validacion["advertencias"]:
        print("\n⚠️  Advertencias:")
        for adv in validacion["advertencias"]:
            print(f"  - {adv}")
    
    # Guardar
    consolidador.guardar()
    
    print("\n✅ Consolidación completada")


if __name__ == "__main__":
    main()

