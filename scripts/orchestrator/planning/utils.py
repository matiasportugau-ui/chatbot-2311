"""
Planning Agent Utilities
Helper functions for parsing and analysis
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


def load_consolidation_plan(plan_path: str = ".cursor/plans/UNIFIED_CONSOLIDATION_PRODUCTION_PLAN.md") -> Dict[str, Any]:
    """Load and parse the consolidation plan"""
    plan_file = Path(plan_path)

    if not plan_file.exists():
        return {"error": f"Plan file not found: {plan_path}"}

    try:
        with open(plan_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract phase information
        phases = {}
        current_phase = None

        for line in content.split('\n'):
            # Match phase headers
            phase_match = re.match(r'^### .*PHASE (\d+):', line, re.IGNORECASE)
            if phase_match:
                phase_num = int(phase_match.group(1))
                current_phase = phase_num
                phases[phase_num] = {
                    "number": phase_num,
                    "title": line.strip(),
                    "tasks": []
                }

            # Match task items
            if current_phase is not None:
                task_match = re.match(r'- \[ \] \*\*T(\d+)\.(\d+):\*\*', line)
                if task_match:
                    phase = int(task_match.group(1))
                    task_num = int(task_match.group(2))
                    if phase == current_phase:
                        phases[current_phase]["tasks"].append({
                            "task_id": f"T{phase}.{task_num}",
                            "line": line.strip()
                        })

        return {
            "phases": phases,
            "total_phases": len(phases),
            "loaded_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Error loading plan: {str(e)}"}


def extract_pr_metadata(pr_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract PR metadata from GitHub API response"""
    return {
        "pr_number": pr_data.get("number"),
        "title": pr_data.get("title"),
        "body": pr_data.get("body"),
        "author": pr_data.get("author", {}).get("login") if isinstance(pr_data.get("author"), dict) else pr_data.get("author"),
        "state": pr_data.get("state"),
        "base_branch": pr_data.get("baseRefName"),
        "head_branch": pr_data.get("headRefName"),
        "created_at": pr_data.get("createdAt"),
        "updated_at": pr_data.get("updatedAt"),
        "merged_at": pr_data.get("mergedAt"),
        "labels": [label.get("name") for label in pr_data.get("labels", [])] if isinstance(pr_data.get("labels"), list) else [],
        "files_changed": len(pr_data.get("files", [])),
        "additions": sum(f.get("additions", 0) for f in pr_data.get("files", [])),
        "deletions": sum(f.get("deletions", 0) for f in pr_data.get("files", []))
    }


def categorize_files(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Categorize changed files by type"""
    categories = {
        "configuration": [],
        "source_code": [],
        "documentation": [],
        "tests": [],
        "scripts": [],
        "dependencies": []
    }

    file_extensions = {
        ".json": "configuration",
        ".yaml": "configuration",
        ".yml": "configuration",
        ".toml": "configuration",
        ".py": "source_code",
        ".ts": "source_code",
        ".tsx": "source_code",
        ".js": "source_code",
        ".jsx": "source_code",
        ".md": "documentation",
        ".mdx": "documentation",
        ".test.py": "tests",
        ".spec.py": "tests",
        ".test.ts": "tests",
        ".spec.ts": "tests",
        ".sh": "scripts",
        ".ps1": "scripts",
        "requirements.txt": "dependencies",
        "package.json": "dependencies",
        "package-lock.json": "dependencies"
    }

    for file in files:
        path = file.get("path", "")
        file_name = Path(path).name

        categorized = False
        for ext, category in file_extensions.items():
            if path.endswith(ext) or file_name == ext:
                categories[category].append({
                    "path": path,
                    "status": file.get("status", "modified"),
                    "additions": file.get("additions", 0),
                    "deletions": file.get("deletions", 0)
                })
                categorized = True
                break

        if not categorized:
            categories["source_code"].append({
                "path": path,
                "status": file.get("status", "modified"),
                "additions": file.get("additions", 0),
                "deletions": file.get("deletions", 0)
            })

    return categories


def map_to_bmc_components(file_path: str) -> List[str]:
    """Map file path to BMC components"""
    path_lower = file_path.lower()
    components = []

    if "quotation" in path_lower or "cotizacion" in path_lower:
        components.append("quotation_engine")
    if "whatsapp" in path_lower:
        components.append("whatsapp_integration")
    if "n8n" in path_lower or "workflow" in path_lower:
        components.append("n8n_workflows")
    if "qdrant" in path_lower or "vector" in path_lower:
        components.append("qdrant")
    if "chatwoot" in path_lower:
        components.append("chatwoot")
    if "dashboard" in path_lower:
        components.append("dashboard")
    if "agent" in path_lower and "background" in path_lower:
        components.append("background_agents")

    return components if components else ["general"]


def check_dependencies(pr_data: Dict[str, Any]) -> Dict[str, Any]:
    """Check for new or updated dependencies"""
    files = pr_data.get("files", [])
    dependencies = {
        "new": [],
        "updated": [],
        "removed": []
    }

    for file in files:
        path = file.get("path", "")
        if "requirements.txt" in path or "package.json" in path:
            # This is a dependency file
            if file.get("status") == "added":
                dependencies["new"].append(path)
            elif file.get("status") == "modified":
                dependencies["updated"].append(path)
            elif file.get("status") == "removed":
                dependencies["removed"].append(path)

    return dependencies

