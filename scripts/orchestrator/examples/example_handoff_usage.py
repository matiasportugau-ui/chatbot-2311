#!/usr/bin/env python3
"""
Example: Using Agent Handoff System
Demonstrates how to execute phases with context handoff
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.orchestrator.main_orchestrator import MainOrchestrator
from scripts.orchestrator.context_manager import ContextManager
from scripts.orchestrator.state_manager import StateManager
from scripts.orchestrator.agent_handoff import AgentHandoff


def example_1_normal_execution():
    """Example 1: Normal execution without handoff"""
    print("="*60)
    print("Example 1: Normal Execution")
    print("="*60)
    
    orchestrator = MainOrchestrator()
    
    # Execute Phase 0 normally
    orchestrator.execute_phase(0, use_separate_agent=False)
    
    print("\n✅ Phase 0 executed normally")


def example_2_with_handoff_preparation():
    """Example 2: Execute with handoff preparation"""
    print("\n" + "="*60)
    print("Example 2: Execution with Handoff Preparation")
    print("="*60)
    
    orchestrator = MainOrchestrator()
    
    # Execute Phase 0 normally
    orchestrator.execute_phase(0, use_separate_agent=False)
    
    # Execute Phase 1 with handoff preparation
    orchestrator.execute_phase(1, use_separate_agent=True)
    
    print("\n✅ Phase 1 handoff prepared")
    print("   Check: consolidation/handoffs/handoff_phase_1.json")


def example_3_load_and_use_handoff():
    """Example 3: Load and use handoff package"""
    print("\n" + "="*60)
    print("Example 3: Load and Use Handoff Package")
    print("="*60)
    
    state_manager = StateManager()
    context_manager = ContextManager(state_manager)
    agent_handoff = AgentHandoff(context_manager, state_manager)
    
    # Load handoff for Phase 1
    try:
        handoff = agent_handoff.load_handoff(1)
        
        print(f"Execution ID: {handoff['execution_id']}")
        print(f"From Phase: {handoff['from_phase']}")
        print(f"To Phase: {handoff['to_phase']}")
        print(f"\nPrevious Phase Context Keys: {list(handoff['previous_phase_context'].keys())}")
        print(f"Shared Artifacts: {list(handoff['shared_artifacts'].keys())}")
        print(f"Global Context: {list(handoff['global_context'].keys())}")
        
        # Use context in your execution
        previous_context = handoff['previous_phase_context']
        shared_artifacts = handoff['shared_artifacts']
        
        print("\n✅ Handoff loaded successfully")
        print("   You can now use this context to execute Phase 1")
        
    except FileNotFoundError:
        print("⚠️  Handoff file not found. Run Example 2 first.")


def example_4_context_management():
    """Example 4: Manual context management"""
    print("\n" + "="*60)
    print("Example 4: Manual Context Management")
    print("="*60)
    
    state_manager = StateManager()
    context_manager = ContextManager(state_manager)
    
    # Add context to Phase 0
    context_manager.add_phase_context(0, {
        "discovery_complete": True,
        "repositories_found": 5,
        "components_identified": 7
    })
    
    # Add shared artifact
    context_manager.add_shared_artifact(
        "repository_list",
        ["repo1", "repo2", "repo3"],
        "List of repositories to consolidate"
    )
    
    # Set global context
    context_manager.set_global_context("execution_mode", "production")
    
    # Get context summary
    summary = context_manager.get_context_summary()
    print(f"Context Summary: {summary}")
    
    print("\n✅ Context managed successfully")


def example_5_export_context_for_agent():
    """Example 5: Export context for agent execution"""
    print("\n" + "="*60)
    print("Example 5: Export Context for Agent")
    print("="*60)
    
    state_manager = StateManager()
    context_manager = ContextManager(state_manager)
    
    # Export complete context package for Phase 1
    context_package = context_manager.export_context_for_agent(1)
    
    print(f"Context Package for Phase 1:")
    print(f"  - Execution ID: {context_package['execution_id']}")
    print(f"  - Completed Phases: {context_package['state_summary']['completed_phases']}")
    print(f"  - Progress: {context_package['state_summary']['progress']:.1f}%")
    print(f"  - Previous Context Keys: {list(context_package['previous_phase_context'].keys())}")
    
    print("\n✅ Context package exported")
    print("   This package contains everything needed to execute Phase 1")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Agent Handoff Examples")
    print("="*60)
    
    # Run examples
    example_4_context_management()
    example_1_normal_execution()
    example_2_with_handoff_preparation()
    example_3_load_and_use_handoff()
    example_5_export_context_for_agent()
    
    print("\n" + "="*60)
    print("Examples Complete")
    print("="*60)

