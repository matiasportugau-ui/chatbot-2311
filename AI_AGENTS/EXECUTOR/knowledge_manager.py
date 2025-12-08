#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knowledge Manager
================

Gestiona la carga y acceso a:
- Base de conocimiento de productos (conocimiento_consolidado.json)
- Documentación del proyecto (archivos .md, .txt)
- Conversaciones históricas de MongoDB
- Indexación para búsqueda rápida
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
import os
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai not installed.")

# Add project root to path
_current_dir = Path(__file__).parent
_project_root = _current_dir.parent.parent
import sys
sys.path.insert(0, str(_project_root))

try:
    from mongodb_service import MongoDBService
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False


class KnowledgeManager:
    """Gestiona todo el conocimiento disponible para el bot"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or _project_root
        self.knowledge_cache = {}
        self.documentation_cache = {}
        self.conversations_cache = []
        
        if MONGODB_AVAILABLE:
            try:
                # Use factory function to ensure connection
                import mongodb_service
                self.mongodb_service = mongodb_service.get_mongodb_service()
            except Exception as e:
                print(f"[WARNING] MongoDB no disponible: {e}")
        
        # Initialize OpenAI for Embeddings
        self.openai_client = None
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = OpenAI()
            except Exception as e:
                 print(f"[WARNING] OpenAI client init failed: {e}")

    def generate_embedding(self, text: str) -> List[float]:
        """Generates embedding for given text using OpenAI"""
        if not self.openai_client:
            return []
        try:
            text = text.replace("\n", " ")
            return self.openai_client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding
        except Exception as e:
            print(f"[ERROR] Embedding generation failed: {e}")
            return []

    def buscar_informacion_relevante(self, query: str, max_results: int = 5) -> Dict:
        """Busca información relevante usando Vector Search (si disponible) o Fallback"""
        resultados = {
            'productos': [],
            'documentacion': [],
            'conversaciones': []
        }
        
        # 1. Try Vector Search first
        if self.mongodb_service and self.openai_client:
            try:
                vector = self.generate_embedding(query)
                if vector:
                    db = self.mongodb_service.get_database()
                    col = db["kb_interactions"] 
                    
                    # Atlas Vector Search Pipeline
                    pipeline = [
                        {
                            "$vectorSearch": {
                                "index": "vector_index",
                                "path": "embedding",
                                "queryVector": vector,
                                "numCandidates": max_results * 10,
                                "limit": max_results
                            }
                        },
                        {
                            "$project": {
                                "_id": 1,
                                "mensaje_cliente": 1,
                                "respuesta_agente": 1, # Normalizado name
                                "respuesta_bot": 1, # Legacy name
                                "intencion": 1,
                                "score": { "$meta": "vectorSearchScore" }
                            }
                        }
                    ]
                    
                    cursor = col.aggregate(pipeline)
                    semantic_results = list(cursor)
                    
                    if semantic_results:
                        # Normalize results
                        for res in semantic_results:
                            resultados['conversaciones'].append({
                                'mensaje_cliente': res.get('mensaje_cliente'),
                                'respuesta_bot': res.get('respuesta_agente') or res.get('respuesta_bot'),
                                'score': res.get('score')
                            })
                        # If we found good semantic matches, we might return early or mix with keyword search
                        # For now, let's keep keyword search as fallback/augmentation for products
            except Exception as e:
                print(f"[WARNING] Vector Search failed: {e}")

        # 2. Legacy Keyword Search (Fallback & Augmentation)
        query_lower = query.lower()
        
        # Buscar en productos
        productos = self.cargar_base_conocimiento_productos()
        for nombre, info in productos.items():
            if nombre.startswith('_'):
                continue
            contenido = json.dumps(info, default=str).lower()
            if any(palabra in contenido for palabra in query_lower.split()):
                # Avoid duplicates if found by vector search (though vector search populates 'conversaciones', not 'productos')
                resultados['productos'].append(info)
                if len(resultados['productos']) >= max_results:
                    break
        
        # Buscar en documentación
        doc = self.cargar_documentacion_proyecto()
        for doc_item in doc:
            contenido_lower = doc_item['contenido'].lower()
            if any(palabra in contenido_lower for palabra in query_lower.split()):
                resultados['documentacion'].append(doc_item)
                if len(resultados['documentacion']) >= max_results:
                    break
        
        # Buscar en conversaciones (si no hay resultados semánticos)
        # Note: Vector search adds to 'conversaciones'. If we strictly want fallback, we check if empty.
        # But for now, let's mix or ensure we have something.
        if not resultados['conversaciones']:
            conversaciones = self.cargar_conversaciones_historicas(limit=50)
            for conv in conversaciones:
                mensaje_lower = conv.get('mensaje_cliente', '').lower()
                if any(palabra in mensaje_lower for palabra in query_lower.split()):
                    resultados['conversaciones'].append(conv)
                    if len(resultados['conversaciones']) >= max_results:
                        break
                        
        return resultados
    
    def cargar_base_conocimiento_productos(self) -> Dict:
        """Carga la base de conocimiento de productos desde conocimiento_consolidado.json"""
        if 'productos' in self.knowledge_cache:
            return self.knowledge_cache['productos']
        
        kb_file = self.project_root / "conocimiento_consolidado.json"
        
        if not kb_file.exists():
            print(f"[WARNING] conocimiento_consolidado.json no encontrado en {kb_file}")
            return {}
        
        try:
            with open(kb_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraer información de productos
            productos_info = {}
            if 'conocimiento_productos' in data:
                for producto_data in data['conocimiento_productos']:
                    nombre = producto_data.get('nombre', '').lower()
                    if nombre:
                        productos_info[nombre] = producto_data
            
            # Agregar información adicional
            productos_info['_metadata'] = {
                'total_productos': len([p for p in productos_info.keys() if not p.startswith('_')]),
                'fecha_carga': datetime.now().isoformat(),
                'patrones_venta': data.get('patrones_venta', []),
                'metricas': data.get('metricas_evolucion', {})
            }
            
            self.knowledge_cache['productos'] = productos_info
            return productos_info
            
        except Exception as e:
            print(f"[ERROR] Error cargando base de conocimiento: {e}")
            return {}
    
    def cargar_documentacion_proyecto(self) -> List[Dict]:
        """Carga documentación del proyecto (archivos .md, .txt)"""
        if 'documentacion' in self.documentation_cache:
            return self.documentation_cache['documentacion']
        
        documentacion = []
        extensions = ['.md', '.txt', '.rst']
        
        # Directorios a escanear
        dirs_to_scan = [
            self.project_root,
            self.project_root / 'docs',
            self.project_root / 'AI_AGENTS',
        ]
        
        for directory in dirs_to_scan:
            if not directory.exists():
                continue
            
            for file_path in directory.rglob('*'):
                if file_path.suffix.lower() in extensions:
                    # Ignorar algunos archivos
                    if any(ignore in str(file_path) for ignore in ['node_modules', '.git', '__pycache__', '.cursor']):
                        continue
                    
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        # Extraer título si es markdown
                        titulo = file_path.stem
                        if content.startswith('#'):
                            primera_linea = content.split('\n')[0]
                            titulo = primera_linea.lstrip('#').strip()
                        
                        documentacion.append({
                            'titulo': titulo,
                            'archivo': str(file_path.relative_to(self.project_root)),
                            'contenido': content[:5000],  # Limitar tamaño
                            'tipo': file_path.suffix,
                            'ruta_completa': str(file_path)
                        })
                    except Exception as e:
                        print(f"[WARNING] Error leyendo {file_path}: {e}")
        
        self.documentation_cache['documentacion'] = documentacion
        return documentacion
    
    def cargar_conversaciones_historicas(self, limit: int = 100) -> List[Dict]:
        """Carga conversaciones históricas de MongoDB"""
        if self.conversations_cache:
            return self.conversations_cache[:limit]
        
        if not self.mongodb_service:
            return []
        
        try:
            # Obtener interacciones de MongoDB
            db = self.mongodb_service.get_database()
            collection = db.get_collection('InteraccionCliente')
            
            # Obtener conversaciones recientes y exitosas
            conversaciones = list(collection.find(
                {},
                sort=[('timestamp', -1)],
                limit=limit
            ))
            
            # Formatear conversaciones
            formatted = []
            for conv in conversaciones:
                formatted.append({
                    'id': str(conv.get('_id', '')),
                    'mensaje_cliente': conv.get('mensaje', ''),
                    'respuesta_bot': conv.get('respuesta', ''),
                    'intencion': conv.get('intencion', ''),
                    'confianza': conv.get('confianza', 0.0),
                    'timestamp': conv.get('timestamp', ''),
                    'completada': conv.get('cotizacion_completada', False)
                })
            
            self.conversations_cache = formatted
            return formatted[:limit]
            
        except Exception as e:
            print(f"[WARNING] Error cargando conversaciones históricas: {e}")
            return []
    
        # Continue with Product Search (Keyword based for now until products are also embedded)
        # Buscar en productos
        
        # Buscar en productos
        productos = self.cargar_base_conocimiento_productos()
        for nombre, info in productos.items():
            if nombre.startswith('_'):
                continue
            contenido = json.dumps(info, default=str).lower()
            if any(palabra in contenido for palabra in query_lower.split()):
                resultados['productos'].append(info)
                if len(resultados['productos']) >= max_results:
                    break
        
        # Buscar en documentación
        doc = self.cargar_documentacion_proyecto()
        for doc_item in doc:
            contenido_lower = doc_item['contenido'].lower()
            if any(palabra in contenido_lower for palabra in query_lower.split()):
                resultados['documentacion'].append(doc_item)
                if len(resultados['documentacion']) >= max_results:
                    break
        
        # Buscar en conversaciones
        conversaciones = self.cargar_conversaciones_historicas(limit=50)
        for conv in conversaciones:
            mensaje_lower = conv.get('mensaje_cliente', '').lower()
            if any(palabra in mensaje_lower for palabra in query_lower.split()):
                resultados['conversaciones'].append(conv)
                if len(resultados['conversaciones']) >= max_results:
                    break
        
        return resultados
    
    def obtener_ejemplos_few_shot(self, tema: str, cantidad: int = 3) -> List[Dict]:
        """Obtiene ejemplos de conversaciones exitosas similares al tema"""
        conversaciones = self.cargar_conversaciones_historicas(limit=100)
        
        # Filtrar conversaciones exitosas (alta confianza o completadas)
        exitosas = [
            c for c in conversaciones
            if c.get('confianza', 0) > 0.7 or c.get('completada', False)
        ]
        
        # Filtrar por tema (búsqueda simple por palabras clave)
        tema_lower = tema.lower()
        relevantes = []
        for conv in exitosas:
            mensaje = conv.get('mensaje_cliente', '').lower()
            if any(palabra in mensaje for palabra in tema_lower.split()):
                relevantes.append(conv)
        
        # Si no hay suficientes relevantes, usar las más exitosas
        if len(relevantes) < cantidad:
            relevantes = exitosas[:cantidad]
        
        return relevantes[:cantidad]
    
    def obtener_info_producto(self, nombre_producto: str) -> Optional[Dict]:
        """Obtiene información específica de un producto"""
        productos = self.cargar_base_conocimiento_productos()
        nombre_lower = nombre_producto.lower()
        
        # Buscar coincidencia exacta o parcial
        for nombre, info in productos.items():
            if nombre.startswith('_'):
                continue
            if nombre_lower in nombre or nombre in nombre_lower:
                return info
        
        return None
    
    def obtener_patrones_venta(self) -> List[Dict]:
        """Obtiene patrones de venta aprendidos"""
        productos = self.cargar_base_conocimiento_productos()
        return productos.get('_metadata', {}).get('patrones_venta', [])
    
    def formatear_contexto_productos(self) -> str:
        """Formatea información de productos para incluir en prompts"""
        productos = self.cargar_base_conocimiento_productos()
        
        contexto = "BASE DE CONOCIMIENTO DE PRODUCTOS:\n\n"
        
        for nombre, info in productos.items():
            if nombre.startswith('_'):
                continue
            
            contexto += f"**{nombre.upper()}**\n"
            if isinstance(info, dict):
                for key, value in info.items():
                    if key not in ['_id', 'id']:
                        contexto += f"- {key}: {value}\n"
            contexto += "\n"
        
        return contexto

