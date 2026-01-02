#!/usr/bin/env python3
"""
Schema Validator - Validador de schemas JSON.
Fase -1: Validación y Testing Base
"""

from system.validation.config_validator import ConfigValidator
from typing import Dict, Any


class SchemaValidator:
    """Valida datos contra schemas JSON."""
    
    def __init__(self):
        pass
    
    def validate(self, data: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Valida datos contra un schema."""
        validation = {
            "valid": True,
            "errors": []
        }
        
        # Basic validation - can be enhanced with jsonschema library
        if schema.get("type") == "object" and not isinstance(data, dict):
            validation["valid"] = False
            validation["errors"].append("Data is not an object")
        
        required = schema.get("required", [])
        if isinstance(data, dict):
            for field in required:
                if field not in data:
                    validation["valid"] = False
                    validation["errors"].append(f"Missing required field: {field}")
        
        return validation

