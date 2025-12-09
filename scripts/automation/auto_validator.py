#!/usr/bin/env python3
"""
Auto Validator - Validador automático.
Fase -4: Automatización
"""

import json
from pathlib import Path
from typing import Dict, Any, List


class AutoValidator:
    """Valida automáticamente outputs de fases."""
    
    def __init__(self, validation_rules_file: str = "system/validation/validation_rules.json"):
        self.rules_file = Path(validation_rules_file)
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        """Carga reglas de validación."""
        if self.rules_file.exists():
            try:
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def validate_phase_output(self, phase: int, output_file: str) -> Dict[str, Any]:
        """Valida el output de una fase."""
        validation = {
            "phase": phase,
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        output_path = Path(output_file)
        if not output_path.exists():
            validation["valid"] = False
            validation["errors"].append(f"Output file not found: {output_file}")
            return validation
        
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                output_data = json.load(f)
            
            # Basic validation
            if not isinstance(output_data, dict):
                validation["valid"] = False
                validation["errors"].append("Output is not a valid JSON object")
            
            # Check for required fields
            required_fields = self.rules.get(str(phase), {}).get("required_fields", [])
            for field in required_fields:
                if field not in output_data:
                    validation["warnings"].append(f"Missing recommended field: {field}")
            
        except json.JSONDecodeError as e:
            validation["valid"] = False
            validation["errors"].append(f"Invalid JSON: {e}")
        except Exception as e:
            validation["valid"] = False
            validation["errors"].append(f"Error validating: {e}")
        
        return validation

