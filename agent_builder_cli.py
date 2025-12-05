#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Builder CLI - Interactive Command Line Interface
Provides an interactive interface for creating agents and managing consultations
"""

import sys
from datetime import datetime, timedelta
from typing import Optional

from agent_builder import (
    get_agent_builder,
    AgentType,
    AgentBlueprint,
    Consultation
)
from agent_builder_agenda import (
    get_agent_builder_agenda,
    TaskPriority,
    TaskStatus
)


class AgentBuilderCLI:
    """Interactive CLI for Agent Builder"""
    
    def __init__(self):
        self.builder = get_agent_builder()
        self.agenda = get_agent_builder_agenda()
        self.current_agent: Optional[AgentBlueprint] = None
    
    def print_header(self):
        """Print CLI header"""
        print("\n" + "=" * 70)
        print("  AGENT BUILDER - Personalized Agent Development System")
        print("=" * 70)
        print("  Desarrolla agentes con consultas progresivamente más profundas")
        print("=" * 70 + "\n")
    
    def print_menu(self):
        """Print main menu"""
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Crear nuevo agente")
        print("2. Listar agentes")
        print("3. Seleccionar agente")
        print("4. Consultar con el Builder")
        print("5. Ver agenda y tareas")
        print("6. Crear tarea")
        print("7. Programar consulta")
        print("8. Ver progreso")
        print("9. Generar reporte")
        print("0. Salir")
        print()
    
    def create_agent(self):
        """Create a new agent blueprint"""
        print("\n--- CREAR NUEVO AGENTE ---")
        
        name = input("Nombre del agente: ").strip()
        if not name:
            print("❌ El nombre es requerido")
            return
        
        print("\nTipos de agente disponibles:")
        for i, agent_type in enumerate(AgentType, 1):
            print(f"{i}. {agent_type.value}")
        
        try:
            type_choice = int(input("\nSelecciona el tipo (1-6): "))
            agent_type = list(AgentType)[type_choice - 1]
        except (ValueError, IndexError):
            print("❌ Selección inválida")
            return
        
        capabilities = input(
            "\nCapacidades iniciales (separadas por coma): "
        ).strip()
        capabilities_list = [
            c.strip() for c in capabilities.split(",")
            if c.strip()
        ]
        
        # Create the blueprint
        blueprint = self.builder.create_agent_blueprint(
            agent_name=name,
            agent_type=agent_type,
            initial_capabilities=capabilities_list
        )
        
        self.current_agent = blueprint
        
        print(f"\n✅ Agente creado exitosamente!")
        print(f"   ID: {blueprint.agent_id}")
        print(f"   Nombre: {blueprint.agent_name}")
        print(f"   Tipo: {blueprint.agent_type.value}")
        print(f"   Capacidades: {len(blueprint.capabilities)}")
    
    def list_agents(self):
        """List all agent blueprints"""
        print("\n--- AGENTES DISPONIBLES ---")
        
        blueprints = self.builder.list_blueprints()
        
        if not blueprints:
            print("No hay agentes creados aún.")
            return
        
        for i, blueprint in enumerate(blueprints, 1):
            print(f"\n{i}. {blueprint.agent_name}")
            print(f"   ID: {blueprint.agent_id}")
            print(f"   Tipo: {blueprint.agent_type.value}")
            print(f"   Etapa: {blueprint.development_stage}")
            print(f"   Progreso: {blueprint.completion_percentage:.1f}%")
            print(f"   Consultas: {len(blueprint.consultations)}")
            print(f"   Actualizado: {blueprint.updated_at.strftime('%Y-%m-%d %H:%M')}")
    
    def select_agent(self):
        """Select an agent to work with"""
        print("\n--- SELECCIONAR AGENTE ---")
        
        blueprints = self.builder.list_blueprints()
        
        if not blueprints:
            print("No hay agentes creados aún.")
            return
        
        for i, blueprint in enumerate(blueprints, 1):
            print(f"{i}. {blueprint.agent_name} ({blueprint.agent_type.value})")
        
        try:
            choice = int(input("\nSelecciona un agente: "))
            self.current_agent = blueprints[choice - 1]
            print(f"✅ Agente seleccionado: {self.current_agent.agent_name}")
        except (ValueError, IndexError):
            print("❌ Selección inválida")
    
    def consult(self):
        """Conduct a consultation"""
        if not self.current_agent:
            print("❌ Primero selecciona un agente")
            return
        
        print(f"\n--- CONSULTA CON BUILDER: {self.current_agent.agent_name} ---")
        print(f"Consultas previas: {len(self.current_agent.consultations)}")
        
        # Get suggested topics
        suggestions = self.agenda.suggest_next_consultation_topics(
            self.current_agent.agent_id
        )
        
        if suggestions:
            print("\nTemas sugeridos para consulta:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
            print()
        
        topic = input("Tema de consulta: ").strip()
        if not topic:
            print("❌ El tema es requerido")
            return
        
        # Conduct consultation
        print("\n⏳ Generando consulta personalizada...")
        consultation = self.builder.consult(
            self.current_agent.agent_id,
            topic
        )
        
        # Display results
        print(f"\n✅ Consulta completada!")
        print(f"   Nivel: {consultation.level.value.upper()}")
        print(f"   ID: {consultation.consultation_id}")
        
        print(f"\n📋 RECOMENDACIONES ({len(consultation.recommendations)}):")
        for i, rec in enumerate(consultation.recommendations, 1):
            print(f"   {i}. {rec}")
        
        if consultation.insights:
            print(f"\n💡 INSIGHTS ({len(consultation.insights)}):")
            for i, insight in enumerate(consultation.insights, 1):
                print(f"   {i}. {insight}")
        
        if consultation.code_examples:
            print(f"\n💻 EJEMPLOS DE CÓDIGO ({len(consultation.code_examples)}):")
            for i, example in enumerate(consultation.code_examples, 1):
                print(f"\n   {i}. {example['title']}")
                print("   " + "-" * 60)
                print("   " + example['code'].replace("\n", "\n   "))
                print("   " + "-" * 60)
        
        if consultation.next_steps:
            print(f"\n➡️ PRÓXIMOS PASOS ({len(consultation.next_steps)}):")
            for i, step in enumerate(consultation.next_steps, 1):
                print(f"   {i}. {step}")
        
        # Refresh current agent
        self.current_agent = self.builder.get_blueprint(self.current_agent.agent_id)
        
        print(f"\n📊 Progreso actualizado: {self.current_agent.completion_percentage:.1f}%")
        print(f"   Etapa: {self.current_agent.development_stage}")
    
    def view_agenda(self):
        """View agenda and tasks"""
        if not self.current_agent:
            print("❌ Primero selecciona un agente")
            return
        
        print(f"\n--- AGENDA: {self.current_agent.agent_name} ---")
        
        # Get upcoming consultations
        upcoming = self.agenda.get_upcoming_agenda(
            days=7,
            agent_id=self.current_agent.agent_id
        )
        
        if upcoming:
            print("\n📅 CONSULTAS PROGRAMADAS (próximos 7 días):")
            for item in upcoming:
                print(f"   • {item.title}")
                print(f"     Fecha: {item.scheduled_time.strftime('%Y-%m-%d %H:%M')}")
                print(f"     Duración: {item.duration_minutes} min")
                print()
        
        # Get tasks by status
        pending = self.agenda.get_tasks_by_status(
            TaskStatus.PENDING,
            agent_id=self.current_agent.agent_id
        )
        
        in_progress = self.agenda.get_tasks_by_status(
            TaskStatus.IN_PROGRESS,
            agent_id=self.current_agent.agent_id
        )
        
        completed = self.agenda.get_tasks_by_status(
            TaskStatus.COMPLETED,
            agent_id=self.current_agent.agent_id
        )
        
        print(f"\n📝 TAREAS:")
        print(f"   Pendientes: {len(pending)}")
        print(f"   En Progreso: {len(in_progress)}")
        print(f"   Completadas: {len(completed)}")
        
        if pending:
            print("\n   Tareas pendientes:")
            for task in pending[:5]:
                priority_emoji = {
                    "low": "🟢",
                    "medium": "🟡",
                    "high": "🟠",
                    "urgent": "🔴"
                }
                emoji = priority_emoji.get(task.priority.value, "⚪")
                print(f"   {emoji} {task.title}")
                if task.due_date:
                    print(f"      Vence: {task.due_date.strftime('%Y-%m-%d')}")
        
        # Get milestones
        milestones = self.agenda.get_milestones(
            agent_id=self.current_agent.agent_id
        )
        
        if milestones:
            print(f"\n🎯 HITOS ({len(milestones)}):")
            for milestone in milestones:
                status = "✅" if milestone.completed else "⏳"
                print(f"   {status} {milestone.title}")
                print(f"      Fecha objetivo: {milestone.target_date.strftime('%Y-%m-%d')}")
    
    def create_task(self):
        """Create a development task"""
        if not self.current_agent:
            print("❌ Primero selecciona un agente")
            return
        
        print(f"\n--- CREAR TAREA: {self.current_agent.agent_name} ---")
        
        title = input("Título de la tarea: ").strip()
        if not title:
            print("❌ El título es requerido")
            return
        
        description = input("Descripción: ").strip()
        
        print("\nPrioridad:")
        print("1. Baja")
        print("2. Media")
        print("3. Alta")
        print("4. Urgente")
        
        try:
            priority_choice = int(input("Selecciona prioridad (1-4): "))
            priorities = [
                TaskPriority.LOW,
                TaskPriority.MEDIUM,
                TaskPriority.HIGH,
                TaskPriority.URGENT
            ]
            priority = priorities[priority_choice - 1]
        except (ValueError, IndexError):
            priority = TaskPriority.MEDIUM
            print("ℹ️  Usando prioridad media por defecto")
        
        days_str = input("Días hasta vencimiento (Enter para omitir): ").strip()
        due_date = None
        if days_str:
            try:
                days = int(days_str)
                due_date = datetime.now() + timedelta(days=days)
            except ValueError:
                print("⚠️  Días inválidos, omitiendo fecha de vencimiento")
        
        hours_str = input("Horas estimadas (default 1): ").strip()
        estimated_hours = 1.0
        if hours_str:
            try:
                estimated_hours = float(hours_str)
            except ValueError:
                print("⚠️  Horas inválidas, usando 1 hora")
        
        # Create task
        task = self.agenda.create_task(
            agent_id=self.current_agent.agent_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            estimated_hours=estimated_hours
        )
        
        print(f"\n✅ Tarea creada!")
        print(f"   ID: {task.task_id}")
        print(f"   Título: {task.title}")
        print(f"   Prioridad: {task.priority.value}")
        if task.due_date:
            print(f"   Vence: {task.due_date.strftime('%Y-%m-%d')}")
    
    def schedule_consultation(self):
        """Schedule a consultation"""
        if not self.current_agent:
            print("❌ Primero selecciona un agente")
            return
        
        print(f"\n--- PROGRAMAR CONSULTA: {self.current_agent.agent_name} ---")
        
        topic = input("Tema de la consulta: ").strip()
        if not topic:
            print("❌ El tema es requerido")
            return
        
        days_str = input("Días desde hoy (default 1): ").strip()
        days = 1
        if days_str:
            try:
                days = int(days_str)
            except ValueError:
                print("⚠️  Días inválidos, usando 1 día")
        
        hour_str = input("Hora (0-23, default 10): ").strip()
        hour = 10
        if hour_str:
            try:
                hour = int(hour_str)
                if not (0 <= hour <= 23):
                    hour = 10
                    print("⚠️  Hora inválida, usando 10:00")
            except ValueError:
                print("⚠️  Hora inválida, usando 10:00")
        
        scheduled_time = datetime.now() + timedelta(days=days)
        scheduled_time = scheduled_time.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        duration_str = input("Duración en minutos (default 60): ").strip()
        duration = 60
        if duration_str:
            try:
                duration = int(duration_str)
            except ValueError:
                print("⚠️  Duración inválida, usando 60 minutos")
        
        # Schedule consultation
        item = self.agenda.schedule_consultation(
            agent_id=self.current_agent.agent_id,
            topic=topic,
            scheduled_time=scheduled_time,
            duration_minutes=duration
        )
        
        print(f"\n✅ Consulta programada!")
        print(f"   Tema: {topic}")
        print(f"   Fecha: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Duración: {duration} minutos")
    
    def view_progress(self):
        """View development progress"""
        if not self.current_agent:
            print("❌ Primero selecciona un agente")
            return
        
        print(f"\n--- PROGRESO: {self.current_agent.agent_name} ---")
        
        summary = self.agenda.get_progress_summary(self.current_agent.agent_id)
        
        print(f"\n📊 RESUMEN:")
        print(f"   Etapa: {self.current_agent.development_stage}")
        print(f"   Progreso: {self.current_agent.completion_percentage:.1f}%")
        print(f"   Consultas: {len(self.current_agent.consultations)}")
        
        print(f"\n📝 TAREAS:")
        print(f"   Total: {summary['tasks']['total']}")
        print(f"   Completadas: {summary['tasks']['completed']}")
        print(f"   En Progreso: {summary['tasks']['in_progress']}")
        print(f"   Pendientes: {summary['tasks']['pending']}")
        print(f"   Atrasadas: {summary['tasks']['overdue']}")
        print(f"   Tasa de completitud: {summary['completion_rate']:.1f}%")
        
        print(f"\n🎯 HITOS:")
        print(f"   Total: {summary['milestones']['total']}")
        print(f"   Completados: {summary['milestones']['completed']}")
        print(f"   Pendientes: {summary['milestones']['pending']}")
        
        print(f"\n⏰ TIEMPO:")
        print(f"   Estimado: {summary['hours']['estimated']:.1f}h")
        print(f"   Real: {summary['hours']['actual']:.1f}h")
        print(f"   Eficiencia: {summary['hours']['efficiency']:.1%}")
    
    def generate_report(self):
        """Generate development report"""
        if not self.current_agent:
            print("❌ Primero selecciona un agente")
            return
        
        print(f"\n--- REPORTE: {self.current_agent.agent_name} ---")
        
        report = self.builder.generate_report(self.current_agent.agent_id)
        
        print(f"\n📄 INFORMACIÓN GENERAL:")
        print(f"   Nombre: {report['agent_name']}")
        print(f"   Tipo: {report['agent_type']}")
        print(f"   Etapa: {report['development_stage']}")
        print(f"   Progreso: {report['completion_percentage']:.1f}%")
        print(f"   Creado: {datetime.fromisoformat(report['created_at']).strftime('%Y-%m-%d')}")
        print(f"   Actualizado: {datetime.fromisoformat(report['updated_at']).strftime('%Y-%m-%d')}")
        
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   Consultas: {report['total_consultations']}")
        print(f"   Capacidades: {report['capabilities_count']}")
        print(f"   Intents: {report['intents_count']}")
        print(f"   Workflows: {report['workflows_count']}")
        
        if report['consultation_history']:
            print(f"\n📚 HISTORIAL DE CONSULTAS:")
            for i, consult in enumerate(report['consultation_history'], 1):
                print(f"\n   {i}. {consult['topic']}")
                print(f"      Nivel: {consult['level']}")
                print(f"      Fecha: {datetime.fromisoformat(consult['timestamp']).strftime('%Y-%m-%d %H:%M')}")
                print(f"      Recomendaciones: {consult['recommendations_count']}")
                print(f"      Insights: {consult['insights_count']}")
    
    def run(self):
        """Run the interactive CLI"""
        self.print_header()
        
        while True:
            self.print_menu()
            
            try:
                choice = input("Selecciona una opción: ").strip()
                
                if choice == "1":
                    self.create_agent()
                elif choice == "2":
                    self.list_agents()
                elif choice == "3":
                    self.select_agent()
                elif choice == "4":
                    self.consult()
                elif choice == "5":
                    self.view_agenda()
                elif choice == "6":
                    self.create_task()
                elif choice == "7":
                    self.schedule_consultation()
                elif choice == "8":
                    self.view_progress()
                elif choice == "9":
                    self.generate_report()
                elif choice == "0":
                    print("\n👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción inválida")
                
                input("\nPresiona Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("\nPresiona Enter para continuar...")


def main():
    """Main entry point"""
    cli = AgentBuilderCLI()
    cli.run()


if __name__ == "__main__":
    main()
