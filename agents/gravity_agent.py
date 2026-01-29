#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gravity Agent - Development Automation Orchestrator
=====================================================

Specialized agent for interpreting and orchestrating automated development
of the chatbot-2311 project. Acts as the central coordinator (gravity point)
for all automated development activities.

Capabilities:
- Project state interpretation and analysis
- Automated development orchestration
- Intelligent decision-making for development workflows
- Integration with existing orchestrator system
- Context-aware planning and execution
- Real-time monitoring and adaptation
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

# Add project paths
_current_dir = Path(__file__).parent
_project_root = _current_dir.parent
sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_project_root / "scripts"))

# Import orchestrator components
try:
    from scripts.orchestrator.main_orchestrator import MainOrchestrator
    from scripts.orchestrator.state_manager import StateManager
    from scripts.orchestrator.context_manager import ContextManager
    from scripts.orchestrator.dependency_resolver import DependencyResolver
    from scripts.orchestrator.status_reporter import StatusReporter
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    ORCHESTRATOR_AVAILABLE = False
    print(f"⚠️  Warning: Orchestrator components not available: {e}")

# Import AI integrator if available
try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False


class AgentMode(Enum):
    """Gravity Agent operation modes"""
    INTERPRET = "interpret"  # Analyze and interpret project state
    ORCHESTRATE = "orchestrate"  # Execute automated development
    MONITOR = "monitor"  # Monitor ongoing execution
    ADAPT = "adapt"  # Adapt plans based on changes
    FULL_CYCLE = "full_cycle"  # Complete interpret-orchestrate-monitor cycle


class ProjectState(Enum):
    """Project development states"""
    INITIALIZING = "initializing"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ERROR = "error"
    NEEDS_REVIEW = "needs_review"


@dataclass
class DevelopmentTask:
    """Represents a development task"""
    id: str
    title: str
    description: str
    phase: int
    priority: str  # critical, high, medium, low
    status: str  # pending, in_progress, completed, failed, blocked
    dependencies: List[str]
    estimated_time: Optional[str] = None
    actual_time: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ProjectInterpretation:
    """Result of project state interpretation"""
    current_state: ProjectState
    current_phase: int
    completed_phases: List[int]
    pending_phases: List[int]
    blockers: List[str]
    opportunities: List[str]
    recommendations: List[str]
    confidence: float  # 0.0 to 1.0
    context: Dict[str, Any]
    timestamp: str


class GravityAgent:
    """
    Gravity Agent - Central orchestrator for automated development
    
    Acts as the "gravity point" that coordinates all automated development
    activities, interpreting project state and orchestrating execution.
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize Gravity Agent"""
        self.config = config or {}
        self.mode = AgentMode.FULL_CYCLE
        self.integrator = None
        self.orchestrator = None
        self.state_manager = None
        self.context_manager = None
        
        # Initialize AI integrator
        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.integrator = get_model_integrator()
                print("✅ AI integrator initialized")
            except Exception as e:
                print(f"⚠️  AI integrator not available: {e}")
        
        # Initialize orchestrator
        if ORCHESTRATOR_AVAILABLE:
            try:
                config_file = self.config.get("orchestrator_config", 
                    "scripts/orchestrator/config/orchestrator_config.json")
                self.orchestrator = MainOrchestrator(config_file)
                self.state_manager = self.orchestrator.state_manager
                self.context_manager = ContextManager(self.state_manager)
                print("✅ Orchestrator system initialized")
            except Exception as e:
                print(f"⚠️  Orchestrator initialization error: {e}")
        
        # Agent state
        self.interpretation_history: List[ProjectInterpretation] = []
        self.execution_history: List[Dict] = []
        self.active_tasks: List[DevelopmentTask] = []
        
    def interpret_project_state(self, deep_analysis: bool = True) -> ProjectInterpretation:
        """
        Interpret current project state
        
        Analyzes:
        - Current phase and progress
        - Dependencies and blockers
        - Opportunities for optimization
        - Recommended next actions
        
        Args:
            deep_analysis: Whether to perform deep analysis using AI
            
        Returns:
            ProjectInterpretation object
        """
        print("\n" + "="*80)
        print("🔍 GRAVITY AGENT: Interpreting Project State")
        print("="*80 + "\n")
        
        # Gather basic state information
        current_phase = 0
        completed_phases = []
        pending_phases = []
        blockers = []
        opportunities = []
        recommendations = []
        
        if self.state_manager:
            current_phase = self.state_manager.get_current_phase()
            overall_status = self.state_manager.get_overall_status()
            
            # Get phase statuses
            for phase in range(16):  # Phases 0-15
                phase_status = self.state_manager.get_phase_status(phase)
                if phase_status == "completed":
                    completed_phases.append(phase)
                elif phase_status in ["pending", "not_started"]:
                    pending_phases.append(phase)
                elif phase_status == "blocked":
                    blockers.append(f"Phase {phase} is blocked")
        
        # Analyze project files and structure
        project_health = self._analyze_project_health()
        
        # Check for blockers
        blockers.extend(project_health.get("blockers", []))
        
        # Identify opportunities
        opportunities.extend(project_health.get("opportunities", []))
        
        # Determine current state
        if blockers:
            current_state = ProjectState.BLOCKED
        elif current_phase > 0 and pending_phases:
            current_state = ProjectState.IN_PROGRESS
        elif not completed_phases and not pending_phases:
            current_state = ProjectState.INITIALIZING
        elif all(phase in completed_phases for phase in range(16)):
            current_state = ProjectState.COMPLETED
        else:
            current_state = ProjectState.READY
        
        # AI-powered deep analysis
        if deep_analysis and self.integrator:
            ai_analysis = self._ai_interpret_project_state(
                current_phase, completed_phases, blockers, project_health
            )
            recommendations.extend(ai_analysis.get("recommendations", []))
            opportunities.extend(ai_analysis.get("opportunities", []))
            confidence = ai_analysis.get("confidence", 0.7)
        else:
            confidence = 0.6
        
        # Generate recommendations
        if not recommendations:
            recommendations = self._generate_basic_recommendations(
                current_state, current_phase, blockers
            )
        
        interpretation = ProjectInterpretation(
            current_state=current_state,
            current_phase=current_phase,
            completed_phases=completed_phases,
            pending_phases=pending_phases,
            blockers=blockers,
            opportunities=opportunities,
            recommendations=recommendations,
            confidence=confidence,
            context={
                "project_health": project_health,
                "overall_status": overall_status if self.state_manager else "unknown",
                "timestamp": datetime.now().isoformat()
            },
            timestamp=datetime.now().isoformat()
        )
        
        # Store interpretation
        self.interpretation_history.append(interpretation)
        
        # Print summary
        self._print_interpretation_summary(interpretation)
        
        return interpretation
    
    def orchestrate_development(self, 
                                target_phase: Optional[int] = None,
                                auto_approve: bool = True,
                                max_phases: Optional[int] = None) -> Dict:
        """
        Orchestrate automated development execution
        
        Args:
            target_phase: Specific phase to execute (None = continue from current)
            auto_approve: Automatically approve phase execution
            max_phases: Maximum number of phases to execute
            
        Returns:
            Execution result dictionary
        """
        print("\n" + "="*80)
        print("🚀 GRAVITY AGENT: Orchestrating Development")
        print("="*80 + "\n")
        
        if not self.orchestrator:
            return {
                "success": False,
                "error": "Orchestrator not available",
                "message": "Cannot orchestrate without orchestrator system"
            }
        
        # Initialize orchestrator if needed
        if not self.state_manager.get_overall_status():
            print("📋 Initializing orchestrator...")
            self.orchestrator.initialize()
        
        # Get current state
        interpretation = self.interpret_project_state(deep_analysis=False)
        
        # Check for blockers
        if interpretation.blockers:
            print("⚠️  Blockers detected:")
            for blocker in interpretation.blockers:
                print(f"   - {blocker}")
            return {
                "success": False,
                "error": "Blockers detected",
                "blockers": interpretation.blockers,
                "recommendations": interpretation.recommendations
            }
        
        # Determine execution plan
        start_phase = target_phase if target_phase is not None else interpretation.current_phase
        end_phase = start_phase + max_phases if max_phases else 15
        
        print(f"📊 Execution Plan:")
        print(f"   Start Phase: {start_phase}")
        print(f"   End Phase: {end_phase}")
        print(f"   Auto-approve: {auto_approve}")
        print()
        
        # Execute phases
        execution_results = []
        phases_executed = 0
        
        try:
            for phase in range(start_phase, min(end_phase + 1, 16)):
                print(f"\n{'─'*60}")
                print(f"Executing Phase {phase}")
                print(f"{'─'*60}\n")
                
                phase_start_time = time.time()
                success = self.orchestrator.execute_phase(phase)
                phase_duration = time.time() - phase_start_time
                
                execution_results.append({
                    "phase": phase,
                    "success": success,
                    "duration": f"{phase_duration:.2f}s",
                    "timestamp": datetime.now().isoformat()
                })
                
                phases_executed += 1
                
                if not success:
                    print(f"⚠️  Phase {phase} failed")
                    break
            
            # Summary
            successful_phases = sum(1 for r in execution_results if r["success"])
            
            result = {
                "success": successful_phases == len(execution_results),
                "phases_executed": phases_executed,
                "successful_phases": successful_phases,
                "failed_phases": phases_executed - successful_phases,
                "execution_results": execution_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store execution
            self.execution_history.append(result)
            
            # Print summary
            print("\n" + "="*80)
            print("📊 EXECUTION SUMMARY")
            print("="*80)
            print(f"Phases Executed: {phases_executed}")
            print(f"Successful: {successful_phases}")
            print(f"Failed: {phases_executed - successful_phases}")
            print("="*80 + "\n")
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "phases_executed": phases_executed,
                "execution_results": execution_results,
                "timestamp": datetime.now().isoformat()
            }
            self.execution_history.append(error_result)
            return error_result
    
    def monitor_execution(self, interval: int = 30) -> Dict:
        """
        Monitor ongoing execution
        
        Args:
            interval: Monitoring interval in seconds
            
        Returns:
            Monitoring result
        """
        print("\n" + "="*80)
        print("👁️  GRAVITY AGENT: Monitoring Execution")
        print("="*80 + "\n")
        
        if not self.state_manager:
            return {"success": False, "error": "State manager not available"}
        
        overall_status = self.state_manager.get_overall_status()
        current_phase = self.state_manager.get_current_phase()
        
        monitoring_data = {
            "overall_status": overall_status,
            "current_phase": current_phase,
            "phase_status": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Get status for each phase
        for phase in range(16):
            phase_status = self.state_manager.get_phase_status(phase)
            monitoring_data["phase_status"][phase] = phase_status
        
        # Print monitoring info
        print(f"Overall Status: {overall_status}")
        print(f"Current Phase: {current_phase}")
        print(f"\nPhase Statuses:")
        for phase, status in monitoring_data["phase_status"].items():
            if status != "not_started":
                print(f"  Phase {phase}: {status}")
        
        return monitoring_data
    
    def adapt_plan(self, new_context: Dict) -> Dict:
        """
        Adapt development plan based on new context
        
        Args:
            new_context: New context information
            
        Returns:
            Adaptation result
        """
        print("\n" + "="*80)
        print("🔄 GRAVITY AGENT: Adapting Plan")
        print("="*80 + "\n")
        
        # Re-interpret with new context
        interpretation = self.interpret_project_state(deep_analysis=True)
        
        # Analyze adaptation needs
        adaptations = []
        
        # Check if priorities need to change
        if new_context.get("urgent_issues"):
            adaptations.append({
                "type": "priority_shift",
                "description": "Urgent issues detected, adjusting priorities",
                "actions": ["Review blockers", "Re-prioritize phases"]
            })
        
        # Check if dependencies changed
        if new_context.get("dependency_changes"):
            adaptations.append({
                "type": "dependency_update",
                "description": "Dependencies changed, updating execution plan",
                "actions": ["Re-evaluate dependencies", "Update phase order"]
            })
        
        result = {
            "success": True,
            "adaptations": adaptations,
            "updated_interpretation": interpretation,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def run_full_cycle(self, 
                      start_phase: Optional[int] = None,
                      end_phase: Optional[int] = None,
                      auto_approve: bool = True) -> Dict:
        """
        Run complete interpret-orchestrate-monitor cycle
        
        Args:
            start_phase: Starting phase (None = current)
            end_phase: Ending phase (None = 15)
            auto_approve: Auto-approve execution
            
        Returns:
            Complete cycle result
        """
        print("\n" + "="*80)
        print("🔄 GRAVITY AGENT: Full Cycle Execution")
        print("="*80 + "\n")
        
        cycle_start = time.time()
        
        # Step 1: Interpret
        print("STEP 1: INTERPRETING PROJECT STATE")
        print("─"*60)
        interpretation = self.interpret_project_state(deep_analysis=True)
        
        if interpretation.blockers:
            print("\n⚠️  Blockers detected. Cannot proceed with orchestration.")
            return {
                "success": False,
                "step": "interpret",
                "blockers": interpretation.blockers,
                "recommendations": interpretation.recommendations
            }
        
        # Step 2: Orchestrate
        print("\nSTEP 2: ORCHESTRATING DEVELOPMENT")
        print("─"*60)
        execution_result = self.orchestrate_development(
            target_phase=start_phase,
            auto_approve=auto_approve,
            max_phases=(end_phase - start_phase) if start_phase and end_phase else None
        )
        
        # Step 3: Monitor
        print("\nSTEP 3: MONITORING EXECUTION")
        print("─"*60)
        monitoring_result = self.monitor_execution()
        
        cycle_duration = time.time() - cycle_start
        
        result = {
            "success": execution_result.get("success", False),
            "cycle_duration": f"{cycle_duration:.2f}s",
            "interpretation": {
                "current_state": interpretation.current_state.value,
                "current_phase": interpretation.current_phase,
                "recommendations": interpretation.recommendations
            },
            "execution": execution_result,
            "monitoring": monitoring_result,
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n" + "="*80)
        print("✅ FULL CYCLE COMPLETED")
        print("="*80)
        print(f"Duration: {cycle_duration:.2f}s")
        print(f"Success: {result['success']}")
        print("="*80 + "\n")
        
        return result
    
    def _analyze_project_health(self) -> Dict:
        """Analyze overall project health"""
        health = {
            "blockers": [],
            "warnings": [],
            "opportunities": [],
            "metrics": {}
        }
        
        # Check critical files
        critical_files = [
            "scripts/orchestrator/main_orchestrator.py",
            "scripts/orchestrator/config/orchestrator_config.json",
            ".cursorrules"
        ]
        
        missing_files = []
        for file_path in critical_files:
            if not Path(_project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            health["blockers"].append(f"Missing critical files: {', '.join(missing_files)}")
        
        # Check orchestrator config
        config_file = Path(_project_root / "scripts/orchestrator/config/orchestrator_config.json")
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    if config.get("execution_mode") == "automated":
                        health["opportunities"].append("Automated execution mode enabled")
            except Exception as e:
                health["warnings"].append(f"Config file error: {e}")
        
        return health
    
    def _ai_interpret_project_state(self, 
                                    current_phase: int,
                                    completed_phases: List[int],
                                    blockers: List[str],
                                    project_health: Dict) -> Dict:
        """Use AI to interpret project state"""
        if not self.integrator:
            return {"recommendations": [], "opportunities": [], "confidence": 0.5}
        
        try:
            system_prompt = """You are a specialized AI agent for interpreting and orchestrating automated development.

Analyze the project state and provide:
1. Actionable recommendations for next steps
2. Opportunities for optimization
3. Confidence level (0.0-1.0) in your analysis

Be specific, actionable, and prioritize based on impact."""
            
            prompt = f"""Current Project State:
- Current Phase: {current_phase}
- Completed Phases: {completed_phases}
- Blockers: {blockers}
- Project Health: {json.dumps(project_health, indent=2)}

Provide analysis in JSON format:
{{
    "recommendations": ["rec1", "rec2"],
    "opportunities": ["opp1", "opp2"],
    "confidence": 0.0-1.0
}}"""
            
            response = self.integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            if response and "content" in response:
                content = response["content"].strip()
                result = self._extract_json_from_text(content)
                if result:
                    return result
            
            return {"recommendations": [], "opportunities": [], "confidence": 0.5}
            
        except Exception as e:
            print(f"⚠️  AI interpretation error: {e}")
            return {"recommendations": [], "opportunities": [], "confidence": 0.5}
    
    def _generate_basic_recommendations(self,
                                       current_state: ProjectState,
                                       current_phase: int,
                                       blockers: List[str]) -> List[str]:
        """Generate basic recommendations without AI"""
        recommendations = []
        
        if current_state == ProjectState.BLOCKED:
            recommendations.append("Resolve blockers before proceeding")
            recommendations.append("Review dependency chain")
        
        if current_state == ProjectState.READY:
            recommendations.append(f"Proceed with Phase {current_phase}")
            recommendations.append("Verify dependencies are met")
        
        if current_state == ProjectState.IN_PROGRESS:
            recommendations.append("Continue current phase execution")
            recommendations.append("Monitor for blockers")
        
        return recommendations
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """Extract JSON from text response"""
        import re
        
        json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return None
    
    def _print_interpretation_summary(self, interpretation: ProjectInterpretation):
        """Print interpretation summary"""
        print("📊 PROJECT STATE INTERPRETATION")
        print("─"*60)
        print(f"Current State: {interpretation.current_state.value}")
        print(f"Current Phase: {interpretation.current_phase}")
        print(f"Completed Phases: {len(interpretation.completed_phases)}")
        print(f"Pending Phases: {len(interpretation.pending_phases)}")
        print(f"Confidence: {interpretation.confidence:.2f}")
        
        if interpretation.blockers:
            print(f"\n🚫 Blockers ({len(interpretation.blockers)}):")
            for blocker in interpretation.blockers:
                print(f"   - {blocker}")
        
        if interpretation.opportunities:
            print(f"\n💡 Opportunities ({len(interpretation.opportunities)}):")
            for opp in interpretation.opportunities[:5]:
                print(f"   - {opp}")
        
        if interpretation.recommendations:
            print(f"\n✅ Recommendations ({len(interpretation.recommendations)}):")
            for rec in interpretation.recommendations[:5]:
                print(f"   - {rec}")
        
        print("─"*60 + "\n")
    
    def save_report(self, filename: Optional[str] = None) -> Path:
        """Save agent report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gravity_agent_report_{timestamp}.json"
        
        filepath = Path(_project_root / filename)
        
        report = {
            "agent": "GravityAgent",
            "timestamp": datetime.now().isoformat(),
            "interpretations": [
                {
                    "current_state": i.current_state.value,
                    "current_phase": i.current_phase,
                    "blockers": i.blockers,
                    "recommendations": i.recommendations,
                    "timestamp": i.timestamp
                }
                for i in self.interpretation_history
            ],
            "executions": self.execution_history,
            "config": self.config
        }
        
        filepath.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        return filepath


def main():
    """CLI interface for Gravity Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gravity Agent - Development Automation Orchestrator"
    )
    
    parser.add_argument(
        "--mode",
        choices=["interpret", "orchestrate", "monitor", "adapt", "full_cycle"],
        default="full_cycle",
        help="Agent operation mode"
    )
    
    parser.add_argument(
        "--phase",
        type=int,
        help="Specific phase to execute"
    )
    
    parser.add_argument(
        "--start-phase",
        type=int,
        help="Starting phase for execution"
    )
    
    parser.add_argument(
        "--end-phase",
        type=int,
        help="Ending phase for execution"
    )
    
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        default=True,
        help="Auto-approve phase execution"
    )
    
    parser.add_argument(
        "--no-auto-approve",
        action="store_false",
        dest="auto_approve",
        help="Disable auto-approval"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to orchestrator config file"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for report"
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    config = {}
    if args.config:
        config["orchestrator_config"] = args.config
    
    agent = GravityAgent(config)
    
    print("="*80)
    print("🌌 GRAVITY AGENT - Development Automation Orchestrator")
    print("="*80)
    print(f"Mode: {args.mode}")
    print("="*80 + "\n")
    
    # Execute based on mode
    if args.mode == "interpret":
        interpretation = agent.interpret_project_state()
        result = {"interpretation": interpretation}
    
    elif args.mode == "orchestrate":
        result = agent.orchestrate_development(
            target_phase=args.phase,
            auto_approve=args.auto_approve
        )
    
    elif args.mode == "monitor":
        result = agent.monitor_execution()
    
    elif args.mode == "adapt":
        result = agent.adapt_plan({})
    
    elif args.mode == "full_cycle":
        result = agent.run_full_cycle(
            start_phase=args.start_phase,
            end_phase=args.end_phase,
            auto_approve=args.auto_approve
        )
    
    # Save report
    if args.output:
        report_path = agent.save_report(args.output)
    else:
        report_path = agent.save_report()
    
    print(f"\n📄 Report saved to: {report_path}")
    
    return 0 if result.get("success", False) else 1


if __name__ == "__main__":
    sys.exit(main())
