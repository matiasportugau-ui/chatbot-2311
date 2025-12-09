"""
JSON Validation Utilities
Validates JSON structure and content
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple


class JSONValidator:
    """Validates JSON files and structures"""
    
    @staticmethod
    def load_json(file_path: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Load JSON file
        Returns: (data, error_message)
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data, None
        except json.JSONDecodeError as e:
            return None, f"JSON decode error: {str(e)}"
        except IOError as e:
            return None, f"IO error: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def has_key(data: Dict[str, Any], key: str) -> bool:
        """Check if JSON has a specific key"""
        return key in data
    
    @staticmethod
    @staticmethod
    def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """
        Get nested value from JSON using dot notation
        Example: get_nested_value(data, "phases.0.status")
        """
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    @staticmethod
    def validate_structure(data: Dict[str, Any], required_keys: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate that JSON has required keys
        Returns: (is_valid, error_message)
        """
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            return False, f"Missing required keys: {', '.join(missing_keys)}"
        
        return True, None
    
    @staticmethod
    def validate_value_type(data: Dict[str, Any], key: str, expected_type: type) -> Tuple[bool, Optional[str]]:
        """
        Validate that a key has the expected type
        Returns: (is_valid, error_message)
        """
        if key not in data:
            return False, f"Key {key} not found"
        
        if not isinstance(data[key], expected_type):
            return False, f"Key {key} has wrong type. Expected {expected_type}, got {type(data[key])}"
        
        return True, None
    
    @staticmethod
    def validate_array_length(data: Dict[str, Any], key: str, min_length: int = 0, max_length: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate array length
        Returns: (is_valid, error_message)
        """
        if key not in data:
            return False, f"Key {key} not found"
        
        if not isinstance(data[key], list):
            return False, f"Key {key} is not an array"
        
        arr_length = len(data[key])
        
        if arr_length < min_length:
            return False, f"Array {key} has {arr_length} items, expected at least {min_length}"
        
        if max_length is not None and arr_length > max_length:
            return False, f"Array {key} has {arr_length} items, expected at most {max_length}"
        
        return True, None

