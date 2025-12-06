"""
File Validation Utilities
Validates file existence, JSON validity, and other file checks
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class FileValidator:
    """Validates files for success criteria"""
    
    @staticmethod
    def file_exists(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Check if file exists
        Returns: (exists, error_message)
        """
        path = Path(file_path)
        if path.exists() and path.is_file():
            return True, None
        return False, f"File does not exist: {file_path}"
    
    @staticmethod
    def json_valid(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Check if file is valid JSON
        Returns: (is_valid, error_message)
        """
        exists, error = FileValidator.file_exists(file_path)
        if not exists:
            return False, error
        
        try:
            with open(file_path, 'r') as f:
                json.load(f)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON in {file_path}: {str(e)}"
        except IOError as e:
            return False, f"Error reading {file_path}: {str(e)}"
    
    @staticmethod
    def json_schema_valid(file_path: str, schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Check if JSON file matches schema
        Returns: (is_valid, error_message)
        """
        is_valid, error = FileValidator.json_valid(file_path)
        if not is_valid:
            return False, error
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Simple schema validation (can be enhanced with jsonschema library)
            for key, expected_type in schema.items():
                if key not in data:
                    return False, f"Missing required key: {key}"
                
                if not isinstance(data[key], expected_type):
                    return False, f"Key {key} has wrong type. Expected {expected_type}, got {type(data[key])}"
            
            return True, None
        except Exception as e:
            return False, f"Schema validation error: {str(e)}"
    
    @staticmethod
    def file_not_empty(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Check if file is not empty
        Returns: (not_empty, error_message)
        """
        exists, error = FileValidator.file_exists(file_path)
        if not exists:
            return False, error
        
        path = Path(file_path)
        if path.stat().st_size == 0:
            return False, f"File is empty: {file_path}"
        
        return True, None
    
    @staticmethod
    def directory_exists(dir_path: str) -> Tuple[bool, Optional[str]]:
        """
        Check if directory exists
        Returns: (exists, error_message)
        """
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            return True, None
        return False, f"Directory does not exist: {dir_path}"
    
    @staticmethod
    def files_in_directory(dir_path: str, min_files: int = 1) -> Tuple[bool, Optional[str]]:
        """
        Check if directory has minimum number of files
        Returns: (has_min_files, error_message)
        """
        exists, error = FileValidator.directory_exists(dir_path)
        if not exists:
            return False, error
        
        path = Path(dir_path)
        file_count = len(list(path.iterdir()))
        
        if file_count < min_files:
            return False, f"Directory {dir_path} has {file_count} files, expected at least {min_files}"
        
        return True, None

