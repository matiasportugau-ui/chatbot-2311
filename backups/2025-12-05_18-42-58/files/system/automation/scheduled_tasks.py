#!/usr/bin/env python3
"""
Scheduled Tasks - Tareas programadas del sistema.
Fase -4: Automatización
"""

from system.automation.task_scheduler import TaskScheduler
from system.backup.auto_backup import AutoBackup
from system.context.state_manager import StateManager
from datetime import datetime
from typing import Dict, Any


class ScheduledTasks:
    """Define y gestiona tareas programadas."""
    
    def __init__(self, scheduler: TaskScheduler):
        self.scheduler = scheduler
        self.auto_backup = AutoBackup()
        self.state_manager = StateManager()
    
    def setup_default_tasks(self):
        """Configura tareas por defecto."""
        # Backup cada hora
        self.scheduler.schedule_task(
            "hourly_backup",
            self._hourly_backup,
            3600  # 1 hora
        )
        
        # Checkpoint cada 30 minutos
        self.scheduler.schedule_task(
            "checkpoint",
            self._create_checkpoint,
            1800  # 30 minutos
        )
    
    def _hourly_backup(self):
        """Tarea de backup horario."""
        try:
            state = self.state_manager.state
            self.auto_backup.backup_state(state)
            print("Hourly backup completed")
        except Exception as e:
            print(f"Error in hourly backup: {e}")
    
    def _create_checkpoint(self):
        """Crea un checkpoint periódico."""
        try:
            self.state_manager.create_checkpoint(
                f"periodic_checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
        except Exception as e:
            print(f"Error creating checkpoint: {e}")

