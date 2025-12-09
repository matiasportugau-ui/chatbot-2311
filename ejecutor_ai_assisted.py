#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-Assisted System Executor
============================

Enhanced version of ejecutor_completo.py that uses the ExecutionAIAgent
for intelligent guidance, suggestions, and monitoring.

Usage:
    python ejecutor_ai_assisted.py --mode react
    python ejecutor_ai_assisted.py --mode plan --execute
    python ejecutor_ai_assisted.py --mode suggest
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from execution_ai_agent import ExecutionAIAgent
    from ejecutor_completo import (
        print_success,
        print_warning,
        print_error,
        print_info,
        print_header,
    )
except ImportError as e:
    print(f"Error importing modules: {e}")

    # Fallback print functions
    def print_success(text):
        print(f"✅ {text}")

    def print_warning(text):
        print(f"⚠️  {text}")

    def print_error(text):
        print(f"❌ {text}")

    def print_info(text):
        print(f"ℹ️  {text}")

    def print_header(text):
        print(f"\n{'=' * 80}\n{text}\n{'=' * 80}\n")


def main():
    """Main entry point for AI-assisted executor"""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI-Assisted System Executor for Chatbot BMC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # ReAct cycle (intelligent step-by-step execution)\n"
            "  python ejecutor_ai_assisted.py --mode react\n\n"
            "  # Create and execute plan\n"
            "  python ejecutor_ai_assisted.py --mode plan --execute\n\n"
            "  # Get suggestions only\n"
            "  python ejecutor_ai_assisted.py --mode suggest\n\n"
            "  # Interactive execution with AI guidance\n"
            "  python ejecutor_ai_assisted.py --mode execute --interactive"
        ),
    )

    parser.add_argument(
        "--mode",
        choices=["react", "plan", "execute", "suggest", "monitor", "full"],
        default="full",
        help="Execution mode (default: full)",
    )

    parser.add_argument("--goal", help="Goal for planning/execution")

    parser.add_argument(
        "--execute", action="store_true", help="Execute plan after creating it (for plan mode)"
    )

    parser.add_argument(
        "--interactive", action="store_true", help="Interactive mode (ask for confirmation)"
    )

    parser.add_argument("--output", help="Output file for reports")

    parser.add_argument("--no-ai", action="store_true", help="Disable AI features (use basic mode)")

    args = parser.parse_args()

    # Load environment variables
    print_info("Cargando configuración...")
    try:
        from dotenv import load_dotenv

        if Path(".env.local").exists():
            load_dotenv(".env.local", override=True)
        elif Path(".env").exists():
            load_dotenv(".env", override=True)
    except ImportError:
        pass

    # Initialize AI agent
    print_header("INICIALIZANDO AGENTE DE IA PARA EJECUCIÓN")

    system_context = {}
    agent = ExecutionAIAgent(system_context=system_context)

    if not agent.is_available() and not args.no_ai:
        print_warning("IA no disponible - funcionando en modo básico")
        print_info("Configura OPENAI_API_KEY, GROQ_API_KEY, o GEMINI_API_KEY")
    elif agent.is_available():
        print_success("Agente de IA disponible - Funciones inteligentes habilitadas")
        print_info("• Diagnóstico inteligente")
        print_info("• Planificación automática")
        print_info("• Sugerencias contextuales")
        print_info("• Monitoreo y seguimiento")

    print()

    # Execute based on mode
    if args.mode == "react":
        # ReAct cycle mode
        situation = args.goal or "Review and prepare chatbot system for execution"
        print_header("MODO REACT: THINK → ACT → OBSERVE")
        print_info("El agente analizará la situación y ejecutará acciones")
        print()

        result = agent.react_cycle(situation, max_iterations=5)

        if result.get("success"):
            print_success("\nCiclo ReAct completado exitosamente")
        else:
            print_warning("\nCiclo ReAct completado con advertencias")

        print_info(f"Iteraciones: {result.get('iterations', 0)}")

    elif args.mode == "plan":
        # Planning mode
        goal = args.goal or "Review and execute chatbot system"
        print_header("MODO PLANIFICACIÓN")
        print_info(f"Objetivo: {goal}")
        print()

        plan = agent.create_execution_plan(goal, system_context)
        print_success(f"Plan de ejecución creado ({len(plan)} tareas)")

        # Show plan summary
        print("\nResumen del Plan:")
        categories = {}
        for task in plan:
            cat = task.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(task)

        for cat, tasks in categories.items():
            print(f"\n  {cat.upper()}: {len(tasks)} tareas")
            for task in tasks[:3]:  # Show first 3
                print(f"    • {task.title} ({task.priority.value})")
            if len(tasks) > 3:
                print(f"    ... y {len(tasks) - 3} más")

        # Execute if requested
        if args.execute:
            print()
            response = input("¿Ejecutar el plan ahora? [S/n]: ").strip().lower()
            if response != "n":
                result = agent.execute_plan(interactive=args.interactive)
                print_success("\nEjecución completada")
            else:
                print_info("Plan guardado. Ejecuta con --mode execute")

    elif args.mode == "execute":
        # Execution mode
        print_header("MODO EJECUCIÓN")

        if not agent.execution_plan:
            goal = args.goal or "Review and execute chatbot system"
            print_info("No hay plan existente. Creando uno...")
            agent.create_execution_plan(goal, system_context)

        result = agent.execute_plan(interactive=args.interactive)

        print()
        if result.get("failed", 0) == 0:
            print_success("Todas las tareas completadas exitosamente")
        else:
            failed_count = result.get("failed", 0)
            print_warning(f"{failed_count} tareas fallaron")

    elif args.mode == "suggest":
        # Suggestions mode
        print_header("MODO SUGERENCIAS")
        print_info("Analizando sistema y generando sugerencias...")
        print()

        # First, do a quick review to get context
        if agent.reviewer:
            print_info("Realizando revisión rápida del sistema...")
            review_result = agent.reviewer.review()
            system_context["review"] = review_result

        suggestions = agent.get_suggestions(system_context)

        print_success(f"{len(suggestions)} sugerencias generadas:\n")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")

        print()
        response = (
            input("¿Deseas crear un plan basado en estas sugerencias? [s/N]: ").strip().lower()
        )
        if response == "s":
            goal = args.goal or "Implement suggestions"
            plan = agent.create_execution_plan(goal, system_context)
            print_success(f"Plan creado con {len(plan)} tareas")

    elif args.mode == "monitor":
        # Monitoring mode
        import time

        print_header("MODO MONITOREO")
        print_info("Iniciando monitoreo del sistema...")
        print()

        agent.monitoring_active = True
        try:
            while True:
                result = agent._act_monitor_progress({})
                if result.get("success"):
                    print_info(f"Estado: {result.get('output', {}).get('timestamp', 'N/A')}")
                time.sleep(10)  # Check every 10 seconds
        except KeyboardInterrupt:
            print("\n\nMonitoreo detenido por el usuario")
            agent.monitoring_active = False

    elif args.mode == "full":
        # Full mode: ReAct cycle with planning
        print_header("MODO COMPLETO: PLANIFICACIÓN + EJECUCIÓN INTELIGENTE")
        print_info("Este modo combina planificación inteligente con ejecución")
        print()

        goal = args.goal or "Review, install, configure, and execute chatbot system"

        # Step 1: Create plan
        print("Paso 1: Creando plan de ejecución...")
        plan = agent.create_execution_plan(goal, system_context)
        print_success(f"Plan creado ({len(plan)} tareas)")

        # Step 2: Show plan
        print("\nPlan de Ejecución:")
        for i, task in enumerate(plan, 1):
            status_icon = "⏳" if task.status.value == "pending" else "✅"
            print(f"  {i}. {status_icon} {task.title} ({task.priority.value})")
            if task.description:
                print(f"     {task.description[:60]}...")

        # Step 3: Execute
        print()
        if args.interactive:
            response = input("¿Ejecutar el plan? [S/n]: ").strip().lower()
            if response == "n":
                print_info("Plan guardado. Ejecuta con --mode execute")
                return
        else:
            print_info("Ejecutando plan automáticamente...")

        result = agent.execute_plan(interactive=args.interactive)

        # Step 4: Summary
        print()
        print_header("RESUMEN FINAL")
        completed = result.get("completed", 0)
        print_success(f"Tareas completadas: {completed}")
        if result.get("failed", 0) > 0:
            failed = result.get("failed", 0)
            print_error(f"Tareas fallidas: {failed}")
        if result.get("skipped", 0) > 0:
            skipped = result.get("skipped", 0)
            print_warning(f"Tareas saltadas: {skipped}")

        # Get final suggestions
        if agent.is_available():
            print()
            print_info("Obteniendo sugerencias finales...")
            final_suggestions = agent.get_suggestions(system_context)
            if final_suggestions:
                print("\nPróximos pasos sugeridos:")
                for suggestion in final_suggestions[:3]:
                    print(f"  • {suggestion}")

    # Save report
    if args.output or args.mode in ["react", "execute", "full"]:
        report_path = agent.save_execution_report(args.output)
        print()
        print_success(f"Reporte guardado en: {report_path}")

    print()
    print_success("Proceso completado")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nError fatal: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
