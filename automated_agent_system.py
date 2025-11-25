#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Agent System - Unified Entry Point
Main orchestration class integrating all agent components
"""

import os
import logging
import signal
import sys
from typing import Optional, Dict, Any

from agent_coordinator import AgentCoordinator, get_coordinator
from agent_router import AgentRouter, get_router
from agent_scheduler import AgentScheduler, get_scheduler
from agent_workflows import WorkflowEngine, get_workflow_engine
from agent_monitoring import AgentMonitoring, get_monitoring
from background_agent_followup import FollowUpAgent
from proactive_agent_actions import ProactiveAgentActions, get_proactive_actions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutomatedAgentSystem:
    """Unified automated agent system"""
    
    def __init__(self, ia_instance: Optional[Any] = None):
        """
        Initialize the automated agent system
        
        Args:
            ia_instance: IA instance for integration
        """
        self.ia_instance = ia_instance
        self.running = False
        
        # Core components
        self.coordinator: Optional[AgentCoordinator] = None
        self.router: Optional[AgentRouter] = None
        self.scheduler: Optional[AgentScheduler] = None
        self.workflow_engine: Optional[WorkflowEngine] = None
        self.monitoring: Optional[AgentMonitoring] = None
        
        # Agent instances
        self.followup_agent: Optional[FollowUpAgent] = None
        self.proactive_actions: Optional[ProactiveAgentActions] = None
        
        logger.info("Automated Agent System initialized")
    
    def initialize(self):
        """Initialize all agent components"""
        try:
            logger.info("Initializing Automated Agent System...")
            
            # Initialize core components
            self.coordinator = get_coordinator()
            self.router = get_router(self.coordinator)
            self.scheduler = get_scheduler(self.coordinator)
            self.workflow_engine = get_workflow_engine(self.coordinator, self.router)
            self.monitoring = get_monitoring(self.coordinator)
            
            # Set IA instance in coordinator if available
            if self.ia_instance:
                self.coordinator.set_ia_instance(self.ia_instance)
            
            # Initialize follow-up agent
            self.followup_agent = FollowUpAgent(
                coordinator=self.coordinator,
                ia_instance=self.ia_instance
            )
            
            # Initialize proactive actions
            self.proactive_actions = get_proactive_actions(
                coordinator=self.coordinator,
                scheduler=self.scheduler,
                workflow_engine=self.workflow_engine,
                ia_instance=self.ia_instance
            )
            
            logger.info("✅ All agent components initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing agent system: {e}", exc_info=True)
            raise
    
    def start(self):
        """Start the automated agent system"""
        if self.running:
            logger.warning("Agent system is already running")
            return
        
        try:
            logger.info("🚀 Starting Automated Agent System...")
            
            # Start core components
            if self.coordinator:
                self.coordinator.start()
            
            if self.scheduler:
                self.scheduler.start()
            
            if self.monitoring:
                self.monitoring.start()
            
            # Set up automated actions
            if self.proactive_actions:
                self.proactive_actions.setup_automated_actions()
            
            self.running = True
            logger.info("✅ Automated Agent System started")
            
        except Exception as e:
            logger.error(f"❌ Error starting agent system: {e}", exc_info=True)
            raise
    
    def stop(self):
        """Stop the automated agent system"""
        if not self.running:
            return
        
        try:
            logger.info("🛑 Stopping Automated Agent System...")
            
            # Stop components in reverse order
            if self.monitoring:
                self.monitoring.stop()
            
            if self.scheduler:
                self.scheduler.stop()
            
            if self.coordinator:
                self.coordinator.stop()
            
            self.running = False
            logger.info("✅ Automated Agent System stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping agent system: {e}", exc_info=True)
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        status = {
            "running": self.running,
            "components": {
                "coordinator": self.coordinator is not None,
                "router": self.router is not None,
                "scheduler": self.scheduler is not None,
                "workflow_engine": self.workflow_engine is not None,
                "monitoring": self.monitoring is not None,
                "followup_agent": self.followup_agent is not None,
                "proactive_actions": self.proactive_actions is not None
            }
        }
        
        # Add detailed status from components
        if self.coordinator:
            status["agent_status"] = self.coordinator.get_agent_status()
        
        if self.scheduler:
            status["scheduled_tasks"] = len(self.scheduler.list_scheduled_tasks())
        
        if self.monitoring:
            status["monitoring"] = self.monitoring.get_dashboard_data()
        
        return status
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        health = {
            "healthy": True,
            "components": {}
        }
        
        # Check coordinator
        if self.coordinator:
            try:
                coordinator_health = self.coordinator.health_check()
                health["components"]["coordinator"] = coordinator_health
            except Exception as e:
                health["components"]["coordinator"] = {"healthy": False, "error": str(e)}
                health["healthy"] = False
        
        # Check scheduler
        if self.scheduler:
            health["components"]["scheduler"] = {"healthy": self.scheduler.running}
            if not self.scheduler.running:
                health["healthy"] = False
        
        # Check monitoring
        if self.monitoring:
            health["components"]["monitoring"] = {"healthy": self.monitoring.running}
            if not self.monitoring.running:
                health["healthy"] = False
        
        return health
    
    def run_interactive(self):
        """Run in interactive mode"""
        print("=" * 70)
        print("🤖 Automated Agent System - Interactive Mode")
        print("=" * 70)
        print("\nCommands:")
        print("  status    - Show system status")
        print("  health    - Perform health check")
        print("  agents    - List registered agents")
        print("  schedules - List scheduled tasks")
        print("  workflows - List available workflows")
        print("  metrics   - Show metrics")
        print("  alerts    - Show alerts")
        print("  quit      - Exit")
        print("=" * 70)
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "quit" or command == "exit":
                    break
                elif command == "status":
                    status = self.get_status()
                    print(f"\nStatus: {status}")
                elif command == "health":
                    health = self.health_check()
                    print(f"\nHealth: {health}")
                elif command == "agents":
                    if self.coordinator:
                        agents = self.coordinator.get_agent_status()
                        print(f"\nAgents: {agents}")
                elif command == "schedules":
                    if self.scheduler:
                        schedules = self.scheduler.list_scheduled_tasks()
                        print(f"\nScheduled Tasks: {schedules}")
                elif command == "workflows":
                    if self.workflow_engine:
                        workflows = self.workflow_engine.list_workflows()
                        print(f"\nWorkflows: {workflows}")
                elif command == "metrics":
                    if self.monitoring:
                        metrics = self.monitoring.get_metrics()
                        print(f"\nMetrics: {metrics}")
                elif command == "alerts":
                    if self.monitoring:
                        alerts = self.monitoring.get_alerts(limit=10)
                        print(f"\nAlerts: {alerts}")
                elif command == "help":
                    print("\nCommands: status, health, agents, schedules, workflows, metrics, alerts, quit")
                else:
                    print(f"Unknown command: {command}. Type 'help' for commands.")
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def run_continuous(self):
        """Run continuously (for background service)"""
        self.start()
        
        # Set up signal handlers
        def signal_handler(sig, frame):
            logger.info("Received interrupt signal, shutting down...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Keep running
        try:
            while self.running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
            self.stop()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated Agent System")
    parser.add_argument("--mode", choices=["interactive", "continuous"], default="interactive",
                       help="Run mode (default: interactive)")
    parser.add_argument("--ia", action="store_true",
                       help="Enable IA integration")
    
    args = parser.parse_args()
    
    # Initialize IA if requested
    ia_instance = None
    if args.ia:
        try:
            from ia_conversacional_integrada import IAConversacionalIntegrada
            ia_instance = IAConversacionalIntegrada()
            logger.info("✅ IA integration enabled")
        except Exception as e:
            logger.warning(f"Could not initialize IA: {e}")
    
    # Create and initialize system
    system = AutomatedAgentSystem(ia_instance=ia_instance)
    system.initialize()
    
    # Run based on mode
    if args.mode == "continuous":
        system.run_continuous()
    else:
        system.start()
        try:
            system.run_interactive()
        finally:
            system.stop()


if __name__ == "__main__":
    main()

