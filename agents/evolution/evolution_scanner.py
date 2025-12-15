#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evolution Scanner - Part of the Master Evolution Agent.
Scans the workspace to map the evolutionary landscape (Repositories & Branches).
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

class EvolutionScanner:
    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path).resolve()
        
    def scan_workspace(self) -> Dict[str, Any]:
        """
        Scans workspace for Git repositories and their states.
        """
        landscape = {
            "root_path": str(self.workspace),
            "repositories": [],
            "entropy_level": "Unknown"
        }
        
        # In this specific context, we are likely inside one repo, 
        # but the request mentioned "CLOUD AGENT REVISANDO TODAS LAS RAMAS Y REPOS".
        # So we check if current dir is a repo, and also look at subdirs.
        
        # Check current dir
        if (self.workspace / ".git").is_dir():
            landscape["repositories"].append(self._analyze_repo(self.workspace))
            
        # Check subdirs (depth 1) for other repos
        for item in self.workspace.iterdir():
            if item.is_dir() and (item / ".git").is_dir():
                # Avoid duplicates if workspace is itself a repo
                if item != self.workspace: 
                     landscape["repositories"].append(self._analyze_repo(item))
                     
        landscape["entropy_level"] = self._calculate_entropy(landscape["repositories"])
        return landscape

    def _analyze_repo(self, repo_path: Path) -> Dict[str, Any]:
        """
        Analyzes a single git repository.
        """
        info = {
            "name": repo_path.name,
            "path": str(repo_path),
            "branches": [],
            "current_branch": "",
            "clean_status": False
        }
        
        try:
            # Get current branch
            res = subprocess.run(
                ["git", "branch", "--show-current"], 
                cwd=repo_path, capture_output=True, text=True, check=True
            )
            info["current_branch"] = res.stdout.strip()
            
            # Get all branches
            res = subprocess.run(
                ["git", "branch", "-a"], 
                cwd=repo_path, capture_output=True, text=True, check=True
            )
            info["branches"] = [b.strip().replace("* ", "") for b in res.stdout.splitlines()]
            
            # Check status
            res = subprocess.run(
                ["git", "status", "--porcelain"], 
                cwd=repo_path, capture_output=True, text=True, check=True
            )
            info["clean_status"] = (len(res.stdout.strip()) == 0)
            
        except subprocess.CalledProcessError as e:
            info["error"] = str(e)
            
        return info

    def _calculate_entropy(self, repos: List[Dict]) -> str:
        """
        Heuristic to guess 'Entropy Level' based on branch counts and dirty states.
        """
        total_branches = sum(len(r.get("branches", [])) for r in repos)
        dirty_repos = sum(1 for r in repos if not r.get("clean_status", True))
        
        if total_branches > 10 or dirty_repos > 0:
            return "High"
        elif total_branches > 3:
            return "Medium"
        return "Low"

if __name__ == "__main__":
    scanner = EvolutionScanner()
    result = scanner.scan_workspace()
    print(json.dumps(result, indent=2))
