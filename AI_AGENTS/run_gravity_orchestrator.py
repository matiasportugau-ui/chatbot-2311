#!/usr/bin/env python3
"""
Quick Start Script for Gravity Training Orchestrator
Ejecuta el flujo completo de análisis e integración del PR #87
"""

import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from AI_AGENTS.gravity_training_orchestrator import GravityTrainingOrchestrator


def print_banner():
    """Print welcome banner"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              🚀 GRAVITY TRAINING ORCHESTRATOR AGENT 🚀                       ║
║                                                                              ║
║           Automated Training System Integration for ChatBot BMC             ║
║                          Based on PR #87                                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def run_quick_start():
    """Run quick start workflow"""
    print_banner()
    
    print("\n🔧 Initializing Gravity Training Orchestrator...\n")
    
    # Initialize agent
    agent = GravityTrainingOrchestrator(
        workspace_path="/workspace",
        auto_approve=True,
        execution_mode="automated"
    )
    
    print("✅ Agent initialized successfully!")
    print(f"   Execution ID: {agent.execution_id}")
    print(f"   Output directory: {agent.output_dir}")
    
    # Step 1: Analyze PR #87
    print("\n" + "="*80)
    print("STEP 1: Analyzing PR #87")
    print("="*80 + "\n")
    
    try:
        analysis = agent.analyze_pr_87()
        print("✅ PR #87 analyzed successfully!")
        print(f"   - Files: {len(analysis.get('summary', {}).get('files', []))}")
        print(f"   - Additions: {analysis.get('summary', {}).get('additions', 0)}")
        print(f"   - Components: {len(analysis.get('components_identified', []))}")
    except Exception as e:
        print(f"❌ Error analyzing PR: {e}")
        return 1
    
    # Step 2: Generate Status Report
    print("\n" + "="*80)
    print("STEP 2: Generating Initial Status Report")
    print("="*80 + "\n")
    
    try:
        status_report = agent.generate_status_report()
        print(status_report)
    except Exception as e:
        print(f"❌ Error generating status report: {e}")
        return 1
    
    # Step 3: Execute Phase 0 (Planning)
    print("\n" + "="*80)
    print("STEP 3: Executing Phase 0 - Analysis & Planning")
    print("="*80 + "\n")
    
    try:
        phase_0_result = agent.execute_integration_phase("phase_0")
        
        if phase_0_result["status"] == "completed":
            print("\n✅ Phase 0 completed successfully!")
            print(f"   - Steps completed: {len(phase_0_result['steps_completed'])}")
            print(f"   - Steps failed: {len(phase_0_result['steps_failed'])}")
            
            # Show validation results
            print("\n   Validation Results:")
            for criterion, result in phase_0_result.get("validation_results", {}).items():
                icon = "✅" if result else "❌"
                print(f"   {icon} {criterion}")
        else:
            print(f"\n❌ Phase 0 failed: {phase_0_result['status']}")
            return 1
    except Exception as e:
        print(f"❌ Error executing Phase 0: {e}")
        return 1
    
    # Step 4: Show available outputs
    print("\n" + "="*80)
    print("STEP 4: Generated Outputs")
    print("="*80 + "\n")
    
    output_files = list(agent.output_dir.glob("*.*"))
    if output_files:
        print("📁 Files generated:")
        for file in output_files:
            size = file.stat().st_size
            print(f"   - {file.name} ({size} bytes)")
    else:
        print("   No output files found")
    
    # Step 5: Next steps
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80 + "\n")
    
    print("""
To continue with the full integration, you can:

1️⃣  Execute the complete integration flow:
   python AI_AGENTS/gravity_training_orchestrator.py --mode execute

2️⃣  Execute specific phases:
   python AI_AGENTS/gravity_training_orchestrator.py --mode execute --phase phase_1
   python AI_AGENTS/gravity_training_orchestrator.py --mode execute --phase phase_2
   etc.

3️⃣  Generate status reports:
   python AI_AGENTS/gravity_training_orchestrator.py --mode status

4️⃣  Review generated outputs:
   cat consolidation/training_integration/pr_87_analysis.json
   cat consolidation/training_integration/implementation_plan.json
   cat consolidation/training_integration/integration_checklist.json

5️⃣  View execution logs:
   tail -f consolidation/training_integration/logs/*.log
    """)
    
    print("\n✅ Quick start completed successfully!")
    print(f"📊 All outputs saved to: {agent.output_dir}")
    
    return 0


def interactive_menu():
    """Interactive menu for agent operations"""
    print_banner()
    
    agent = GravityTrainingOrchestrator(
        workspace_path="/workspace",
        auto_approve=True,
        execution_mode="automated"
    )
    
    while True:
        print("\n" + "="*80)
        print("GRAVITY TRAINING ORCHESTRATOR - Interactive Menu")
        print("="*80)
        print("\nSelect an option:")
        print("  1. Analyze PR #87")
        print("  2. Execute Phase 0 (Planning)")
        print("  3. Execute Phase 1 (Core System)")
        print("  4. Execute Phase 2 (Bot Integration)")
        print("  5. Execute Phase 3 (WhatsApp Integration)")
        print("  6. Execute Phase 4 (Automation)")
        print("  7. Execute Phase 5 (Production Validation)")
        print("  8. Execute ALL Phases (Full Integration)")
        print("  9. Generate Status Report")
        print("  10. Generate Handoff Package")
        print("  0. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            print("\n👋 Exiting... Goodbye!")
            break
        
        elif choice == "1":
            print("\n🔍 Analyzing PR #87...")
            analysis = agent.analyze_pr_87()
            print(json.dumps(analysis, indent=2))
        
        elif choice in ["2", "3", "4", "5", "6", "7"]:
            phase_map = {
                "2": "phase_0",
                "3": "phase_1",
                "4": "phase_2",
                "5": "phase_3",
                "6": "phase_4",
                "7": "phase_5"
            }
            phase_id = phase_map[choice]
            print(f"\n🚀 Executing {phase_id}...")
            result = agent.execute_integration_phase(phase_id)
            print(json.dumps(result, indent=2))
        
        elif choice == "8":
            print("\n🚀 Executing FULL Integration...")
            confirm = input("This will execute all phases. Continue? (yes/no): ").strip().lower()
            if confirm == "yes":
                result = agent.execute_full_integration()
                print(json.dumps(result, indent=2))
            else:
                print("❌ Cancelled")
        
        elif choice == "9":
            print("\n📊 Generating Status Report...")
            report = agent.generate_status_report()
            print(report)
        
        elif choice == "10":
            target_agent = input("Enter target agent name: ").strip()
            phase_id = input("Enter phase ID (e.g., phase_2): ").strip()
            print(f"\n📦 Generating handoff package for {target_agent}...")
            handoff = agent.generate_handoff_package(target_agent, phase_id)
            print(json.dumps(handoff, indent=2))
        
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gravity Training Orchestrator - Quick Start")
    parser.add_argument("--interactive", action="store_true",
                       help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        sys.exit(interactive_menu())
    else:
        sys.exit(run_quick_start())
