#!/usr/bin/env python3
"""
Test Framework - Framework base de testing.
Fase -1: Validación y Testing Base
"""

import unittest
from typing import Dict, Any, List, Callable
from pathlib import Path


class TestFramework:
    """Framework básico de testing."""
    
    def __init__(self):
        self.tests = []
        self.results = []
    
    def add_test(self, test_name: str, test_func: Callable):
        """Agrega un test al framework."""
        self.tests.append({
            "name": test_name,
            "func": test_func
        })
    
    def run_tests(self) -> Dict[str, Any]:
        """Ejecuta todos los tests."""
        results = {
            "total": len(self.tests),
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        for test in self.tests:
            try:
                test["func"]()
                results["passed"] += 1
                results["details"].append({
                    "name": test["name"],
                    "status": "passed"
                })
            except AssertionError as e:
                results["failed"] += 1
                results["details"].append({
                    "name": test["name"],
                    "status": "failed",
                    "error": str(e)
                })
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "name": test["name"],
                    "status": "error",
                    "error": str(e)
                })
        
        return results

