#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Storage Cleanup Assistant
=========================

Asistente de IA que analiza el uso de almacenamiento local y propone
sugerencias de limpieza basadas en análisis inteligente.

Usa recursos de prompt engineering para generar recomendaciones contextuales.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import subprocess


class StorageAnalyzer:
    """Analiza el uso de almacenamiento en el workspace"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root or os.getcwd()).resolve()
        self.analysis_results = {}
        
    def get_file_size(self, file_path: Path) -> int:
        """Obtiene el tamaño de un archivo"""
        try:
            return file_path.stat().st_size
        except:
            return 0
    
    def get_directory_size(self, dir_path: Path) -> int:
        """Calcula el tamaño total de un directorio"""
        total = 0
        try:
            for item in dir_path.rglob('*'):
                if item.is_file():
                    total += self.get_file_size(item)
        except:
            pass
        return total
    
    def analyze_storage(self) -> Dict:
        """Analiza el uso de almacenamiento completo"""
        print("🔍 Analizando uso de almacenamiento...")
        
        results = {
            'total_size': 0,
            'file_count': 0,
            'directory_count': 0,
            'largest_files': [],
            'largest_directories': [],
            'file_types': defaultdict(int),
            'file_types_size': defaultdict(int),
            'old_files': [],
            'duplicate_candidates': [],
            'temporary_files': [],
            'cache_directories': [],
            'node_modules': [],
            'backups': [],
            'git_repos': [],
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Analizar todo el workspace
        for item in self.workspace_root.rglob('*'):
            try:
                if item.is_file():
                    results['file_count'] += 1
                    size = self.get_file_size(item)
                    results['total_size'] += size
                    
                    # Analizar por tipo de archivo
                    ext = item.suffix.lower()
                    results['file_types'][ext] += 1
                    results['file_types_size'][ext] += size
                    
                    # Archivos grandes (>10MB)
                    if size > 10 * 1024 * 1024:
                        results['largest_files'].append({
                            'path': str(item.relative_to(self.workspace_root)),
                            'size': size,
                            'size_mb': size / 1024 / 1024
                        })
                    
                    # Archivos antiguos (>90 días sin modificar)
                    try:
                        mtime = datetime.fromtimestamp(item.stat().st_mtime)
                        if mtime < datetime.now() - timedelta(days=90):
                            results['old_files'].append({
                                'path': str(item.relative_to(self.workspace_root)),
                                'size': size,
                                'last_modified': mtime.isoformat(),
                                'days_old': (datetime.now() - mtime).days
                            })
                    except:
                        pass
                    
                    # Archivos temporales
                    if any(item.name.endswith(ext) for ext in ['.tmp', '.bak', '.log', '.cache']):
                        results['temporary_files'].append({
                            'path': str(item.relative_to(self.workspace_root)),
                            'size': size
                        })
                
                elif item.is_dir():
                    results['directory_count'] += 1
                    
                    # Directorios conocidos grandes
                    dir_name = item.name.lower()
                    if dir_name in ['node_modules', '__pycache__', '.git', 'backups', '.next', '.mypy_cache']:
                        dir_size = self.get_directory_size(item)
                        if dir_name == 'node_modules':
                            results['node_modules'].append({
                                'path': str(item.relative_to(self.workspace_root)),
                                'size': dir_size,
                                'size_mb': dir_size / 1024 / 1024
                            })
                        elif dir_name == 'backups':
                            results['backups'].append({
                                'path': str(item.relative_to(self.workspace_root)),
                                'size': dir_size,
                                'size_mb': dir_size / 1024 / 1024
                            })
                        elif dir_name == '.git':
                            results['git_repos'].append({
                                'path': str(item.relative_to(self.workspace_root)),
                                'size': dir_size,
                                'size_mb': dir_size / 1024 / 1024
                            })
                        else:
                            results['cache_directories'].append({
                                'path': str(item.relative_to(self.workspace_root)),
                                'name': dir_name,
                                'size': dir_size,
                                'size_mb': dir_size / 1024 / 1024
                            })
            except (PermissionError, OSError):
                continue
        
        # Ordenar resultados
        results['largest_files'].sort(key=lambda x: x['size'], reverse=True)
        results['largest_directories'] = sorted(
            results['node_modules'] + results['backups'] + results['cache_directories'],
            key=lambda x: x['size'],
            reverse=True
        )
        results['old_files'].sort(key=lambda x: x['days_old'], reverse=True)
        
        self.analysis_results = results
        return results


class CleanupRecommendationEngine:
    """Genera recomendaciones de limpieza usando IA y análisis"""
    
    def __init__(self, analyzer: StorageAnalyzer):
        self.analyzer = analyzer
        self.recommendations = []
    
    def generate_recommendations(self) -> List[Dict]:
        """Genera recomendaciones basadas en el análisis"""
        results = self.analyzer.analysis_results
        
        recommendations = []
        
        # 1. Archivos grandes
        if results['largest_files']:
            large_files = results['largest_files'][:10]
            total_large_size = sum(f['size'] for f in large_files)
            recommendations.append({
                'category': 'Large Files',
                'priority': 'high',
                'potential_savings_mb': total_large_size / 1024 / 1024,
                'description': f'Found {len(results["largest_files"])} files larger than 10MB',
                'suggestions': [
                    f"Review {len(large_files)} largest files ({total_large_size / 1024 / 1024:.2f} MB total)",
                    "Consider compressing large data files",
                    "Move large files to external storage if not frequently accessed",
                    "Check if large files are necessary for the project"
                ],
                'items': large_files[:5]  # Top 5
            })
        
        # 2. node_modules
        if results['node_modules']:
            total_size = sum(nm['size'] for nm in results['node_modules'])
            recommendations.append({
                'category': 'Node Modules',
                'priority': 'high',
                'potential_savings_mb': total_size / 1024 / 1024,
                'description': f'Found {len(results["node_modules"])} node_modules directories',
                'suggestions': [
                    f"node_modules can be regenerated - potential savings: {total_size / 1024 / 1024:.2f} MB",
                    "Add node_modules to .gitignore if not already",
                    "Consider using .npmrc to reduce cache size",
                    "Run 'npm prune' to remove unused packages"
                ],
                'items': results['node_modules']
            })
        
        # 3. Backups
        if results['backups']:
            total_size = sum(b['size'] for b in results['backups'])
            recommendations.append({
                'category': 'Backups',
                'priority': 'medium',
                'potential_savings_mb': total_size / 1024 / 1024,
                'description': f'Found {len(results["backups"])} backup directories',
                'suggestions': [
                    f"Review old backups - potential savings: {total_size / 1024 / 1024:.2f} MB",
                    "Keep only recent backups (last 7-30 days)",
                    "Compress old backups before deleting",
                    "Consider moving backups to external storage"
                ],
                'items': results['backups']
            })
        
        # 4. Cache directories
        if results['cache_directories']:
            total_size = sum(c['size'] for c in results['cache_directories'])
            recommendations.append({
                'category': 'Cache Directories',
                'priority': 'high',
                'potential_savings_mb': total_size / 1024 / 1024,
                'description': f'Found {len(results["cache_directories"])} cache directories',
                'suggestions': [
                    f"Cache directories can be safely deleted - potential savings: {total_size / 1024 / 1024:.2f} MB",
                    "Add cache directories to .gitignore",
                    "Caches will be regenerated automatically when needed",
                    "Consider periodic cleanup of cache directories"
                ],
                'items': results['cache_directories']
            })
        
        # 5. Archivos antiguos
        if results['old_files']:
            old_files = [f for f in results['old_files'] if f['days_old'] > 180][:20]
            total_size = sum(f['size'] for f in old_files)
            if old_files:
                recommendations.append({
                    'category': 'Old Files',
                    'priority': 'low',
                    'potential_savings_mb': total_size / 1024 / 1024,
                    'description': f'Found {len(results["old_files"])} files not modified in 90+ days',
                    'suggestions': [
                        f"Review {len(old_files)} files not modified in 6+ months",
                        "Archive or delete files that are no longer needed",
                        "Consider moving old files to archive storage",
                        "Verify files are not needed before deleting"
                    ],
                    'items': old_files[:10]
                })
        
        # 6. Archivos temporales
        if results['temporary_files']:
            total_size = sum(t['size'] for t in results['temporary_files'])
            recommendations.append({
                'category': 'Temporary Files',
                'priority': 'high',
                'potential_savings_mb': total_size / 1024 / 1024,
                'description': f'Found {len(results["temporary_files"])} temporary files',
                'suggestions': [
                    f"Delete temporary files - potential savings: {total_size / 1024 / 1024:.2f} MB",
                    "Add temporary file patterns to .gitignore",
                    "Set up automatic cleanup of temporary files",
                    "Temporary files can be safely deleted"
                ],
                'items': results['temporary_files'][:20]
            })
        
        # 7. Tipos de archivo grandes
        large_types = sorted(
            [(ext, size) for ext, size in results['file_types_size'].items() if size > 50 * 1024 * 1024],
            key=lambda x: x[1],
            reverse=True
        )
        if large_types:
            recommendations.append({
                'category': 'Large File Types',
                'priority': 'medium',
                'description': 'File types consuming significant space',
                'suggestions': [
                    f"Review {ext} files - total size: {size / 1024 / 1024:.2f} MB" 
                    for ext, size in large_types[:5]
                ],
                'items': [{'extension': ext, 'size_mb': size / 1024 / 1024, 'count': results['file_types'][ext]} 
                         for ext, size in large_types[:5]]
            })
        
        self.recommendations = recommendations
        return recommendations
    
    def generate_summary(self) -> Dict:
        """Genera un resumen de las recomendaciones"""
        results = self.analyzer.analysis_results
        recommendations = self.recommendations
        
        total_potential_savings = sum(
            r.get('potential_savings_mb', 0) 
            for r in recommendations 
            if 'potential_savings_mb' in r
        )
        
        return {
            'workspace_size_mb': results['total_size'] / 1024 / 1024,
            'total_files': results['file_count'],
            'total_directories': results['directory_count'],
            'recommendations_count': len(recommendations),
            'total_potential_savings_mb': total_potential_savings,
            'potential_savings_percentage': (total_potential_savings / (results['total_size'] / 1024 / 1024) * 100) 
                                           if results['total_size'] > 0 else 0,
            'high_priority_count': len([r for r in recommendations if r.get('priority') == 'high']),
            'medium_priority_count': len([r for r in recommendations if r.get('priority') == 'medium']),
            'low_priority_count': len([r for r in recommendations if r.get('priority') == 'low'])
        }


class StorageCleanupAssistant:
    """Asistente principal que coordina análisis y recomendaciones"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root or os.getcwd()).resolve()
        self.analyzer = StorageAnalyzer(workspace_root)
        self.recommendation_engine = CleanupRecommendationEngine(self.analyzer)
    
    def analyze_and_recommend(self) -> Dict:
        """Ejecuta análisis completo y genera recomendaciones"""
        print("="*80)
        print("STORAGE CLEANUP ASSISTANT")
        print("="*80)
        print()
        
        # Analizar
        print("📊 Paso 1: Analizando almacenamiento...")
        analysis = self.analyzer.analyze_storage()
        print(f"   ✅ Análisis completado")
        print(f"   📁 Total: {analysis['total_size'] / 1024 / 1024 / 1024:.2f} GB")
        print(f"   📄 Archivos: {analysis['file_count']:,}")
        print(f"   📂 Directorios: {analysis['directory_count']:,}")
        print()
        
        # Generar recomendaciones
        print("💡 Paso 2: Generando recomendaciones...")
        recommendations = self.recommendation_engine.generate_recommendations()
        summary = self.recommendation_engine.generate_summary()
        print(f"   ✅ {len(recommendations)} categorías de recomendaciones generadas")
        print(f"   💾 Ahorro potencial: {summary['total_potential_savings_mb']:.2f} MB ({summary['potential_savings_percentage']:.1f}%)")
        print()
        
        return {
            'analysis': analysis,
            'recommendations': recommendations,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def print_report(self, results: Dict):
        """Imprime reporte formateado"""
        analysis = results['analysis']
        recommendations = results['recommendations']
        summary = results['summary']
        
        print("="*80)
        print("REPORTE DE ALMACENAMIENTO Y LIMPIEZA")
        print("="*80)
        print()
        
        print("📊 RESUMEN GENERAL")
        print("-" * 80)
        print(f"Workspace: {self.workspace_root}")
        print(f"Tamaño total: {summary['workspace_size_mb']:.2f} MB ({summary['workspace_size_mb'] / 1024:.2f} GB)")
        print(f"Total archivos: {summary['total_files']:,}")
        print(f"Total directorios: {summary['total_directories']:,}")
        print()
        
        print("💡 RECOMENDACIONES DE LIMPIEZA")
        print("-" * 80)
        print(f"Total recomendaciones: {summary['recommendations_count']}")
        print(f"Ahorro potencial: {summary['total_potential_savings_mb']:.2f} MB ({summary['potential_savings_percentage']:.1f}%)")
        print(f"  🔴 Alta prioridad: {summary['high_priority_count']}")
        print(f"  🟡 Media prioridad: {summary['medium_priority_count']}")
        print(f"  🟢 Baja prioridad: {summary['low_priority_count']}")
        print()
        
        # Mostrar recomendaciones por categoría
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(rec.get('priority', 'medium'), '⚪')
            
            print(f"{priority_icon} {i}. {rec['category']} - {rec['description']}")
            if 'potential_savings_mb' in rec:
                print(f"   💾 Ahorro potencial: {rec['potential_savings_mb']:.2f} MB")
            print("   💡 Sugerencias:")
            for suggestion in rec['suggestions']:
                print(f"      • {suggestion}")
            
            if 'items' in rec and rec['items']:
                print(f"   📋 Ejemplos ({min(5, len(rec['items']))} de {len(rec['items'])}):")
                for item in rec['items'][:5]:
                    if 'path' in item:
                        size_info = f" ({item.get('size_mb', item.get('size', 0) / 1024 / 1024):.2f} MB)" if 'size_mb' in item or 'size' in item else ""
                        print(f"      - {item['path']}{size_info}")
            print()
        
        print("="*80)
    
    def save_report(self, results: Dict, filename: Optional[str] = None):
        """Guarda el reporte en JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"storage_cleanup_report_{timestamp}.json"
        
        filepath = self.workspace_root / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Reporte guardado en: {filepath}")
        return filepath


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Storage Cleanup Assistant - Analiza y recomienda limpieza de almacenamiento"
    )
    parser.add_argument(
        '--workspace',
        type=str,
        help='Ruta del workspace (por defecto: directorio actual)'
    )
    parser.add_argument(
        '--save',
        action='store_true',
        help='Guardar reporte en JSON'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Nombre del archivo de salida'
    )
    
    args = parser.parse_args()
    
    # Crear asistente
    assistant = StorageCleanupAssistant(workspace_root=args.workspace)
    
    # Analizar y generar recomendaciones
    results = assistant.analyze_and_recommend()
    
    # Mostrar reporte
    assistant.print_report(results)
    
    # Guardar si se solicita
    if args.save or args.output:
        assistant.save_report(results, filename=args.output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())



