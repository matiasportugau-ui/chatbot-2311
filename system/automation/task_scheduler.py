#!/usr/bin/env python3
"""
Task Scheduler - Programador de tareas.
Fase -4: Automatización
"""

import time
from datetime import datetime
from typing import Callable, Dict, Any, Optional
from threading import Thread


class TaskScheduler:
    """Programa tareas para ejecución automática."""
    
    def __init__(self):
        self.tasks = []
        self.running = False
        self.thread = None
    
    def schedule_task(self, task_name: str, task_func: Callable, interval_seconds: int):
        """Programa una tarea periódica."""
        self.tasks.append({
            "name": task_name,
            "func": task_func,
            "interval": interval_seconds,
            "last_run": None
        })
    
    def start(self):
        """Inicia el scheduler."""
        self.running = True
        self.thread = Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Detiene el scheduler."""
        self.running = False
    
    def _run_scheduler(self):
        """Ejecuta el scheduler en un thread separado."""
        while self.running:
            for task in self.tasks:
                try:
                    # Check if it's time to run
                    if task["last_run"] is None or \
                       (datetime.now() - task["last_run"]).total_seconds() >= task["interval"]:
                        task["func"]()
                        task["last_run"] = datetime.now()
                except Exception as e:
                    print(f"Error executing task {task['name']}: {e}")
            
            time.sleep(1)  # Check every second

