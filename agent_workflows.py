#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Workflows - Multi-step Workflow Execution Engine
Defines and executes automated workflows with conditional branching
"""

import ast
import logging
import operator
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

from agent_coordinator import AgentCoordinator, TaskPriority, get_coordinator
from agent_router import AgentRouter, get_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING = "waiting"


class StepType(Enum):
    """Workflow step types"""
    TASK = "task"
    CONDITION = "condition"
    PARALLEL = "parallel"
    DELAY = "delay"
    CALLBACK = "callback"


@dataclass
class WorkflowStep:
    """A step in a workflow"""
    step_id: str
    step_type: StepType
    name: str
    config: Dict[str, Any]
    next_steps: List[str] = field(default_factory=list)  # IDs of next steps
    condition: Optional[str] = None  # Condition expression for conditional steps
    timeout: Optional[int] = None  # Timeout in seconds
    retry_count: int = 0
    max_retries: int = 0


@dataclass
class WorkflowDefinition:
    """Workflow definition"""
    workflow_id: str
    name: str
    description: str
    version: str = "1.0"
    steps: List[WorkflowStep] = field(default_factory=list)
    start_step_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Workflow execution instance"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    current_step_id: Optional[str] = None
    step_results: Dict[str, Any] = field(default_factory=dict)
    workflow_data: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class _SafeConditionEvaluator(ast.NodeVisitor):
    """Safely evaluate workflow condition expressions."""

    _COMPARE_OPERATORS = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.In: lambda left, right: left in right,
        ast.NotIn: lambda left, right: left not in right,
        ast.Is: operator.is_,
        ast.IsNot: operator.is_not,
    }

    def __init__(self, context: Dict[str, Any]):
        self.context = context

    def evaluate(self, expression: str) -> Any:
        """Parse and safely evaluate the provided expression."""
        if not expression:
            return True

        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise ValueError("Invalid condition expression") from exc

        return self.visit(tree.body)

    def generic_visit(self, node):
        raise ValueError(f"Unsupported expression: {type(node).__name__}")

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        if isinstance(node.op, ast.And):
            for value in node.values:
                if not self.visit(value):
                    return False
            return True
        if isinstance(node.op, ast.Or):
            for value in node.values:
                if self.visit(value):
                    return True
            return False
        raise ValueError("Unsupported boolean operator")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        if isinstance(node.op, ast.Not):
            return not self.visit(node.operand)
        raise ValueError("Unsupported unary operator")

    def visit_Compare(self, node: ast.Compare) -> Any:
        left = self.visit(node.left)

        for operator_node, comparator in zip(node.ops, node.comparators):
            op_type = type(operator_node)
            if op_type not in self._COMPARE_OPERATORS:
                raise ValueError(f"Unsupported comparison operator: {op_type.__name__}")

            right = self.visit(comparator)
            if not self._COMPARE_OPERATORS[op_type](left, right):
                return False
            left = right

        return True

    def visit_Name(self, node: ast.Name) -> Any:
        lowered = node.id.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        if lowered == "null":
            return None
        if node.id in self.context:
            return self.context[node.id]
        raise ValueError(f"Unknown identifier: {node.id}")

    def visit_Constant(self, node: ast.Constant) -> Any:
        return node.value

    def visit_NameConstant(self, node: ast.NameConstant) -> Any:  # pragma: no cover
        return node.value

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        value = self.visit(node.value)
        attr = node.attr

        if attr.startswith("_"):
            raise ValueError("Access to private attributes is not allowed")

        if isinstance(value, dict):
            return value.get(attr)

        if hasattr(value, attr):
            return getattr(value, attr)

        raise AttributeError(f"Attribute {attr} not found in object {value}")

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        target = self.visit(node.value)
        index = self._evaluate_subscript_index(node.slice)

        try:
            return target[index]
        except (TypeError, KeyError, IndexError) as exc:
            raise ValueError("Invalid subscript access in condition expression") from exc

    def visit_List(self, node: ast.List) -> Any:
        return [self.visit(element) for element in node.elts]

    def visit_Tuple(self, node: ast.Tuple) -> Any:
        return tuple(self.visit(element) for element in node.elts)

    def visit_Set(self, node: ast.Set) -> Any:
        return {self.visit(element) for element in node.elts}

    def visit_Dict(self, node: ast.Dict) -> Any:
        return {
            self.visit(key): self.visit(value)
            for key, value in zip(node.keys, node.values)
        }

    def visit_Call(self, node: ast.Call) -> Any:
        raise ValueError("Function calls are not allowed in condition expressions")

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        raise ValueError("Binary operations are not allowed in condition expressions")

    def visit_Lambda(self, node: ast.Lambda) -> Any:
        raise ValueError("Lambda expressions are not allowed in condition expressions")

    def _evaluate_subscript_index(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            return self.visit_Name(node)
        if hasattr(ast, "Index") and isinstance(node, ast.Index):  # pragma: no cover
            return self._evaluate_subscript_index(node.value)
        raise ValueError("Only constant indexes are allowed in condition expressions")


class WorkflowEngine:
    """Workflow execution engine"""
    
    def __init__(self, coordinator: Optional[AgentCoordinator] = None,
                 router: Optional[AgentRouter] = None):
        """
        Initialize the workflow engine
        
        Args:
            coordinator: Agent coordinator instance
            router: Agent router instance
        """
        self.coordinator = coordinator or get_coordinator()
        self.router = router or get_router(self.coordinator)
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.completed_executions: List[WorkflowExecution] = []
        
        # Load predefined workflows
        self._load_predefined_workflows()
        
        logger.info("Workflow Engine initialized")
    
    def _load_predefined_workflows(self):
        """Load predefined workflows"""
        # Follow-up workflow
        followup_workflow = self._create_followup_workflow()
        self.register_workflow(followup_workflow)
        
        # Quote creation workflow
        quote_workflow = self._create_quote_workflow()
        self.register_workflow(quote_workflow)
        
        logger.info(f"Loaded {len(self.workflow_definitions)} predefined workflows")
    
    def _create_followup_workflow(self) -> WorkflowDefinition:
        """Create predefined follow-up workflow"""
        workflow_id = "followup_workflow"
        
        steps = [
            WorkflowStep(
                step_id="check_conversation",
                step_type=StepType.TASK,
                name="Check Conversation Status",
                config={
                    "task_type": "check_conversation",
                    "required_capabilities": ["follow_up"]
                },
                next_steps=["generate_message"]
            ),
            WorkflowStep(
                step_id="generate_message",
                step_type=StepType.TASK,
                name="Generate Follow-up Message",
                config={
                    "task_type": "generate_followup_message",
                    "use_ai": True
                },
                next_steps=["send_message"]
            ),
            WorkflowStep(
                step_id="send_message",
                step_type=StepType.TASK,
                name="Send Follow-up Message",
                config={
                    "task_type": "send_message",
                    "channel": "whatsapp"
                },
                next_steps=["log_result"]
            ),
            WorkflowStep(
                step_id="log_result",
                step_type=StepType.TASK,
                name="Log Result",
                config={
                    "task_type": "log_followup"
                },
                next_steps=[]
            )
        ]
        
        return WorkflowDefinition(
            workflow_id=workflow_id,
            name="Follow-up Workflow",
            description="Automated follow-up workflow for conversations",
            steps=steps,
            start_step_id="check_conversation"
        )
    
    def _create_quote_workflow(self) -> WorkflowDefinition:
        """Create predefined quote creation workflow"""
        workflow_id = "quote_workflow"
        
        steps = [
            WorkflowStep(
                step_id="validate_data",
                step_type=StepType.TASK,
                name="Validate Quote Data",
                config={
                    "task_type": "validate_quote_data"
                },
                next_steps=["check_condition"],
                max_retries=2
            ),
            WorkflowStep(
                step_id="check_condition",
                step_type=StepType.CONDITION,
                name="Check Data Completeness",
                config={},
                condition="workflow_data.complete == true",
                next_steps=["create_quote", "request_missing_data"]
            ),
            WorkflowStep(
                step_id="request_missing_data",
                step_type=StepType.TASK,
                name="Request Missing Data",
                config={
                    "task_type": "request_missing_data"
                },
                next_steps=[]
            ),
            WorkflowStep(
                step_id="create_quote",
                step_type=StepType.TASK,
                name="Create Quote",
                config={
                    "task_type": "create_quote"
                },
                next_steps=["send_confirmation"]
            ),
            WorkflowStep(
                step_id="send_confirmation",
                step_type=StepType.TASK,
                name="Send Confirmation",
                config={
                    "task_type": "send_message",
                    "channel": "whatsapp"
                },
                next_steps=[]
            )
        ]
        
        return WorkflowDefinition(
            workflow_id=workflow_id,
            name="Quote Creation Workflow",
            description="Automated quote creation workflow",
            steps=steps,
            start_step_id="validate_data"
        )
    
    def register_workflow(self, workflow: WorkflowDefinition):
        """
        Register a workflow definition
        
        Args:
            workflow: Workflow definition
        """
        self.workflow_definitions[workflow.workflow_id] = workflow
        logger.info(f"✅ Registered workflow: {workflow.workflow_id} ({workflow.name})")
    
    def execute_workflow(self, workflow_id: str, initial_data: Dict[str, Any] = None) -> str:
        """
        Execute a workflow
        
        Args:
            workflow_id: ID of workflow to execute
            initial_data: Initial workflow data
            
        Returns:
            execution_id: Unique identifier for this execution
        """
        if workflow_id not in self.workflow_definitions:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflow_definitions[workflow_id]
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            workflow_data=initial_data or {},
            current_step_id=workflow.start_step_id
        )
        
        self.active_executions[execution_id] = execution
        
        # Start execution in background
        import threading
        thread = threading.Thread(target=self._execute_workflow_thread, args=(execution,), daemon=True)
        thread.start()
        
        logger.info(f"🚀 Started workflow execution: {execution_id} (workflow: {workflow_id})")
        
        return execution_id
    
    def _execute_workflow_thread(self, execution: WorkflowExecution):
        """Execute workflow in background thread"""
        try:
            workflow = self.workflow_definitions[execution.workflow_id]
            execution.status = WorkflowStatus.RUNNING
            
            current_step_id = execution.current_step_id or workflow.start_step_id
            
            while current_step_id:
                step = self._get_step_by_id(workflow, current_step_id)
                if not step:
                    execution.status = WorkflowStatus.FAILED
                    execution.error = f"Step {current_step_id} not found"
                    break
                
                # Execute step
                try:
                    result = self._execute_step(step, execution)
                    execution.step_results[step.step_id] = result
                    
                    # Determine next step
                    current_step_id = self._get_next_step(step, execution, result)
                    
                    if not current_step_id:
                        # Workflow completed
                        execution.status = WorkflowStatus.COMPLETED
                        execution.completed_at = datetime.now()
                        break
                    
                    execution.current_step_id = current_step_id
                    
                except Exception as e:
                    logger.error(f"Error executing step {step.step_id}: {e}")
                    
                    # Retry logic
                    if step.retry_count < step.max_retries:
                        step.retry_count += 1
                        logger.info(f"Retrying step {step.step_id} (attempt {step.retry_count})")
                        continue
                    else:
                        execution.status = WorkflowStatus.FAILED
                        execution.error = f"Step {step.step_id} failed: {str(e)}"
                        break
            
        except Exception as e:
            logger.error(f"Error in workflow execution {execution.execution_id}: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
        finally:
            # Move to completed executions
            if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                self.completed_executions.append(execution)
                if execution.execution_id in self.active_executions:
                    del self.active_executions[execution.execution_id]
    
    def _get_step_by_id(self, workflow: WorkflowDefinition, step_id: str) -> Optional[WorkflowStep]:
        """Get step by ID"""
        for step in workflow.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def _execute_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Execute a workflow step"""
        logger.info(f"Executing step: {step.name} ({step.step_id})")
        
        if step.step_type == StepType.TASK:
            return self._execute_task_step(step, execution)
        elif step.step_type == StepType.CONDITION:
            return self._execute_condition_step(step, execution)
        elif step.step_type == StepType.DELAY:
            return self._execute_delay_step(step, execution)
        elif step.step_type == StepType.PARALLEL:
            return self._execute_parallel_step(step, execution)
        elif step.step_type == StepType.CALLBACK:
            return self._execute_callback_step(step, execution)
        else:
            raise ValueError(f"Unknown step type: {step.step_type}")
    
    def _execute_task_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Execute a task step"""
        task_type = step.config.get("task_type")
        payload = step.config.get("payload", {})
        
        # Merge workflow data into payload
        payload.update(execution.workflow_data)
        
        # Submit task to coordinator
        task_id = self.coordinator.submit_task(
            task_type=task_type,
            payload=payload,
            priority=TaskPriority.NORMAL,
            required_capabilities=step.config.get("required_capabilities", [])
        )
        
        # Wait for task completion (simplified - in production, use async/await)
        import time
        max_wait = step.timeout or 300  # Default 5 minutes
        waited = 0
        
        while waited < max_wait:
            task_status = self.coordinator.get_task_status(task_id)
            if task_status and task_status.get("status") == "completed":
                return task_status.get("result")
            elif task_status and task_status.get("status") == "failed":
                raise Exception(f"Task failed: {task_status.get('error')}")
            
            time.sleep(1)
            waited += 1
        
        raise TimeoutError(f"Task {task_id} timed out")
    
    def _execute_condition_step(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        """Execute a condition step"""
        if not step.condition:
            return True
        
        try:
            evaluator = _SafeConditionEvaluator({"workflow_data": execution.workflow_data})
            condition_result = evaluator.evaluate(step.condition)
            return bool(condition_result)
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    def _execute_delay_step(self, step: WorkflowStep, execution: WorkflowExecution) -> None:
        """Execute a delay step"""
        delay_seconds = step.config.get("delay", 0)
        import time
        time.sleep(delay_seconds)
        return None
    
    def _execute_parallel_step(self, step: WorkflowStep, execution: WorkflowExecution) -> List[Any]:
        """Execute parallel steps"""
        # TODO: Implement parallel execution
        return []
    
    def _execute_callback_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Execute a callback step"""
        callback_name = step.config.get("callback")
        if callback_name and hasattr(self, callback_name):
            callback = getattr(self, callback_name)
            return callback(execution)
        return None
    
    def _get_next_step(self, step: WorkflowStep, execution: WorkflowExecution, result: Any) -> Optional[str]:
        """Determine next step based on step type and result"""
        if step.step_type == StepType.CONDITION:
            # Condition step: choose next step based on condition result
            condition_result = bool(result)
            if condition_result and step.next_steps:
                return step.next_steps[0]  # First step for true
            elif not condition_result and len(step.next_steps) > 1:
                return step.next_steps[1]  # Second step for false
            else:
                return None
        else:
            # Regular step: go to first next step
            if step.next_steps:
                return step.next_steps[0]
            return None
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of workflow execution"""
        execution = self.active_executions.get(execution_id)
        if not execution:
            # Check completed executions
            for exec in self.completed_executions:
                if exec.execution_id == execution_id:
                    execution = exec
                    break
        
        if execution:
            return {
                "execution_id": execution.execution_id,
                "workflow_id": execution.workflow_id,
                "status": execution.status.value,
                "current_step_id": execution.current_step_id,
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "error": execution.error,
                "step_results": execution.step_results
            }
        return None
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all registered workflows"""
        return [
            {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "description": wf.description,
                "version": wf.version,
                "steps_count": len(wf.steps)
            }
            for wf in self.workflow_definitions.values()
        ]


# Global workflow engine instance (singleton)
_workflow_engine_instance: Optional[WorkflowEngine] = None


def get_workflow_engine(coordinator: Optional[AgentCoordinator] = None,
                       router: Optional[AgentRouter] = None) -> WorkflowEngine:
    """Get the global workflow engine instance (singleton)"""
    global _workflow_engine_instance
    if _workflow_engine_instance is None:
        _workflow_engine_instance = WorkflowEngine(coordinator, router)
    return _workflow_engine_instance


if __name__ == "__main__":
    # Example usage
    from agent_coordinator import AgentCoordinator
    from agent_router import AgentRouter
    
    coordinator = AgentCoordinator()
    coordinator.start()
    
    router = AgentRouter(coordinator)
    engine = WorkflowEngine(coordinator, router)
    
    # List workflows
    print("Available workflows:")
    for wf in engine.list_workflows():
        print(f"  - {wf['name']} ({wf['workflow_id']})")
    
    coordinator.stop()

