#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent specialized in Root Cause Analysis (inspired by GitLab Duo).
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False

class RootCauseAgent:
    """
    Agent to analyze error logs and stack traces to identify root causes.
    """
    
    def __init__(self):
        self.model_integrator = None
        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.model_integrator = get_model_integrator()
                print("✅ Model Integrator initialized for RootCauseAgent")
            except Exception as e:
                print(f"⚠️  Model Integrator not available: {e}")
    
    def analyze_log_file(self, log_path: str) -> Dict[str, Any]:
        """
        Reads a log file, extracts errors, and asks LLM for root cause.
        """
        path = Path(log_path)
        if not path.exists():
            return {"error": f"Log file not found: {log_path}"}
            
        try:
            content = path.read_text(encoding='utf-8')
            # Take the last 5000 chars to focus on recent errors if file is large
            if len(content) > 5000:
                content = content[-5000:]
                
            return self.analyze_error_text(content)
        except Exception as e:
            return {"error": f"Failed to read log file: {str(e)}"}

    def analyze_error_text(self, error_text: str) -> Dict[str, Any]:
        """
        Analyzes raw error text using LLM.
        """
        if not self.model_integrator:
            return {"error": "Model Integrator not available"}

        system_prompt = """You are an expert software engineer specialized in debugging and Root Cause Analysis.
Analyze the provided error logs or stack traces.
Identify the specific error, its location, and the underlying root cause.
Propose a concrete fix.

Return a JSON object with:
{
  "summary": "Brief summary of the error",
  "root_cause": "Detailed explanation of why this happened",
  "file_location": "File and line number if actionable",
  "suggested_fix": "Code snippet or action to fix it",
  "confidence": "High/Medium/Low"
}"""

        prompt = f"""Analyze the following error log:\n\n{error_text}"""
        
        try:
            response = self.model_integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.0,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            if response and 'content' in response:
                try:
                    return json.loads(response['content'])
                except json.JSONDecodeError:
                    return {"raw_response": response['content'], "error": "Failed to parse JSON"}
            return {"error": "Empty response from model"}
            
        except Exception as e:
            return {"error": f"LLM analysis failed: {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 root_cause_agent.py <log_file>")
        sys.exit(1)
    
    agent = RootCauseAgent()
    result = agent.analyze_log_file(sys.argv[1])
    print(json.dumps(result, indent=2))
