#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script for GitLab Duo-inspired features.
This script demonstrates the functionality of the new agents using mocked AI responses
to ensure a smooth demo experience even without API keys.
"""

import sys
import os
import json
import time
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.insert(0, os.getcwd())

from agents.root_cause_agent import RootCauseAgent
from agents.code_explain_agent import CodeExplainAgent
from agents.security_scan_agent import SecurityScanAgent

# Mock Model Integrator responses
MOCK_RESPONSES = {
    "root_cause": json.dumps({
        "summary": "ConnectionRefusedError in login flow",
        "root_cause": "The API server is trying to connect to a database on localhost:27017, but the connection is refused. likely the MongoDB service is not running.",
        "file_location": "api_server.py:145",
        "suggested_fix": "Start the MongoDB service using `brew services start mongodb-community` or check docker containers.",
        "confidence": "High"
    }),
    "code_explain": """# Code Explanation

## Overview
The provided code snippet demonstrates a simple Python function that calculates the factorial of a number using recursion.

## Key Components
*   **`factorial(n)`**: The main function taking an integer `n`.
*   **Base Case**: Returns 1 if `n` is 0 or 1.
*   **Recursive Step**: Returns `n * factorial(n-1)` otherwise.

## Logic Flow
1.  Check if `n` is small (0 or 1).
2.  If yes, return 1.
3.  If no, multiply `n` by the result of `factorial(n-1)`.
""",
    "security_scan": json.dumps({
        "vulnerabilities": [
            {"package": "flask", "issue": "Version < 2.0 has known CVE-2023-XXXX", "severity": "High"},
            {"package": "requests", "issue": "Old version doesn't support latest SSL", "severity": "Low"}
        ]
    })
}

class MockModelIntegrator:
    def generate(self, prompt, **kwargs):
        # Return canned responses based on the prompt content
        if "Analyze the following error log" in prompt:
            return {'content': MOCK_RESPONSES["root_cause"]}
        elif "Explain the following code" in prompt:
            return {'content': MOCK_RESPONSES["code_explain"]}
        elif "Review the following" in prompt and "security" in prompt.lower():
            return {'content': MOCK_RESPONSES["security_scan"]}
        return {'content': "Mock response"}

def run_demo():
    print("🚀 Starting GitLab Duo Features Demo\n")
    print("This demo uses MOCKED AI responses to show functionality without API keys.\n")
    
    # 1. Demo Root Cause Analysis
    print("=" * 60)
    print("🔍 DEMO 1: Root Cause Analysis Agent")
    print("=" * 60)
    print("Input Log Snippet:")
    log_content = "2023-10-27 10:00:01 ERROR ConnectionRefusedError: [Errno 61] Connection refused at api_server.py:145"
    print(f"  {log_content}")
    print("\nRunning Agent...")
    
    with patch('agents.root_cause_agent.get_model_integrator', return_value=MockModelIntegrator()):
        # We also need to patch the init if it tries to call get_model_integrator immediately
        # But our agents import it inside init inside a try/except blocks or check availability
        # Let's manually inject the mock into the instance
        agent = RootCauseAgent()
        agent.model_integrator = MockModelIntegrator()
        
        result = agent.analyze_error_text(log_content)
        print("\nAgent Output:")
        print(json.dumps(result, indent=2))
        
    time.sleep(2)
        
    # 2. Demo Code Explanation
    print("\n" + "=" * 60)
    print("📝 DEMO 2: Code Explanation Agent")
    print("=" * 60)
    print("Input Code Snippet:")
    code_content = "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
    print(f"  {code_content}")
    print("\nRunning Agent...")
    
    with patch('agents.code_explain_agent.get_model_integrator', return_value=MockModelIntegrator()):
        agent = CodeExplainAgent()
        agent.model_integrator = MockModelIntegrator()
        
        result = agent.explain_code(code_content, filename="math_utils.py")
        print("\nAgent Output:")
        print(result["explanation"])

    time.sleep(2)

    # 3. Demo Security Scan
    print("\n" + "=" * 60)
    print("🛡️ DEMO 3: Security Scan Agent")
    print("=" * 60)
    print("Input: requirements.txt (simulated)")
    print("  flask==0.12\n  requests==1.0.0")
    print("\nRunning Agent...")
    
    with patch('agents.security_scan_agent.get_model_integrator', return_value=MockModelIntegrator()):
        agent = SecurityScanAgent()
        agent.model_integrator = MockModelIntegrator()
        # Mocking file reading for security scan
        agent._analyze_requirements = lambda x: agent._ask_llm_security(x, "requirements.txt")
        
        # We'll just call the internal method for the demo to skip file reading
        result = agent._ask_llm_security("flask==0.12\nrequests==1.0.0", "requirements.txt")
        print("\nAgent Output (Vulnerabilities Found):")
        print(json.dumps(result, indent=2))

    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)

if __name__ == "__main__":
    run_demo()
