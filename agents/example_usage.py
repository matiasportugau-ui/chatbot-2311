#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo de uso del Gravity Orchestrator Agent
==============================================

Este archivo muestra ejemplos de cómo usar el Gravity Orchestrator Agent
en diferentes escenarios.
"""

from agents.gravity_orchestrator_agent import GravityOrchestratorAgent, AgentMode


def example_1_interpret_only():
    """Ejemplo 1: Solo interpretar el estado del proyecto"""
    print("\n" + "="*80)
    print("EJEMPLO 1: Interpretar Estado")
    print("="*80)
    
    # Crear agente en modo interpret
    agent = GravityOrchestratorAgent(mode=AgentMode.INTERPRET)
    
    # Interpretar estado
    state = agent.interpret_project_state()
    
    # Usar la información
    print(f"\n📊 Resumen:")
    print(f"   Fase actual: {state.current_phase}")
    print(f"   Estado general: {state.overall_status}")
    print(f"   Bloqueadores: {len(state.blockers)}")
    print(f"   Próximas acciones: {len(state.next_actions)}")


def example_2_create_plan():
    """Ejemplo 2: Crear un plan de orquestación"""
    print("\n" + "="*80)
    print("EJEMPLO 2: Crear Plan de Orquestación")
    print("="*80)
    
    # Crear agente
    agent = GravityOrchestratorAgent(mode=AgentMode.HYBRID)
    
    # Interpretar estado primero
    agent.interpret_project_state()
    
    # Crear plan
    plan = agent.create_orchestration_plan(
        goal="Completar todas las fases pendientes",
        start_phase=0,
        end_phase=15
    )
    
    # Usar el plan
    print(f"\n📋 Plan creado:")
    print(f"   Fases a ejecutar: {len(plan.phases_to_execute)}")
    print(f"   Tiempo estimado: {plan.estimated_time}")
    print(f"   Riesgo: {plan.risk_assessment['overall_risk']}")


def example_3_execute_single_phase():
    """Ejemplo 3: Ejecutar una fase específica"""
    print("\n" + "="*80)
    print("EJEMPLO 3: Ejecutar Fase Específica")
    print("="*80)
    
    # Crear agente
    agent = GravityOrchestratorAgent(mode=AgentMode.ORCHESTRATE, auto_approve=True)
    
    # Ejecutar fase 0
    result = agent.execute_phase(phase=0)
    
    if result.get("success"):
        print(f"\n✅ Phase 0 ejecutada exitosamente")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown')}")


def example_4_full_orchestration():
    """Ejemplo 4: Orquestación completa"""
    print("\n" + "="*80)
    print("EJEMPLO 4: Orquestación Completa")
    print("="*80)
    
    # Crear agente en modo hybrid
    agent = GravityOrchestratorAgent(mode=AgentMode.HYBRID, auto_approve=True)
    
    # Interpretar estado
    agent.interpret_project_state()
    
    # Crear plan
    agent.create_orchestration_plan(start_phase=0, end_phase=5)
    
    # Ejecutar orquestación
    result = agent.orchestrate_execution(start_phase=0, end_phase=5)
    
    if result.get("success"):
        print("\n✅ Orquestación completada exitosamente")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown')}")


def example_5_get_report():
    """Ejemplo 5: Obtener y guardar reporte"""
    print("\n" + "="*80)
    print("EJEMPLO 5: Generar Reporte")
    print("="*80)
    
    # Crear agente
    agent = GravityOrchestratorAgent(mode=AgentMode.HYBRID)
    
    # Interpretar y planificar
    agent.interpret_project_state()
    agent.create_orchestration_plan()
    
    # Obtener reporte
    report = agent.get_status_report()
    
    # Guardar reporte
    report_path = agent.save_report("consolidation/example_report.json")
    
    print(f"\n✅ Reporte guardado en: {report_path}")
    print(f"   Incluye: {len(report.get('execution_history', []))} ejecuciones")


def example_6_monitoring_loop():
    """Ejemplo 6: Loop de monitoreo continuo"""
    print("\n" + "="*80)
    print("EJEMPLO 6: Monitoreo Continuo")
    print("="*80)
    
    import time
    
    agent = GravityOrchestratorAgent(mode=AgentMode.INTERPRET)
    
    # Monitorear 3 veces con intervalo
    for i in range(3):
        print(f"\n--- Monitoreo {i+1}/3 ---")
        state = agent.interpret_project_state()
        
        print(f"Estado: {state.overall_status}")
        print(f"Fase actual: {state.current_phase}")
        
        if i < 2:  # No esperar después del último
            print("Esperando 5 segundos...")
            time.sleep(5)


def example_7_conditional_execution():
    """Ejemplo 7: Ejecución condicional basada en estado"""
    print("\n" + "="*80)
    print("EJEMPLO 7: Ejecución Condicional")
    print("="*80)
    
    agent = GravityOrchestratorAgent(mode=AgentMode.HYBRID)
    
    # Interpretar estado
    state = agent.interpret_project_state()
    
    # Decidir qué hacer basado en el estado
    if state.blockers:
        print(f"\n⚠️  Bloqueadores detectados: {len(state.blockers)}")
        print("   Resolviendo bloqueadores primero...")
        # Aquí podrías ejecutar lógica para resolver bloqueadores
    else:
        print("\n✅ No hay bloqueadores. Procediendo con ejecución...")
        
        # Ejecutar siguiente fase pendiente
        for phase in range(state.current_phase, 16):
            if state.phases_status.get(phase) == "pending":
                print(f"\n🎯 Ejecutando Phase {phase}...")
                result = agent.execute_phase(phase)
                if result.get("success"):
                    print(f"✅ Phase {phase} completada")
                    break
                else:
                    print(f"❌ Phase {phase} falló: {result.get('error')}")
                    break


if __name__ == "__main__":
    print("\n" + "="*80)
    print("GRAVITY ORCHESTRATOR AGENT - EJEMPLOS DE USO")
    print("="*80)
    
    # Ejecutar ejemplos (comentar los que no quieras ejecutar)
    
    try:
        example_1_interpret_only()
    except Exception as e:
        print(f"❌ Error en ejemplo 1: {e}")
    
    try:
        example_2_create_plan()
    except Exception as e:
        print(f"❌ Error en ejemplo 2: {e}")
    
    # Descomentar para ejecutar (requieren orchestrator funcionando):
    # example_3_execute_single_phase()
    # example_4_full_orchestration()
    # example_5_get_report()
    # example_6_monitoring_loop()
    # example_7_conditional_execution()
    
    print("\n" + "="*80)
    print("✅ Ejemplos completados")
    print("="*80)
