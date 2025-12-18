#!/usr/bin/env python3
"""
Gravity Orchestrator Agent
Specialist in interpreting and orchestrating the automated development of the project.
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure we can import from scripts
sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from scripts.orchestrator.main_orchestrator import MainOrchestrator
    from scripts.orchestrator.state_manager import StateManager
    from scripts.orchestrator.status_reporter import StatusReporter
except ImportError as e:
    print(f"Error importing Orchestrator components: {e}")
    sys.exit(1)

class GravityOrchestratorAgent:
    """
    Gravity Agent: specialized in interpreting and orchestrating project development.
    """
    
    def __init__(self, mode: str = "orchestrate"):
        self.mode = mode
        self.orchestrator = MainOrchestrator()
        self.state_manager = StateManager()
        self.status_reporter = StatusReporter(self.state_manager, None)
        
    def interpret_state(self) -> str:
        """
        Interprets the current state of the project and returns a summary.
        """
        print("Gravity Agent: Interpreting project state...")
        
        try:
            current_phase = self.state_manager.get_current_phase()
            execution_id = self.state_manager.get_execution_id()
            overall_status = self.state_manager.get_overall_status()
            
            summary = [
                f"📊 Project Status Interpretation",
                f"--------------------------------",
                f"🆔 Execution ID: {execution_id}",
                f"🔄 Current Phase: {current_phase}",
                f"🚦 Overall Status: {overall_status}",
                "",
                "Phase Statuses:"
            ]
            
            # Get details for recent phases
            for i in range(max(0, current_phase - 2), current_phase + 1):
                status = self.state_manager.get_phase_status(i)
                summary.append(f"  - Phase {i}: {status}")
                if status == "failed":
                    errors = self.state_manager.get_phase_errors(i)
                    if errors:
                        summary.append(f"    ❌ Errors: {errors}")
            
            return "\n".join(summary)
            
        except Exception as e:
            return f"Error interpreting state: {str(e)}"

    def orchestrate_development(self, auto_fix: bool = True) -> bool:
        """
        Orchestrates the development process by running the MainOrchestrator.
        """
        print("Gravity Agent: Orchestrating development process...")
        
        # Interpret before starting
        print(self.interpret_state())
        
        try:
            if self.mode == "dry-run":
                print("Gravity Agent: Running in DRY-RUN mode. No changes will be applied.")
                return True
                
            success = self.orchestrator.run()
            
            if success:
                print("Gravity Agent: Development orchestration completed successfully! 🚀")
            else:
                print("Gravity Agent: Orchestration stopped due to errors.")
                # Here we could implement "auto_fix" logic using other agents
                if auto_fix:
                    print("Gravity Agent: Attempting analysis for potential fixes...")
                    # Future: Invoke fixer agents
            
            return success
            
        except Exception as e:
            print(f"Gravity Agent: Critical failure during orchestration: {e}")
            return False

    def run(self):
        """
        Main execution method.
        """
        if self.mode == "interpret":
            print(self.interpret_state())
        elif self.mode == "orchestrate":
            self.orchestrate_development()
        else:
            print(f"Unknown mode: {self.mode}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gravity Orchestrator Agent")
    parser.add_argument("--mode", choices=["interpret", "orchestrate", "dry-run"], 
                        default="orchestrate", help="Operation mode")
    
    args = parser.parse_args()
    
    agent = GravityOrchestratorAgent(mode=args.mode)
    agent.run()
