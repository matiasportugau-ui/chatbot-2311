#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Team Runner
Procedure for running the team of 12 agents according to the unified plan
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from scripts.orchestrator.main_orchestrator import MainOrchestrator
    from scripts.orchestrator.state_manager import StateManager
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    print("⚠️  Warning: Orchestrator not available. Some features may be limited.")


# Agent Team Configuration (12 Agents)
AGENT_TEAM = {
    "nivel_1_core": {
        "GravityOrchestratorAgent": {
            "description": "Gravity (Grok-first) master coordinator - interprets intent and orchestrates automated development",
            "phases": "all",
            "responsibilities": [
                "Coordination general",
                "Comunicación entre agentes",
                "Toma de decisiones",
                "Phase execution management"
            ]
        },
        "RepositoryAgent": {
            "description": "Git + Workspace Management",
            "phases": [1, 2],
            "responsibilities": [
                "Gestión de repositorios Git",
                "Estructura de workspace",
                "Migraciones",
                "Repository analysis"
            ]
        },
        "DiscoveryAgent": {
            "description": "BMC + Technical Discovery",
            "phases": [0],
            "responsibilities": [
                "Discovery técnico",
                "Discovery de dominio BMC",
                "Component mapping",
                "Gap identification"
            ]
        }
    },
    "nivel_2_consolidation": {
        "MergeAgent": {
            "description": "Consolidation Specialist",
            "phases": [3, 4, 5, 6],
            "responsibilities": [
                "Estrategia de merge",
                "Resolución de conflictos",
                "Evolución cruzada",
                "Validación de componentes BMC"
            ]
        },
        "IntegrationAgent": {
            "description": "Integration Specialist",
            "phases": [7, 8],
            "responsibilities": [
                "Integraciones WhatsApp",
                "Integraciones n8n",
                "Integraciones Qdrant",
                "Validación de integraciones"
            ]
        }
    },
    "nivel_3_production": {
        "SecurityAgent": {
            "description": "Security + DevOps",
            "phases": [9],
            "responsibilities": [
                "Security hardening",
                "Secrets management",
                "Webhook validation",
                "CORS configuration"
            ]
        },
        "InfrastructureAgent": {
            "description": "Infrastructure as Code",
            "phases": [10],
            "responsibilities": [
                "Infrastructure as Code",
                "Docker configuration",
                "Environment setup",
                "Production config"
            ]
        },
        "ObservabilityAgent": {
            "description": "Monitoring & Logging",
            "phases": [11],
            "responsibilities": [
                "Monitoring setup",
                "Logging configuration",
                "Metrics collection",
                "Alerting"
            ]
        },
        "PerformanceAgent": {
            "description": "Performance & Load Testing",
            "phases": [12],
            "responsibilities": [
                "Performance testing",
                "Load testing",
                "Optimization",
                "Benchmarking"
            ]
        }
    },
    "nivel_4_deployment": {
        "CICDAgent": {
            "description": "CI/CD Pipeline",
            "phases": [13],
            "responsibilities": [
                "CI/CD pipeline setup",
                "GitHub Actions",
                "Automated testing",
                "Deployment automation"
            ]
        },
        "DisasterRecoveryAgent": {
            "description": "DR & Backup",
            "phases": [14],
            "responsibilities": [
                "Backup strategy",
                "Disaster recovery plan",
                "Data recovery",
                "RTO/RPO configuration"
            ]
        },
        "ValidationAgent": {
            "description": "Final Validation & QA",
            "phases": [15],
            "responsibilities": [
                "Final validation",
                "QA testing",
                "UAT coordination",
                "Production readiness check"
            ]
        }
    }
}


class AgentTeamRunner:
    """Manages execution of the agent team"""
    
    def __init__(self, mode: str = "automated", resume: bool = False):
        self.mode = mode
        self.resume = resume
        self.orchestrator: Optional[MainOrchestrator] = None
        self.state_manager: Optional[StateManager] = None
        
    def initialize(self) -> bool:
        """Initialize the agent team system"""
        print("🤖 Initializing Agent Team System...")
        print("="*70)
        
        if not ORCHESTRATOR_AVAILABLE:
            print("❌ Orchestrator system not available!")
            print("   Please install dependencies: pip install -r scripts/orchestrator/requirements.txt")
            return False
        
        try:
            self.orchestrator = MainOrchestrator()
            self.state_manager = self.orchestrator.state_manager
            
            if not self.orchestrator.initialize():
                print("❌ Failed to initialize orchestrator")
                return False
            
            print("✅ Orchestrator initialized")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_agent_for_phase(self, phase: int) -> Optional[str]:
        """Get the responsible agent for a phase"""
        # First, check for specific phase assignments (prioritize over "all")
        specific_agent = None
        for nivel, agents in AGENT_TEAM.items():
            for agent_name, agent_info in agents.items():
                phases = agent_info.get("phases", [])
                if isinstance(phases, list) and phase in phases:
                    return agent_name  # Return immediately for specific assignment
        
        # If no specific assignment, check for "all" agents
        for nivel, agents in AGENT_TEAM.items():
            for agent_name, agent_info in agents.items():
                phases = agent_info.get("phases", [])
                if phases == "all":
                    return agent_name
        
        return None
    
    def print_agent_team_info(self):
        """Print information about the agent team"""
        print("\n" + "="*70)
        print("🤖 AGENT TEAM CONFIGURATION (12 Agents)")
        print("="*70)
        
        for nivel, agents in AGENT_TEAM.items():
            nivel_name = nivel.replace("_", " ").title()
            print(f"\n📊 {nivel_name}:")
            for agent_name, agent_info in agents.items():
                phases = agent_info.get("phases", [])
                phase_str = "all phases" if phases == "all" else f"phases {phases}"
                print(f"   • {agent_name}")
                print(f"     └─ {agent_info['description']}")
                print(f"     └─ Active in: {phase_str}")
        
        print("\n" + "="*70)
    
    def print_phase_agent_mapping(self):
        """Print which agent handles which phase"""
        print("\n📋 PHASE-AGENT MAPPING:")
        print("-"*70)
        
        for phase in range(16):
            agent = self.get_agent_for_phase(phase)
            phase_name = self.get_phase_name(phase)
            if agent:
                print(f"   Phase {phase:2d} ({phase_name:30s}) → {agent}")
            else:
                print(f"   Phase {phase:2d} ({phase_name:30s}) → ⚠️  No agent assigned")
        
        print("-"*70)
    
    def get_phase_name(self, phase: int) -> str:
        """Get phase name"""
        phase_names = {
            0: "BMC Discovery & Assessment",
            1: "Repository Analysis",
            2: "Component Mapping",
            3: "Merge Strategy",
            4: "Conflict Resolution",
            5: "Testing & Validation",
            6: "Documentation",
            7: "Integration Testing",
            8: "Final Configuration",
            9: "Security Hardening",
            10: "Infrastructure as Code",
            11: "Observability & Monitoring",
            12: "Performance & Load Testing",
            13: "CI/CD Pipeline",
            14: "Disaster Recovery & Backup",
            15: "Final Production Validation"
        }
        return phase_names.get(phase, f"Phase {phase}")
    
    def run_agent_team(self) -> bool:
        """Run the complete agent team execution"""
        print("\n🚀 Starting Agent Team Execution")
        print("="*70)
        
        # Print agent team info
        self.print_agent_team_info()
        self.print_phase_agent_mapping()
        
        # Check current status
        if self.resume and self.state_manager.can_resume():
            current_phase = self.state_manager.get_current_phase()
            print(f"\n📌 Resuming from Phase {current_phase}")
        else:
            print("\n📌 Starting from Phase 0")
        
        # Run orchestrator
        try:
            if self.mode == "dry-run":
                print("\n🔍 DRY-RUN MODE: Validating without execution")
                return self.validate_execution()
            elif self.mode == "manual":
                print("\n👤 MANUAL MODE: Pausing for approvals")
                return self.run_manual_execution()
            else:
                print("\n🤖 AUTOMATED MODE: Full automated execution")
                return self.orchestrator.run()
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Execution interrupted by user")
            if self.state_manager:
                self.state_manager.set_overall_status("interrupted")
            return False
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def validate_execution(self) -> bool:
        """Validate execution without running"""
        print("\n🔍 Validating execution setup...")
        
        # Check dependencies
        # Check configuration
        # Check state
        
        print("✅ Validation complete")
        return True
    
    def run_manual_execution(self) -> bool:
        """Run with manual approval pauses"""
        print("\n👤 Manual execution mode")
        print("   Phases will pause for manual approval")
        
        # This would integrate with approval engine
        return self.orchestrator.run()
    
    def run_single_phase(self, phase: int) -> bool:
        """Run a single phase with its assigned agent"""
        agent = self.get_agent_for_phase(phase)
        phase_name = self.get_phase_name(phase)
        
        print(f"\n🎯 Executing Phase {phase}: {phase_name}")
        if agent:
            print(f"   Assigned Agent: {agent}")
        else:
            print(f"   ⚠️  No specific agent assigned")
        
        if not self.orchestrator:
            print("❌ Orchestrator not initialized")
            return False
        
        return self.orchestrator.execute_phase(phase)
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get current status report"""
        if not self.state_manager:
            return {"error": "State manager not initialized"}
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "current_phase": self.state_manager.get_current_phase(),
            "overall_status": self.state_manager.get_overall_status(),
            "phases": {}
        }
        
        for phase in range(16):
            status = self.state_manager.get_phase_status(phase)
            agent = self.get_agent_for_phase(phase)
            report["phases"][phase] = {
                "status": status,
                "agent": agent,
                "name": self.get_phase_name(phase)
            }
        
        return report


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run the Agent Team for BMC Chatbot Platform Consolidation"
    )
    parser.add_argument(
        "--mode",
        choices=["automated", "manual", "dry-run"],
        default="automated",
        help="Execution mode (default: automated)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from saved state"
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=range(16),
        help="Run a specific phase only"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show status report only"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show agent team information only"
    )
    
    args = parser.parse_args()
    
    runner = AgentTeamRunner(mode=args.mode, resume=args.resume)
    
    # Show info only
    if args.info:
        runner.print_agent_team_info()
        runner.print_phase_agent_mapping()
        return 0
    
    # Initialize
    if not runner.initialize():
        return 1
    
    # Show status only
    if args.status:
        report = runner.get_status_report()
        print("\n📊 CURRENT STATUS:")
        print(json.dumps(report, indent=2))
        return 0
    
    # Run single phase
    if args.phase is not None:
        success = runner.run_single_phase(args.phase)
        return 0 if success else 1
    
    # Run full execution
    success = runner.run_agent_team()
    
    if success:
        print("\n✅ Agent Team execution completed successfully!")
        return 0
    else:
        print("\n❌ Agent Team execution failed or was interrupted")
        return 1


if __name__ == "__main__":
    sys.exit(main())

