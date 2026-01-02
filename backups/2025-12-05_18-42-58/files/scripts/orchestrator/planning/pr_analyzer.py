"""
PR Analyzer Module
Implements Phase 1: PR/Change Analysis (Tasks 1.1-1.4)
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys

ORCHESTRATOR_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ORCHESTRATOR_DIR.parent.parent))

from scripts.orchestrator.planning.utils import extract_pr_metadata, categorize_files, check_dependencies, map_to_bmc_components
from scripts.orchestrator.planning.agent_coordinator import PlanningAgentCoordinator


class PRAnalyzer:
    """Analyzes Pull Requests and code changes"""

    def __init__(self, github_integration=None):
        self.github_integration = github_integration
        self.coordinator = PlanningAgentCoordinator()

    def analyze_pr(self, pr_number: Optional[int] = None, pr_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main entry point for PR analysis - Phase 1"""
        if pr_data is None and pr_number:
            pr_data = self._fetch_pr_data(pr_number)

        if not pr_data:
            return {"error": "No PR data available"}

        # Task 1.1: Extract PR Metadata
        metadata = self.extract_pr_metadata(pr_data)

        # Task 1.2: Analyze Changed Files
        files_analysis = self.analyze_changed_files(pr_data)

        # Task 1.3: Understand PR Purpose
        purpose = self.understand_pr_purpose(pr_data, metadata)

        # Task 1.4: Dependency Analysis
        dependencies = self.analyze_dependencies(pr_data)

        return {
            "phase": 1,
            "task_1.1": metadata,
            "task_1.2": files_analysis,
            "task_1.3": purpose,
            "task_1.4": dependencies,
            "analysis_complete": True
        }

    def extract_pr_metadata(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Task 1.1: Extract PR Metadata"""
        # Delegate to RepositoryAgent if available
        task_config = {
            "type": "extract_pr_metadata",
            "pr_data": pr_data
        }

        result = self.coordinator.delegate_task("T1.1", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: use utility function
            return extract_pr_metadata(pr_data)

        return result.get("result", extract_pr_metadata(pr_data))

    def analyze_changed_files(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Task 1.2: Analyze Changed Files"""
        files = pr_data.get("files", [])

        # Delegate to RepositoryAgent
        task_config = {
            "type": "analyze_changed_files",
            "files": files
        }

        result = self.coordinator.delegate_task("T1.2", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: analyze locally
            categories = categorize_files(files)
            affected_modules = []
            bmc_components = []

            for file in files:
                path = file.get("path", "")
                components = map_to_bmc_components(path)
                bmc_components.extend(components)
                affected_modules.append(path)

            return {
                "files": files,
                "total_files": len(files),
                "categories": categories,
                "affected_modules": list(set(affected_modules)),
                "bmc_components": list(set(bmc_components)),
                "additions": sum(f.get("additions", 0) for f in files),
                "deletions": sum(f.get("deletions", 0) for f in files)
            }

        return result.get("result", {})

    def understand_pr_purpose(self, pr_data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Task 1.3: Understand PR Purpose"""
        # Delegate to DiscoveryAgent
        task_config = {
            "type": "understand_pr_purpose",
            "pr_data": pr_data,
            "metadata": metadata
        }

        result = self.coordinator.delegate_task("T1.3", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: analyze from PR body and title
            body = pr_data.get("body", "") or metadata.get("body", "")
            title = metadata.get("title", "")

            # Extract objectives from PR body
            objectives = []
            if "objective" in body.lower():
                # Try to extract objectives
                lines = body.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ["objective", "goal", "purpose", "aim"]):
                        objectives.append(line.strip())

            # Map to consolidation plan phases
            related_phases = []
            phase_keywords = {
                "phase 0": 0, "discovery": 0,
                "phase 1": 1, "repository": 1,
                "phase 2": 2, "component": 2,
                "phase 9": 9, "security": 9,
                "phase 13": 13, "cicd": 13, "pipeline": 13
            }

            body_lower = body.lower()
            for keyword, phase in phase_keywords.items():
                if keyword in body_lower:
                    related_phases.append(phase)

            return {
                "primary_objective": title,
                "description": body[:500] if body else "",
                "objectives": objectives if objectives else [title],
                "business_domain": self._determine_business_domain(body, metadata),
                "related_phases": list(set(related_phases)) if related_phases else [],
                "acceptance_criteria": self._extract_acceptance_criteria(body),
                "dependencies": [],
                "related_issues": []
            }

        return result.get("result", {})

    def analyze_dependencies(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Task 1.4: Dependency Analysis"""
        # Delegate to DiscoveryAgent
        task_config = {
            "type": "analyze_dependencies",
            "pr_data": pr_data
        }

        result = self.coordinator.delegate_task("T1.4", task_config)

        if result.get("error") or result.get("fallback"):
            # Fallback: use utility function
            deps = check_dependencies(pr_data)

            return {
                "new_dependencies": deps["new"],
                "updated_dependencies": deps["updated"],
                "removed_dependencies": deps["removed"],
                "conflicts": [],
                "compatibility": {
                    "python": "3.10+",
                    "compatible": True
                },
                "breaking_changes": False,
                "migration_required": False
            }

        return result.get("result", {})

    def _fetch_pr_data(self, pr_number: int) -> Optional[Dict[str, Any]]:
        """Fetch PR data from GitHub"""
        # Try GitHub CLI first
        try:
            import subprocess
            result = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--json", "number,title,body,author,state,baseRefName,headRefName,createdAt,updatedAt,mergedAt,labels,files"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as e:
            print(f"GitHub CLI not available or error: {e}")

        # Try GitHub API if integration is available
        if self.github_integration and self.github_integration.is_available():
            try:
                # Use PyGithub to fetch PR
                repo = self.github_integration.repository
                pr = repo.get_pull(pr_number)

                return {
                    "number": pr.number,
                    "title": pr.title,
                    "body": pr.body,
                    "author": {"login": pr.user.login},
                    "state": pr.state,
                    "baseRefName": pr.base.ref,
                    "headRefName": pr.head.ref,
                    "createdAt": pr.created_at.isoformat() if pr.created_at else None,
                    "updatedAt": pr.updated_at.isoformat() if pr.updated_at else None,
                    "mergedAt": pr.merged_at.isoformat() if pr.merged_at else None,
                    "labels": [{"name": label.name} for label in pr.labels],
                    "files": [{"path": f.filename, "additions": f.additions, "deletions": f.deletions, "status": f.status} for f in pr.get_files()]
                }
            except Exception as e:
                print(f"Error fetching PR from GitHub API: {e}")

        return None

    def _determine_business_domain(self, body: str, metadata: Dict[str, Any]) -> str:
        """Determine business domain from PR content"""
        content = (body + " " + metadata.get("title", "")).lower()

        if any(keyword in content for keyword in ["deployment", "orchestrator", "agent"]):
            return "deployment_orchestration"
        elif any(keyword in content for keyword in ["quotation", "cotizacion", "product"]):
            return "bmc_quotation"
        elif any(keyword in content for keyword in ["whatsapp", "integration"]):
            return "integration"
        elif any(keyword in content for keyword in ["security", "hardening"]):
            return "security"
        else:
            return "general"

    def _extract_acceptance_criteria(self, body: str) -> List[str]:
        """Extract acceptance criteria from PR body"""
        criteria = []
        lines = body.split('\n')
        in_criteria_section = False

        for line in lines:
            if "acceptance" in line.lower() and "criteria" in line.lower():
                in_criteria_section = True
                continue

            if in_criteria_section:
                if line.strip().startswith('-') or line.strip().startswith('*'):
                    criteria.append(line.strip())
                elif line.strip() == '':
                    break

        return criteria

