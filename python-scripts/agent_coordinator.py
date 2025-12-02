#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Coordinator - Task Distribution and Agent Management
Manages agent registration, task queues, and task assignment
"""

import logging
import uuid
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import deque
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStatus(Enum):
    """Agent status"""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class Agent:
    """Agent representation"""
    agent_id: str
    name: str
    capabilities: List[str]
    status: AgentStatus = AgentStatus.IDLE
    current_tasks: int = 0
    max_concurrent_tasks: int = 5
    registered_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Task representation"""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    required_capabilities: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3


class AgentCoordinator:
    """Coordinates agent tasks and manages agent registry"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: deque = deque()  # Priority queue
        self.lock = threading.RLock()
        self.running = False
        
        # Health check settings
        self.heartbeat_timeout = timedelta(minutes=5)
        self.health_check_interval = timedelta(seconds=30)
        
        logger.info("Agent Coordinator initialized")
    
    def start(self):
        """Start the coordinator"""
        self.running = True
        # Start background health check thread
        health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        health_thread.start()
        logger.info("Agent Coordinator started")
    
    def stop(self):
        """Stop the coordinator"""
        self.running = False
        logger.info("Agent Coordinator stopped")
    
    def register_agent(
        self,
        agent_id: str,
        name: str,
        capabilities: List[str],
        max_concurrent_tasks: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register an agent with the coordinator
        
        Args:
            agent_id: Unique agent identifier
            name: Agent name
            capabilities: List of agent capabilities
            max_concurrent_tasks: Maximum concurrent tasks for this agent
            metadata: Optional metadata
            
        Returns:
            True if registration successful
        """
        with self.lock:
            if agent_id in self.agents:
                logger.warning(f"Agent {agent_id} already registered, updating...")
            
            agent = Agent(
                agent_id=agent_id,
                name=name,
                capabilities=capabilities,
                max_concurrent_tasks=max_concurrent_tasks,
                metadata=metadata or {}
            )
            
            self.agents[agent_id] = agent
            logger.info(f"✅ Registered agent: {agent_id} ({name}) with capabilities: {capabilities}")
            return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent"""
        with self.lock:
            if agent_id not in self.agents:
                logger.warning(f"Agent {agent_id} not found")
                return False
            
            # Reassign pending tasks
            agent = self.agents[agent_id]
            if agent.current_tasks > 0:
                logger.warning(f"Agent {agent_id} has {agent.current_tasks} active tasks")
            
            del self.agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
            return True
    
    def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """Update agent status"""
        with self.lock:
            if agent_id not in self.agents:
                logger.warning(f"Agent {agent_id} not found")
                return False
            
            self.agents[agent_id].status = status
            self.agents[agent_id].last_heartbeat = datetime.now()
            logger.debug(f"Updated agent {agent_id} status to {status.value}")
            return True
    
    def update_agent_heartbeat(self, agent_id: str) -> bool:
        """Update agent heartbeat"""
        with self.lock:
            if agent_id not in self.agents:
                return False
            
            self.agents[agent_id].last_heartbeat = datetime.now()
            if self.agents[agent_id].status == AgentStatus.OFFLINE:
                self.agents[agent_id].status = AgentStatus.IDLE
            return True
    
    def submit_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        required_capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> str:
        """
        Submit a task to the coordinator
        
        Args:
            task_type: Type of task
            payload: Task payload/data
            priority: Task priority
            required_capabilities: Required agent capabilities
            metadata: Optional metadata
            max_retries: Maximum retry attempts
            
        Returns:
            Task ID
        """
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            priority=priority,
            required_capabilities=required_capabilities or [],
            metadata=metadata or {},
            max_retries=max_retries
        )
        
        with self.lock:
            self.tasks[task_id] = task
            
            # Add to priority queue
            priority_value = {
                TaskPriority.CRITICAL: 0,
                TaskPriority.HIGH: 1,
                TaskPriority.NORMAL: 2,
                TaskPriority.LOW: 3
            }[priority]
            
            self.task_queue.append((priority_value, task_id))
            logger.info(f"📥 Submitted task: {task_id} (type: {task_type}, priority: {priority.value})")
        
        return task_id
    
    def assign_task_to_agent(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to an agent"""
        with self.lock:
            if task_id not in self.tasks:
                logger.error(f"Task {task_id} not found")
                return False
            
            if agent_id not in self.agents:
                logger.error(f"Agent {agent_id} not found")
                return False
            
            task = self.tasks[task_id]
            agent = self.agents[agent_id]
            
            # Check if agent can handle more tasks
            if agent.current_tasks >= agent.max_concurrent_tasks:
                logger.warning(f"Agent {agent_id} at capacity ({agent.current_tasks}/{agent.max_concurrent_tasks})")
                return False
            
            # Check agent status
            if agent.status == AgentStatus.OFFLINE:
                logger.warning(f"Agent {agent_id} is offline")
                return False
            
            # Assign task
            task.assigned_agent = agent_id
            task.status = TaskStatus.ASSIGNED
            agent.current_tasks += 1
            
            if agent.status == AgentStatus.IDLE:
                agent.status = AgentStatus.BUSY
            
            logger.info(f"✅ Assigned task {task_id} to agent {agent_id}")
            return True
    
    def complete_task(self, task_id: str, result: Any, agent_id: str) -> bool:
        """Mark a task as completed"""
        with self.lock:
            if task_id not in self.tasks:
                logger.error(f"Task {task_id} not found")
                return False
            
            task = self.tasks[task_id]
            
            if task.assigned_agent != agent_id:
                logger.warning(f"Task {task_id} assigned to {task.assigned_agent}, not {agent_id}")
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            
            # Update agent
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                agent.current_tasks = max(0, agent.current_tasks - 1)
                if agent.current_tasks == 0:
                    agent.status = AgentStatus.IDLE
            
            logger.info(f"✅ Task {task_id} completed by agent {agent_id}")
            return True
    
    def fail_task(self, task_id: str, error: str, agent_id: Optional[str] = None) -> bool:
        """Mark a task as failed"""
        with self.lock:
            if task_id not in self.tasks:
                logger.error(f"Task {task_id} not found")
                return False
            
            task = self.tasks[task_id]
            task.error = error
            
            # Check if we should retry
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.assigned_agent = None
                
                # Re-add to queue
                priority_value = {
                    TaskPriority.CRITICAL: 0,
                    TaskPriority.HIGH: 1,
                    TaskPriority.NORMAL: 2,
                    TaskPriority.LOW: 3
                }[task.priority]
                self.task_queue.append((priority_value, task_id))
                
                logger.info(f"🔄 Retrying task {task_id} (attempt {task.retry_count}/{task.max_retries})")
            else:
                task.status = TaskStatus.FAILED
                logger.error(f"❌ Task {task_id} failed after {task.max_retries} retries: {error}")
            
            # Update agent if provided
            if agent_id and agent_id in self.agents:
                agent = self.agents[agent_id]
                agent.current_tasks = max(0, agent.current_tasks - 1)
                if agent.current_tasks == 0:
                    agent.status = AgentStatus.IDLE
            
            return True
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        with self.lock:
            if task_id not in self.tasks:
                return None
            
            task = self.tasks[task_id]
            return {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": task.status.value,
                "assigned_agent": task.assigned_agent,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "result": task.result,
                "error": task.error,
                "retry_count": task.retry_count
            }
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent status"""
        with self.lock:
            if agent_id not in self.agents:
                return None
            
            agent = self.agents[agent_id]
            return {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "capabilities": agent.capabilities,
                "status": agent.status.value,
                "current_tasks": agent.current_tasks,
                "max_concurrent_tasks": agent.max_concurrent_tasks,
                "registered_at": agent.registered_at.isoformat(),
                "last_heartbeat": agent.last_heartbeat.isoformat(),
                "metadata": agent.metadata
            }
    
    def get_available_agents(self, required_capabilities: List[str]) -> List[Agent]:
        """Get agents that have the required capabilities"""
        with self.lock:
            available = []
            for agent in self.agents.values():
                if agent.status == AgentStatus.OFFLINE:
                    continue
                
                if agent.current_tasks >= agent.max_concurrent_tasks:
                    continue
                
                # Check if agent has all required capabilities
                if all(cap in agent.capabilities for cap in required_capabilities):
                    available.append(agent)
            
            return available
    
    def get_pending_tasks(self, limit: int = 100) -> List[Task]:
        """Get pending tasks"""
        with self.lock:
            pending = [task for task in self.tasks.values() if task.status == TaskStatus.PENDING]
            return sorted(pending, key=lambda t: {
                TaskPriority.CRITICAL: 0,
                TaskPriority.HIGH: 1,
                TaskPriority.NORMAL: 2,
                TaskPriority.LOW: 3
            }[t.priority])[:limit]
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        with self.lock:
            total_agents = len(self.agents)
            online_agents = sum(1 for a in self.agents.values() if a.status != AgentStatus.OFFLINE)
            total_tasks = len(self.tasks)
            pending_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
            running_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
            
            return {
                "status": "healthy" if self.running else "stopped",
                "agents": {
                    "total": total_agents,
                    "online": online_agents,
                    "offline": total_agents - online_agents
                },
                "tasks": {
                    "total": total_tasks,
                    "pending": pending_tasks,
                    "running": running_tasks,
                    "completed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
                    "failed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
                },
                "queue_size": len(self.task_queue)
            }
    
    def _health_check_loop(self):
        """Background health check loop"""
        while self.running:
            try:
                with self.lock:
                    now = datetime.now()
                    for agent_id, agent in list(self.agents.items()):
                        time_since_heartbeat = now - agent.last_heartbeat
                        if time_since_heartbeat > self.heartbeat_timeout:
                            logger.warning(f"Agent {agent_id} heartbeat timeout, marking offline")
                            agent.status = AgentStatus.OFFLINE
                
                time.sleep(self.health_check_interval.total_seconds())
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                time.sleep(5)


# Global coordinator instance (singleton)
_coordinator_instance: Optional[AgentCoordinator] = None


def get_coordinator() -> AgentCoordinator:
    """Get the global coordinator instance"""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = AgentCoordinator()
        _coordinator_instance.start()
    return _coordinator_instance


if __name__ == "__main__":
    # Example usage
    coordinator = AgentCoordinator()
    coordinator.start()
    
    # Register agents
    coordinator.register_agent(
        "conversation_agent",
        "Conversation Agent",
        ["nlp", "intent_classification", "context_management"]
    )
    
    coordinator.register_agent(
        "quote_agent",
        "Quote Agent",
        ["quote_generation", "price_calculation", "validation"]
    )
    
    # Submit a task
    task_id = coordinator.submit_task(
        task_type="process_message",
        payload={"message": "Hola, quiero cotizar"},
        priority=TaskPriority.NORMAL,
        required_capabilities=["nlp"]
    )
    
    print(f"Submitted task: {task_id}")
    print(f"Health check: {coordinator.health_check()}")
    
    coordinator.stop()
