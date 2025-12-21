#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark System for Multimodal Training
=========================================

Sistema de métricas y benchmarking:
- Tasa de Aprendizaje (correcciones integradas)
- Uso de conocimiento dinámico vs estático
- Efectividad de respuestas
- Performance multimodal
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import statistics


@dataclass
class BenchmarkMetrics:
    """Métricas de benchmark"""
    timestamp: str
    total_interactions: int
    dynamic_knowledge_usage: int  # Veces que se usó conocimiento dinámico
    static_knowledge_usage: int  # Veces que se usó conocimiento estático
    learning_rate: float  # Correcciones / Total interacciones
    total_corrections: int
    average_confidence: float
    multimodal_stats: Dict[str, int]  # Por tipo de entrada
    response_quality: Dict[str, float]
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class BenchmarkSystem:
    """Sistema de benchmarking y métricas"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Inicializa el sistema de benchmarking
        
        Args:
            base_dir: Directorio base
        """
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.metrics_file = self.base_dir / "benchmark_metrics.json"
        self.history_file = self.base_dir / "benchmark_history.json"
        
        # Métricas actuales
        self.current_metrics = {
            'interactions': [],
            'corrections': [],
            'knowledge_lookups': [],
            'multimodal_inputs': []
        }
        
        # Historial de benchmarks
        self.history: List[BenchmarkMetrics] = []
        
        # Cargar historial existente
        self._load_history()
    
    def _load_history(self):
        """Carga historial de benchmarks"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = [BenchmarkMetrics(**m) for m in data]
                print(f"✅ Cargados {len(self.history)} benchmarks históricos")
            except Exception as e:
                print(f"⚠️  Error cargando historial: {e}")
    
    def record_interaction(self, interaction_data: Dict[str, Any]):
        """
        Registra una interacción
        
        Args:
            interaction_data: Datos de la interacción
        """
        interaction_data['timestamp'] = datetime.now().isoformat()
        self.current_metrics['interactions'].append(interaction_data)
    
    def record_correction(self, correction_data: Dict[str, Any]):
        """
        Registra una corrección
        
        Args:
            correction_data: Datos de la corrección
        """
        correction_data['timestamp'] = datetime.now().isoformat()
        self.current_metrics['corrections'].append(correction_data)
    
    def record_knowledge_lookup(self, lookup_type: str, 
                               found_in_dynamic: bool,
                               confidence: float):
        """
        Registra una búsqueda de conocimiento
        
        Args:
            lookup_type: Tipo de búsqueda
            found_in_dynamic: Si se encontró en conocimiento dinámico
            confidence: Nivel de confianza
        """
        self.current_metrics['knowledge_lookups'].append({
            'timestamp': datetime.now().isoformat(),
            'type': lookup_type,
            'found_in_dynamic': found_in_dynamic,
            'confidence': confidence
        })
    
    def record_multimodal_input(self, input_type: str, 
                               processing_success: bool,
                               confidence: float):
        """
        Registra entrada multimodal
        
        Args:
            input_type: Tipo de entrada ('audio', 'image', 'document')
            processing_success: Si el procesamiento fue exitoso
            confidence: Nivel de confianza
        """
        self.current_metrics['multimodal_inputs'].append({
            'timestamp': datetime.now().isoformat(),
            'type': input_type,
            'success': processing_success,
            'confidence': confidence
        })
    
    def calculate_metrics(self, period: Optional[str] = None) -> BenchmarkMetrics:
        """
        Calcula métricas del período
        
        Args:
            period: Período ('day', 'week', 'month', None para todo)
            
        Returns:
            BenchmarkMetrics calculadas
        """
        # Filtrar por período si se especifica
        interactions = self._filter_by_period(
            self.current_metrics['interactions'], period
        )
        corrections = self._filter_by_period(
            self.current_metrics['corrections'], period
        )
        lookups = self._filter_by_period(
            self.current_metrics['knowledge_lookups'], period
        )
        multimodal = self._filter_by_period(
            self.current_metrics['multimodal_inputs'], period
        )
        
        # Calcular estadísticas
        total_interactions = len(interactions)
        total_corrections = len(corrections)
        
        # Uso de conocimiento dinámico vs estático
        dynamic_usage = sum(1 for l in lookups if l.get('found_in_dynamic', False))
        static_usage = len(lookups) - dynamic_usage
        
        # Tasa de aprendizaje
        learning_rate = (
            total_corrections / total_interactions 
            if total_interactions > 0 else 0.0
        )
        
        # Confianza promedio
        confidences = [l.get('confidence', 0) for l in lookups if 'confidence' in l]
        avg_confidence = (
            statistics.mean(confidences) 
            if confidences else 0.0
        )
        
        # Estadísticas multimodales
        multimodal_stats = {}
        for m in multimodal:
            input_type = m.get('type', 'unknown')
            multimodal_stats[input_type] = multimodal_stats.get(input_type, 0) + 1
        
        # Calidad de respuestas (basado en correcciones)
        response_quality = {
            'accuracy_rate': 1.0 - learning_rate if learning_rate < 1.0 else 0.0,
            'avg_confidence': avg_confidence,
            'dynamic_knowledge_preference': (
                dynamic_usage / len(lookups) if lookups else 0.0
            )
        }
        
        return BenchmarkMetrics(
            timestamp=datetime.now().isoformat(),
            total_interactions=total_interactions,
            dynamic_knowledge_usage=dynamic_usage,
            static_knowledge_usage=static_usage,
            learning_rate=learning_rate,
            total_corrections=total_corrections,
            average_confidence=avg_confidence,
            multimodal_stats=multimodal_stats,
            response_quality=response_quality
        )
    
    def _filter_by_period(self, data: List[Dict[str, Any]], 
                         period: Optional[str]) -> List[Dict[str, Any]]:
        """Filtra datos por período"""
        if not period or not data:
            return data
        
        now = datetime.now()
        cutoff = {
            'day': now - timedelta(days=1),
            'week': now - timedelta(weeks=1),
            'month': now - timedelta(days=30)
        }.get(period, now - timedelta(days=365))
        
        return [
            d for d in data 
            if datetime.fromisoformat(d['timestamp']) >= cutoff
        ]
    
    def save_benchmark(self, metrics: Optional[BenchmarkMetrics] = None):
        """
        Guarda benchmark actual
        
        Args:
            metrics: Métricas a guardar (calcula si no se proveen)
        """
        if metrics is None:
            metrics = self.calculate_metrics()
        
        # Crear directorio si no existe
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Agregar al historial
        self.history.append(metrics)
        
        # Guardar historial
        try:
            data = [asdict(m) for m in self.history]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Benchmark guardado: {metrics.timestamp}")
        except Exception as e:
            print(f"⚠️  Error guardando benchmark: {e}")
        
        # Guardar métricas actuales también
        self._save_current_metrics()
    
    def _save_current_metrics(self):
        """Guarda métricas actuales"""
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_metrics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Error guardando métricas: {e}")
    
    def get_trend_analysis(self, metric_name: str, 
                          periods: int = 7) -> Dict[str, Any]:
        """
        Analiza tendencias de una métrica
        
        Args:
            metric_name: Nombre de la métrica
            periods: Número de períodos a analizar
            
        Returns:
            Análisis de tendencia
        """
        if len(self.history) < 2:
            return {
                'trend': 'insufficient_data',
                'message': 'Se necesitan al menos 2 benchmarks'
            }
        
        # Obtener últimos N períodos
        recent = self.history[-periods:]
        
        # Extraer valores de la métrica
        values = []
        for benchmark in recent:
            if metric_name in asdict(benchmark):
                values.append(getattr(benchmark, metric_name))
            elif metric_name in benchmark.response_quality:
                values.append(benchmark.response_quality[metric_name])
        
        if not values:
            return {
                'trend': 'metric_not_found',
                'message': f'Métrica {metric_name} no encontrada'
            }
        
        # Calcular tendencia
        if len(values) >= 2:
            # Tendencia simple: comparar primero y último
            first = values[0] if isinstance(values[0], (int, float)) else 0
            last = values[-1] if isinstance(values[-1], (int, float)) else 0
            
            change = last - first
            percent_change = (change / first * 100) if first != 0 else 0
            
            trend_direction = 'improving' if change > 0 else (
                'declining' if change < 0 else 'stable'
            )
            
            return {
                'trend': trend_direction,
                'change': change,
                'percent_change': percent_change,
                'current_value': last,
                'previous_value': first,
                'values': values
            }
        
        return {
            'trend': 'insufficient_data',
            'values': values
        }
    
    def generate_report(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Genera reporte completo de benchmarking
        
        Args:
            output_file: Archivo de salida (opcional)
            
        Returns:
            Reporte completo
        """
        current = self.calculate_metrics()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'current_metrics': asdict(current),
            'trends': {
                'learning_rate': self.get_trend_analysis('learning_rate'),
                'average_confidence': self.get_trend_analysis('average_confidence'),
                'dynamic_knowledge_usage': self.get_trend_analysis('dynamic_knowledge_usage')
            },
            'summary': {
                'total_benchmarks': len(self.history),
                'tracking_since': (
                    self.history[0].timestamp 
                    if self.history else 'N/A'
                ),
                'key_insights': self._generate_insights(current)
            }
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✅ Reporte guardado en {output_file}")
        
        return report
    
    def _generate_insights(self, metrics: BenchmarkMetrics) -> List[str]:
        """Genera insights basados en métricas"""
        insights = []
        
        # Insight sobre tasa de aprendizaje
        if metrics.learning_rate > 0.2:
            insights.append(
                f"⚠️ Alta tasa de aprendizaje ({metrics.learning_rate:.1%}): "
                "El sistema está recibiendo muchas correcciones. "
                "Considera revisar las respuestas base."
            )
        elif metrics.learning_rate < 0.05:
            insights.append(
                f"✅ Baja tasa de aprendizaje ({metrics.learning_rate:.1%}): "
                "Las respuestas son generalmente correctas."
            )
        
        # Insight sobre uso de conocimiento dinámico
        total_lookups = metrics.dynamic_knowledge_usage + metrics.static_knowledge_usage
        if total_lookups > 0:
            dynamic_ratio = metrics.dynamic_knowledge_usage / total_lookups
            if dynamic_ratio > 0.5:
                insights.append(
                    f"📈 Alto uso de conocimiento dinámico ({dynamic_ratio:.1%}): "
                    "El sistema está aprendiendo efectivamente de las correcciones."
                )
        
        # Insight sobre confianza
        if metrics.average_confidence < 0.7:
            insights.append(
                f"⚠️ Confianza promedio baja ({metrics.average_confidence:.1%}): "
                "Muchas respuestas requieren validación."
            )
        
        # Insight sobre multimodal
        if metrics.multimodal_stats:
            total_multimodal = sum(metrics.multimodal_stats.values())
            insights.append(
                f"🎯 Procesamiento multimodal: {total_multimodal} entradas "
                f"({', '.join(f'{k}:{v}' for k,v in metrics.multimodal_stats.items())})"
            )
        
        return insights
    
    def reset_current_metrics(self):
        """Resetea métricas actuales (después de guardar benchmark)"""
        self.current_metrics = {
            'interactions': [],
            'corrections': [],
            'knowledge_lookups': [],
            'multimodal_inputs': []
        }
        print("🔄 Métricas actuales reseteadas")


# Ejemplo de uso
if __name__ == "__main__":
    # Crear sistema de benchmark
    benchmark = BenchmarkSystem()
    
    # Simular algunas métricas
    benchmark.record_interaction({'type': 'query', 'success': True})
    benchmark.record_knowledge_lookup('price_check', found_in_dynamic=True, confidence=0.95)
    benchmark.record_multimodal_input('audio', True, 0.9)
    
    # Calcular y mostrar métricas
    metrics = benchmark.calculate_metrics()
    print(f"\n📊 Métricas Actuales:")
    print(f"  - Interacciones: {metrics.total_interactions}")
    print(f"  - Tasa de Aprendizaje: {metrics.learning_rate:.1%}")
    print(f"  - Uso Dinámico/Estático: {metrics.dynamic_knowledge_usage}/{metrics.static_knowledge_usage}")
    print(f"  - Confianza Promedio: {metrics.average_confidence:.1%}")
    
    # Guardar benchmark
    benchmark.save_benchmark(metrics)
    
    # Generar reporte
    report = benchmark.generate_report()
    print(f"\n📋 Insights:")
    for insight in report['summary']['key_insights']:
        print(f"  {insight}")
