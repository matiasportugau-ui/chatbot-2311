#!/usr/bin/env python3
"""
Ejemplo de uso del Gravity Agent
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.gravity_agent import GravityAgent


def example_1_interpret_state():
    """Ejemplo 1: Interpretar estado del proyecto"""
    print("\n" + "="*80)
    print("Ejemplo 1: Interpretar Estado del Proyecto")
    print("="*80 + "\n")
    
    agent = GravityAgent()
    state = agent.interpret_project_state()
    
    print(f"Fase actual: {state.current_phase}")
    print(f"Estado general: {state.overall_status}")
    print(f"Tareas activas: {len(state.active_tasks)}")
    print(f"Bloqueadores: {len(state.blockers)}")
    print(f"Dependencias cumplidas: {state.dependencies_met}")


def example_2_orchestrate():
    """Ejemplo 2: Orquestar desarrollo"""
    print("\n" + "="*80)
    print("Ejemplo 2: Orquestar Desarrollo Automatizado")
    print("="*80 + "\n")
    
    agent = GravityAgent()
    result = agent.orchestrate_development(target_phase=5)
    
    print(f"\nResumen de ejecución:")
    print(f"  - Fases ejecutadas: {result['summary']['phases_executed']}")
    print(f"  - Fases fallidas: {result['summary']['phases_failed']}")
    print(f"  - Tareas delegadas: {result['summary']['tasks_delegated']}")
    print(f"  - Tasa de éxito: {result['summary']['success_rate']:.2f}%")


def example_3_analyze_pr():
    """Ejemplo 3: Analizar PR"""
    print("\n" + "="*80)
    print("Ejemplo 3: Analizar Pull Request")
    print("="*80 + "\n")
    
    agent = GravityAgent()
    
    # Analizar PR #87
    pr_result = agent.analyze_pr(pr_number=87)
    
    if "error" in pr_result:
        print(f"Error: {pr_result['error']}")
    else:
        print(f"Análisis completado:")
        if "analysis" in pr_result:
            print(f"  - Cambios detectados: {len(pr_result.get('analysis', {}).get('files_changed', []))}")
        if "plan" in pr_result:
            print(f"  - Plan generado: Sí")
        if "task_list" in pr_result:
            print(f"  - Tareas identificadas: {len(pr_result.get('task_list', {}).get('tasks', []))}")


def example_4_monitor():
    """Ejemplo 4: Monitorear proyecto"""
    print("\n" + "="*80)
    print("Ejemplo 4: Monitorear Proyecto")
    print("="*80 + "\n")
    
    agent = GravityAgent()
    result = agent.monitor_project(interval=30)
    
    print(f"Monitoreo completado:")
    print(f"  - Checks realizados: {len(result.get('checks', []))}")
    print(f"  - Acciones tomadas: {len(result.get('actions_taken', []))}")
    if result.get('actions_taken'):
        for action in result['actions_taken']:
            print(f"    - {action.get('action')}: {action.get('blocker')}")


def example_5_status_report():
    """Ejemplo 5: Reporte de estado"""
    print("\n" + "="*80)
    print("Ejemplo 5: Reporte de Estado Completo")
    print("="*80 + "\n")
    
    agent = GravityAgent()
    status = agent.get_status_report()
    
    print(f"Agente: {status['agent']}")
    print(f"Timestamp: {status['timestamp']}")
    print(f"\nComponentes:")
    for component, available in status['components'].items():
        status_icon = "✅" if available else "❌"
        print(f"  {status_icon} {component}: {available}")
    
    if status.get('project_state'):
        state = status['project_state']
        print(f"\nEstado del Proyecto:")
        print(f"  - Fase actual: {state.get('current_phase')}")
        print(f"  - Estado general: {state.get('overall_status')}")
        print(f"  - Bloqueadores: {len(state.get('blockers', []))}")


def main():
    """Ejecutar todos los ejemplos"""
    print("\n" + "="*80)
    print("Gravity Agent - Ejemplos de Uso")
    print("="*80)
    
    examples = [
        ("1", "Interpretar Estado", example_1_interpret_state),
        ("2", "Orquestar Desarrollo", example_2_orchestrate),
        ("3", "Analizar PR", example_3_analyze_pr),
        ("4", "Monitorear Proyecto", example_4_monitor),
        ("5", "Reporte de Estado", example_5_status_report),
    ]
    
    print("\nEjemplos disponibles:")
    for num, name, _ in examples:
        print(f"  {num}. {name}")
    
    print("\nEjecutando todos los ejemplos...\n")
    
    for num, name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error en ejemplo {num} ({name}): {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("Ejemplos completados")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
