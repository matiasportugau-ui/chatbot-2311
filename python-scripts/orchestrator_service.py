#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator Service - Main Orchestration Controller
Coordinates all agents and workflows
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from agent_coordinator import AgentCoordinator, TaskPriority, get_coordinator
from agent_router import AgentRouter, get_router

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import workflow engine
try:
    from agent_workflows import WorkflowEngine, get_workflow_engine
    WORKFLOW_ENGINE_AVAILABLE = True
except ImportError:
    WORKFLOW_ENGINE_AVAILABLE = False
    logger.warning("Workflow engine not available")

# Try to import shared context service
try:
    from shared_context_service import get_shared_context_service
    SHARED_CONTEXT_AVAILABLE = True
except ImportError:
    SHARED_CONTEXT_AVAILABLE = False
    logger.warning("Shared context service not available")


class OrchestratorService:
    """Main orchestration service"""
    
    def __init__(self):
        """Initialize orchestrator service"""
        self.coordinator = get_coordinator()
        self.router = get_router(self.coordinator)
        
        if WORKFLOW_ENGINE_AVAILABLE:
            self.workflow_engine = get_workflow_engine(self.coordinator, self.router)
        else:
            self.workflow_engine = None
            logger.warning("Workflow engine not available, workflow features disabled")
        
        if SHARED_CONTEXT_AVAILABLE:
            self.shared_context = get_shared_context_service()
        else:
            self.shared_context = None
        
        self.initialized = False
        logger.info("Orchestrator Service initialized")
    
    def initialize_agents(self):
        """Initialize and register all agents"""
        if self.initialized:
            logger.warning("Agents already initialized")
            return
        
        logger.info("🚀 Initializing agents...")
        
        # Register Conversation Agent
        self.coordinator.register_agent(
            agent_id="conversation_agent",
            name="Conversation Agent",
            capabilities=[
                "nlp",
                "intent_classification",
                "entity_extraction",
                "context_management",
                "multi_turn_conversation"
            ],
            max_concurrent_tasks=10,
            metadata={
                "type": "primary_interface",
                "handles": ["customer_messages", "queries", "conversations"]
            }
        )
        
        # Register Quote Agent
        self.coordinator.register_agent(
            agent_id="quote_agent",
            name="Quote Agent",
            capabilities=[
                "quote_generation",
                "price_calculation",
                "validation",
                "product_knowledge",
                "specification_parsing"
            ],
            max_concurrent_tasks=5,
            metadata={
                "type": "specialist",
                "handles": ["quote_requests", "price_calculations", "quote_validation"]
            }
        )
        
        # Register Follow-up Agent
        self.coordinator.register_agent(
            agent_id="followup_agent",
            name="Follow-up Agent",
            capabilities=[
                "follow_up",
                "message_generation",
                "scheduling",
                "whatsapp_integration",
                "n8n_integration"
            ],
            max_concurrent_tasks=3,
            metadata={
                "type": "background",
                "handles": ["follow_ups", "automated_messages", "scheduling"]
            }
        )
        
        # Register Data Sync Agent
        self.coordinator.register_agent(
            agent_id="data_sync_agent",
            name="Data Sync Agent",
            capabilities=[
                "google_sheets_sync",
                "mongodb_operations",
                "external_api_integration",
                "data_transformation",
                "mercadolibre_integration"
            ],
            max_concurrent_tasks=5,
            metadata={
                "type": "integration",
                "handles": ["data_sync", "external_integrations", "data_updates"]
            }
        )
        
        # Register Analytics Agent
        self.coordinator.register_agent(
            agent_id="analytics_agent",
            name="Analytics Agent",
            capabilities=[
                "data_analysis",
                "report_generation",
                "performance_metrics",
                "anomaly_detection",
                "insights"
            ],
            max_concurrent_tasks=3,
            metadata={
                "type": "analytics",
                "handles": ["analytics", "reports", "metrics", "insights"]
            }
        )
        
        self.initialized = True
        logger.info(f"✅ Registered {len(self.coordinator.agents)} agents")
    
    def process_incoming_message(
        self,
        message: str,
        phone: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process an incoming message through the orchestration system
        
        Args:
            message: User message
            phone: User phone number
            session_id: Optional session ID
            metadata: Optional metadata
            
        Returns:
            Processing result
        """
        logger.info(f"📨 Processing message from {phone}: {message[:50]}...")
        
        # Get or create session
        if self.shared_context and not session_id:
            session_id = self.shared_context.create_session(
                user_phone=phone,
                initial_message=message,
                metadata={"source": "orchestrator", **(metadata or {})}
            )
        
        # Route to conversation agent
        task_id = self.router.route_task(
            task_type="process_message",
            payload={
                "message": message,
                "phone": phone,
                "session_id": session_id
            },
            priority=TaskPriority.NORMAL,
            required_capabilities=["nlp", "intent_classification"],
            metadata=metadata
        )
        
        # Wait for task completion (in production, use async/await)
        import time
        max_wait = 30  # 30 seconds timeout
        waited = 0
        
        while waited < max_wait:
            task_status = self.coordinator.get_task_status(task_id)
            if task_status:
                if task_status["status"] == "completed":
                    result = task_status.get("result", {})
                    logger.info(f"✅ Message processed successfully (task: {task_id})")
                    return {
                        "success": True,
                        "task_id": task_id,
                        "session_id": session_id,
                        "result": result
                    }
                elif task_status["status"] == "failed":
                    error = task_status.get("error", "Unknown error")
                    logger.error(f"❌ Message processing failed (task: {task_id}): {error}")
                    return {
                        "success": False,
                        "task_id": task_id,
                        "session_id": session_id,
                        "error": error
                    }
            
            time.sleep(0.5)
            waited += 0.5
        
        logger.warning(f"⚠️ Message processing timeout (task: {task_id})")
        return {
            "success": False,
            "task_id": task_id,
            "session_id": session_id,
            "error": "Processing timeout"
        }
    
    def coordinate_workflow(
        self,
        workflow_id: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Coordinate a workflow execution
        
        Args:
            workflow_id: Workflow ID to execute
            initial_data: Initial workflow data
            
        Returns:
            Execution ID
        """
        if not self.workflow_engine:
            raise RuntimeError("Workflow engine not available")
        
        logger.info(f"🔄 Coordinating workflow: {workflow_id}")
        
        execution_id = self.workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            initial_data=initial_data or {}
        )
        
        logger.info(f"✅ Workflow execution started: {execution_id}")
        return execution_id
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        health = self.coordinator.health_check()
        
        agents_status = {}
        for agent_id in self.coordinator.agents.keys():
            agents_status[agent_id] = self.coordinator.get_agent_status(agent_id)
        
        workflows = []
        if self.workflow_engine:
            workflows = self.workflow_engine.list_workflows()
        
        return {
            "status": "operational" if health["status"] == "healthy" else "degraded",
            "orchestrator": {
                "initialized": self.initialized,
                "agents_registered": len(self.coordinator.agents)
            },
            "health": health,
            "agents": agents_status,
            "workflows": workflows,
            "shared_context_available": SHARED_CONTEXT_AVAILABLE,
            "workflow_engine_available": WORKFLOW_ENGINE_AVAILABLE
        }
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        return self.coordinator.get_agent_status(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return [
            self.coordinator.get_agent_status(agent_id)
            for agent_id in self.coordinator.agents.keys()
        ]
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle errors in the orchestration system
        
        Args:
            error: Exception that occurred
            context: Context information
            
        Returns:
            Error handling result
        """
        logger.error(f"❌ Error in orchestrator: {error}", exc_info=True)
        
        # Log error to analytics agent (if available)
        try:
            self.router.route_task(
                task_type="log_error",
                payload={
                    "error": str(error),
                    "error_type": type(error).__name__,
                    "context": context
                },
                priority=TaskPriority.LOW,
                required_capabilities=["analytics"]
            )
        except Exception as e:
            logger.warning(f"Failed to log error to analytics agent: {e}")
        
        return {
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__,
            "handled": True
        }


# Global orchestrator instance (singleton)
_orchestrator_instance: Optional[OrchestratorService] = None


def get_orchestrator() -> OrchestratorService:
    """Get the global orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = OrchestratorService()
        _orchestrator_instance.initialize_agents()
    return _orchestrator_instance


if __name__ == "__main__":
    # Example usage
    orchestrator = OrchestratorService()
    orchestrator.initialize_agents()
    
    # Get system status
    status = orchestrator.get_system_status()
    print("System Status:")
    print(f"  Status: {status['status']}")
    print(f"  Agents: {status['orchestrator']['agents_registered']}")
    print(f"  Health: {status['health']}")
    
    # List agents
    agents = orchestrator.list_agents()
    print("\nRegistered Agents:")
    for agent in agents:
        print(f"  - {agent['name']} ({agent['agent_id']})")
        print(f"    Capabilities: {agent['capabilities']}")
        print(f"    Status: {agent['status']}")
