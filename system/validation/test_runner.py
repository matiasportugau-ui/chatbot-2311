#!/usr/bin/env python3
"""
Test Runner - Ejecutor de tests.
Fase -1: Validación y Testing Base
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
from system.validation.test_framework import TestFramework


class TestRunner:
    """Ejecuta tests y genera reportes."""
    
    def __init__(self, test_framework: TestFramework):
        self.framework = test_framework
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Ejecuta todos los tests."""
        return self.framework.run_tests()
    
    def run_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """Ejecuta una suite específica de tests."""
        # Filter tests by suite
        suite_tests = [t for t in self.framework.tests if suite_name in t.get("suite", "")]
        original_tests = self.framework.tests
        self.framework.tests = suite_tests
        
        results = self.framework.run_tests()
        self.framework.tests = original_tests
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Genera un reporte de tests."""
        report = f"""
Test Execution Report
====================
Total Tests: {results['total']}
Passed: {results['passed']}
Failed: {results['failed']}
Success Rate: {(results['passed'] / results['total'] * 100) if results['total'] > 0 else 0:.1f}%

Details:
"""
        for detail in results['details']:
            status_icon = "✅" if detail['status'] == "passed" else "❌"
            report += f"{status_icon} {detail['name']}: {detail['status']}\n"
            if 'error' in detail:
                report += f"   Error: {detail['error']}\n"
        
        return report

