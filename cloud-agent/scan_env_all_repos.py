#!/usr/bin/env python3
"""
Scan all repos + all branches for .env files (keys-only).
SECURITY: This script NEVER reads/prints secret VALUES, only KEY names.

Outputs:
  - out/env_inventory.json: Full inventory of repos/branches/files/keys
  - out/env_keys_unified.json: Unified list of all unique keys
  - env/.env.unified.example: Template with all keys as placeholders
"""
import os
import re
import json
import subprocess
import tempfile
import pathlib
from typing import Dict, List

import requests

# Patterns for .env files
ENV_PATH_RE = re.compile(r"(^|/)(\.env(\..*)?|.*\.env|\.envrc)$")
KEY_RE = re.compile(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=')

API = "https://api.github.com"


def sh(cmd: List[str], cwd: str | None = None) -> str:
    """Execute shell command and return stdout."""
    r = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)
    return r.stdout


def gh_get(url: str, token: str, params=None):
    """Make authenticated GitHub API GET request."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def list_repos(owner: str, token: str, repo_filter: str | None) -> List[dict]:
    """List all repositories for the given owner."""
    repos = []
    page = 1
    while True:
        # Try user repos first; for orgs, use: f"{API}/orgs/{owner}/repos"
        url = f"{API}/users/{owner}/repos"
        try:
            data = gh_get(url, token, params={"per_page": 100, "page": page, "type": "all"})
        except requests.exceptions.HTTPError:
            # Fallback to org endpoint
            url = f"{API}/orgs/{owner}/repos"
            data = gh_get(url, token, params={"per_page": 100, "page": page, "type": "all"})
        
        if not data:
            break
        for r in data:
            name = r["name"]
            if repo_filter and repo_filter.lower() not in name.lower():
                continue
            repos.append(r)
        page += 1
    return repos


def extract_keys_from_text(txt: str) -> List[str]:
    """Extract environment variable keys from text (no values!)."""
    keys = set()
    for line in txt.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = KEY_RE.match(line)
        if m:
            keys.add(m.group(1))
    return sorted(keys)


def scan_repo(full_name: str, clone_url: str, branch_limit: int, branch_allow_regex: str | None) -> Dict:
    """Scan a single repository for .env files across branches."""
    allow = re.compile(branch_allow_regex) if branch_allow_regex else None

    with tempfile.TemporaryDirectory() as tmp:
        repo_dir = pathlib.Path(tmp) / full_name.replace("/", "__")

        # Shallow clone without checkout (fast, no blobs)
        sh(["git", "clone", "--no-checkout", "--filter=blob:none", clone_url, str(repo_dir)])

        # Fetch all remote branches
        sh(["git", "fetch", "origin", "+refs/heads/*:refs/remotes/origin/*"], cwd=str(repo_dir))

        refs = sh(["git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin"], cwd=str(repo_dir)).splitlines()
        branches = [r.replace("origin/", "") for r in refs if r.startswith("origin/")]

        if allow:
            branches = [b for b in branches if allow.search(b)]
        branches = sorted(set(branches))
        if branch_limit > 0:
            branches = branches[:branch_limit]

        out = {"repo": full_name, "branches": {}}

        for b in branches:
            ref = f"origin/{b}"
            files = sh(["git", "ls-tree", "-r", "--name-only", ref], cwd=str(repo_dir)).splitlines()
            env_files = [f for f in files if ENV_PATH_RE.search(f)]
            if not env_files:
                continue

            out["branches"][b] = {"files": {}}
            for fp in env_files:
                try:
                    content = sh(["git", "show", f"{ref}:{fp}"], cwd=str(repo_dir))
                except subprocess.CalledProcessError:
                    continue
                keys = extract_keys_from_text(content)
                out["branches"][b]["files"][fp] = {"keys": keys, "key_count": len(keys)}
        return out


def build_unified_example(inventory: List[Dict]) -> tuple[str, List[str]]:
    """Build unified .env.example from all discovered keys."""
    all_keys = set()
    for repo in inventory:
        for bdata in repo.get("branches", {}).values():
            for fdata in bdata.get("files", {}).values():
                for k in fdata.get("keys", []):
                    all_keys.add(k)
    keys_sorted = sorted(all_keys)
    example = "\n".join([f"{k}=__REQUIRED__" for k in keys_sorted]) + ("\n" if keys_sorted else "")
    return example, keys_sorted


def main():
    token = os.getenv("GH_SCAN_TOKEN")
    owner = os.getenv("GH_OWNER")
    repo_filter = os.getenv("REPO_FILTER") or None
    branch_limit = int(os.getenv("BRANCH_LIMIT", "0"))
    branch_allow_regex = os.getenv("BRANCH_ALLOW_REGEX") or None

    if not token or not owner:
        raise SystemExit("Missing GH_SCAN_TOKEN or GH_OWNER environment variables")

    out_dir = pathlib.Path("out")
    out_dir.mkdir(exist_ok=True)
    env_dir = pathlib.Path("env")
    env_dir.mkdir(exist_ok=True)

    print(f"[scan] Listing repos for owner: {owner}")
    repos = list_repos(owner, token, repo_filter)
    print(f"[scan] Found {len(repos)} repositories")
    
    inventory = []

    for r in repos:
        full_name = r["full_name"]
        clone_url = r["clone_url"]
        print(f"[scan] Scanning {full_name}")
        try:
            inventory.append(scan_repo(full_name, clone_url, branch_limit, branch_allow_regex))
        except Exception as e:
            print(f"[warn] Failed to scan {full_name}: {e}")
            inventory.append({"repo": full_name, "branches": {}, "error": str(e)})

    unified_example, unified_keys = build_unified_example(inventory)

    # Write outputs
    (out_dir / "env_inventory.json").write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (env_dir / ".env.unified.example").write_text(unified_example, encoding="utf-8")
    (out_dir / "env_keys_unified.json").write_text(
        json.dumps(unified_keys, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"[done] Scanned {len(repos)} repos, found {len(unified_keys)} unique keys")
    print(f"[done] Outputs: out/env_inventory.json, out/env_keys_unified.json, env/.env.unified.example")


if __name__ == "__main__":
    main()

# EXPORT_SEAL v1
# project: bmc-uy
# prompt_id: cloud-agent-pack
# version: 1.0.0
# file: scripts/scan_env_all_repos.py
# lang: py
# created_at: 2025-12-14T00:00:00Z
# author: Matias Portugau
# origin: github-cloud-agent-blueprint
# notes: Multi-repo + multi-branch env scan; keys-only; outputs inventory + unified env example.
