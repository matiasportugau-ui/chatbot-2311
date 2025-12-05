#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Builder - Visual Demo
Shows the progression of consultations with visual output
"""

from agent_builder import get_agent_builder, AgentType
from agent_builder_agenda import get_agent_builder_agenda, TaskPriority
from datetime import datetime, timedelta


def print_banner(text):
    """Print a fancy banner"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_section(emoji, title):
    """Print a section header"""
    print(f"\n{emoji} {title}")
    print("-" * 70)


def demo_progressive_consultations():
    """Demonstrate progressive consultation system"""
    
    print_banner("🤖 Agent Builder - Progressive Consultation Demo")
    
    builder = get_agent_builder()
    agenda = get_agent_builder_agenda()
    
    # Create agent
    print_section("📝", "Step 1: Creating Agent Blueprint")
    agent = builder.create_agent_blueprint(
        agent_name="Demo Sales Agent",
        agent_type=AgentType.SALES,
        initial_capabilities=["quotes", "sales", "support"]
    )
    print(f"✓ Created: {agent.agent_name}")
    print(f"  Type: {agent.agent_type.value}")
    print(f"  Stage: {agent.development_stage} ({agent.completion_percentage:.0f}%)")
    
    # Consultation topics
    topics = [
        ("How do I configure my sales agent?", "Basic Setup"),
        ("How can I integrate with the quote system?", "Integration"),
        ("What's the best way to handle errors?", "Error Handling"),
        ("How do I implement workflows?", "Workflows"),
        ("How can I optimize performance?", "Optimization")
    ]
    
    # Progressive consultations
    for i, (topic, label) in enumerate(topics, 1):
        print_section("💬", f"Consultation {i}: {label}")
        
        consultation = builder.consult(agent.agent_id, topic)
        
        # Show progression
        agent = builder.get_blueprint(agent.agent_id)
        
        print(f"Topic: {topic}")
        print(f"Level: {consultation.level.value.upper()} ⭐" * (i if i <= 4 else 4))
        print(f"Stage: {agent.development_stage.upper()} ({agent.completion_percentage:.0f}%)")
        
        # Show progress bar
        progress = int(agent.completion_percentage / 5)
        bar = "█" * progress + "░" * (20 - progress)
        print(f"Progress: [{bar}] {agent.completion_percentage:.0f}%")
        
        # Show top recommendations
        print(f"\nTop 3 Recommendations:")
        for j, rec in enumerate(consultation.recommendations[:3], 1):
            print(f"  {j}. {rec}")
        
        # Show insights at intermediate+ levels
        if consultation.insights:
            print(f"\nKey Insights:")
            for insight in consultation.insights[:2]:
                print(f"  💡 {insight}")
        
        # Show code example count
        if consultation.code_examples:
            print(f"\n📝 Includes {len(consultation.code_examples)} code example(s)")
        
        print()
    
    # Final summary
    print_section("📊", "Final Development Summary")
    
    summary = agenda.get_progress_summary(agent.agent_id)
    report = builder.generate_report(agent.agent_id)
    
    print(f"Agent: {report['agent_name']}")
    print(f"Stage: {report['development_stage'].upper()}")
    print(f"Completion: {report['completion_percentage']:.0f}%")
    print(f"Total Consultations: {report['total_consultations']}")
    print(f"Capabilities: {report['capabilities_count']}")
    
    # Consultation history
    print(f"\n📚 Consultation History:")
    for i, c in enumerate(report['consultation_history'], 1):
        print(f"  {i}. {c['topic'][:50]}... ({c['level'].upper()})")
    
    # Next steps
    print(f"\n➡️  Next Steps:")
    suggestions = agenda.suggest_next_consultation_topics(agent.agent_id)
    for i, suggestion in enumerate(suggestions[:3], 1):
        print(f"  {i}. {suggestion}")
    
    print_banner("✅ Demo Complete!")
    
    print("The Agent Builder has guided you through 5 consultations,")
    print("progressing from BASIC to ADVANCED levels automatically.")
    print()
    print("Each consultation provided:")
    print("  ✓ Level-appropriate recommendations")
    print("  ✓ Working code examples")
    print("  ✓ Actionable insights")
    print("  ✓ Clear next steps")
    print()
    print("Your agent is now at the TESTING stage (75% complete)!")
    print()
    print("Try it yourself:")
    print("  $ python agent_builder_cli.py")
    print()


if __name__ == "__main__":
    demo_progressive_consultations()
