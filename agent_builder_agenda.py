#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Builder Agenda - Personalized Schedule Management
Manages consultation schedules, development tasks, and progress tracking
for agent development projects.
"""

import json
import logging
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of development tasks"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for tasks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AgendaItemType(Enum):
    """Types of agenda items"""
    CONSULTATION = "consultation"
    TASK = "task"
    MILESTONE = "milestone"
    REVIEW = "review"
    LEARNING = "learning"


@dataclass
class DevelopmentTask:
    """A development task in the agenda"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_hours: float = 1.0
    actual_hours: float = 0.0
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        data['created_at'] = self.created_at.isoformat()
        data['due_date'] = self.due_date.isoformat() if self.due_date else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data


@dataclass
class AgendaItem:
    """An item in the development agenda"""
    item_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    item_type: AgendaItemType = AgendaItemType.TASK
    title: str = ""
    description: str = ""
    scheduled_time: datetime = field(default_factory=datetime.now)
    duration_minutes: int = 60
    completed: bool = False
    notes: str = ""
    related_task_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['item_type'] = self.item_type.value
        data['scheduled_time'] = self.scheduled_time.isoformat()
        return data


@dataclass
class DevelopmentMilestone:
    """A major milestone in agent development"""
    milestone_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    title: str = ""
    description: str = ""
    target_date: datetime = field(default_factory=datetime.now)
    completed: bool = False
    completed_at: Optional[datetime] = None
    criteria: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['target_date'] = self.target_date.isoformat()
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data


class AgentBuilderAgenda:
    """
    Manages personalized agenda and schedules for agent development.
    Tracks tasks, consultations, milestones, and progress.
    """
    
    def __init__(self, storage_path: str = "./data/agent_builder"):
        """
        Initialize the agenda system
        
        Args:
            storage_path: Path to store agenda data
        """
        self.storage_path = storage_path
        self.agenda_path = os.path.join(storage_path, "agendas")
        os.makedirs(self.agenda_path, exist_ok=True)
        
        self.tasks: Dict[str, DevelopmentTask] = {}
        self.agenda_items: Dict[str, AgendaItem] = {}
        self.milestones: Dict[str, DevelopmentMilestone] = {}
        
        self.load_all_data()
        
        logger.info(
            f"Agenda initialized: {len(self.tasks)} tasks, "
            f"{len(self.agenda_items)} agenda items, "
            f"{len(self.milestones)} milestones"
        )
    
    def create_task(
        self,
        agent_id: str,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        estimated_hours: float = 1.0,
        tags: Optional[List[str]] = None
    ) -> DevelopmentTask:
        """
        Create a new development task
        
        Args:
            agent_id: ID of the agent this task is for
            title: Task title
            description: Task description
            priority: Task priority
            due_date: Due date for the task
            estimated_hours: Estimated hours to complete
            tags: Tags for categorization
        
        Returns:
            Created task
        """
        task = DevelopmentTask(
            agent_id=agent_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            estimated_hours=estimated_hours,
            tags=tags or []
        )
        
        self.tasks[task.task_id] = task
        self.save_task(task)
        
        logger.info(f"Created task: {title} for agent {agent_id}")
        return task
    
    def schedule_consultation(
        self,
        agent_id: str,
        topic: str,
        scheduled_time: datetime,
        duration_minutes: int = 60,
        notes: str = ""
    ) -> AgendaItem:
        """
        Schedule a consultation session
        
        Args:
            agent_id: ID of the agent
            topic: Consultation topic
            scheduled_time: When the consultation should occur
            duration_minutes: Duration in minutes
            notes: Additional notes
        
        Returns:
            Created agenda item
        """
        item = AgendaItem(
            agent_id=agent_id,
            item_type=AgendaItemType.CONSULTATION,
            title=f"Consultation: {topic}",
            description=topic,
            scheduled_time=scheduled_time,
            duration_minutes=duration_minutes,
            notes=notes
        )
        
        self.agenda_items[item.item_id] = item
        self.save_agenda_item(item)
        
        logger.info(
            f"Scheduled consultation for agent {agent_id}: {topic} "
            f"at {scheduled_time.strftime('%Y-%m-%d %H:%M')}"
        )
        return item
    
    def create_milestone(
        self,
        agent_id: str,
        title: str,
        description: str,
        target_date: datetime,
        criteria: Optional[List[str]] = None
    ) -> DevelopmentMilestone:
        """
        Create a development milestone
        
        Args:
            agent_id: ID of the agent
            title: Milestone title
            description: Milestone description
            target_date: Target completion date
            criteria: Success criteria
        
        Returns:
            Created milestone
        """
        milestone = DevelopmentMilestone(
            agent_id=agent_id,
            title=title,
            description=description,
            target_date=target_date,
            criteria=criteria or []
        )
        
        self.milestones[milestone.milestone_id] = milestone
        self.save_milestone(milestone)
        
        logger.info(f"Created milestone: {title} for agent {agent_id}")
        return milestone
    
    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        actual_hours: Optional[float] = None
    ):
        """
        Update task status
        
        Args:
            task_id: Task ID
            status: New status
            actual_hours: Actual hours worked (optional)
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = status
        
        if actual_hours is not None:
            task.actual_hours = actual_hours
        
        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now()
        
        self.save_task(task)
        logger.info(f"Updated task {task.title} to status: {status.value}")
    
    def complete_agenda_item(self, item_id: str, notes: str = ""):
        """
        Mark an agenda item as completed
        
        Args:
            item_id: Agenda item ID
            notes: Completion notes
        """
        if item_id not in self.agenda_items:
            raise ValueError(f"Agenda item {item_id} not found")
        
        item = self.agenda_items[item_id]
        item.completed = True
        if notes:
            item.notes = notes
        
        self.save_agenda_item(item)
        logger.info(f"Completed agenda item: {item.title}")
    
    def complete_milestone(
        self,
        milestone_id: str,
        achievements: Optional[List[str]] = None
    ):
        """
        Complete a milestone
        
        Args:
            milestone_id: Milestone ID
            achievements: List of achievements
        """
        if milestone_id not in self.milestones:
            raise ValueError(f"Milestone {milestone_id} not found")
        
        milestone = self.milestones[milestone_id]
        milestone.completed = True
        milestone.completed_at = datetime.now()
        
        if achievements:
            milestone.achievements.extend(achievements)
        
        self.save_milestone(milestone)
        logger.info(f"Completed milestone: {milestone.title}")
    
    def get_agenda_for_date(
        self,
        date: datetime,
        agent_id: Optional[str] = None
    ) -> List[AgendaItem]:
        """
        Get agenda items for a specific date
        
        Args:
            date: Date to query
            agent_id: Filter by agent ID (optional)
        
        Returns:
            List of agenda items
        """
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        items = []
        for item in self.agenda_items.values():
            if start_of_day <= item.scheduled_time < end_of_day:
                if agent_id is None or item.agent_id == agent_id:
                    items.append(item)
        
        return sorted(items, key=lambda x: x.scheduled_time)
    
    def get_upcoming_agenda(
        self,
        days: int = 7,
        agent_id: Optional[str] = None
    ) -> List[AgendaItem]:
        """
        Get upcoming agenda items
        
        Args:
            days: Number of days to look ahead
            agent_id: Filter by agent ID (optional)
        
        Returns:
            List of upcoming agenda items
        """
        now = datetime.now()
        future = now + timedelta(days=days)
        
        items = []
        for item in self.agenda_items.values():
            if not item.completed and now <= item.scheduled_time <= future:
                if agent_id is None or item.agent_id == agent_id:
                    items.append(item)
        
        return sorted(items, key=lambda x: x.scheduled_time)
    
    def get_tasks_by_status(
        self,
        status: TaskStatus,
        agent_id: Optional[str] = None
    ) -> List[DevelopmentTask]:
        """
        Get tasks by status
        
        Args:
            status: Task status to filter by
            agent_id: Filter by agent ID (optional)
        
        Returns:
            List of tasks
        """
        tasks = []
        for task in self.tasks.values():
            if task.status == status:
                if agent_id is None or task.agent_id == agent_id:
                    tasks.append(task)
        
        return sorted(tasks, key=lambda x: x.created_at, reverse=True)
    
    def get_overdue_tasks(
        self,
        agent_id: Optional[str] = None
    ) -> List[DevelopmentTask]:
        """
        Get overdue tasks
        
        Args:
            agent_id: Filter by agent ID (optional)
        
        Returns:
            List of overdue tasks
        """
        now = datetime.now()
        overdue = []
        
        for task in self.tasks.values():
            if (task.status != TaskStatus.COMPLETED and
                task.due_date and task.due_date < now):
                if agent_id is None or task.agent_id == agent_id:
                    overdue.append(task)
        
        return sorted(overdue, key=lambda x: x.due_date)
    
    def get_milestones(
        self,
        agent_id: Optional[str] = None,
        completed: Optional[bool] = None
    ) -> List[DevelopmentMilestone]:
        """
        Get milestones
        
        Args:
            agent_id: Filter by agent ID (optional)
            completed: Filter by completion status (optional)
        
        Returns:
            List of milestones
        """
        milestones = []
        for milestone in self.milestones.values():
            if agent_id is not None and milestone.agent_id != agent_id:
                continue
            if completed is not None and milestone.completed != completed:
                continue
            milestones.append(milestone)
        
        return sorted(milestones, key=lambda x: x.target_date)
    
    def get_progress_summary(self, agent_id: str) -> Dict[str, Any]:
        """
        Get progress summary for an agent
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Progress summary
        """
        agent_tasks = [t for t in self.tasks.values() if t.agent_id == agent_id]
        agent_milestones = [m for m in self.milestones.values() if m.agent_id == agent_id]
        
        completed_tasks = [t for t in agent_tasks if t.status == TaskStatus.COMPLETED]
        in_progress_tasks = [t for t in agent_tasks if t.status == TaskStatus.IN_PROGRESS]
        pending_tasks = [t for t in agent_tasks if t.status == TaskStatus.PENDING]
        
        completed_milestones = [m for m in agent_milestones if m.completed]
        
        total_estimated = sum(t.estimated_hours for t in agent_tasks)
        total_actual = sum(t.actual_hours for t in agent_tasks)
        
        return {
            "agent_id": agent_id,
            "tasks": {
                "total": len(agent_tasks),
                "completed": len(completed_tasks),
                "in_progress": len(in_progress_tasks),
                "pending": len(pending_tasks),
                "overdue": len(self.get_overdue_tasks(agent_id))
            },
            "milestones": {
                "total": len(agent_milestones),
                "completed": len(completed_milestones),
                "pending": len(agent_milestones) - len(completed_milestones)
            },
            "hours": {
                "estimated": total_estimated,
                "actual": total_actual,
                "efficiency": total_actual / total_estimated if total_estimated > 0 else 0
            },
            "completion_rate": (
                len(completed_tasks) / len(agent_tasks) * 100
                if agent_tasks else 0
            )
        }
    
    def suggest_next_consultation_topics(self, agent_id: str) -> List[str]:
        """
        Suggest topics for the next consultation based on current state
        
        Args:
            agent_id: Agent ID
        
        Returns:
            List of suggested topics
        """
        suggestions = []
        
        # Check for blocked tasks
        blocked_tasks = [
            t for t in self.tasks.values()
            if t.agent_id == agent_id and t.status == TaskStatus.BLOCKED
        ]
        if blocked_tasks:
            suggestions.append(
                f"Resolving blockers: {', '.join(t.title for t in blocked_tasks[:3])}"
            )
        
        # Check for overdue tasks
        overdue = self.get_overdue_tasks(agent_id)
        if overdue:
            suggestions.append(
                f"Addressing overdue tasks: {', '.join(t.title for t in overdue[:3])}"
            )
        
        # Check for upcoming milestones
        upcoming_milestones = [
            m for m in self.milestones.values()
            if m.agent_id == agent_id and not m.completed
            and m.target_date <= datetime.now() + timedelta(days=14)
        ]
        if upcoming_milestones:
            suggestions.append(
                f"Preparing for milestone: {upcoming_milestones[0].title}"
            )
        
        # Check for tasks with many dependencies
        complex_tasks = [
            t for t in self.tasks.values()
            if t.agent_id == agent_id and len(t.dependencies) > 2
            and t.status == TaskStatus.PENDING
        ]
        if complex_tasks:
            suggestions.append(
                f"Breaking down complex tasks: {complex_tasks[0].title}"
            )
        
        # General suggestions based on current stage
        in_progress = len([
            t for t in self.tasks.values()
            if t.agent_id == agent_id and t.status == TaskStatus.IN_PROGRESS
        ])
        
        if in_progress == 0:
            suggestions.append("Getting started: Prioritizing initial tasks")
        elif in_progress > 5:
            suggestions.append("Managing workload: Focusing efforts")
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def save_task(self, task: DevelopmentTask):
        """Save a task to disk"""
        filepath = os.path.join(self.agenda_path, f"task_{task.task_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(task.to_dict(), f, indent=2, ensure_ascii=False)
    
    def save_agenda_item(self, item: AgendaItem):
        """Save an agenda item to disk"""
        filepath = os.path.join(self.agenda_path, f"agenda_{item.item_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(item.to_dict(), f, indent=2, ensure_ascii=False)
    
    def save_milestone(self, milestone: DevelopmentMilestone):
        """Save a milestone to disk"""
        filepath = os.path.join(
            self.agenda_path,
            f"milestone_{milestone.milestone_id}.json"
        )
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(milestone.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_all_data(self):
        """Load all tasks, agenda items, and milestones from disk"""
        if not os.path.exists(self.agenda_path):
            return
        
        for filename in os.listdir(self.agenda_path):
            filepath = os.path.join(self.agenda_path, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if filename.startswith("task_"):
                    task = self._dict_to_task(data)
                    self.tasks[task.task_id] = task
                elif filename.startswith("agenda_"):
                    item = self._dict_to_agenda_item(data)
                    self.agenda_items[item.item_id] = item
                elif filename.startswith("milestone_"):
                    milestone = self._dict_to_milestone(data)
                    self.milestones[milestone.milestone_id] = milestone
                    
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
    
    def _dict_to_task(self, data: Dict[str, Any]) -> DevelopmentTask:
        """Convert dictionary to DevelopmentTask"""
        data['status'] = TaskStatus(data['status'])
        data['priority'] = TaskPriority(data['priority'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['due_date'] = (
            datetime.fromisoformat(data['due_date'])
            if data.get('due_date') else None
        )
        data['completed_at'] = (
            datetime.fromisoformat(data['completed_at'])
            if data.get('completed_at') else None
        )
        return DevelopmentTask(**data)
    
    def _dict_to_agenda_item(self, data: Dict[str, Any]) -> AgendaItem:
        """Convert dictionary to AgendaItem"""
        data['item_type'] = AgendaItemType(data['item_type'])
        data['scheduled_time'] = datetime.fromisoformat(data['scheduled_time'])
        return AgendaItem(**data)
    
    def _dict_to_milestone(self, data: Dict[str, Any]) -> DevelopmentMilestone:
        """Convert dictionary to DevelopmentMilestone"""
        data['target_date'] = datetime.fromisoformat(data['target_date'])
        data['completed_at'] = (
            datetime.fromisoformat(data['completed_at'])
            if data.get('completed_at') else None
        )
        return DevelopmentMilestone(**data)


# Singleton instance
_agenda_instance: Optional[AgentBuilderAgenda] = None


def get_agent_builder_agenda() -> AgentBuilderAgenda:
    """Get or create the singleton AgentBuilderAgenda instance"""
    global _agenda_instance
    if _agenda_instance is None:
        _agenda_instance = AgentBuilderAgenda()
    return _agenda_instance


if __name__ == "__main__":
    # Demo usage
    agenda = get_agent_builder_agenda()
    
    # Create some tasks
    task1 = agenda.create_task(
        agent_id="agent_123",
        title="Implement routing logic",
        description="Add context-aware routing for sales agent",
        priority=TaskPriority.HIGH,
        due_date=datetime.now() + timedelta(days=3),
        estimated_hours=4.0,
        tags=["routing", "implementation"]
    )
    
    task2 = agenda.create_task(
        agent_id="agent_123",
        title="Add error handling",
        description="Implement comprehensive error handling and fallbacks",
        priority=TaskPriority.MEDIUM,
        due_date=datetime.now() + timedelta(days=5),
        estimated_hours=2.0,
        tags=["error-handling", "reliability"]
    )
    
    print(f"\n=== Created Tasks ===")
    print(f"1. {task1.title} (Priority: {task1.priority.value})")
    print(f"2. {task2.title} (Priority: {task2.priority.value})")
    
    # Schedule a consultation
    consultation = agenda.schedule_consultation(
        agent_id="agent_123",
        topic="Advanced workflow integration",
        scheduled_time=datetime.now() + timedelta(days=2, hours=10),
        duration_minutes=90,
        notes="Focus on multi-step workflows and error recovery"
    )
    
    print(f"\n=== Scheduled Consultation ===")
    print(f"Topic: {consultation.description}")
    print(f"Time: {consultation.scheduled_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"Duration: {consultation.duration_minutes} minutes")
    
    # Create a milestone
    milestone = agenda.create_milestone(
        agent_id="agent_123",
        title="MVP Release",
        description="Release minimum viable product for sales agent",
        target_date=datetime.now() + timedelta(days=14),
        criteria=[
            "All core features implemented",
            "Error handling in place",
            "Integration tests passing",
            "Documentation complete"
        ]
    )
    
    print(f"\n=== Created Milestone ===")
    print(f"Title: {milestone.title}")
    print(f"Target: {milestone.target_date.strftime('%Y-%m-%d')}")
    print(f"Criteria: {len(milestone.criteria)} items")
    
    # Get progress summary
    summary = agenda.get_progress_summary("agent_123")
    
    print(f"\n=== Progress Summary ===")
    print(f"Tasks: {summary['tasks']['total']} total")
    print(f"  - Completed: {summary['tasks']['completed']}")
    print(f"  - In Progress: {summary['tasks']['in_progress']}")
    print(f"  - Pending: {summary['tasks']['pending']}")
    print(f"Milestones: {summary['milestones']['total']} total")
    print(f"Completion Rate: {summary['completion_rate']:.1f}%")
    
    # Get suggestions
    suggestions = agenda.suggest_next_consultation_topics("agent_123")
    
    print(f"\n=== Suggested Consultation Topics ===")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")
