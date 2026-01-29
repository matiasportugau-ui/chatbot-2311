#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo de uso del Gravity Agent
=================================

Este script muestra cómo usar el Gravity Agent programáticamente
para interpretar y orquestar el desarrollo automatizado.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.gravity_agent import GravityAgent, ExecutionMode


def example_analyze_pr():
    """Ejemplo: Analizar un PR específico"""
    print("=" * 80)
    print("Ejemplo 1: Analizar PR #87")
    print("=" * 80)
    
    # Crear agente en modo dry-run para no ejecutar cambios
    agent = GravityAgent(execution_mode=ExecutionMode.DRY_RUN)
    
    # Analizar PR
    result = agent.interpret_and_orchestrate(pr_number=87)
    
    print("\n📊 Resultado:")
    print(f"   - Estado: {result.get('status')}")
    print(f"   - Intención detectada: {result.get('interpretation', {}).get('intent')}")
    print(f"   - Componentes afectados: {len(result.get('interpretation', {}).get('affected_components', []))}")
    
    return result


def example_analyze_local_changes():
    """Ejemplo: Analizar cambios locales"""
    print("\n" + "=" * 80)
    print("Ejemplo 2: Analizar cambios locales")
    print("=" * 80)
    
    # Crear agente en modo analysis_only
    agent = GravityAgent(execution_mode=ExecutionMode.ANALYSIS_ONLY)
    
    # Analizar cambios locales
    result = agent.interpret_and_orchestrate(local_changes=True)
    
    print("\n📊 Resultado:")
    print(f"   - Estado: {result.get('status')}")
    if 'interpretation' in result:
        interpretation = result['interpretation']
        print(f"   - Archivos cambiados: {interpretation.get('context', {}).get('change_count', 0)}")
        print(f"   - Componentes afectados: {interpretation.get('affected_components', [])}")
    
    return result


def example_custom_pr_data():
    """Ejemplo: Analizar con datos de PR personalizados"""
    print("\n" + "=" * 80)
    print("Ejemplo 3: Analizar con datos de PR personalizados")
    print("=" * 80)
    
    # Datos de PR simulados
    pr_data = {
        "title": "Add new feature: Gravity Agent",
        "body": "This PR adds a new Gravity Agent for automated development orchestration.",
        "changed_files": [
            {"file": "agents/gravity_agent.py", "additions": 500, "deletions": 0},
            {"file": "agents/GRAVITY_AGENT_README.md", "additions": 200, "deletions": 0}
        ]
    }
    
    agent = GravityAgent(execution_mode=ExecutionMode.ANALYSIS_ONLY)
    result = agent.interpret_pr(pr_data=pr_data)
    
    print("\n📊 Resultado:")
    print(f"   - Intención: {result.get('intent')}")
    print(f"   - Complejidad: {result.get('estimated_complexity')}")
    print(f"   - Confianza: {result.get('confidence', 0):.2%}")
    print(f"   - Recomendaciones: {len(result.get('recommendations', []))}")
    
    return result


def example_orchestrate_execution():
    """Ejemplo: Orquestar ejecución de un plan"""
    print("\n" + "=" * 80)
    print("Ejemplo 4: Orquestar ejecución")
    print("=" * 80)
    
    # Crear agente
    agent = GravityAgent(execution_mode=ExecutionMode.DRY_RUN)
    
    # Generar un plan básico
    interpretation = {
        "intent": "Feature addition",
        "estimated_complexity": "medium",
        "affected_components": ["agents"],
        "required_agents": ["PlanningAgent"]
    }
    
    plan = agent.generate_orchestration_plan(interpretation)
    
    print("\n📋 Plan generado:")
    print(f"   - ID: {plan.get('plan_id')}")
    print(f"   - Fases: {len(plan.get('phases', []))}")
    print(f"   - Duración estimada: {plan.get('estimated_duration')} minutos")
    
    # Nota: No ejecutamos en este ejemplo porque estamos en modo DRY_RUN
    print("\n⚠️  Nota: Ejecución omitida (modo DRY_RUN)")
    
    return plan


def main():
    """Ejecutar todos los ejemplos"""
    print("\n🌌 Gravity Agent - Ejemplos de Uso\n")
    
    try:
        # Ejemplo 1: Analizar PR (requiere acceso a GitHub)
        # Descomentar si tienes acceso a GitHub
        # example_analyze_pr()
        
        # Ejemplo 2: Analizar cambios locales
        example_analyze_local_changes()
        
        # Ejemplo 3: Analizar con datos personalizados
        example_custom_pr_data()
        
        # Ejemplo 4: Generar plan de orquestación
        example_orchestrate_execution()
        
        print("\n" + "=" * 80)
        print("✅ Todos los ejemplos completados")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
