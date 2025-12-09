#!/usr/bin/env python3
"""
Config Validator - Validador de configuración.
Fase -1: Validación y Testing Base
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class ConfigValidator:
    """Valida archivos de configuración."""
    
    def __init__(self, schema_file: Optional[str] = None):
        self.schema_file = Path(schema_file) if schema_file else None
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """Carga el schema de validación."""
        if self.schema_file and self.schema_file.exists():
            try:
                with open(self.schema_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None
        return None
    
    def validate_config_file(self, config_file: str) -> Dict[str, Any]:
        """Valida un archivo de configuración."""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        config_path = Path(config_file)
        if not config_path.exists():
            validation["valid"] = False
            validation["errors"].append(f"Config file not found: {config_file}")
            return validation
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Basic structure validation
            if not isinstance(config_data, dict):
                validation["valid"] = False
                validation["errors"].append("Config must be a JSON object")
                return validation
            
            # Schema validation if schema available
            if self.schema:
                schema_errors = self._validate_against_schema(config_data, self.schema)
                validation["errors"].extend(schema_errors)
                if schema_errors:
                    validation["valid"] = False
            
        except json.JSONDecodeError as e:
            validation["valid"] = False
            validation["errors"].append(f"Invalid JSON: {e}")
        except Exception as e:
            validation["valid"] = False
            validation["errors"].append(f"Error validating config: {e}")
        
        return validation
    
    def _validate_against_schema(self, data: Dict, schema: Dict) -> List[str]:
        """Valida datos contra un schema."""
        errors = []
        # Basic schema validation - can be enhanced
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        return errors

