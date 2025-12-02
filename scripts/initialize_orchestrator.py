#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialize Orchestrator System
Registers all agents and starts the orchestration system
"""

import sys
import logging
from pathlib import Path

# Add python-scripts to path
python_scripts = Path(__file__).parent.parent / "python-scripts"
if str(python_scripts) not in sys.path:
    sys.path.insert(0, str(python_scripts))

from orchestrator_service import OrchestratorService, get_orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Initialize orchestrator system"""
    print("🚀 Initializing BMC Uruguay Multi-Agent Orchestration System")
    print("=" * 70)
    
    try:
        # Get orchestrator instance
        orchestrator = get_orchestrator()
        
        # Initialize agents
        print("\n📋 Registering agents...")
        orchestrator.initialize_agents()
        
        # Get system status
        print("\n📊 System Status:")
        status = orchestrator.get_system_status()
        
        print(f"  Status: {status['status']}")
        print(f"  Agents Registered: {status['orchestrator']['agents_registered']}")
        print(f"  Shared Context: {'✅ Available' if status['shared_context_available'] else '❌ Not Available'}")
        
        # List agents
        print("\n👥 Registered Agents:")
        agents = orchestrator.list_agents()
        for agent in agents:
            print(f"  ✅ {agent['name']} ({agent['agent_id']})")
            print(f"     Capabilities: {', '.join(agent['capabilities'][:3])}...")
            print(f"     Status: {agent['status']}")
            print()
        
        # Health check
        print("\n🏥 Health Check:")
        health = orchestrator.coordinator.health_check()
        print(f"  Coordinator Status: {health['status']}")
        print(f"  Total Agents: {health['agents']['total']}")
        print(f"  Online Agents: {health['agents']['online']}")
        print(f"  Pending Tasks: {health['tasks']['pending']}")
        print(f"  Queue Size: {health['queue_size']}")
        
        print("\n" + "=" * 70)
        print("✅ Orchestrator System Initialized Successfully!")
        print("=" * 70)
        print("\n📚 Next Steps:")
        print("  1. Start API server: python api_server.py")
        print("  2. Start background agents: python background_agent_followup.py --continuous")
        print("  3. Test system: curl http://localhost:8000/api/orchestrator/status")
        print("\n📖 Documentation:")
        print("  - Phase 0 Plan: PHASE_0_ORCHESTRATION_DEPLOYMENT_PLAN.md")
        print("  - Team Instructions: TEAM_INSTRUCTIONS_PHASE_0.md")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing orchestrator: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
