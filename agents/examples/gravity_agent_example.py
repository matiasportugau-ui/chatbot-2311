#!/usr/bin/env python3
"""
Gravity Agent Usage Examples
=============================

This file demonstrates various ways to use the Gravity Agent
for interpreting and orchestrating automated development.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.gravity_agent import GravityAgent, AgentMode


def example_1_interpret_only():
    """Example 1: Interpret project state without execution"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Interpret Project State")
    print("="*80 + "\n")
    
    agent = GravityAgent()
    interpretation = agent.interpret_project_state(deep_analysis=True)
    
    print(f"\n✅ Interpretation Complete")
    print(f"   Current State: {interpretation.current_state.value}")
    print(f"   Current Phase: {interpretation.current_phase}")
    print(f"   Blockers: {len(interpretation.blockers)}")
    print(f"   Recommendations: {len(interpretation.recommendations)}")
    
    return interpretation


def example_2_orchestrate_single_phase():
    """Example 2: Orchestrate a single phase"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Orchestrate Single Phase")
    print("="*80 + "\n")
    
    agent = GravityAgent()
    
    # First, interpret to understand state
    interpretation = agent.interpret_project_state()
    
    if interpretation.blockers:
        print("⚠️  Blockers detected. Cannot proceed.")
        return None
    
    # Execute current phase
    current_phase = interpretation.current_phase
    result = agent.orchestrate_development(
        target_phase=current_phase,
        auto_approve=True,
        max_phases=1
    )
    
    print(f"\n✅ Execution Complete")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Phases Executed: {result.get('phases_executed', 0)}")
    
    return result


def example_3_full_cycle():
    """Example 3: Run complete interpret-orchestrate-monitor cycle"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Full Cycle Execution")
    print("="*80 + "\n")
    
    agent = GravityAgent()
    
    # Run full cycle for phases 0-2
    result = agent.run_full_cycle(
        start_phase=0,
        end_phase=2,
        auto_approve=True
    )
    
    print(f"\n✅ Full Cycle Complete")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Duration: {result.get('cycle_duration', 'N/A')}")
    
    return result


def example_4_monitor_execution():
    """Example 4: Monitor ongoing execution"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Monitor Execution")
    print("="*80 + "\n")
    
    agent = GravityAgent()
    monitoring_result = agent.monitor_execution()
    
    print(f"\n✅ Monitoring Complete")
    print(f"   Overall Status: {monitoring_result.get('overall_status', 'N/A')}")
    print(f"   Current Phase: {monitoring_result.get('current_phase', 'N/A')}")
    
    return monitoring_result


def example_5_adapt_plan():
    """Example 5: Adapt plan based on new context"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Adapt Plan")
    print("="*80 + "\n")
    
    agent = GravityAgent()
    
    # Simulate new context (e.g., urgent issue detected)
    new_context = {
        "urgent_issues": ["Critical bug in Phase 3"],
        "dependency_changes": ["New dependency added"]
    }
    
    adaptation_result = agent.adapt_plan(new_context)
    
    print(f"\n✅ Adaptation Complete")
    print(f"   Adaptations: {len(adaptation_result.get('adaptations', []))}")
    
    return adaptation_result


def example_6_save_report():
    """Example 6: Generate and save report"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Generate Report")
    print("="*80 + "\n")
    
    agent = GravityAgent()
    
    # Run some operations
    interpretation = agent.interpret_project_state()
    
    # Save report
    report_path = agent.save_report("example_report.json")
    
    print(f"\n✅ Report Saved")
    print(f"   Path: {report_path}")
    
    return report_path


def main():
    """Run all examples"""
    print("="*80)
    print("GRAVITY AGENT - USAGE EXAMPLES")
    print("="*80)
    
    examples = [
        ("Interpret Only", example_1_interpret_only),
        ("Orchestrate Single Phase", example_2_orchestrate_single_phase),
        ("Full Cycle", example_3_full_cycle),
        ("Monitor Execution", example_4_monitor_execution),
        ("Adapt Plan", example_5_adapt_plan),
        ("Save Report", example_6_save_report),
    ]
    
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nSelect example to run (1-6) or 'all' for all examples:")
    choice = input("> ").strip().lower()
    
    if choice == "all":
        for name, func in examples:
            try:
                print(f"\n{'='*80}")
                print(f"Running: {name}")
                print('='*80)
                func()
            except Exception as e:
                print(f"❌ Error in {name}: {e}")
                import traceback
                traceback.print_exc()
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        idx = int(choice) - 1
        name, func = examples[idx]
        try:
            func()
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
