#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent specialized in Code Explanation (inspired by GitLab Duo).
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

class CodeExplainAgent:
    """
    Agent to explain code logic, data flow, and architecture using Markdown and Mermaid diagrams.
    """
    
    def __init__(self):
        self.model_integrator = None
        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.model_integrator = get_model_integrator()
                # print("✅ Model Integrator initialized for CodeExplainAgent")
            except Exception as e:
                print(f"⚠️  Model Integrator not available: {e}")
    
    def explain_file(self, file_path: str) -> Dict[str, Any]:
        """
        Reads a file and provides a detailed explanation.
        """
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}
            
        try:
            content = path.read_text(encoding='utf-8')
            return self.explain_code(content, filename=path.name)
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

    def explain_code(self, code_text: str, filename: str = "code snippet") -> Dict[str, Any]:
        """
        Explains code using LLM.
        """
        if not self.model_integrator:
            return {"error": "Model Integrator not available"}

        system_prompt = """You are an expert technical writer and software architect.
Your goal is to explain the provided code clearly and concisely.
Include:
1. High-level purpose.
2. Key components/classes/functions.
3. Logical flow.
4. If complex, provide a Mermaid sequence or class diagram.

Format your response in Markdown.
"""

        prompt = f"""Explain the following code ({filename}):\n\n```\n{code_text}\n```"""
        
        try:
            response = self.model_integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=2000
            )
            
            if response and 'content' in response:
                return {
                    "filename": filename,
                    "explanation": response['content']
                }
            return {"error": "Empty response from model"}
            
        except Exception as e:
            return {"error": f"LLM explanation failed: {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 code_explain_agent.py <file_path>")
        sys.exit(1)
    
    agent = CodeExplainAgent()
    result = agent.explain_file(sys.argv[1])
    
    if "explanation" in result:
        print(result["explanation"])
    else:
        print(json.dumps(result, indent=2))
