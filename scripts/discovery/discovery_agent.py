#!/usr/bin/env python3
"""
DiscoveryAgent: Phase 0 BMC Discovery & Assessment Agent
Orchestrates all Phase 0 discovery tasks
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class DiscoveryAgent:
    """
    DiscoveryAgent for Phase 0: BMC Discovery & Assessment
    
    Combines technical discovery with BMC domain discovery:
    - Repository and workspace analysis
    - BMC component inventory
    - Integration validation
    - Quotation engine assessment
    - Production gap identification
    - Baseline creation
    """
    
    def __init__(self, workspace_path: str = "/Users/matias/chatbot2511/chatbot-2311",
                 output_dir: str = "consolidation/discovery"):
        self.workspace_path = Path(workspace_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.scripts_dir = Path(__file__).parent
        self.results = {}
    
    def execute_phase_0(self) -> Dict[str, Any]:
        """Execute all Phase 0 tasks"""
        print("=" * 80)
        print("🔍 Phase 0: BMC Discovery & Assessment")
        print("=" * 80)
        print()
        
        execution_results = {
            "phase": 0,
            "agent": "DiscoveryAgent",
            "start_time": datetime.now().isoformat(),
            "tasks": {},
            "outputs": [],
            "status": "in_progress"
        }
        
        try:
            # T0.1: Analyze repositories
            print("📦 T0.1: Analyzing repositories...")
            result = self._execute_task("T0.1", "analyze_repositories.py", [])
            execution_results["tasks"]["T0.1"] = result
            if result["success"]:
                execution_results["outputs"].append(result["output"])
            
            # T0.2: Analyze workspace
            print("📁 T0.2: Analyzing workspace...")
            result = self._execute_task("T0.2", "analyze_workspace.py", [
                "--workspace", str(self.workspace_path)
            ])
            execution_results["tasks"]["T0.2"] = result
            if result["success"]:
                execution_results["outputs"].append(result["output"])
            
            # T0.3: Inventory BMC components
            print("📋 T0.3: Inventorying BMC components...")
            result = self._execute_task("T0.3", "inventory_bmc_components.py", [
                "--workspace", str(self.workspace_path)
            ])
            execution_results["tasks"]["T0.3"] = result
            if result["success"]:
                execution_results["outputs"].append(result["output"])
            
            # T0.4: Validate integrations
            print("🔌 T0.4: Validating integrations...")
            result = self._execute_task("T0.4", "validate_integrations.py", [
                "--workspace", str(self.workspace_path)
            ])
            execution_results["tasks"]["T0.4"] = result
            if result["success"]:
                execution_results["outputs"].append(result["output"])
            
            # T0.5: Assess quotation engine
            print("💰 T0.5: Assessing quotation engine...")
            result = self._execute_task("T0.5", "assess_quotation_engine.py", [
                "--workspace", str(self.workspace_path)
            ])
            execution_results["tasks"]["T0.5"] = result
            if result["success"]:
                execution_results["outputs"].append(result["output"])
            
            # T0.6: Identify production gaps
            print("⚠️  T0.6: Identifying production gaps...")
            result = self._execute_task("T0.6", "identify_production_gaps.py", [
                "--discovery-dir", str(self.output_dir)
            ])
            execution_results["tasks"]["T0.6"] = result
            if result["success"]:
                execution_results["outputs"].append(result["output"])
            
            # T0.7: Create production baseline
            print("📊 T0.7: Creating production baseline...")
            result = self._execute_task("T0.7", "create_production_baseline.py", [
                "--discovery-dir", str(self.output_dir)
            ])
            execution_results["tasks"]["T0.7"] = result
            if result["success"]:
                execution_results["outputs"].append(result["output"])
            
            # Determine overall status
            all_success = all(task.get("success", False) for task in execution_results["tasks"].values())
            execution_results["status"] = "completed" if all_success else "partial"
            execution_results["end_time"] = datetime.now().isoformat()
            
            # Save execution summary
            summary_file = self.output_dir / "phase_0_execution_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(execution_results, f, indent=2, ensure_ascii=False)
            
            print()
            print("=" * 80)
            if all_success:
                print("✅ Phase 0 completed successfully!")
            else:
                print("⚠️  Phase 0 completed with some issues")
            print("=" * 80)
            print(f"📄 Execution summary: {summary_file}")
            
            return execution_results
            
        except Exception as e:
            execution_results["status"] = "failed"
            execution_results["error"] = str(e)
            execution_results["end_time"] = datetime.now().isoformat()
            print(f"❌ Phase 0 failed: {e}")
            return execution_results
    
    def _execute_task(self, task_id: str, script_name: str, args: List[str]) -> Dict[str, Any]:
        """Execute a discovery task script"""
        script_path = self.scripts_dir / script_name
        
        if not script_path.exists():
            return {
                "task_id": task_id,
                "success": False,
                "error": f"Script not found: {script_path}"
            }
        
        try:
            # Determine output file based on task
            output_map = {
                "T0.1": "repository_analysis.json",
                "T0.2": "workspace_analysis.json",
                "T0.3": "bmc_inventory.json",
                "T0.4": "integrations_status.json",
                "T0.5": "quotation_assessment.json",
                "T0.6": "production_gaps.json",
                "T0.7": "production_baseline.json"
            }
            
            output_file = self.output_dir / output_map.get(task_id, "unknown.json")
            
            # Build command
            cmd = [sys.executable, str(script_path)] + args + [
                "--output", str(output_file)
            ]
            
            # Execute script
            result = subprocess.run(
                cmd,
                cwd=str(self.workspace_path),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                return {
                    "task_id": task_id,
                    "success": True,
                    "output": str(output_file),
                    "message": "Task completed successfully"
                }
            else:
                return {
                    "task_id": task_id,
                    "success": False,
                    "error": result.stderr,
                    "stdout": result.stdout
                }
        
        except subprocess.TimeoutExpired:
            return {
                "task_id": task_id,
                "success": False,
                "error": "Script execution timed out"
            }
        except Exception as e:
            return {
                "task_id": task_id,
                "success": False,
                "error": str(e)
            }
    
    def get_results(self) -> Dict[str, Any]:
        """Get all discovery results"""
        results = {}
        
        result_files = {
            "repository_analysis": "repository_analysis.json",
            "workspace_analysis": "workspace_analysis.json",
            "bmc_inventory": "bmc_inventory.json",
            "integrations_status": "integrations_status.json",
            "quotation_assessment": "quotation_assessment.json",
            "production_gaps": "production_gaps.json",
            "production_baseline": "production_baseline.json"
        }
        
        for key, filename in result_files.items():
            file_path = self.output_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        results[key] = json.load(f)
                except Exception as e:
                    results[key] = {"error": str(e)}
        
        return results


def main():
    """Main entry point for DiscoveryAgent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DiscoveryAgent: Phase 0 BMC Discovery")
    parser.add_argument("--workspace", "-w", default="/Users/matias/chatbot2511/chatbot-2311",
                       help="Workspace path")
    parser.add_argument("--output-dir", "-o", default="consolidation/discovery",
                       help="Output directory for discovery results")
    
    args = parser.parse_args()
    
    # Create and execute agent
    agent = DiscoveryAgent(
        workspace_path=args.workspace,
        output_dir=args.output_dir
    )
    
    # Execute Phase 0
    results = agent.execute_phase_0()
    
    # Return exit code
    return 0 if results.get("status") in ["completed", "partial"] else 1


if __name__ == "__main__":
    sys.exit(main())

