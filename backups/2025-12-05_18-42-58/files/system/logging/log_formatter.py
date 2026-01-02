#!/usr/bin/env python3
"""
Log Formatter - Formateador de logs.
Fase -3: Logging y Auditoría
"""

import json
from datetime import datetime
from typing import Dict, Any


class LogFormatter:
    """Formatea logs en diferentes formatos."""
    
    @staticmethod
    def format_json(level: str, message: str, **kwargs) -> str:
        """Formatea log como JSON."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
            **kwargs
        }
        return json.dumps(log_entry, ensure_ascii=False)
    
    @staticmethod
    def format_text(level: str, message: str, **kwargs) -> str:
        """Formatea log como texto."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        extra = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        if extra:
            return f"[{timestamp}] {level.upper()} | {message} | {extra}"
        return f"[{timestamp}] {level.upper()} | {message}"

