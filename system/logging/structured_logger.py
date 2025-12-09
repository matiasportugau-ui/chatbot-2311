#!/usr/bin/env python3
"""
Structured Logger - Sistema de logging estructurado.
Fase -3: Logging y Auditoría
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class StructuredLogger:
    """Logger con formato estructurado (JSON)."""
    
    def __init__(self, log_file: str = "system/logs/execution.log", log_level: int = logging.INFO):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("structured_logger")
        self.logger.setLevel(log_level)
        
        # File handler with JSON formatter
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(console_handler)
    
    def log(self, level: str, message: str, **kwargs):
        """Log con datos estructurados."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
            **kwargs
        }
        
        if level.upper() == "DEBUG":
            self.logger.debug(json.dumps(log_data))
        elif level.upper() == "INFO":
            self.logger.info(json.dumps(log_data))
        elif level.upper() == "WARNING":
            self.logger.warning(json.dumps(log_data))
        elif level.upper() == "ERROR":
            self.logger.error(json.dumps(log_data))
        elif level.upper() == "CRITICAL":
            self.logger.critical(json.dumps(log_data))


class JSONFormatter(logging.Formatter):
    """Formatter que convierte logs a JSON."""
    
    def format(self, record):
        # If already JSON, return as is
        if isinstance(record.msg, str) and record.msg.startswith('{'):
            return record.msg
        # Otherwise create JSON structure
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        return json.dumps(log_data)

