#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo de uso del Agente de Investigación de Repositorios iOS
==============================================================

Este script muestra cómo usar el agente para investigar repositorios iOS,
evaluar el workspace local, y generar un plan de consolidación.
"""

from repo_research_agent import RepoResearchAgent
from pathlib import Path
import json

def main():
    """Ejemplo de uso completo del agente"""
    
    print("="*80)
    print("EJEMPLO: Agente de Investigación de Repositorios iOS")
    print("="*80)
    print()
    
    # 1. Crear instancia del agente
    print("📦 Inicializando agente...")
    workspace_path = Path(__file__).parent  # Directorio actual
    agent = RepoResearchAgent(workspace_path=str(workspace_path))
    print("✅ Agente inicializado\n")
    
    # 2. Investigar repositorios iOS en GitHub
    print("🔍 Fase 1: Investigando repositorios iOS en GitHub...")
    print("-" * 80)
    try:
        github_results = agent.research_github_ios_repos(
            owner="matiasportugau-ui",
            keywords=["ios", "swift", "swiftui", "uikit", "xcode"]
        )
        print(f"\n✅ Encontrados {github_results.get('total_ios_repos', 0)} repositorios iOS")
        print(f"   Total branches: {github_results.get('summary', {}).get('total_branches', 0)}")
        print(f"   Total workflows: {github_results.get('summary', {}).get('total_workflows', 0)}")
    except Exception as e:
        print(f"⚠️  Error en investigación de GitHub: {e}")
        github_results = {}
    print()
    
    # 3. Evaluar workspace local
    print("📁 Fase 2: Evaluando workspace local...")
    print("-" * 80)
    try:
        workspace_results = agent.evaluate_local_workspace()
        print(f"\n✅ Workspace evaluado")
        print(f"   Total archivos: {workspace_results.get('files', {}).get('total_files', 0)}")
        print(f"   Total módulos: {workspace_results.get('modules', {}).get('total_modules', 0)}")
        print(f"   Es repo Git: {workspace_results.get('git_status', {}).get('is_git_repo', False)}")
    except Exception as e:
        print(f"⚠️  Error evaluando workspace: {e}")
        workspace_results = {}
    print()
    
    # 4. Identificar mejoras cruzadas
    print("🔄 Fase 3: Identificando mejoras cruzadas...")
    print("-" * 80)
    try:
        improvements = agent.identify_cross_improvements()
        print(f"\n✅ Identificadas {len(improvements)} mejoras")
        
        # Mostrar algunas mejoras
        if improvements:
            print("\n   Primeras mejoras:")
            for i, improvement in enumerate(improvements[:5], 1):
                print(f"   {i}. [{improvement.get('priority', 'unknown')}] {improvement.get('description', '')[:60]}...")
    except Exception as e:
        print(f"⚠️  Error identificando mejoras: {e}")
        improvements = []
    print()
    
    # 5. Generar plan de consolidación
    print("📋 Fase 4: Generando plan de consolidación...")
    print("-" * 80)
    try:
        consolidation_plan = agent.generate_consolidation_plan()
        print(f"\n✅ Plan de consolidación generado")
        print(f"   Total fases: {len(consolidation_plan.get('phases', []))}")
        print(f"   Timeline: {consolidation_plan.get('timeline', 'No especificado')}")
        
        # Mostrar fases
        if consolidation_plan.get('phases'):
            print("\n   Fases del plan:")
            for phase in consolidation_plan['phases']:
                phase_name = phase.get('name', phase.get('phase', 'Unknown'))
                print(f"   - {phase_name}")
    except Exception as e:
        print(f"⚠️  Error generando plan: {e}")
        consolidation_plan = {}
    print()
    
    # 6. Generar reporte completo
    print("📊 Generando reporte completo...")
    print("-" * 80)
    try:
        report = agent.generate_full_report()
        
        # Guardar reporte
        output_file = agent.save_report(report, filename="ejemplo_repo_research_report.json")
        print(f"\n✅ Reporte guardado en: {output_file}")
        
        # Mostrar resumen
        print("\n📊 Resumen del Reporte:")
        print(f"   - Repositorios iOS: {len(agent.github_repos)}")
        print(f"   - Módulos en workspace: {agent.local_workspace_analysis.get('modules', {}).get('total_modules', 0)}")
        print(f"   - Mejoras identificadas: {len(agent.improvements_identified)}")
        print(f"   - Fases del plan: {len(consolidation_plan.get('phases', []))}")
        print(f"   - Recomendaciones: {len(report.get('recommendations', []))}")
        
        # Mostrar recomendaciones
        if report.get('recommendations'):
            print("\n💡 Recomendaciones:")
            for i, rec in enumerate(report['recommendations'][:5], 1):
                print(f"   {i}. {rec}")
        
    except Exception as e:
        print(f"⚠️  Error generando reporte: {e}")
    
    print("\n" + "="*80)
    print("✅ Ejemplo completado")
    print("="*80)
    print("\n📄 Revisa el archivo 'ejemplo_repo_research_report.json' para ver el reporte completo")


if __name__ == "__main__":
    main()


