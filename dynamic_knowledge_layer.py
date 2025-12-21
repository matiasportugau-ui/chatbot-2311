#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamic Knowledge Layer System
================================

Sistema de capas de conocimiento priorizadas:
- Nivel 1 (Máxima prioridad): dynamic_knowledge.json (correcciones de agentes)
- Nivel 2 (Estático): Manuales y PDFs originales

Regla: Si hay contradicción, el Nivel 1 siempre gana.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib


@dataclass
class KnowledgeEntry:
    """Entrada de conocimiento corregido"""
    id: str
    topic: str  # ej: "precio_isodec_100mm", "tiempo_entrega"
    value: Any
    source: str  # 'agent_correction', 'manual', 'training'
    confidence: float
    corrected_by: Optional[str] = None  # ID del agente que corrigió
    timestamp: str = None
    replaces: Optional[str] = None  # ID de entrada que reemplaza
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ConflictLog:
    """Log de conflicto entre correcciones"""
    id: str
    topic: str
    old_value: Any
    new_value: Any
    old_source: str
    new_source: str
    timestamp: str
    resolved: bool = False
    resolution: Optional[str] = None


class DynamicKnowledgeLayer:
    """Gestor de conocimiento dinámico con priorización"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Inicializa el sistema de conocimiento dinámico
        
        Args:
            base_dir: Directorio base (por defecto: directorio del script)
        """
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.dynamic_file = self.base_dir / "dynamic_knowledge.json"
        self.conflicts_file = self.base_dir / "knowledge_conflicts.json"
        
        # Nivel 1: Conocimiento dinámico (máxima prioridad)
        self.dynamic_knowledge: Dict[str, KnowledgeEntry] = {}
        
        # Log de conflictos
        self.conflicts: List[ConflictLog] = []
        
        # Cargar conocimiento existente
        self.load()
    
    def load(self):
        """Carga conocimiento dinámico y conflictos desde archivos"""
        # Cargar conocimiento dinámico
        if self.dynamic_file.exists():
            try:
                with open(self.dynamic_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for entry_id, entry_data in data.items():
                        self.dynamic_knowledge[entry_id] = KnowledgeEntry(**entry_data)
                print(f"✅ Cargadas {len(self.dynamic_knowledge)} entradas de conocimiento dinámico")
            except Exception as e:
                print(f"⚠️  Error cargando conocimiento dinámico: {e}")
        
        # Cargar conflictos
        if self.conflicts_file.exists():
            try:
                with open(self.conflicts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conflicts = [ConflictLog(**c) for c in data]
                print(f"✅ Cargados {len(self.conflicts)} conflictos")
            except Exception as e:
                print(f"⚠️  Error cargando conflictos: {e}")
    
    def save(self):
        """Guarda conocimiento dinámico y conflictos"""
        # Guardar conocimiento dinámico
        try:
            data = {k: asdict(v) for k, v in self.dynamic_knowledge.items()}
            with open(self.dynamic_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Guardadas {len(self.dynamic_knowledge)} entradas de conocimiento dinámico")
        except Exception as e:
            print(f"⚠️  Error guardando conocimiento dinámico: {e}")
        
        # Guardar conflictos
        try:
            data = [asdict(c) for c in self.conflicts]
            with open(self.conflicts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Error guardando conflictos: {e}")
    
    def add_correction(self, topic: str, value: Any, corrected_by: str, 
                      metadata: Optional[Dict[str, Any]] = None) -> KnowledgeEntry:
        """
        Agrega una corrección de agente al conocimiento dinámico
        
        Args:
            topic: Tema de la corrección
            value: Nuevo valor
            corrected_by: ID del agente que corrige
            metadata: Metadatos adicionales
            
        Returns:
            KnowledgeEntry creada
        """
        # Generar ID único
        entry_id = self._generate_id(topic, value)
        
        # Verificar si existe entrada previa
        if topic in [e.topic for e in self.dynamic_knowledge.values()]:
            # Detectar conflicto
            existing_entries = [e for e in self.dynamic_knowledge.values() if e.topic == topic]
            for existing in existing_entries:
                if existing.value != value:
                    self._log_conflict(topic, existing.value, value, 
                                     existing.source, 'agent_correction')
        
        # Crear nueva entrada
        entry = KnowledgeEntry(
            id=entry_id,
            topic=topic,
            value=value,
            source='agent_correction',
            confidence=0.95,  # Alta confianza en correcciones de agentes
            corrected_by=corrected_by,
            metadata=metadata or {}
        )
        
        self.dynamic_knowledge[entry_id] = entry
        self.save()
        
        return entry
    
    def get_value(self, topic: str, default: Any = None, 
                 include_static: bool = True) -> Tuple[Any, float]:
        """
        Obtiene valor para un tema con priorización
        
        Args:
            topic: Tema a buscar
            default: Valor por defecto si no se encuentra
            include_static: Si buscar en conocimiento estático
            
        Returns:
            Tupla (valor, confianza)
        """
        # Nivel 1: Buscar en conocimiento dinámico (máxima prioridad)
        matching_entries = [e for e in self.dynamic_knowledge.values() if e.topic == topic]
        
        if matching_entries:
            # Ordenar por timestamp (más reciente primero)
            latest = sorted(matching_entries, 
                          key=lambda e: e.timestamp, 
                          reverse=True)[0]
            return (latest.value, latest.confidence)
        
        # Nivel 2: Conocimiento estático (si está habilitado)
        if include_static:
            # Aquí se integraría con el sistema de conocimiento estático
            # Por ahora retornamos el default
            pass
        
        return (default, 0.0)
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[KnowledgeEntry]:
        """
        Busca en el conocimiento dinámico
        
        Args:
            query: Consulta de búsqueda
            limit: Máximo de resultados
            
        Returns:
            Lista de entradas relevantes
        """
        query_lower = query.lower()
        matches = []
        
        for entry in self.dynamic_knowledge.values():
            # Buscar en topic y metadata
            if query_lower in entry.topic.lower():
                matches.append((entry, 1.0))
            elif 'keywords' in entry.metadata:
                keywords = entry.metadata.get('keywords', [])
                if any(query_lower in kw.lower() for kw in keywords):
                    matches.append((entry, 0.8))
        
        # Ordenar por relevancia y timestamp
        matches.sort(key=lambda x: (x[1], x[0].timestamp), reverse=True)
        
        return [m[0] for m in matches[:limit]]
    
    def _log_conflict(self, topic: str, old_value: Any, new_value: Any,
                     old_source: str, new_source: str):
        """Registra un conflicto de conocimiento"""
        conflict_id = self._generate_id(f"conflict_{topic}", str(datetime.now()))
        
        conflict = ConflictLog(
            id=conflict_id,
            topic=topic,
            old_value=old_value,
            new_value=new_value,
            old_source=old_source,
            new_source=new_source,
            timestamp=datetime.now().isoformat()
        )
        
        self.conflicts.append(conflict)
        print(f"⚠️  Conflicto detectado en '{topic}': {old_value} -> {new_value}")
    
    def get_unresolved_conflicts(self) -> List[ConflictLog]:
        """Obtiene conflictos sin resolver"""
        return [c for c in self.conflicts if not c.resolved]
    
    def resolve_conflict(self, conflict_id: str, resolution: str) -> bool:
        """
        Resuelve un conflicto
        
        Args:
            conflict_id: ID del conflicto
            resolution: Decisión ('accept_new', 'keep_old', 'merge')
            
        Returns:
            True si se resolvió exitosamente
        """
        for conflict in self.conflicts:
            if conflict.id == conflict_id:
                conflict.resolved = True
                conflict.resolution = resolution
                
                # Aplicar resolución
                if resolution == 'accept_new':
                    # Ya está en dynamic_knowledge por defecto
                    pass
                elif resolution == 'keep_old':
                    # Remover la entrada nueva
                    to_remove = [k for k, v in self.dynamic_knowledge.items() 
                               if v.topic == conflict.topic and v.value == conflict.new_value]
                    for key in to_remove:
                        del self.dynamic_knowledge[key]
                
                self.save()
                return True
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del conocimiento dinámico"""
        total_entries = len(self.dynamic_knowledge)
        by_source = {}
        by_agent = {}
        
        for entry in self.dynamic_knowledge.values():
            # Por fuente
            by_source[entry.source] = by_source.get(entry.source, 0) + 1
            
            # Por agente
            if entry.corrected_by:
                by_agent[entry.corrected_by] = by_agent.get(entry.corrected_by, 0) + 1
        
        return {
            'total_entries': total_entries,
            'by_source': by_source,
            'by_agent': by_agent,
            'total_conflicts': len(self.conflicts),
            'unresolved_conflicts': len(self.get_unresolved_conflicts())
        }
    
    def _generate_id(self, *parts) -> str:
        """Genera ID único para entradas"""
        combined = "_".join(str(p) for p in parts)
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    def export_for_training(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Exporta conocimiento dinámico para entrenamiento
        
        Args:
            output_file: Archivo de salida (opcional)
            
        Returns:
            Diccionario con datos de entrenamiento
        """
        training_data = {
            'corrections': [],
            'patterns': {},
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'total_entries': len(self.dynamic_knowledge),
                'statistics': self.get_statistics()
            }
        }
        
        # Agrupar correcciones por tema
        for entry in self.dynamic_knowledge.values():
            training_data['corrections'].append({
                'topic': entry.topic,
                'value': entry.value,
                'confidence': entry.confidence,
                'source': entry.source,
                'timestamp': entry.timestamp
            })
            
            # Detectar patrones
            if entry.topic not in training_data['patterns']:
                training_data['patterns'][entry.topic] = {
                    'count': 0,
                    'agents': set()
                }
            
            training_data['patterns'][entry.topic]['count'] += 1
            if entry.corrected_by:
                training_data['patterns'][entry.topic]['agents'].add(entry.corrected_by)
        
        # Convertir sets a listas para JSON
        for pattern in training_data['patterns'].values():
            pattern['agents'] = list(pattern['agents'])
        
        # Guardar si se especifica archivo
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Datos de entrenamiento exportados a {output_file}")
        
        return training_data
