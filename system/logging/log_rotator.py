#!/usr/bin/env python3
"""
Log Rotator - Rotación de logs.
Fase -3: Logging y Auditoría
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional


class LogRotator:
    """Rota logs para evitar que crezcan demasiado."""
    
    def __init__(self, log_file: str, max_size_mb: int = 10, backup_count: int = 5):
        self.log_file = Path(log_file)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.backup_count = backup_count
    
    def should_rotate(self) -> bool:
        """Verifica si se debe rotar el log."""
        if not self.log_file.exists():
            return False
        return self.log_file.stat().st_size >= self.max_size_bytes
    
    def rotate(self) -> Optional[str]:
        """Rota el log."""
        if not self.should_rotate():
            return None
        
        # Rotate existing backups
        for i in range(self.backup_count - 1, 0, -1):
            old_backup = Path(f"{self.log_file}.{i}")
            new_backup = Path(f"{self.log_file}.{i + 1}")
            if old_backup.exists():
                if i + 1 <= self.backup_count:
                    shutil.move(str(old_backup), str(new_backup))
        
        # Move current log to .1
        backup_file = Path(f"{self.log_file}.1")
        if self.log_file.exists():
            shutil.move(str(self.log_file), str(backup_file))
            return str(backup_file)
        
        return None

