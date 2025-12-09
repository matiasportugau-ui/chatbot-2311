#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Training System
===============

Sistema de entrenamiento interno que:
- Carga documentación completa
- Encuentra conversaciones similares
- Extrae conocimiento de conversaciones
- Actualiza base de conocimiento automáticamente
- Genera ejemplos few-shot
- Analiza eficacia de respuestas
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

# Add project root to path
_current_dir = Path(__file__).parent
_project_root = _current_dir.parent.parent
import sys
sys.path.insert(0, str(_project_root))

from AI_AGENTS.EXECUTOR.knowledge_manager import KnowledgeManager

try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False


class TrainingSystem:
    """Sistema de entrenamiento y mejora continua"""
    
    def __init__(self, knowledge_manager: KnowledgeManager):
        self.km = knowledge_manager
        self.model_integrator = None
        
        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.model_integrator = get_model_integrator()
            except Exception as e:
                print(f"[WARNING] Model integrator no disponible: {e}")
        
        self.learning_history = []
        self.improvement_suggestions = []
    
    def cargar_documentacion_completa(self) -> Dict:
        """Carga toda la documentación disponible"""
        return {
            'productos': self.km.cargar_base_conocimiento_productos(),
            'documentacion': self.km.cargar_documentacion_proyecto(),
            'conversaciones': self.km.cargar_conversaciones_historicas(limit=200),
            'patrones_venta': self.km.obtener_patrones_venta()
        }
    
    def encontrar_conversaciones_similares(self, mensaje: str, n: int = 5) -> List[Dict]:
        """Encuentra conversaciones similares usando búsqueda semántica simple"""
        conversaciones = self.km.cargar_conversaciones_historicas(limit=100)
        
        mensaje_lower = mensaje.lower()
        palabras_clave = set(mensaje_lower.split())
        
        # Calcular similitud simple (coincidencia de palabras)
        scored = []
        for conv in conversaciones:
            mensaje_conv = conv.get('mensaje_cliente', '').lower()
            palabras_conv = set(mensaje_conv.split())
            
            # Calcular intersección
            interseccion = palabras_clave.intersection(palabras_conv)
            if interseccion:
                score = len(interseccion) / max(len(palabras_clave), 1)
                # Bonus por alta confianza o completada
                if conv.get('confianza', 0) > 0.8:
                    score *= 1.2
                if conv.get('completada', False):
                    score *= 1.3
                
                scored.append((score, conv))
        
        # Ordenar por score y retornar top n
        scored.sort(key=lambda x: x[0], reverse=True)
        return [conv for _, conv in scored[:n]]
    
    def extraer_conocimiento_conversacion(self, conversacion: Dict) -> Dict:
        """Extrae conocimiento útil de una conversación"""
        conocimiento = {
            'productos_mencionados': [],
            'patrones_consulta': [],
            'respuestas_efectivas': [],
            'informacion_nueva': {}
        }
        
        mensaje = conversacion.get('mensaje_cliente', '')
        respuesta = conversacion.get('respuesta_bot', '')
        
        # Extraer productos mencionados
        productos = self.km.cargar_base_conocimiento_productos()
        for nombre_producto in productos.keys():
            if nombre_producto.startswith('_'):
                continue
            if nombre_producto.lower() in mensaje.lower():
                conocimiento['productos_mencionados'].append(nombre_producto)
        
        # Si la conversación fue exitosa, guardar como ejemplo
        if conversacion.get('confianza', 0) > 0.8 or conversacion.get('completada', False):
            conocimiento['respuestas_efectivas'].append({
                'mensaje': mensaje,
                'respuesta': respuesta,
                'intencion': conversacion.get('intencion', ''),
                'confianza': conversacion.get('confianza', 0)
            })
        
        return conocimiento
    
    def actualizar_base_conocimiento(self, nuevo_conocimiento: Dict) -> bool:
        """Actualiza la base de conocimiento con nueva información"""
        kb_file = self.km.project_root / "conocimiento_consolidado.json"
        
        if not kb_file.exists():
            print(f"[ERROR] conocimiento_consolidado.json no encontrado")
            return False
        
        try:
            # Cargar conocimiento existente
            with open(kb_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Crear backup
            backup_file = kb_file.parent / f"conocimiento_consolidado.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Actualizar con nuevo conocimiento
            # Agregar nuevas interacciones
            if 'interacciones' not in data:
                data['interacciones'] = []
            
            nuevas_interacciones = nuevo_conocimiento.get('respuestas_efectivas', [])
            for interaccion in nuevas_interacciones:
                # Evitar duplicados
                existe = any(
                    i.get('mensaje') == interaccion.get('mensaje')
                    for i in data['interacciones']
                )
                if not existe:
                    data['interacciones'].append({
                        'mensaje': interaccion.get('mensaje'),
                        'respuesta': interaccion.get('respuesta'),
                        'intencion': interaccion.get('intencion'),
                        'confianza': interaccion.get('confianza'),
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Actualizar patrones de venta si hay nuevos
            if 'patrones_venta' not in data:
                data['patrones_venta'] = []
            
            # Guardar
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Limpiar caché
            self.km.knowledge_cache.clear()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error actualizando base de conocimiento: {e}")
            return False
    
    def generar_ejemplos_few_shot(self, tema: str) -> List[str]:
        """Genera ejemplos few-shot formateados para prompts"""
        conversaciones = self.encontrar_conversaciones_similares(tema, n=5)
        
        ejemplos = []
        for conv in conversaciones:
            ejemplo = f"Usuario: {conv.get('mensaje_cliente', '')}\n"
            ejemplo += f"Asistente: {conv.get('respuesta_bot', '')}\n"
            ejemplos.append(ejemplo)
        
        return ejemplos
    
    def procesar_conversacion_para_aprendizaje(self, conversacion: Dict) -> bool:
        """Procesa una conversación para extraer y guardar conocimiento"""
        # Solo procesar conversaciones exitosas
        if conversacion.get('confianza', 0) < 0.7 and not conversacion.get('completada', False):
            return False
        
        try:
            # Extraer conocimiento
            conocimiento = self.extraer_conocimiento_conversacion(conversacion)
            
            # Actualizar base de conocimiento
            if conocimiento.get('respuestas_efectivas'):
                return self.actualizar_base_conocimiento(conocimiento)
            
            return False
            
        except Exception as e:
            print(f"[ERROR] Error procesando conversación para aprendizaje: {e}")
            return False
    
    def analizar_eficacia_respuestas(self) -> Dict:
        """Analiza la eficacia de las respuestas del bot"""
        conversaciones = self.km.cargar_conversaciones_historicas(limit=100)
        
        if not conversaciones:
            return {
                'total_conversaciones': 0,
                'confianza_promedio': 0.0,
                'tasa_completadas': 0.0,
                'areas_mejora': []
            }
        
        total = len(conversaciones)
        confianza_total = sum(c.get('confianza', 0) for c in conversaciones)
        completadas = sum(1 for c in conversaciones if c.get('completada', False))
        
        # Identificar áreas de mejora
        baja_confianza = [c for c in conversaciones if c.get('confianza', 0) < 0.6]
        
        return {
            'total_conversaciones': total,
            'confianza_promedio': confianza_total / total if total > 0 else 0.0,
            'tasa_completadas': completadas / total if total > 0 else 0.0,
            'conversaciones_baja_confianza': len(baja_confianza),
            'areas_mejora': [
                'Mejorar respuestas con confianza < 0.6',
                f'Total de conversaciones analizadas: {total}'
            ]
        }
    
    def generar_insights_mejora(self) -> Dict:
        """Genera insights y sugerencias de mejora"""
        analisis = self.analizar_eficacia_respuestas()
        documentacion = self.km.cargar_documentacion_proyecto()
        
        insights = {
            'metricas': analisis,
            'sugerencias': [],
            'gaps_conocimiento': []
        }
        
        # Sugerencias basadas en análisis
        if analisis['confianza_promedio'] < 0.7:
            insights['sugerencias'].append(
                'Confianza promedio baja - considerar mejorar prompts con más contexto'
            )
        
        if analisis['tasa_completadas'] < 0.5:
            insights['sugerencias'].append(
                'Tasa de conversaciones completadas baja - mejorar flujo de cotización'
            )
        
        # Verificar gaps en documentación
        productos = self.km.cargar_base_conocimiento_productos()
        productos_nombres = [p for p in productos.keys() if not p.startswith('_')]
        
        # Buscar documentación sobre productos
        doc_productos = [d for d in documentacion if any(
            p in d['contenido'].lower() for p in productos_nombres
        )]
        
        if len(doc_productos) < len(productos_nombres):
            insights['gaps_conocimiento'].append(
                f'Falta documentación para {len(productos_nombres) - len(doc_productos)} productos'
            )
        
        return insights

