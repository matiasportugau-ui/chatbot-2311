#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent specialized in Security Scanning (inspired by GitLab Duo's Dependency Scanning).
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False

class SecurityScanAgent:
    """
    Agent to scan dependencies and code for potential vulnerabilities.
    """
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.model_integrator = None
        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.model_integrator = get_model_integrator()
                # print("✅ Model Integrator initialized for SecurityScanAgent")
            except Exception as e:
                print(f"⚠️  Model Integrator not available: {e}")
    
    def scan_dependencies(self) -> Dict[str, Any]:
        """
        Scans requirements.txt and package.json for known issues or asks AI for review.
        """
        results = {
            "python_vulnerabilities": [],
            "node_vulnerabilities": [],
            "summary": "No critical issues found."
        }
        
        req_file = self.repo_path / "requirements.txt"
        package_file = self.repo_path / "package.json"
        
        if req_file.exists():
            results["python_vulnerabilities"] = self._analyze_requirements(req_file.read_text())
            
        if package_file.exists():
            results["node_vulnerabilities"] = self._analyze_package_json(package_file.read_text())
            
        vuln_count = len(results["python_vulnerabilities"]) + len(results["node_vulnerabilities"])
        if vuln_count > 0:
            results["summary"] = f"Found {vuln_count} potential security warnings."
            
        return results

    def _analyze_requirements(self, content: str) -> List[Dict[str, str]]:
        """
        Analyzes python requirements. 
        Uses basic heuristics and LLM if available.
        """
        warnings = []
        # Basic heuristic checks
        if "django<3" in content.lower():
            warnings.append({"package": "Django", "issue": "Likely outdated Django version", "severity": "High"})
        if "flask<2" in content.lower():
            warnings.append({"package": "Flask", "issue": "Old Flask version", "severity": "Medium"})
            
        # LLM Check
        if self.model_integrator:
            ai_warnings = self._ask_llm_security(content, "requirements.txt")
            if ai_warnings:
                warnings.extend(ai_warnings)
                
        return warnings

    def _analyze_package_json(self, content: str) -> List[Dict[str, str]]:
        """
        Analyzes package.json.
        """
        warnings = []
        try:
            data = json.loads(content)
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}
            
            # Basic checks
            if "axios" in all_deps and all_deps["axios"].startswith("^0."):
                 warnings.append({"package": "axios", "issue": "Ensure axios version is secure (check CVEs for 0.x)", "severity": "Low"})

        except json.JSONDecodeError:
            return [{"package": "package.json", "issue": "Invalid JSON", "severity": "High"}]
            
        # LLM Check
        if self.model_integrator:
            ai_warnings = self._ask_llm_security(content, "package.json")
            if ai_warnings:
                warnings.extend(ai_warnings)
                
        return warnings

    def _ask_llm_security(self, content: str, filename: str) -> List[Dict[str, str]]:
        """
        Asks LLM to identify security risks in dependency file.
        """
        prompt = f"""Review the following {filename} for security vulnerabilities.
Focus on KNOWN high-risk outdated packages or dangerous configurations.
Return a JSON array of objects with keys: "package", "issue", "severity".
Return empty array if no obvious issues found.

{content[:2000]}
""" # Truncate to avoid token limits

        try:
            response = self.model_integrator.generate(
                prompt=prompt,
                temperature=0.0,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            if response and 'content' in response:
                try:
                    data = json.loads(response['content'])
                    if isinstance(data, list):
                        return data
                    elif "vulnerabilities" in data:
                        return data["vulnerabilities"]
                except:
                    pass
        except:
            pass
        return []

if __name__ == "__main__":
    agent = SecurityScanAgent()
    scan_results = agent.scan_dependencies()
    print(json.dumps(scan_results, indent=2))
