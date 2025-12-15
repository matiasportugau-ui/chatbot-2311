#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feature Extractor - Part of the Master Evolution Agent.
Identifies and hashes code components ("features") to compare across branches.
"""

import hashlib
import ast
import os
from pathlib import Path
from typing import Dict, Any

class FeatureExtractor:
    def __init__(self):
        pass
        
    def extract_features(self, file_path: str) -> Dict[str, Any]:
        """
        Parses a file and extracts a signature of its contents.
        Currently focuses on Python, with fallback for others.
        """
        path = Path(file_path)
        if not path.exists():
            return {"error": "File not found"}
            
        content = path.read_text(encoding='utf-8', errors='ignore')
        
        features = {
            "path": str(path),
            "size": len(content),
            "hash": self._hash_content(content),
            "components": []
        }
        
        if path.suffix == '.py':
            features["components"] = self._analyze_python_ast(content)
            
        return features

    def _hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:12]
        
    def _analyze_python_ast(self, content: str) -> list:
        """
        Extracts top-level classes and functions from Python code.
        """
        components = []
        try:
            tree = ast.parse(content)
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    components.append({
                        "type": "function",
                        "name": node.name,
                        "line_start": node.lineno
                    })
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    components.append({
                        "type": "class",
                        "name": node.name,
                        "line_start": node.lineno,
                        "methods": methods
                    })
        except SyntaxError:
            pass # Invalid python syntax, ignore AST analysis
        return components

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 feature_extractor.py <file>")
        sys.exit(1)
        
    extractor = FeatureExtractor()
    print(extractor.extract_features(sys.argv[1]))
