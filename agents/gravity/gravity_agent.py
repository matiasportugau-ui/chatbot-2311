#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gravity Agent
=============

Specialist Agent in "Gravity Mode" designed to:
1. Interpret the project state, structure, and intent.
2. Orchestrate the automated development process.

"Gravity" refers to the central force that pulls together all aspects of development:
- Codebase understanding
- Task planning
- Execution orchestration
- Quality assurance
- Deployment

Usage:
    from agents.gravity.gravity_agent import GravityAgent
    agent = GravityAgent()
    agent.run_gravity_mode()
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import existing orchestration tools if available
try:
    from scripts.orchestrator.main_orchestrator import MainOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False

# Import existing AI agent base if available
try:
    from AI_AGENTS.EXECUTOR.execution_ai_agent import ExecutionAIAgent
    BASE_AGENT_AVAILABLE = True
except ImportError:
    BASE_AGENT_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [GRAVITY] - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / "system/logs/gravity_agent.log")
    ]
)
logger = logging.getLogger("GravityAgent")

class GravityState(Enum):
    INITIALIZING = "initializing"
    INTERPRETING = "interpreting"
    PLANNING = "planning"
    ORCHESTRATING = "orchestrating"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    FAILED = "failed"
    IDLE = "idle"

class GravityAgent:
    """
    The Gravity Agent: A specialist in interpreting and orchestrating automated development.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.root_dir = project_root
        self.state = GravityState.INITIALIZING
        self.context = {}
        self.execution_plan = []
        self.orchestrator = MainOrchestrator() if ORCHESTRATOR_AVAILABLE else None
        self.ai_agent = ExecutionAIAgent() if BASE_AGENT_AVAILABLE else None
        
        self.config = self._load_config(config_path)
        logger.info("Gravity Agent initialized.")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration or use defaults"""
        # Default config
        config = {
            "mode": "gravity",
            "auto_approve": True,
            "max_concurrent_tasks": 3,
            "polling_interval": 10,
            "log_level": "INFO"
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    config.update(user_config)
            except Exception as e:
                logger.error(f"Failed to load config from {config_path}: {e}")
        
        return config

    def interpret_project(self) -> Dict:
        """
        Interprets the current state of the project.
        Analyzes directory structure, recent changes, and active configurations.
        """
        self.state = GravityState.INTERPRETING
        logger.info("Interpreting project state...")
        
        # Read execution reports if available
        execution_report = self._read_execution_report()
        
        interpretation = {
            "timestamp": datetime.now().isoformat(),
            "structure_analysis": self._analyze_structure(),
            "orchestrator_status": "Available" if self.orchestrator else "Unavailable",
            "active_agents": self._scan_agents(),
            "git_status": self._check_git_status(),
            "previous_execution": execution_report
        }
        
        if execution_report:
            logger.info(f"Previous execution status: {execution_report.get('status', 'Unknown')}")
        
        self.context["interpretation"] = interpretation
        logger.info("Project interpretation completed.")
        return interpretation

    def _analyze_structure(self) -> Dict:
        """Analyze key project directories"""
        key_dirs = ["scripts", "src", "agents", "AI_AGENTS", "config", "system"]
        analysis = {}
        for d in key_dirs:
            path = self.root_dir / d
            if path.exists():
                analysis[d] = {
                    "exists": True,
                    "file_count": len(list(path.glob("**/*"))) if path.is_dir() else 0
                }
            else:
                analysis[d] = {"exists": False}
        return analysis

    def _scan_agents(self) -> List[str]:
        """Scan for available agent implementations"""
        agents = []
        if (self.root_dir / "agents").exists():
            agents.extend([p.name for p in (self.root_dir / "agents").glob("*.py")])
        if (self.root_dir / "AI_AGENTS").exists():
            agents.extend([p.name for p in (self.root_dir / "AI_AGENTS").glob("*.py")])
        return agents

    def _check_git_status(self) -> str:
        """Check basic git status if available"""
        if (self.root_dir / ".git").exists():
            return "Git repository detected"
        return "Not a git repository"
        
    def _read_execution_report(self) -> Optional[Dict]:
        """Read the last execution report"""
        report_path = self.root_dir / "EXECUTION_COMPLETE_REPORT.md"
        if report_path.exists():
            try:
                content = report_path.read_text(encoding="utf-8")
                # Simple parsing for demonstration
                status = "Unknown"
                if "SUCCESS" in content:
                    status = "Success"
                elif "FAILED" in content:
                    status = "Failed"
                return {"path": str(report_path), "status": status, "summary": content[:200] + "..."}
            except Exception as e:
                logger.warning(f"Failed to read execution report: {e}")
        return None

    def plan_development(self, goal: str = "Automated System Execution") -> List[Dict]:
        """
        Generates a high-level development or execution plan based on interpretation.
        """
        self.state = GravityState.PLANNING
        logger.info(f"Planning development for goal: {goal}")
        
        # Adjust plan based on interpretation
        plan = [
            {
                "id": "init_verify",
                "name": "Initial System Verification",
                "type": "verification",
                "priority": "high",
                "status": "pending"
            }
        ]
        
        if self.orchestrator:
             plan.append({
                "id": "orchestrator_run",
                "name": "Run Main Orchestrator",
                "type": "execution",
                "priority": "critical",
                "status": "pending",
                "details": {"phases": "all"}
            })
        else:
            plan.append({
                "id": "manual_simulation",
                "name": "Simulate Execution (Orchestrator Missing)",
                "type": "simulation",
                "priority": "medium",
                "status": "pending"
            })
            
        plan.append({
            "id": "post_analysis",
            "name": "Post-Execution Analysis",
            "type": "analysis",
            "priority": "medium",
            "status": "pending"
        })
        
        self.execution_plan = plan
        self.context["plan"] = plan
        logger.info(f"Generated plan with {len(plan)} tasks.")
        return plan

    def orchestrate_execution(self) -> bool:
        """
        Orchestrates the execution of the planned tasks.
        """
        self.state = GravityState.ORCHESTRATING
        logger.info("Starting orchestration...")
        
        if not self.execution_plan:
            logger.warning("No plan to execute. Running planning phase first.")
            self.plan_development()
            
        success = True
        
        for task in self.execution_plan:
            logger.info(f"Executing task: {task['name']} ({task['id']})")
            task['status'] = 'in_progress'
            
            task_success = self._execute_task(task)
            
            if task_success:
                task['status'] = 'completed'
                logger.info(f"Task {task['name']} completed successfully.")
            else:
                task['status'] = 'failed'
                logger.error(f"Task {task['name']} failed.")
                success = False
                if task['priority'] == 'critical':
                    logger.error("Critical task failed. Stopping execution.")
                    break
        
        self.state = GravityState.COMPLETED if success else GravityState.FAILED
        return success

    def _execute_task(self, task: Dict) -> bool:
        """Execute a single planned task"""
        task_id = task['id']
        
        if task_id == "init_verify":
            return self._verify_system_integrity()
            
        elif task_id == "orchestrator_run":
            if self.orchestrator:
                try:
                    logger.info("Handing off to Main Orchestrator...")
                    return self.orchestrator.run()
                except Exception as e:
                    logger.error(f"Orchestrator execution failed: {e}")
                    return False
            else:
                return False

        elif task_id == "manual_simulation":
            logger.info("Simulating execution steps...")
            time.sleep(1)
            return True
                
        elif task_id == "post_analysis":
            logger.info("Performing post-execution analysis...")
            # Here we could update the EXECUTION_COMPLETE_REPORT.md
            return True
            
        return False

    def _verify_system_integrity(self) -> bool:
        """Verify essential system components"""
        # Check for essential files
        required_files = ["requirements.txt", "package.json"]
        missing = [f for f in required_files if not (self.root_dir / f).exists()]
        
        if missing:
            logger.warning(f"Missing essential files: {missing}")
            # In gravity mode, we might try to recover, but for now just warn
            return False
        
        return True

    def run_gravity_mode(self):
        """
        Main entry point for Gravity Mode.
        """
        print("\n" + "="*60)
        print("🌌 STARTING GRAVITY AGENT MODE 🌌")
        print("Specialist in Interpreting and Orchestrating Automated Development")
        print("="*60 + "\n")
        
        try:
            # 1. Interpret
            self.interpret_project()
            
            # 2. Plan
            self.plan_development()
            
            # 3. Orchestrate
            success = self.orchestrate_execution()
            
            if success:
                print("\n✅ Gravity Mode Execution Completed Successfully.")
            else:
                print("\n❌ Gravity Mode Execution Encountered Issues.")
                
        except KeyboardInterrupt:
            print("\n⚠️ Gravity Mode Interrupted by User.")
        except Exception as e:
            logger.exception("Fatal error in Gravity Mode")
            print(f"\n❌ Fatal Error: {e}")

if __name__ == "__main__":
    agent = GravityAgent()
    agent.run_gravity_mode()
