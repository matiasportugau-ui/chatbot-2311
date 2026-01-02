"""
Metric Validation Utilities
Validates metrics against thresholds
"""

from typing import Dict, Any, Optional, Union, Tuple
from .json_validator import JSONValidator


class MetricValidator:
    """Validates metrics in JSON files"""
    
    @staticmethod
    def validate_metric_threshold(file_path: str, metric_path: str, 
                                   min_value: Optional[Union[int, float]] = None,
                                   max_value: Optional[Union[int, float]] = None,
                                   exact_value: Optional[Union[int, float]] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate a metric against thresholds
        Returns: (is_valid, error_message)
        """
        data, error = JSONValidator.load_json(file_path)
        if error:
            return False, error
        
        metric_value = JSONValidator.get_nested_value(data, metric_path)
        
        if metric_value is None:
            return False, f"Metric not found at path: {metric_path}"
        
        if not isinstance(metric_value, (int, float)):
            return False, f"Metric at {metric_path} is not a number: {type(metric_value)}"
        
        if exact_value is not None:
            if metric_value != exact_value:
                return False, f"Metric {metric_path} is {metric_value}, expected {exact_value}"
            return True, None
        
        if min_value is not None and metric_value < min_value:
            return False, f"Metric {metric_path} is {metric_value}, expected at least {min_value}"
        
        if max_value is not None and metric_value > max_value:
            return False, f"Metric {metric_path} is {metric_value}, expected at most {max_value}"
        
        return True, None
    
    @staticmethod
    def validate_metric_exists(file_path: str, metric_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a metric exists
        Returns: (exists, error_message)
        """
        data, error = JSONValidator.load_json(file_path)
        if error:
            return False, error
        
        metric_value = JSONValidator.get_nested_value(data, metric_path)
        
        if metric_value is None:
            return False, f"Metric not found at path: {metric_path}"
        
        return True, None
    
    @staticmethod
    def get_metric_value(file_path: str, metric_path: str) -> Tuple[Optional[Union[int, float]], Optional[str]]:
        """
        Get metric value from JSON file
        Returns: (value, error_message)
        """
        data, error = JSONValidator.load_json(file_path)
        if error:
            return None, error
        
        metric_value = JSONValidator.get_nested_value(data, metric_path)
        
        if metric_value is None:
            return None, f"Metric not found at path: {metric_path}"
        
        return metric_value, None

