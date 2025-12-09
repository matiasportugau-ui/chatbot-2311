#!/usr/bin/env python3
"""
Backup Scheduler - Programador de backups automáticos.
Fase -5: Backup y Recuperación
"""

import time
from datetime import datetime
from typing import Callable, Optional
from auto_backup import AutoBackup


class BackupScheduler:
    """Programa backups automáticos."""
    
    def __init__(self, auto_backup: AutoBackup):
        self.auto_backup = auto_backup
        self.running = False
    
    def schedule_periodic_backup(self, interval_seconds: int, backup_func: Callable):
        """Programa backups periódicos."""
        self.running = True
        while self.running:
            try:
                backup_func()
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"Error in scheduled backup: {e}")
                time.sleep(interval_seconds)

