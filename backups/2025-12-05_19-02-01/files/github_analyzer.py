#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Repository Analyzer
Discovers all repositories, branches, workflows, and PRs under matiasportugau-ui
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import subprocess
from pathlib import Path

# GitHub API configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN_HERE")  # Replace with your actual GitHub token
GITHUB_OWNER = "matiasportugau-ui"
GITHUB_API_BASE = "https://api.github.com"

# Headers for GitHub API
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Codebase-Analyzer"
}


class GitHubAnalyzer:
    """Analyze GitHub repositories, branches, workflows, and PRs"""
    
    def __init__(self):
        self.repositories = []
        self.all_branches = {}
        self.all_workflows = {}
        self.all_prs = {}
        self.local_repos = []
    
    def discover_repositories(self) -> List[Dict[str, Any]]:
        """Discover all repositories under matiasportugau-ui (try org first, then user)"""
        print(f"🔍 Discovering repositories under {GITHUB_OWNER}...")
        
        repos = []
        page = 1
        per_page = 100
        
        # Try organization endpoint first
        url = f"{GITHUB_API_BASE}/orgs/{GITHUB_OWNER}/repos"
        try:
            response = requests.get(url, headers=HEADERS, params={"page": 1, "per_page": 1}, timeout=10)
            if response.status_code == 404:
                # Try user endpoint instead
                print(f"  ⚠️  Organization not found, trying user endpoint...")
                url = f"{GITHUB_API_BASE}/users/{GITHUB_OWNER}/repos"
        except:
            # Try user endpoint
            url = f"{GITHUB_API_BASE}/users/{GITHUB_OWNER}/repos"
        
        while True:
            params = {
                "page": page,
                "per_page": per_page,
                "type": "all"  # all, owner, member
            }
            
            try:
                response = requests.get(url, headers=HEADERS, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                
                for repo in data:
                    repo_info = {
                        "name": repo["name"],
                        "full_name": repo["full_name"],
                        "owner": repo["owner"]["login"],
                        "url": repo["html_url"],
                        "api_url": repo["url"],
                        "description": repo.get("description", ""),
                        "language": repo.get("language", ""),
                        "default_branch": repo.get("default_branch", "main"),
                        "visibility": repo.get("visibility", "unknown"),
                        "private": repo.get("private", False),
                        "fork": repo.get("fork", False),
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "topics": repo.get("topics", []),
                        "updated_at": repo.get("updated_at", ""),
                        "created_at": repo.get("created_at", ""),
                        "archived": repo.get("archived", False),
                        "disabled": repo.get("disabled", False)
                    }
                    repos.append(repo_info)
                    print(f"  ✅ Found: {repo_info['full_name']}")
                
                # Check if there are more pages
                if len(data) < per_page:
                    break
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Error fetching repositories: {e}")
                break
        
        # Also discover repos from local git remotes
        print(f"\n🔍 Discovering repositories from local git remotes...")
        discovered_from_local = set()
        for local_repo in self.local_repos:
            github_url = local_repo.get("github_url")
            if github_url and github_url not in discovered_from_local:
                # Extract owner/repo from URL
                try:
                    # Format: https://github.com/owner/repo
                    parts = github_url.replace("https://github.com/", "").split("/")
                    if len(parts) >= 2:
                        owner, repo_name = parts[0], parts[1]
                        if owner == GITHUB_OWNER or owner == "matiasportugau-ui":
                            # Try to get repo info
                            repo_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo_name}"
                            repo_response = requests.get(repo_url, headers=HEADERS, timeout=10)
                            if repo_response.status_code == 200:
                                repo = repo_response.json()
                                repo_info = {
                                    "name": repo["name"],
                                    "full_name": repo["full_name"],
                                    "owner": repo["owner"]["login"],
                                    "url": repo["html_url"],
                                    "api_url": repo["url"],
                                    "description": repo.get("description", ""),
                                    "language": repo.get("language", ""),
                                    "default_branch": repo.get("default_branch", "main"),
                                    "visibility": repo.get("visibility", "unknown"),
                                    "private": repo.get("private", False),
                                    "fork": repo.get("fork", False),
                                    "stars": repo.get("stargazers_count", 0),
                                    "forks": repo.get("forks_count", 0),
                                    "topics": repo.get("topics", []),
                                    "updated_at": repo.get("updated_at", ""),
                                    "created_at": repo.get("created_at", ""),
                                    "archived": repo.get("archived", False),
                                    "disabled": repo.get("disabled", False),
                                    "discovered_from": "local_git"
                                }
                                if repo_info["full_name"] not in [r["full_name"] for r in repos]:
                                    repos.append(repo_info)
                                    print(f"  ✅ Found from local: {repo_info['full_name']}")
                                    discovered_from_local.add(github_url)
                except Exception as e:
                    pass
        
        self.repositories = repos
        print(f"\n📊 Total repositories discovered: {len(repos)}")
        return repos
    
    def enumerate_branches(self, repo_name: str) -> List[Dict[str, Any]]:
        """Enumerate all branches for a repository"""
        branches = []
        page = 1
        per_page = 100
        
        url = f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{repo_name}/branches"
        
        while True:
            params = {"page": page, "per_page": per_page}
            
            try:
                response = requests.get(url, headers=HEADERS, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                
                for branch in data:
                    branch_info = {
                        "name": branch["name"],
                        "sha": branch["commit"]["sha"],
                        "protected": branch.get("protected", False)
                    }
                    branches.append(branch_info)
                
                if len(data) < per_page:
                    break
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Error fetching branches for {repo_name}: {e}")
                break
        
        return branches
    
    def discover_workflows(self, repo_name: str) -> List[Dict[str, Any]]:
        """Discover GitHub Actions workflows"""
        workflows = []
        
        # Get workflow files via contents API
        url = f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{repo_name}/contents/.github/workflows"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            
            if response.status_code == 404:
                # No workflows directory
                return workflows
            
            response.raise_for_status()
            files = response.json()
            
            for file in files:
                if file["type"] == "file" and file["name"].endswith((".yml", ".yaml")):
                    # Get file content
                    content_url = file["download_url"]
                    content_response = requests.get(content_url, timeout=30)
                    
                    workflow_info = {
                        "name": file["name"],
                        "path": file["path"],
                        "sha": file["sha"],
                        "size": file["size"],
                        "content": content_response.text if content_response.status_code == 200 else ""
                    }
                    workflows.append(workflow_info)
        
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error fetching workflows for {repo_name}: {e}")
        
        return workflows
    
    def analyze_pull_requests(self, repo_name: str, state: str = "all", limit: int = 100) -> List[Dict[str, Any]]:
        """Analyze pull requests"""
        prs = []
        page = 1
        per_page = 100
        max_pages = (limit + per_page - 1) // per_page
        
        url = f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{repo_name}/pulls"
        
        while page <= max_pages:
            params = {
                "state": state,
                "page": page,
                "per_page": per_page,
                "sort": "updated",
                "direction": "desc"
            }
            
            try:
                response = requests.get(url, headers=HEADERS, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                
                for pr in data:
                    # Get files changed
                    files_url = f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{repo_name}/pulls/{pr['number']}/files"
                    files_response = requests.get(files_url, headers=HEADERS, timeout=30)
                    files_changed = []
                    if files_response.status_code == 200:
                        files_changed = [f["filename"] for f in files_response.json()]
                    
                    pr_info = {
                        "number": pr["number"],
                        "title": pr["title"],
                        "body": pr.get("body", ""),
                        "state": pr["state"],
                        "merged": pr.get("merged", False),
                        "draft": pr.get("draft", False),
                        "head": {
                            "ref": pr["head"]["ref"],
                            "sha": pr["head"]["sha"]
                        },
                        "base": {
                            "ref": pr["base"]["ref"],
                            "sha": pr["base"]["sha"]
                        },
                        "author": pr["user"]["login"],
                        "created_at": pr["created_at"],
                        "updated_at": pr["updated_at"],
                        "labels": [label["name"] for label in pr.get("labels", [])],
                        "files_changed": files_changed,
                        "additions": pr.get("additions", 0),
                        "deletions": pr.get("deletions", 0),
                        "changed_files": pr.get("changed_files", len(files_changed))
                    }
                    prs.append(pr_info)
                
                if len(data) < per_page:
                    break
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Error fetching PRs for {repo_name}: {e}")
                break
        
        return prs[:limit]
    
    def discover_local_repos(self, base_paths: List[str]) -> List[Dict[str, Any]]:
        """Discover local git repositories"""
        print("\n🔍 Discovering local git repositories...")
        
        local_repos = []
        
        for base_path in base_paths:
            path = Path(base_path)
            if not path.exists():
                continue
            
            # Find all .git directories
            for git_dir in path.rglob(".git"):
                if git_dir.is_dir():
                    repo_path = git_dir.parent
                    
                    try:
                        # Get git remote info
                        result = subprocess.run(
                            ["git", "-C", str(repo_path), "remote", "-v"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        
                        remotes = {}
                        if result.returncode == 0:
                            for line in result.stdout.strip().split("\n"):
                                if line:
                                    parts = line.split()
                                    if len(parts) >= 2:
                                        remote_name = parts[0]
                                        remote_url = parts[1]
                                        remotes[remote_name] = remote_url
                        
                        # Get current branch
                        branch_result = subprocess.run(
                            ["git", "-C", str(repo_path), "branch", "--show-current"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
                        
                        repo_info = {
                            "path": str(repo_path),
                            "name": repo_path.name,
                            "current_branch": current_branch,
                            "remotes": remotes,
                            "github_url": self._extract_github_url(remotes)
                        }
                        local_repos.append(repo_info)
                        print(f"  ✅ Found local repo: {repo_path.name}")
                    
                    except Exception as e:
                        print(f"  ⚠️  Error processing {repo_path}: {e}")
        
        self.local_repos = local_repos
        print(f"\n📊 Total local repositories: {len(local_repos)}")
        return local_repos
    
    def _extract_github_url(self, remotes: Dict[str, str]) -> Optional[str]:
        """Extract GitHub URL from remotes"""
        for remote_url in remotes.values():
            if "github.com" in remote_url:
                # Convert SSH to HTTPS if needed
                if remote_url.startswith("git@"):
                    remote_url = remote_url.replace("git@github.com:", "https://github.com/")
                    remote_url = remote_url.replace(".git", "")
                elif remote_url.startswith("https://github.com/"):
                    remote_url = remote_url.replace(".git", "")
                return remote_url
        return None
    
    def analyze_all(self) -> Dict[str, Any]:
        """Run complete analysis"""
        print("=" * 70)
        print("GitHub Repository Analysis")
        print("=" * 70)
        
        # Discover local repos first (needed for discover_repositories)
        base_paths = [
            "/Users/matias/chatbot2511/chatbot-2311",
            "/Users/matias/Projects",
            "/Users/matias/Master_TEMP",
            "/Users/matias/Documents/GitHub"
        ]
        local_repos = self.discover_local_repos(base_paths)
        
        # Discover repositories
        repos = self.discover_repositories()
        
        # Analyze each repository
        for repo in repos:
            repo_name = repo["name"]
            print(f"\n📦 Analyzing {repo_name}...")
            
            # Get branches
            print(f"  🌿 Fetching branches...")
            branches = self.enumerate_branches(repo_name)
            self.all_branches[repo_name] = branches
            print(f"    Found {len(branches)} branches")
            
            # Get workflows
            print(f"  ⚙️  Fetching workflows...")
            workflows = self.discover_workflows(repo_name)
            self.all_workflows[repo_name] = workflows
            print(f"    Found {len(workflows)} workflows")
            
            # Get PRs
            print(f"  🔀 Fetching pull requests...")
            prs = self.analyze_pull_requests(repo_name, state="all", limit=100)
            self.all_prs[repo_name] = prs
            print(f"    Found {len(prs)} PRs")
        
        
        # Compile results
        results = {
            "repositories": repos,
            "branches": self.all_branches,
            "workflows": self.all_workflows,
            "pull_requests": self.all_prs,
            "local_repositories": local_repos,
            "summary": {
                "total_repos": len(repos),
                "total_branches": sum(len(b) for b in self.all_branches.values()),
                "total_workflows": sum(len(w) for w in self.all_workflows.values()),
                "total_prs": sum(len(p) for p in self.all_prs.values()),
                "total_local_repos": len(local_repos)
            }
        }
        
        return results


if __name__ == "__main__":
    analyzer = GitHubAnalyzer()
    results = analyzer.analyze_all()
    
    # Save results
    output_file = "github_analysis_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "=" * 70)
    print("✅ Analysis Complete!")
    print(f"📄 Results saved to: {output_file}")
    print("=" * 70)
    
    # Print summary
    summary = results["summary"]
    print(f"\n📊 Summary:")
    print(f"  Repositories: {summary['total_repos']}")
    print(f"  Branches: {summary['total_branches']}")
    print(f"  Workflows: {summary['total_workflows']}")
    print(f"  Pull Requests: {summary['total_prs']}")
    print(f"  Local Repos: {summary['total_local_repos']}")

