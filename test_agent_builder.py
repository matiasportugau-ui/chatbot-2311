#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Agent Builder System
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_builder import (
    AgentBuilder,
    AgentType,
    ConsultationLevel,
    AgentBlueprint,
    Consultation
)
from agent_builder_agenda import (
    AgentBuilderAgenda,
    TaskStatus,
    TaskPriority,
    AgendaItemType
)


class TestAgentBuilder:
    """Tests for AgentBuilder"""
    
    def __init__(self):
        self.temp_dir = None
        self.builder = None
    
    def setup(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.builder = AgentBuilder(storage_path=self.temp_dir)
    
    def teardown(self):
        """Clean up test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_blueprint(self):
        """Test creating an agent blueprint"""
        print("\n--- Test: Create Blueprint ---")
        
        blueprint = self.builder.create_agent_blueprint(
            agent_name="TestAgent",
            agent_type=AgentType.SALES,
            initial_capabilities=["test_capability"]
        )
        
        assert blueprint.agent_name == "TestAgent"
        assert blueprint.agent_type == AgentType.SALES
        assert len(blueprint.capabilities) == 1
        assert blueprint.capabilities[0] == "test_capability"
        assert blueprint.development_stage == "planning"
        assert blueprint.completion_percentage == 0.0
        
        print("✅ Blueprint created successfully")
        print(f"   ID: {blueprint.agent_id}")
        print(f"   Name: {blueprint.agent_name}")
        return blueprint
    
    def test_consult_progression(self):
        """Test consultation level progression"""
        print("\n--- Test: Consultation Progression ---")
        
        blueprint = self.builder.create_agent_blueprint(
            agent_name="ProgressionTest",
            agent_type=AgentType.SUPPORT
        )
        
        # First consultation should be BASIC
        c1 = self.builder.consult(blueprint.agent_id, "Test topic 1")
        assert c1.level == ConsultationLevel.BASIC
        print(f"✅ Consultation 1: {c1.level.value}")
        
        # Consultations 2-4 should be INTERMEDIATE
        c2 = self.builder.consult(blueprint.agent_id, "Test topic 2")
        assert c2.level == ConsultationLevel.INTERMEDIATE
        print(f"✅ Consultation 2: {c2.level.value}")
        
        c3 = self.builder.consult(blueprint.agent_id, "Test topic 3")
        assert c3.level == ConsultationLevel.INTERMEDIATE
        print(f"✅ Consultation 3: {c3.level.value}")
        
        c4 = self.builder.consult(blueprint.agent_id, "Test topic 4")
        assert c4.level == ConsultationLevel.INTERMEDIATE
        print(f"✅ Consultation 4: {c4.level.value}")
        
        # Consultations 5-8 should be ADVANCED
        c5 = self.builder.consult(blueprint.agent_id, "Test topic 5")
        assert c5.level == ConsultationLevel.ADVANCED
        print(f"✅ Consultation 5: {c5.level.value}")
        
        # Refresh blueprint to check stage
        blueprint = self.builder.get_blueprint(blueprint.agent_id)
        assert blueprint.development_stage == "testing"
        print(f"✅ Development stage: {blueprint.development_stage}")
        
        return blueprint
    
    def test_consultation_content(self):
        """Test consultation content generation"""
        print("\n--- Test: Consultation Content ---")
        
        blueprint = self.builder.create_agent_blueprint(
            agent_name="ContentTest",
            agent_type=AgentType.CUSTOM
        )
        
        consultation = self.builder.consult(
            blueprint.agent_id,
            "How do I implement workflows?"
        )
        
        assert len(consultation.recommendations) > 0
        assert len(consultation.insights) > 0
        assert len(consultation.code_examples) > 0
        assert len(consultation.next_steps) > 0
        
        print(f"✅ Recommendations: {len(consultation.recommendations)}")
        print(f"✅ Insights: {len(consultation.insights)}")
        print(f"✅ Code Examples: {len(consultation.code_examples)}")
        print(f"✅ Next Steps: {len(consultation.next_steps)}")
        
        return consultation
    
    def test_persistence(self):
        """Test blueprint persistence"""
        print("\n--- Test: Persistence ---")
        
        # Create blueprint
        blueprint = self.builder.create_agent_blueprint(
            agent_name="PersistenceTest",
            agent_type=AgentType.ANALYTICS
        )
        
        agent_id = blueprint.agent_id
        
        # Create new builder instance (simulates restart)
        builder2 = AgentBuilder(storage_path=self.temp_dir)
        
        # Check if blueprint was loaded
        loaded_blueprint = builder2.get_blueprint(agent_id)
        assert loaded_blueprint is not None
        assert loaded_blueprint.agent_name == "PersistenceTest"
        assert loaded_blueprint.agent_type == AgentType.ANALYTICS
        
        print("✅ Blueprint persisted and loaded successfully")
        return loaded_blueprint
    
    def test_report_generation(self):
        """Test report generation"""
        print("\n--- Test: Report Generation ---")
        
        blueprint = self.builder.create_agent_blueprint(
            agent_name="ReportTest",
            agent_type=AgentType.QUOTES
        )
        
        # Add some consultations
        for i in range(3):
            self.builder.consult(blueprint.agent_id, f"Test topic {i+1}")
        
        # Generate report
        report = self.builder.generate_report(blueprint.agent_id)
        
        assert report['agent_name'] == "ReportTest"
        assert report['agent_type'] == "quotes"
        assert report['total_consultations'] == 3
        assert len(report['consultation_history']) == 3
        
        print(f"✅ Report generated successfully")
        print(f"   Consultations: {report['total_consultations']}")
        print(f"   Stage: {report['development_stage']}")
        
        return report
    
    def run_all(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("RUNNING AGENT BUILDER TESTS")
        print("=" * 60)
        
        try:
            self.setup()
            
            self.test_create_blueprint()
            self.test_consult_progression()
            self.test_consultation_content()
            self.test_persistence()
            self.test_report_generation()
            
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED")
            print("=" * 60 + "\n")
            return True
            
        except AssertionError as e:
            print("\n" + "=" * 60)
            print(f"❌ TEST FAILED: {e}")
            print("=" * 60 + "\n")
            return False
        except Exception as e:
            print("\n" + "=" * 60)
            print(f"❌ ERROR: {e}")
            print("=" * 60 + "\n")
            return False
        finally:
            self.teardown()


class TestAgentBuilderAgenda:
    """Tests for AgentBuilderAgenda"""
    
    def __init__(self):
        self.temp_dir = None
        self.agenda = None
    
    def setup(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.agenda = AgentBuilderAgenda(storage_path=self.temp_dir)
    
    def teardown(self):
        """Clean up test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_task(self):
        """Test creating a task"""
        print("\n--- Test: Create Task ---")
        
        task = self.agenda.create_task(
            agent_id="test_agent",
            title="Test Task",
            description="Test description",
            priority=TaskPriority.HIGH,
            estimated_hours=2.0
        )
        
        assert task.title == "Test Task"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.PENDING
        assert task.estimated_hours == 2.0
        
        print("✅ Task created successfully")
        print(f"   ID: {task.task_id}")
        print(f"   Title: {task.title}")
        return task
    
    def test_schedule_consultation(self):
        """Test scheduling a consultation"""
        print("\n--- Test: Schedule Consultation ---")
        
        scheduled_time = datetime.now() + timedelta(days=1)
        
        item = self.agenda.schedule_consultation(
            agent_id="test_agent",
            topic="Test Consultation",
            scheduled_time=scheduled_time,
            duration_minutes=90
        )
        
        assert item.item_type == AgendaItemType.CONSULTATION
        assert "Test Consultation" in item.title
        assert item.duration_minutes == 90
        assert not item.completed
        
        print("✅ Consultation scheduled successfully")
        print(f"   Time: {item.scheduled_time.strftime('%Y-%m-%d %H:%M')}")
        return item
    
    def test_create_milestone(self):
        """Test creating a milestone"""
        print("\n--- Test: Create Milestone ---")
        
        target_date = datetime.now() + timedelta(days=14)
        
        milestone = self.agenda.create_milestone(
            agent_id="test_agent",
            title="Test Milestone",
            description="Test milestone description",
            target_date=target_date,
            criteria=["Criterion 1", "Criterion 2"]
        )
        
        assert milestone.title == "Test Milestone"
        assert len(milestone.criteria) == 2
        assert not milestone.completed
        
        print("✅ Milestone created successfully")
        print(f"   Title: {milestone.title}")
        print(f"   Criteria: {len(milestone.criteria)}")
        return milestone
    
    def test_task_status_update(self):
        """Test updating task status"""
        print("\n--- Test: Update Task Status ---")
        
        task = self.agenda.create_task(
            agent_id="test_agent",
            title="Status Test Task",
            priority=TaskPriority.MEDIUM
        )
        
        # Update to in progress
        self.agenda.update_task_status(
            task.task_id,
            TaskStatus.IN_PROGRESS,
            actual_hours=1.5
        )
        
        updated_task = self.agenda.tasks[task.task_id]
        assert updated_task.status == TaskStatus.IN_PROGRESS
        assert updated_task.actual_hours == 1.5
        
        # Complete the task
        self.agenda.update_task_status(
            task.task_id,
            TaskStatus.COMPLETED
        )
        
        updated_task = self.agenda.tasks[task.task_id]
        assert updated_task.status == TaskStatus.COMPLETED
        assert updated_task.completed_at is not None
        
        print("✅ Task status updated successfully")
        return updated_task
    
    def test_progress_summary(self):
        """Test progress summary"""
        print("\n--- Test: Progress Summary ---")
        
        agent_id = "test_agent_summary"
        
        # Create tasks
        self.agenda.create_task(
            agent_id=agent_id,
            title="Task 1",
            priority=TaskPriority.HIGH
        )
        
        task2 = self.agenda.create_task(
            agent_id=agent_id,
            title="Task 2",
            priority=TaskPriority.MEDIUM,
            estimated_hours=3.0
        )
        
        # Complete one task
        self.agenda.update_task_status(
            task2.task_id,
            TaskStatus.COMPLETED,
            actual_hours=2.5
        )
        
        # Create milestone
        self.agenda.create_milestone(
            agent_id=agent_id,
            title="Test Milestone",
            description="Test",
            target_date=datetime.now() + timedelta(days=7)
        )
        
        # Get summary
        summary = self.agenda.get_progress_summary(agent_id)
        
        assert summary['tasks']['total'] == 2
        assert summary['tasks']['completed'] == 1
        assert summary['tasks']['pending'] == 1
        assert summary['milestones']['total'] == 1
        assert summary['completion_rate'] == 50.0
        
        print("✅ Progress summary generated successfully")
        print(f"   Total tasks: {summary['tasks']['total']}")
        print(f"   Completed: {summary['tasks']['completed']}")
        print(f"   Completion rate: {summary['completion_rate']:.1f}%")
        return summary
    
    def test_suggestions(self):
        """Test intelligent suggestions"""
        print("\n--- Test: Intelligent Suggestions ---")
        
        agent_id = "test_agent_suggestions"
        
        # Create overdue task
        overdue_task = self.agenda.create_task(
            agent_id=agent_id,
            title="Overdue Task",
            priority=TaskPriority.HIGH,
            due_date=datetime.now() - timedelta(days=1)
        )
        
        # Get suggestions
        suggestions = self.agenda.suggest_next_consultation_topics(agent_id)
        
        assert len(suggestions) > 0
        # Should suggest addressing overdue tasks
        assert any("overdue" in s.lower() for s in suggestions)
        
        print("✅ Suggestions generated successfully")
        print(f"   Suggestions: {len(suggestions)}")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
        
        return suggestions
    
    def run_all(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("RUNNING AGENT BUILDER AGENDA TESTS")
        print("=" * 60)
        
        try:
            self.setup()
            
            self.test_create_task()
            self.test_schedule_consultation()
            self.test_create_milestone()
            self.test_task_status_update()
            self.test_progress_summary()
            self.test_suggestions()
            
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED")
            print("=" * 60 + "\n")
            return True
            
        except AssertionError as e:
            print("\n" + "=" * 60)
            print(f"❌ TEST FAILED: {e}")
            print("=" * 60 + "\n")
            return False
        except Exception as e:
            print("\n" + "=" * 60)
            print(f"❌ ERROR: {e}")
            print("=" * 60 + "\n")
            return False
        finally:
            self.teardown()


def main():
    """Run all test suites"""
    print("\n" + "=" * 70)
    print("  AGENT BUILDER TEST SUITE")
    print("=" * 70)
    
    builder_tests = TestAgentBuilder()
    builder_passed = builder_tests.run_all()
    
    agenda_tests = TestAgentBuilderAgenda()
    agenda_passed = agenda_tests.run_all()
    
    print("\n" + "=" * 70)
    print("  FINAL RESULTS")
    print("=" * 70)
    print(f"Agent Builder Tests: {'✅ PASSED' if builder_passed else '❌ FAILED'}")
    print(f"Agenda Tests: {'✅ PASSED' if agenda_passed else '❌ FAILED'}")
    print("=" * 70 + "\n")
    
    return builder_passed and agenda_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
