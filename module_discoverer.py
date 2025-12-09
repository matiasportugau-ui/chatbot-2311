#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Discovery and Analysis
Discovers and classifies modules across all repositories and branches
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import subprocess

# Keywords for relevance scoring
PRIMARY_KEYWORDS = [
    "chatbot", "chat", "conversation", "message", "whatsapp", 
    "lead", "crm", "sheets", "google", "quote", "quotation", 
    "cotizacion", "dashboard", "ingest", "ingestion"
]

SECONDARY_KEYWORDS = [
    "agent", "ai", "model", "integration", "webhook", "n8n", 
    "workflow", "pricing", "product", "client", "customer", 
    "analytics", "insights"
]

ALL_KEYWORDS = PRIMARY_KEYWORDS + SECONDARY_KEYWORDS


class ModuleDiscoverer:
    """Discover and classify modules across repositories"""
    
    def __init__(self):
        self.modules = []
        self.keyword_patterns = [re.compile(rf"\b{kw}\b", re.IGNORECASE) for kw in ALL_KEYWORDS]
    
    def classify_file_type(self, file_path: str, content: str = "") -> str:
        """Classify file/module type"""
        path_lower = file_path.lower()
        name_lower = Path(file_path).name.lower()
        
        # UI Components
        if any(path_lower.endswith(ext) for ext in [".tsx", ".jsx"]):
            return "UI"
        if "component" in name_lower or "page" in name_lower or "view" in name_lower:
            return "UI"
        
        # Services
        if "service" in name_lower or "api" in name_lower or "client" in name_lower:
            return "Service"
        
        # Hooks
        if name_lower.startswith("use") and (path_lower.endswith(".ts") or path_lower.endswith(".js")):
            return "Hook"
        
        # Stores
        if "store" in name_lower or "state" in name_lower or "redux" in name_lower:
            return "Store"
        
        # Domain Models
        if "model" in name_lower or "entity" in name_lower or "type" in name_lower:
            return "Domain"
        
        # Integrations
        if "integration" in name_lower or "integrate" in name_lower:
            return "Integration"
        
        # Workflows
        if ".github/workflows" in path_lower or name_lower.endswith((".yml", ".yaml")):
            if "workflow" in path_lower or "action" in path_lower:
                return "Workflow"
        
        # Utilities
        if "util" in name_lower or "helper" in name_lower or "utils" in name_lower:
            return "Utility"
        
        # Config
        if "config" in name_lower or name_lower.endswith((".config.", ".env", ".json")):
            return "Other"
        
        # Default
        return "Other"
    
    def score_relevance(self, file_path: str, content: str = "") -> tuple[str, str]:
        """Score relevance to target system"""
        text_to_search = f"{file_path} {content}".lower()
        
        # Count keyword matches
        primary_matches = sum(1 for kw in PRIMARY_KEYWORDS if kw in text_to_search)
        secondary_matches = sum(1 for kw in SECONDARY_KEYWORDS if kw in text_to_search)
        
        # Score relevance
        if primary_matches >= 2 or (primary_matches >= 1 and secondary_matches >= 2):
            relevance = "High"
        elif primary_matches >= 1 or secondary_matches >= 2:
            relevance = "Medium"
        elif secondary_matches >= 1:
            relevance = "Low"
        else:
            relevance = "None"
        
        # Build justification
        matched_keywords = []
        for kw in ALL_KEYWORDS:
            if kw in text_to_search:
                matched_keywords.append(kw)
        
        justification = f"Matches keywords: {', '.join(matched_keywords[:5])}" if matched_keywords else "No keyword matches"
        
        return relevance, justification
    
    def discover_modules_in_path(self, repo_path: str, repo_name: str, branch: str = "main") -> List[Dict[str, Any]]:
        """Discover modules in a specific path"""
        modules = []
        path = Path(repo_path)
        
        if not path.exists():
            return modules
        
        # File patterns to analyze
        code_patterns = [
            "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx", 
            "**/*.py", "**/*.json", "**/.github/workflows/*.yml"
        ]
        
        for pattern in code_patterns:
            for file_path in path.rglob(pattern):
                # Skip node_modules, .git, and other ignored directories
                if any(ignore in str(file_path) for ignore in ["node_modules", ".git", "__pycache__", ".next", "dist", "build"]):
                    continue
                
                try:
                    # Read file content (limit size)
                    content = ""
                    if file_path.is_file():
                        try:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read(10000)  # First 10KB for keyword matching
                        except:
                            pass
                    
                    # Classify module
                    module_type = self.classify_file_type(str(file_path), content)
                    
                    # Score relevance
                    relevance, justification = self.score_relevance(str(file_path), content)
                    
                    # Get relative path
                    try:
                        rel_path = str(file_path.relative_to(path))
                    except:
                        rel_path = str(file_path)
                    
                    module = {
                        "repo": repo_name,
                        "branch": branch,
                        "path": rel_path,
                        "name": file_path.name,
                        "type": module_type,
                        "description": self._generate_description(file_path, content, module_type),
                        "relevance": relevance,
                        "justification": justification,
                        "action": self._suggest_action(relevance, module_type, content),
                        "related_prs": [],  # Will be filled later
                        "notes": ""
                    }
                    
                    modules.append(module)
                
                except Exception as e:
                    pass
        
        return modules
    
    def _generate_description(self, file_path: Path, content: str, module_type: str) -> str:
        """Generate module description"""
        name = file_path.name.lower()
        path_str = str(file_path).lower()
        
        # Try to infer purpose from name and path
        if "chatbot" in name or "chat" in name:
            return "Chatbot interface or conversation handling"
        elif "quote" in name or "cotizacion" in name:
            return "Quote/quotation generation or management"
        elif "dashboard" in name:
            return "Dashboard UI component or analytics"
        elif "sheet" in name or "google" in name:
            return "Google Sheets integration"
        elif "lead" in name or "crm" in name:
            return "Lead management or CRM functionality"
        elif "integration" in path_str:
            return "External service integration"
        elif "service" in name:
            return "Business logic service"
        elif "component" in name:
            return "UI component"
        elif "hook" in name:
            return "React hook"
        elif "store" in name:
            return "State management store"
        elif "workflow" in path_str:
            return "GitHub Actions workflow"
        else:
            return f"{module_type} module"
    
    def _suggest_action(self, relevance: str, module_type: str, content: str) -> str:
        """Suggest action for module"""
        if relevance == "None":
            return "review"
        elif relevance in ["High", "Medium"]:
            if len(content) < 100:
                return "document"
            elif "TODO" in content or "FIXME" in content:
                return "refactor"
            else:
                return "integrate"
        else:
            return "review"
    
    def map_prs_to_modules(self, modules: List[Dict], prs: Dict[str, List[Dict]]) -> List[Dict]:
        """Map pull requests to affected modules"""
        for module in modules:
            repo = module["repo"]
            module_path = module["path"]
            
            if repo in prs:
                related = []
                for pr in prs[repo]:
                    # Check if PR affects this module
                    if module_path in pr.get("files_changed", []):
                        related.append(pr["number"])
                
                module["related_prs"] = related
        
        return modules
    
    def analyze_all_repositories(self, github_data: Dict, local_repos: List[Dict]) -> Dict[str, Any]:
        """Analyze all repositories and discover modules"""
        print("=" * 70)
        print("Module Discovery and Analysis")
        print("=" * 70)
        
        all_modules = []
        repos_data = github_data.get("repositories", [])
        branches_data = github_data.get("branches", {})
        prs_data = github_data.get("pull_requests", {})
        
        # Analyze GitHub repositories (main branch for now)
        print("\n📦 Analyzing GitHub repositories...")
        for repo in repos_data:
            repo_name = repo["name"]
            default_branch = repo.get("default_branch", "main")
            
            print(f"\n  🔍 {repo_name} (branch: {default_branch})...")
            
            # Try to find local clone
            local_path = None
            for local_repo in local_repos:
                if repo_name.lower() in local_repo["name"].lower() or local_repo["name"].lower() in repo_name.lower():
                    local_path = local_repo["path"]
                    break
            
            if local_path:
                modules = self.discover_modules_in_path(local_path, repo_name, default_branch)
                all_modules.extend(modules)
                print(f"    ✅ Found {len(modules)} modules")
            else:
                print(f"    ⚠️  Local clone not found, marking as #ZonaDesconocida")
                # Create placeholder module
                all_modules.append({
                    "repo": repo_name,
                    "branch": default_branch,
                    "path": "#ZonaDesconocida",
                    "name": repo_name,
                    "type": "Other",
                    "description": f"Repository {repo_name} - local clone not found",
                    "relevance": "Medium",
                    "justification": "Repository exists but not analyzed",
                    "action": "review",
                    "related_prs": [],
                    "notes": "#ZonaDesconocida - Local clone needed for analysis"
                })
        
        # Analyze local repositories not in GitHub
        print("\n📦 Analyzing additional local repositories...")
        analyzed_repos = {repo["name"] for repo in repos_data}
        
        for local_repo in local_repos:
            repo_name = local_repo["name"]
            if repo_name not in analyzed_repos:
                print(f"\n  🔍 {repo_name}...")
                modules = self.discover_modules_in_path(local_repo["path"], repo_name, local_repo.get("current_branch", "main"))
                all_modules.extend(modules)
                print(f"    ✅ Found {len(modules)} modules")
        
        # Map PRs to modules
        print("\n🔗 Mapping pull requests to modules...")
        all_modules = self.map_prs_to_modules(all_modules, prs_data)
        
        # Compile statistics
        total_modules = len(all_modules)
        relevant_modules = sum(1 for m in all_modules if m["relevance"] in ["High", "Medium"])
        
        by_type = {}
        for module in all_modules:
            m_type = module["type"]
            by_type[m_type] = by_type.get(m_type, 0) + 1
        
        by_repo = {}
        for module in all_modules:
            repo = module["repo"]
            by_repo[repo] = by_repo.get(repo, 0) + 1
        
        results = {
            "modules": all_modules,
            "statistics": {
                "total_modules": total_modules,
                "relevant_modules": relevant_modules,
                "by_type": by_type,
                "by_repo": by_repo
            }
        }
        
        return results


if __name__ == "__main__":
    # Load GitHub analysis results
    with open("github_analysis_results.json", "r") as f:
        github_data = json.load(f)
    
    discoverer = ModuleDiscoverer()
    module_results = discoverer.analyze_all_repositories(
        github_data,
        github_data.get("local_repositories", [])
    )
    
    # Save module results
    with open("module_analysis_results.json", "w") as f:
        json.dump(module_results, f, indent=2, default=str)
    
    print("\n" + "=" * 70)
    print("✅ Module Discovery Complete!")
    print(f"📄 Results saved to: module_analysis_results.json")
    print("=" * 70)
    
    stats = module_results["statistics"]
    print(f"\n📊 Statistics:")
    print(f"  Total modules: {stats['total_modules']}")
    print(f"  Relevant modules: {stats['relevant_modules']}")
    print(f"\n  By type:")
    for m_type, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
        print(f"    {m_type}: {count}")
    print(f"\n  By repository:")
    for repo, count in sorted(stats['by_repo'].items(), key=lambda x: -x[1])[:10]:
        print(f"    {repo}: {count}")

