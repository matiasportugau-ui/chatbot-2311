#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Router - Intelligent Task Routing
Routes tasks to the most appropriate agent based on capabilities and load
"""

import logging
from typing import Dict, List, Optional, Any
from agent_coordinator import AgentCoordinator, Agent, TaskPriority, get_coordinator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentRouter:
    """Intelligent router for assigning tasks to agents"""
    
    def __init__(self, coordinator: Optional[AgentCoordinator] = None):
        """
        Initialize the router
        
        Args:
            coordinator: Agent coordinator instance
        """
        self.coordinator = coordinator or get_coordinator()
        
        # Routing strategies
        self.routing_strategies = {
            "least_busy": self._route_least_busy,
            "round_robin": self._route_round_robin,
            "capability_match": self._route_capability_match,
            "balanced": self._route_balanced
        }
        
        self.default_strategy = "balanced"
        self.round_robin_index = {}  # Track round-robin position per task type
        
        logger.info("Agent Router initialized")
    
    def route_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        required_capabilities: Optional[List[str]] = None,
        strategy: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Route a task to an appropriate agent
        
        Args:
            task_type: Type of task
            payload: Task payload
            priority: Task priority
            required_capabilities: Required capabilities
            strategy: Routing strategy (optional)
            metadata: Optional metadata
            
        Returns:
            Task ID if successfully routed, None otherwise
        """
        # Submit task to coordinator
        task_id = self.coordinator.submit_task(
            task_type=task_type,
            payload=payload,
            priority=priority,
            required_capabilities=required_capabilities or [],
            metadata=metadata
        )
        
        # Find best agent
        strategy = strategy or self.default_strategy
        agent = self.find_best_agent(
            required_capabilities or [],
            task_type=task_type,
            strategy=strategy
        )
        
        if not agent:
            logger.warning(f"⚠️ No available agent found for task {task_id} (capabilities: {required_capabilities})")
            return task_id  # Task is queued, will be assigned when agent available
        
        # Assign task to agent
        if self.coordinator.assign_task_to_agent(task_id, agent.agent_id):
            logger.info(f"✅ Routed task {task_id} to agent {agent.agent_id} using strategy '{strategy}'")
            return task_id
        else:
            logger.warning(f"⚠️ Failed to assign task {task_id} to agent {agent.agent_id}")
            return task_id
    
    def find_best_agent(
        self,
        required_capabilities: List[str],
        task_type: Optional[str] = None,
        strategy: str = "balanced"
    ) -> Optional[Agent]:
        """
        Find the best agent for a task
        
        Args:
            required_capabilities: Required agent capabilities
            task_type: Type of task (for routing hints)
            strategy: Routing strategy
            
        Returns:
            Best agent or None if none available
        """
        # Get available agents
        available_agents = self.coordinator.get_available_agents(required_capabilities)
        
        if not available_agents:
            return None
        
        # Use routing strategy
        router_func = self.routing_strategies.get(strategy, self.routing_strategies[self.default_strategy])
        return router_func(available_agents, task_type)
    
    def _route_least_busy(self, agents: List[Agent], task_type: Optional[str] = None) -> Optional[Agent]:
        """Route to least busy agent"""
        if not agents:
            return None
        
        # Sort by current tasks (ascending), then by max capacity
        sorted_agents = sorted(
            agents,
            key=lambda a: (
                a.current_tasks / max(a.max_concurrent_tasks, 1),  # Utilization ratio
                a.current_tasks  # Absolute tasks
            )
        )
        
        return sorted_agents[0]
    
    def _route_round_robin(self, agents: List[Agent], task_type: Optional[str] = None) -> Optional[Agent]:
        """Route using round-robin"""
        if not agents:
            return None
        
        # Use task type as key for round-robin tracking
        key = task_type or "default"
        
        if key not in self.round_robin_index:
            self.round_robin_index[key] = 0
        
        # Sort agents by ID for consistent ordering
        sorted_agents = sorted(agents, key=lambda a: a.agent_id)
        
        # Get next agent in round-robin
        index = self.round_robin_index[key] % len(sorted_agents)
        agent = sorted_agents[index]
        
        # Update index for next time
        self.round_robin_index[key] = (index + 1) % len(sorted_agents)
        
        return agent
    
    def _route_capability_match(self, agents: List[Agent], task_type: Optional[str] = None) -> Optional[Agent]:
        """Route to agent with best capability match"""
        if not agents:
            return None
        
        # Score agents based on capability match
        scored_agents = []
        for agent in agents:
            # Count matching capabilities
            matching_caps = len(set(agent.capabilities))
            # Prefer agents with more capabilities (more versatile)
            score = matching_caps - (agent.current_tasks / max(agent.max_concurrent_tasks, 1))
            scored_agents.append((score, agent))
        
        # Sort by score (descending)
        scored_agents.sort(key=lambda x: x[0], reverse=True)
        
        return scored_agents[0][1] if scored_agents else None
    
    def _route_balanced(self, agents: List[Agent], task_type: Optional[str] = None) -> Optional[Agent]:
        """Balanced routing: considers load, capabilities, and availability"""
        if not agents:
            return None
        
        scored_agents = []
        for agent in agents:
            # Calculate score
            # Lower utilization = higher score
            utilization = agent.current_tasks / max(agent.max_concurrent_tasks, 1)
            availability_score = 1.0 - utilization
            
            # Prefer agents with more capabilities (more versatile)
            capability_score = len(agent.capabilities) / 10.0  # Normalize
            
            # Prefer idle agents
            status_score = 1.0 if agent.status.value == "idle" else 0.5
            
            # Combined score
            total_score = (availability_score * 0.5) + (capability_score * 0.3) + (status_score * 0.2)
            
            scored_agents.append((total_score, agent))
        
        # Sort by score (descending)
        scored_agents.sort(key=lambda x: x[0], reverse=True)
        
        return scored_agents[0][1] if scored_agents else None
    
    def get_available_agents(self, capabilities: List[str]) -> List[Dict[str, Any]]:
        """Get available agents with capabilities"""
        agents = self.coordinator.get_available_agents(capabilities)
        return [
            {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "capabilities": agent.capabilities,
                "current_tasks": agent.current_tasks,
                "max_concurrent_tasks": agent.max_concurrent_tasks,
                "utilization": agent.current_tasks / max(agent.max_concurrent_tasks, 1)
            }
            for agent in agents
        ]
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return {
            "default_strategy": self.default_strategy,
            "available_strategies": list(self.routing_strategies.keys()),
            "round_robin_positions": self.round_robin_index.copy()
        }


# Global router instance (singleton)
_router_instance: Optional[AgentRouter] = None


def get_router(coordinator: Optional[AgentCoordinator] = None) -> AgentRouter:
    """Get the global router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = AgentRouter(coordinator)
    return _router_instance


if __name__ == "__main__":
    # Example usage
    from agent_coordinator import AgentCoordinator, TaskPriority
    
    coordinator = AgentCoordinator()
    coordinator.start()
    
    router = AgentRouter(coordinator)
    
    # Register agents
    coordinator.register_agent(
        "conversation_agent",
        "Conversation Agent",
        ["nlp", "intent_classification", "context_management"],
        max_concurrent_tasks=10
    )
    
    coordinator.register_agent(
        "quote_agent",
        "Quote Agent",
        ["quote_generation", "price_calculation", "validation"],
        max_concurrent_tasks=5
    )
    
    # Route a task
    task_id = router.route_task(
        task_type="process_message",
        payload={"message": "Hola, quiero cotizar"},
        priority=TaskPriority.NORMAL,
        required_capabilities=["nlp"],
        strategy="balanced"
    )
    
    print(f"Routed task: {task_id}")
    print(f"Available agents: {router.get_available_agents(['nlp'])}")
    
    coordinator.stop()
