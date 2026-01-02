"""
GitHub Integration
Creates and updates GitHub issues for execution tracking
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    print("Warning: PyGithub not available. GitHub integration disabled.")


class GitHubIntegration:
    """Handles GitHub API integration for execution tracking"""
    
    def __init__(self, token: Optional[str] = None, repo: Optional[str] = None, 
                 owner: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.repo_name = repo or os.getenv("GITHUB_REPO", "chatbot-2311")
        self.owner = owner or os.getenv("GITHUB_OWNER")
        
        self.github = None
        self.repository = None
        
        if GITHUB_AVAILABLE and self.token:
            try:
                self.github = Github(self.token)
                if self.owner:
                    self.repository = self.github.get_repo(f"{self.owner}/{self.repo_name}")
            except Exception as e:
                print(f"Warning: Could not initialize GitHub client: {e}")
    
    def is_available(self) -> bool:
        """Check if GitHub integration is available"""
        return GITHUB_AVAILABLE and self.github is not None and self.repository is not None
    
    def create_execution_issue(self, execution_id: str, current_phase: int = 0) -> Optional[int]:
        """Create GitHub issue for execution tracking"""
        if not self.is_available():
            print("GitHub integration not available. Skipping issue creation.")
            return None
        
        title = f"[AUTO] Consolidation Execution - {execution_id[:8]}"
        body = self._generate_issue_body(execution_id, current_phase)
        labels = ["automation", "consolidation", "production"]
        
        try:
            issue = self.repository.create_issue(
                title=title,
                body=body,
                labels=labels
            )
            return issue.number
        except Exception as e:
            print(f"Error creating GitHub issue: {e}")
            return None
    
    def update_phase_status(self, issue_number: int, phase: int, status: str, 
                           details: Optional[Dict[str, Any]] = None) -> bool:
        """Update phase status in GitHub issue"""
        if not self.is_available():
            return False
        
        try:
            issue = self.repository.get_issue(issue_number)
            comment = self._generate_status_comment(phase, status, details)
            issue.create_comment(comment)
            return True
        except Exception as e:
            print(f"Error updating GitHub issue: {e}")
            return False
    
    def post_approval_notification(self, issue_number: int, phase: int, 
                                   approval_report: Dict[str, Any]) -> bool:
        """Post approval notification to GitHub issue"""
        if not self.is_available():
            return False
        
        try:
            issue = self.repository.get_issue(issue_number)
            comment = self._generate_approval_comment(phase, approval_report)
            issue.create_comment(comment)
            return True
        except Exception as e:
            print(f"Error posting approval notification: {e}")
            return False
    
    def create_status_comment(self, issue_number: int, phase: int, 
                             details: Dict[str, Any]) -> bool:
        """Create status comment in GitHub issue"""
        if not self.is_available():
            return False
        
        try:
            issue = self.repository.get_issue(issue_number)
            comment = self._format_status_comment(phase, details)
            issue.create_comment(comment)
            return True
        except Exception as e:
            print(f"Error creating status comment: {e}")
            return False
    
    def update_issue_body(self, issue_number: int, execution_id: str, 
                         current_phase: int, progress: float) -> bool:
        """Update main issue body with current status"""
        if not self.is_available():
            return False
        
        try:
            issue = self.repository.get_issue(issue_number)
            body = self._generate_issue_body(execution_id, current_phase, progress)
            issue.edit(body=body)
            return True
        except Exception as e:
            print(f"Error updating issue body: {e}")
            return False
    
    def close_issue(self, issue_number: int, final_report: Optional[str] = None) -> bool:
        """Close GitHub issue"""
        if not self.is_available():
            return False
        
        try:
            issue = self.repository.get_issue(issue_number)
            if final_report:
                issue.create_comment(final_report)
            issue.edit(state="closed")
            return True
        except Exception as e:
            print(f"Error closing issue: {e}")
            return False
    
    def _generate_issue_body(self, execution_id: str, current_phase: int, 
                            progress: float = 0.0) -> str:
        """Generate GitHub issue body"""
        return f"""# Automated Consolidation Execution

**Execution ID:** `{execution_id}`  
**Current Phase:** {current_phase}  
**Progress:** {progress:.1f}%

## Phase Status

| Phase | Status | Approved |
|-------|--------|----------|
| 0 | Pending | - |
| 1 | Pending | - |
| 2 | Pending | - |
| 3 | Pending | - |
| 4 | Pending | - |
| 5 | Pending | - |
| 6 | Pending | - |
| 7 | Pending | - |
| 8 | Pending | - |
| 9 | Pending | - |
| 10 | Pending | - |
| 11 | Pending | - |
| 12 | Pending | - |
| 13 | Pending | - |
| 14 | Pending | - |
| 15 | Pending | - |

## Recent Activity

- Execution started at {datetime.utcnow().isoformat()}

---
*This issue is automatically managed by the consolidation orchestrator.*
"""
    
    def _generate_status_comment(self, phase: int, status: str, 
                               details: Optional[Dict[str, Any]]) -> str:
        """Generate status comment"""
        comment = f"## Phase {phase} Status Update\n\n"
        comment += f"**Status:** {status}\n"
        comment += f"**Timestamp:** {datetime.utcnow().isoformat()}\n\n"
        
        if details:
            comment += "**Details:**\n"
            for key, value in details.items():
                comment += f"- {key}: {value}\n"
        
        return comment
    
    def _generate_approval_comment(self, phase: int, 
                                  approval_report: Dict[str, Any]) -> str:
        """Generate approval comment"""
        approved = approval_report.get("approved", False)
        status_emoji = "✅" if approved else "❌"
        
        comment = f"## {status_emoji} Phase {phase} Approval\n\n"
        comment += f"**Status:** {'Auto-approved' if approved else 'Approval failed'}\n"
        comment += f"**Criteria Met:** {approval_report.get('criteria_met', False)}\n\n"
        
        if approval_report.get("passed_checks"):
            comment += "**Passed Checks:**\n"
            for check in approval_report["passed_checks"]:
                comment += f"- ✅ {check}\n"
            comment += "\n"
        
        if approval_report.get("failed_checks"):
            comment += "**Failed Checks:**\n"
            for check in approval_report["failed_checks"]:
                comment += f"- ❌ {check}\n"
        
        return comment
    
    def _format_status_comment(self, phase: int, details: Dict[str, Any]) -> str:
        """Format status comment"""
        comment = f"## Phase {phase} Update\n\n"
        for key, value in details.items():
            comment += f"**{key}:** {value}\n"
        return comment

