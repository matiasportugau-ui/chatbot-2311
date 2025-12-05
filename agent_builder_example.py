#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Builder Integration Example
Demonstrates integration with the existing agent system
"""

import sys
import os

# Add parent directory to path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_builder import get_agent_builder, AgentType
from agent_builder_agenda import get_agent_builder_agenda, TaskPriority
from datetime import datetime, timedelta


def example_sales_agent_development():
    """
    Example: Developing a sales agent using the builder
    """
    print("\n" + "=" * 70)
    print("  EXAMPLE: Developing a Sales Agent with Agent Builder")
    print("=" * 70)
    
    builder = get_agent_builder()
    agenda = get_agent_builder_agenda()
    
    # Step 1: Create the agent blueprint
    print("\n📝 Step 1: Creating Sales Agent Blueprint")
    sales_agent = builder.create_agent_blueprint(
        agent_name="BMC Sales Agent",
        agent_type=AgentType.SALES,
        initial_capabilities=[
            "crear_cotizaciones",
            "responder_consultas",
            "recomendar_productos"
        ]
    )
    
    print(f"✅ Created: {sales_agent.agent_name}")
    print(f"   Type: {sales_agent.agent_type.value}")
    print(f"   ID: {sales_agent.agent_id}")
    
    # Step 2: First consultation - Basic setup
    print("\n💬 Step 2: Initial Consultation - Basic Setup")
    c1 = builder.consult(
        sales_agent.agent_id,
        "¿Cómo configuro el agente de ventas para BMC Uruguay?"
    )
    
    print(f"   Level: {c1.level.value.upper()}")
    print(f"   Recommendations: {len(c1.recommendations)}")
    print("\n   Top 3 Recommendations:")
    for i, rec in enumerate(c1.recommendations[:3], 1):
        print(f"   {i}. {rec}")
    
    # Step 3: Create development tasks based on recommendations
    print("\n✅ Step 3: Creating Development Tasks")
    
    tasks = [
        agenda.create_task(
            agent_id=sales_agent.agent_id,
            title="Configurar agent_config.json para sales agent",
            description="Añadir configuración del sales agent al config",
            priority=TaskPriority.HIGH,
            due_date=datetime.now() + timedelta(days=2),
            estimated_hours=1.0,
            tags=["configuration", "setup"]
        ),
        agenda.create_task(
            agent_id=sales_agent.agent_id,
            title="Implementar lógica de routing",
            description="Routing basado en intents de ventas",
            priority=TaskPriority.HIGH,
            due_date=datetime.now() + timedelta(days=3),
            estimated_hours=3.0,
            tags=["routing", "core"]
        ),
        agenda.create_task(
            agent_id=sales_agent.agent_id,
            title="Definir workflows de cotización",
            description="Workflows para generación automática de cotizaciones",
            priority=TaskPriority.MEDIUM,
            due_date=datetime.now() + timedelta(days=5),
            estimated_hours=4.0,
            tags=["workflows", "quotes"]
        )
    ]
    
    print(f"   Created {len(tasks)} tasks")
    for task in tasks:
        print(f"   • {task.title} (Priority: {task.priority.value})")
    
    # Step 4: Schedule next consultation
    print("\n📅 Step 4: Scheduling Next Consultation")
    next_consultation = agenda.schedule_consultation(
        agent_id=sales_agent.agent_id,
        topic="Integración avanzada de workflows",
        scheduled_time=datetime.now() + timedelta(days=4),
        duration_minutes=90,
        notes="Discutir integración con sistema de cotizaciones existente"
    )
    
    print(f"   Scheduled: {next_consultation.description}")
    print(f"   Time: {next_consultation.scheduled_time.strftime('%Y-%m-%d %H:%M')}")
    
    # Step 5: Create milestone
    print("\n🎯 Step 5: Creating Development Milestone")
    milestone = agenda.create_milestone(
        agent_id=sales_agent.agent_id,
        title="Sales Agent MVP",
        description="Versión mínima viable del agente de ventas",
        target_date=datetime.now() + timedelta(days=14),
        criteria=[
            "Routing configurado y funcionando",
            "Workflows de cotización implementados",
            "Integración con sistema existente",
            "Tests básicos pasando",
            "Documentación inicial completa"
        ]
    )
    
    print(f"   Milestone: {milestone.title}")
    print(f"   Target: {milestone.target_date.strftime('%Y-%m-%d')}")
    print(f"   Criteria: {len(milestone.criteria)} items")
    
    # Step 6: Second consultation - Intermediate level
    print("\n💬 Step 6: Second Consultation - Advanced Integration")
    c2 = builder.consult(
        sales_agent.agent_id,
        "¿Cómo integro el agente con el sistema de cotizaciones existente?"
    )
    
    print(f"   Level: {c2.level.value.upper()}")
    print(f"   Insights: {len(c2.insights)}")
    print("\n   Key Insights:")
    for i, insight in enumerate(c2.insights[:2], 1):
        print(f"   {i}. {insight}")
    
    if c2.code_examples:
        print(f"\n   Code Examples: {len(c2.code_examples)}")
        print(f"   First Example: {c2.code_examples[0]['title']}")
    
    # Step 7: View progress
    print("\n📊 Step 7: Checking Development Progress")
    summary = agenda.get_progress_summary(sales_agent.agent_id)
    
    print(f"   Development Stage: {sales_agent.development_stage}")
    print(f"   Completion: {sales_agent.completion_percentage:.1f}%")
    print(f"   Consultations: {len(sales_agent.consultations)}")
    print(f"   Tasks: {summary['tasks']['total']} (Pending: {summary['tasks']['pending']})")
    print(f"   Milestones: {summary['milestones']['total']}")
    
    # Step 8: Get suggestions for next consultation
    print("\n💡 Step 8: Intelligent Suggestions for Next Steps")
    suggestions = agenda.suggest_next_consultation_topics(sales_agent.agent_id)
    
    print("   Suggested consultation topics:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")
    
    # Step 9: Generate comprehensive report
    print("\n📄 Step 9: Generating Development Report")
    report = builder.generate_report(sales_agent.agent_id)
    
    print(f"   Agent: {report['agent_name']}")
    print(f"   Type: {report['agent_type']}")
    print(f"   Stage: {report['development_stage']}")
    print(f"   Progress: {report['completion_percentage']:.1f}%")
    print(f"   Total Consultations: {report['total_consultations']}")
    print(f"   Capabilities: {report['capabilities_count']}")
    
    print("\n" + "=" * 70)
    print("  ✅ Example Complete!")
    print("=" * 70)
    print("\n  The Sales Agent is now in development with:")
    print(f"  • {len(sales_agent.consultations)} consultations completed")
    print(f"  • {summary['tasks']['total']} development tasks")
    print(f"  • {summary['milestones']['total']} milestone defined")
    print(f"  • Progressing through {sales_agent.development_stage} stage")
    print("\n  Next Steps:")
    print("  1. Complete the development tasks")
    print("  2. Attend scheduled consultations")
    print("  3. Progress to advanced and expert levels")
    print("  4. Integrate with the automated agent system")
    print("=" * 70 + "\n")
    
    return sales_agent


def example_workflow_integration():
    """
    Example: Using builder with workflow integration
    """
    print("\n" + "=" * 70)
    print("  EXAMPLE: Agent Builder with Workflow Integration")
    print("=" * 70)
    
    builder = get_agent_builder()
    
    # Create workflow-focused agent
    print("\n📝 Creating Workflow Agent")
    workflow_agent = builder.create_agent_blueprint(
        agent_name="Workflow Automation Agent",
        agent_type=AgentType.CUSTOM,
        initial_capabilities=[
            "multi_step_workflows",
            "conditional_branching",
            "parallel_execution"
        ]
    )
    
    print(f"✅ Created: {workflow_agent.agent_name}")
    
    # Multiple consultations to reach advanced level
    print("\n💬 Progressive Consultations on Workflows")
    
    topics = [
        "Workflow basics and setup",
        "Conditional branching in workflows",
        "Parallel task execution",
        "Error handling in workflows",
        "Advanced workflow patterns"
    ]
    
    for i, topic in enumerate(topics, 1):
        consultation = builder.consult(workflow_agent.agent_id, topic)
        print(f"\n   Consultation {i}: {topic}")
        print(f"   Level: {consultation.level.value.upper()}")
        print(f"   Recommendations: {len(consultation.recommendations)}")
        
        # Refresh agent to see stage progression
        workflow_agent = builder.get_blueprint(workflow_agent.agent_id)
        print(f"   Stage: {workflow_agent.development_stage} ({workflow_agent.completion_percentage:.0f}%)")
    
    print("\n📊 Final State:")
    print(f"   Total Consultations: {len(workflow_agent.consultations)}")
    print(f"   Development Stage: {workflow_agent.development_stage}")
    print(f"   Completion: {workflow_agent.completion_percentage:.1f}%")
    
    print("\n" + "=" * 70 + "\n")
    
    return workflow_agent


def main():
    """Run integration examples"""
    print("\n" + "=" * 70)
    print("  AGENT BUILDER - Integration Examples")
    print("=" * 70)
    print("\n  These examples demonstrate how to use the Agent Builder")
    print("  to develop agents with progressive consultations.")
    print("\n" + "=" * 70)
    
    # Run examples
    sales_agent = example_sales_agent_development()
    workflow_agent = example_workflow_integration()
    
    print("\n" + "=" * 70)
    print("  📚 For More Information")
    print("=" * 70)
    print("\n  Documentation: AGENT_BUILDER_GUIDE.md")
    print("  Interactive CLI: python agent_builder_cli.py")
    print("  Tests: python test_agent_builder.py")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
