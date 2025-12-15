#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Judge Agent - Part of the Master Evolution Agent.
Uses the 'Evolution Matrix' to score divergent features and pick a winner.
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path to import model_integrator if needed
sys.path.insert(0, str(Path(__file__).parents[2]))

try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False

class JudgeAgent:
    def __init__(self):
        self.model_integrator = None
        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.model_integrator = get_model_integrator()
            except Exception as e:
                print(f"⚠️  Model Integrator not available: {e}")
                self.model_integrator = None
                print("Please ensure 'model_integrator' is installed and configured correctly.")
                
    def judge_features(self, feature_a: Dict, feature_b: Dict, context: str = "") -> Dict[str, Any]:
        """
        Compares two implementation variants (A vs B) and decides a winner, or suggests combining them.
        """
        if not self.model_integrator:
            return {"error": "Model Integrator needed for judgement", "winner": "Unknown", "action": "Manual Review"}

        system_prompt = """You are the Nexus Evolution Architect.
Your goal is to select the superior code implementation based on these Evolutionary Values:
1. Agentic Over Robotic (100pts): AI-driven logic > rigid state machines.
2. Production Readiness (80pts): Logging, error handling, security.
3. Human-Centric UX (60pts): Natural conversation > rigid forms.

Compare the two options provided and output JSON decision.
If both options have distinct, valuable features that are not mutually exclusive, suggest 'Combine' as the action."""

        prompt = f"""
COMPARE:
Option A ({feature_a.get('path', 'Unknown')}):
{json.dumps(feature_a.get('components', []), indent=2)}

Option B ({feature_b.get('path', 'Unknown')}):
{json.dumps(feature_b.get('components', []), indent=2)}

CONTEXT: {context}

Output format:
{{
  "winner": "A|B|None",
  "action": "Keep A|Keep B|Combine",
  "score_a": <0-100>,
  "score_b": <0-100>,
  "score_combined": <0-100>,
  "reason": "Explanation based on values"
}}
"""
        try:
            response = self.model_integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            if response and 'content' in response:
                 return json.loads(response['content'])
        except Exception as e:
            return {"error": str(e), "winner": "Manual Review", "action": "Manual Review"}
            
        return {"error": "No response", "winner": "Manual Review", "action": "Manual Review"}

if __name__ == "__main__":
    # Test stub
    agent = JudgeAgent()
    print(agent.judge_features(
        {"path": "file_v1.py", "components": [{"type": "function", "name": "regex_chat"}]},
        {"path": "file_v2.py", "components": [{"type": "class", "name": "AIChatAgent"}]}
    ))
