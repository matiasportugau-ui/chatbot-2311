#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Builder - Personalized Agenda for Agent Development
Creates and manages agent configurations with consultation history tracking.
Provides progressively deeper insights and development assistance.
"""

import json
import logging
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of agents that can be built"""
    SALES = "sales"
    SUPPORT = "support"
    FOLLOW_UP = "follow_up"
    QUOTES = "quotes"
    ANALYTICS = "analytics"
    CUSTOM = "custom"


class ConsultationLevel(Enum):
    """Levels of consultation depth"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class Consultation:
    """Represents a consultation session"""
    consultation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    topic: str = ""
    level: ConsultationLevel = ConsultationLevel.BASIC
    questions: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    code_examples: List[Dict[str, str]] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['level'] = self.level.value
        return data


@dataclass
class AgentBlueprint:
    """Blueprint for an agent being built"""
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = ""
    agent_type: AgentType = AgentType.CUSTOM
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Agent configuration
    capabilities: List[str] = field(default_factory=list)
    intents: List[str] = field(default_factory=list)
    workflows: List[str] = field(default_factory=list)
    priority_level: str = "NORMAL"
    
    # Development tracking
    consultations: List[Consultation] = field(default_factory=list)
    development_stage: str = "planning"  # planning, development, testing, production
    completion_percentage: float = 0.0
    
    # Custom configuration
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['agent_type'] = self.agent_type.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['consultations'] = [c.to_dict() for c in self.consultations]
        return data


class AgentBuilder:
    """
    Agent Builder with Personalized Agenda System
    Provides progressive consultation and development assistance
    """
    
    def __init__(self, storage_path: str = "./data/agent_builder"):
        """
        Initialize the Agent Builder
        
        Args:
            storage_path: Path to store agent blueprints and consultation history
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        self.blueprints: Dict[str, AgentBlueprint] = {}
        self.load_blueprints()
        
        logger.info(f"Agent Builder initialized with {len(self.blueprints)} existing blueprints")
    
    def create_agent_blueprint(
        self,
        agent_name: str,
        agent_type: AgentType,
        initial_capabilities: Optional[List[str]] = None
    ) -> AgentBlueprint:
        """
        Create a new agent blueprint
        
        Args:
            agent_name: Name for the agent
            agent_type: Type of agent to build
            initial_capabilities: Initial list of capabilities
        
        Returns:
            New agent blueprint
        """
        blueprint = AgentBlueprint(
            agent_name=agent_name,
            agent_type=agent_type,
            capabilities=initial_capabilities or []
        )
        
        self.blueprints[blueprint.agent_id] = blueprint
        self.save_blueprint(blueprint)
        
        logger.info(f"Created new agent blueprint: {agent_name} ({agent_type.value})")
        return blueprint
    
    def consult(
        self,
        agent_id: str,
        topic: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Consultation:
        """
        Conduct a consultation for an agent being developed.
        Each consultation provides progressively deeper insights.
        
        Args:
            agent_id: ID of the agent blueprint
            topic: Topic of consultation
            context: Additional context for the consultation
        
        Returns:
            Consultation with recommendations and insights
        """
        if agent_id not in self.blueprints:
            raise ValueError(f"Agent blueprint {agent_id} not found")
        
        blueprint = self.blueprints[agent_id]
        
        # Determine consultation level based on history
        consultation_count = len(blueprint.consultations)
        level = self._determine_consultation_level(consultation_count)
        
        # Create consultation
        consultation = Consultation(
            topic=topic,
            level=level
        )
        
        # Generate recommendations based on level and context
        self._generate_recommendations(consultation, blueprint, context)
        
        # Add to blueprint history
        blueprint.consultations.append(consultation)
        blueprint.updated_at = datetime.now()
        
        # Update development stage
        self._update_development_stage(blueprint)
        
        # Save updated blueprint
        self.save_blueprint(blueprint)
        
        logger.info(
            f"Consultation completed for {blueprint.agent_name}: "
            f"{topic} (Level: {level.value})"
        )
        
        return consultation
    
    def _determine_consultation_level(self, consultation_count: int) -> ConsultationLevel:
        """Determine consultation level based on history"""
        if consultation_count == 0:
            return ConsultationLevel.BASIC
        elif consultation_count <= 3:
            return ConsultationLevel.INTERMEDIATE
        elif consultation_count <= 7:
            return ConsultationLevel.ADVANCED
        else:
            return ConsultationLevel.EXPERT
    
    def _generate_recommendations(
        self,
        consultation: Consultation,
        blueprint: AgentBlueprint,
        context: Optional[Dict[str, Any]]
    ):
        """Generate recommendations based on consultation level"""
        level = consultation.level
        topic = consultation.topic.lower()
        
        # Basic level recommendations
        if level == ConsultationLevel.BASIC:
            consultation.recommendations.extend([
                f"Define the core purpose of your {blueprint.agent_type.value} agent",
                "Identify the main capabilities and intents the agent should handle",
                "Establish basic workflows and response patterns",
                "Set up agent configuration in agent_config.json"
            ])
            
            consultation.insights.extend([
                "Start with a clear, focused scope for your agent",
                "Use existing agent patterns as templates",
                "Test with simple scenarios first"
            ])
            
            consultation.code_examples.append({
                "title": "Basic Agent Registration",
                "code": """
from agent_coordinator import get_coordinator, TaskPriority

coordinator = get_coordinator()
agent_id = coordinator.register_agent(
    agent_type="{agent_type}",
    agent_instance=my_agent,
    capabilities=["{capability}"]
)
""".format(
                    agent_type=blueprint.agent_type.value,
                    capability=blueprint.capabilities[0] if blueprint.capabilities and len(blueprint.capabilities) > 0 else "basic_capability"
                )
            })
        
        # Intermediate level recommendations
        elif level == ConsultationLevel.INTERMEDIATE:
            consultation.recommendations.extend([
                "Implement advanced routing logic for complex scenarios",
                "Add context awareness to your agent's responses",
                "Integrate with the workflow engine for multi-step processes",
                "Implement error handling and fallback mechanisms"
            ])
            
            consultation.insights.extend([
                "Context retention improves multi-turn conversations",
                "Use the router's intent analysis for better request handling",
                "Implement graceful degradation for unexpected inputs",
                "Monitor agent performance metrics"
            ])
            
            consultation.code_examples.append({
                "title": "Advanced Agent with Context",
                "code": """
from agent_router import get_router, RoutingContext

router = get_router()

context = RoutingContext(
    message=user_message,
    user_id=user_id,
    session_data=session_data,
    urgency="high" if is_urgent else "normal"
)

decision = router.route_message(user_message, context)
"""
            })
        
        # Advanced level recommendations
        elif level == ConsultationLevel.ADVANCED:
            consultation.recommendations.extend([
                "Implement proactive agent behaviors and automation",
                "Add comprehensive monitoring and alerting",
                "Create custom workflows with conditional branching",
                "Integrate with external systems (MongoDB, WhatsApp, n8n)",
                "Implement A/B testing for response optimization"
            ])
            
            consultation.insights.extend([
                "Proactive agents can significantly improve user engagement",
                "Use the workflow engine for complex multi-step automation",
                "Monitor and optimize based on metrics and user feedback",
                "Consider implementing machine learning for intent classification",
                "Design for scalability and concurrent operations"
            ])
            
            consultation.code_examples.append({
                "title": "Proactive Agent with Workflow",
                "code": """
from agent_workflows import get_workflow_engine, WorkflowStep, StepType
from proactive_agent_actions import get_proactive_actions

workflow_engine = get_workflow_engine()
proactive_actions = get_proactive_actions()

# Create custom workflow
workflow_id = workflow_engine.create_workflow(
    name="follow_up_abandoned_quotes",
    steps=[
        WorkflowStep(
            step_id="detect",
            step_type=StepType.TASK,
            agent_type="analytics",
            task_type="detect_abandoned_quotes"
        ),
        WorkflowStep(
            step_id="generate_message",
            step_type=StepType.TASK,
            agent_type="sales",
            task_type="generate_followup"
        ),
        WorkflowStep(
            step_id="send",
            step_type=StepType.TASK,
            agent_type="follow_up",
            task_type="send_message"
        )
    ]
)
"""
            })
        
        # Expert level recommendations
        else:  # EXPERT
            consultation.recommendations.extend([
                "Implement custom agent architectures with specialized capabilities",
                "Build agent collaboration and multi-agent systems",
                "Create self-improving agents with learning capabilities",
                "Design advanced scheduling with dynamic priorities",
                "Implement comprehensive security and compliance measures",
                "Build custom analytics and reporting dashboards"
            ])
            
            consultation.insights.extend([
                "Multi-agent systems can handle complex, distributed workflows",
                "Implement agent specialization for optimal performance",
                "Use event-driven architectures for real-time responsiveness",
                "Consider implementing reinforcement learning for optimization",
                "Design for fault tolerance and disaster recovery",
                "Leverage distributed computing for high-volume scenarios"
            ])
            
            consultation.code_examples.append({
                "title": "Multi-Agent Collaboration System",
                "code": """
from automated_agent_system import AutomatedAgentSystem
from agent_coordinator import TaskPriority

system = AutomatedAgentSystem(ia_instance=ia)
system.start()

# Create collaborative workflow
def collaborative_quote_generation(customer_data):
    # Analytics agent analyzes customer history
    analysis_task = system.coordinator.submit_task(
        task_type="analyze_customer",
        payload=customer_data,
        priority=TaskPriority.HIGH
    )
    
    # Sales agent creates personalized quote
    quote_task = system.coordinator.submit_task(
        task_type="create_quote",
        payload={"customer_analysis": analysis_task.result},
        priority=TaskPriority.HIGH
    )
    
    # Follow-up agent schedules reminders
    followup_task = system.coordinator.submit_task(
        task_type="schedule_followup",
        payload={"quote_id": quote_task.result["quote_id"]},
        priority=TaskPriority.NORMAL
    )
    
    return quote_task.result
"""
            })
        
        # Add topic-specific recommendations
        if "workflow" in topic:
            consultation.recommendations.append(
                "Study the WorkflowEngine class in agent_workflows.py for workflow patterns"
            )
            consultation.next_steps.append("Create a custom workflow for your use case")
        
        if "monitoring" in topic or "metrics" in topic:
            consultation.recommendations.append(
                "Implement custom metrics collection using the AgentMonitoring class"
            )
            consultation.next_steps.append("Set up alerts for critical agent failures")
        
        if "integration" in topic:
            consultation.recommendations.append(
                "Review integration patterns in proactive_agent_actions.py"
            )
            consultation.next_steps.append("Test integration with external services")
        
        # Always provide next steps
        if not consultation.next_steps:
            consultation.next_steps.extend([
                f"Test the {blueprint.agent_type.value} agent with real scenarios",
                "Review and refine based on consultation recommendations",
                "Schedule next consultation to discuss implementation progress"
            ])
    
    def _update_development_stage(self, blueprint: AgentBlueprint):
        """Update development stage based on consultation count and content"""
        consultation_count = len(blueprint.consultations)
        
        if consultation_count >= 8:
            blueprint.development_stage = "production"
            blueprint.completion_percentage = 95.0
        elif consultation_count >= 5:
            blueprint.development_stage = "testing"
            blueprint.completion_percentage = 75.0
        elif consultation_count >= 2:
            blueprint.development_stage = "development"
            blueprint.completion_percentage = 50.0
        else:
            blueprint.development_stage = "planning"
            blueprint.completion_percentage = 25.0
    
    def get_blueprint(self, agent_id: str) -> Optional[AgentBlueprint]:
        """Get an agent blueprint by ID"""
        return self.blueprints.get(agent_id)
    
    def list_blueprints(self) -> List[AgentBlueprint]:
        """List all agent blueprints"""
        return list(self.blueprints.values())
    
    def update_blueprint(
        self,
        agent_id: str,
        updates: Dict[str, Any]
    ) -> AgentBlueprint:
        """
        Update an agent blueprint
        
        Args:
            agent_id: ID of the blueprint to update
            updates: Dictionary of updates to apply
        
        Returns:
            Updated blueprint
        """
        if agent_id not in self.blueprints:
            raise ValueError(f"Agent blueprint {agent_id} not found")
        
        blueprint = self.blueprints[agent_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(blueprint, key):
                setattr(blueprint, key, value)
        
        blueprint.updated_at = datetime.now()
        self.save_blueprint(blueprint)
        
        logger.info(f"Updated blueprint {blueprint.agent_name}")
        return blueprint
    
    def delete_blueprint(self, agent_id: str):
        """Delete an agent blueprint"""
        if agent_id in self.blueprints:
            blueprint = self.blueprints.pop(agent_id)
            
            # Delete file
            filepath = os.path.join(
                self.storage_path,
                f"blueprint_{agent_id}.json"
            )
            if os.path.exists(filepath):
                os.remove(filepath)
            
            logger.info(f"Deleted blueprint {blueprint.agent_name}")
    
    def save_blueprint(self, blueprint: AgentBlueprint):
        """Save a blueprint to disk"""
        filepath = os.path.join(
            self.storage_path,
            f"blueprint_{blueprint.agent_id}.json"
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(blueprint.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_blueprints(self):
        """Load all blueprints from disk"""
        if not os.path.exists(self.storage_path):
            return
        
        for filename in os.listdir(self.storage_path):
            if filename.startswith("blueprint_") and filename.endswith(".json"):
                filepath = os.path.join(self.storage_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Reconstruct blueprint
                    blueprint = self._dict_to_blueprint(data)
                    self.blueprints[blueprint.agent_id] = blueprint
                    
                except Exception as e:
                    logger.error(f"Error loading blueprint {filename}: {e}")
    
    def _dict_to_blueprint(self, data: Dict[str, Any]) -> AgentBlueprint:
        """Convert dictionary to AgentBlueprint"""
        try:
            # Parse dates
            data['created_at'] = datetime.fromisoformat(data['created_at'])
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            
            # Parse agent type
            data['agent_type'] = AgentType(data['agent_type'])
            
            # Parse consultations
            consultations = []
            for c_data in data.get('consultations', []):
                c_data['timestamp'] = datetime.fromisoformat(c_data['timestamp'])
                c_data['level'] = ConsultationLevel(c_data['level'])
                consultations.append(Consultation(**c_data))
            data['consultations'] = consultations
            
            return AgentBlueprint(**data)
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing blueprint data: {e}")
            raise ValueError(f"Invalid blueprint data format: {e}")
    
    def generate_report(self, agent_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive report for an agent blueprint
        
        Args:
            agent_id: ID of the blueprint
        
        Returns:
            Report dictionary
        """
        if agent_id not in self.blueprints:
            raise ValueError(f"Agent blueprint {agent_id} not found")
        
        blueprint = self.blueprints[agent_id]
        
        report = {
            "agent_name": blueprint.agent_name,
            "agent_type": blueprint.agent_type.value,
            "development_stage": blueprint.development_stage,
            "completion_percentage": blueprint.completion_percentage,
            "created_at": blueprint.created_at.isoformat(),
            "updated_at": blueprint.updated_at.isoformat(),
            "total_consultations": len(blueprint.consultations),
            "capabilities_count": len(blueprint.capabilities),
            "intents_count": len(blueprint.intents),
            "workflows_count": len(blueprint.workflows),
            "consultation_history": [
                {
                    "topic": c.topic,
                    "level": c.level.value,
                    "timestamp": c.timestamp.isoformat(),
                    "recommendations_count": len(c.recommendations),
                    "insights_count": len(c.insights)
                }
                for c in blueprint.consultations
            ]
        }
        
        return report


# Singleton instance
_builder_instance: Optional[AgentBuilder] = None


def get_agent_builder() -> AgentBuilder:
    """Get or create the singleton AgentBuilder instance"""
    global _builder_instance
    if _builder_instance is None:
        _builder_instance = AgentBuilder()
    return _builder_instance


if __name__ == "__main__":
    # Demo usage
    builder = get_agent_builder()
    
    # Create a new agent blueprint
    blueprint = builder.create_agent_blueprint(
        agent_name="CustomerSupportAgent",
        agent_type=AgentType.SUPPORT,
        initial_capabilities=["answer_questions", "handle_complaints"]
    )
    
    print(f"\n=== Created Agent Blueprint ===")
    print(f"Name: {blueprint.agent_name}")
    print(f"Type: {blueprint.agent_type.value}")
    print(f"ID: {blueprint.agent_id}")
    
    # First consultation - Basic level
    consultation1 = builder.consult(
        blueprint.agent_id,
        "How do I set up the agent routing?"
    )
    
    print(f"\n=== Consultation 1 ({consultation1.level.value}) ===")
    print(f"Topic: {consultation1.topic}")
    print(f"Recommendations: {len(consultation1.recommendations)}")
    for i, rec in enumerate(consultation1.recommendations, 1):
        print(f"  {i}. {rec}")
    
    # Second consultation - Progresses to intermediate
    consultation2 = builder.consult(
        blueprint.agent_id,
        "How can I add context awareness to responses?"
    )
    
    print(f"\n=== Consultation 2 ({consultation2.level.value}) ===")
    print(f"Topic: {consultation2.topic}")
    print(f"Insights: {len(consultation2.insights)}")
    for i, insight in enumerate(consultation2.insights, 1):
        print(f"  {i}. {insight}")
    
    # Generate report
    report = builder.generate_report(blueprint.agent_id)
    print(f"\n=== Development Report ===")
    print(f"Stage: {report['development_stage']}")
    print(f"Completion: {report['completion_percentage']}%")
    print(f"Total Consultations: {report['total_consultations']}")
