#!/usr/bin/env python3
"""Scan .env-like files across ALL repos + ALL branches (keys-only).

Security invariant:
- NEVER prints or stores secret values, only variable NAMES (keys).

Outputs:
- out/env_inventory.json
- out/env_keys_unified.json
- env/.env.unified.example

Env vars:
- GH_SCAN_TOKEN (required)
- GH_OWNER (required)
- REPO_FILTER (optional substring match)
- BRANCH_LIMIT (optional int; 0 = unlimited)
- BRANCH_ALLOW_REGEX (optional regex)
"""

import json
import os
import pathlib
import re
import subprocess
import tempfile
from typing import Dict, List, Optional

import requests

API = "https://api.github.com"

ENV_PATH_RE = re.compile(r"(^|/)(\.env(\..*)?|.*\.env|\.envrc)$")
KEY_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")


def sh(cmd: List[str], cwd: str | None = None, env: Optional[dict] = None) -> str:
    r = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True, env=env)
    return r.stdout


def gh_get(url: str, token: str, params=None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def owner_is_org(owner: str, token: str) -> bool:
    data = gh_get(f"{API}/users/{owner}", token)
    return (data.get("type") or "").lower() == "organization"


def list_repos(owner: str, token: str, repo_filter: Optional[str]) -> List[dict]:
    repos: List[dict] = []
    page = 1

    # Owner can be either user or org
    if owner_is_org(owner, token):
        base_url = f"{API}/orgs/{owner}/repos"
        extra = {"type": "all"}
    else:
        base_url = f"{API}/users/{owner}/repos"
        extra = {"type": "all"}

    while True:
        data = gh_get(
            base_url,
            token,
            params={"per_page": 100, "page": page, **extra},
        )
        if not data:
            break

        for r in data:
            name = r.get("name") or ""
            if repo_filter and repo_filter.lower() not in name.lower():
                continue
            repos.append(r)

        page += 1

    return repos


def extract_keys_from_text(txt: str) -> List[str]:
    keys = set()
    for line in txt.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = KEY_RE.match(line)
        if m:
            keys.add(m.group(1))
    return sorted(keys)


def git_env_for_token(token: str, askpass_path: str) -> dict:
    # Avoid embedding tokens in URLs/args (prevents leaking in logs).
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = askpass_path
    env["GIT_PASSWORD"] = token
    return env


def scan_repo(
    full_name: str,
    clone_url: str,
    token: str,
    branch_limit: int,
    branch_allow_regex: Optional[str],
) -> Dict:
    allow = re.compile(branch_allow_regex) if branch_allow_regex else None

    with tempfile.TemporaryDirectory() as tmp:
        repo_dir = pathlib.Path(tmp) / full_name.replace("/", "__")
        askpass = pathlib.Path(tmp) / "git_askpass.py"
        askpass.write_text(
            """#!/usr/bin/env python3
import os, sys
p = (sys.argv[1] if len(sys.argv) > 1 else '').lower()
if 'username' in p:
    print('x-access-token')
else:
    print(os.environ.get('GIT_PASSWORD',''))
""",
            encoding="utf-8",
        )
        askpass.chmod(0o700)

        env = git_env_for_token(token, str(askpass))

        # Lightweight clone (no blobs; no checkout)
        sh(
            [
                "git",
                "clone",
                "--no-checkout",
                "--filter=blob:none",
                "--no-tags",
                "--quiet",
                clone_url,
                str(repo_dir),
            ],
            env=env,
        )

        # Fetch all remote branches
        sh(
            [
                "git",
                "fetch",
                "--quiet",
                "origin",
                "+refs/heads/*:refs/remotes/origin/*",
                "--prune",
            ],
            cwd=str(repo_dir),
            env=env,
        )

        refs = sh(
            [
                "git",
                "for-each-ref",
                "--format=%(refname:short)",
                "refs/remotes/origin",
            ],
            cwd=str(repo_dir),
            env=env,
        ).splitlines()

        branches = [r.replace("origin/", "") for r in refs if r.startswith("origin/")]

        if allow:
            branches = [b for b in branches if allow.search(b)]

        branches = sorted(set(branches))
        if branch_limit > 0:
            branches = branches[:branch_limit]

        out: Dict = {"repo": full_name, "branches": {}}

        for b in branches:
            ref = f"origin/{b}"
            files = sh(["git", "ls-tree", "-r", "--name-only", ref], cwd=str(repo_dir), env=env).splitlines()
            env_files = [f for f in files if ENV_PATH_RE.search(f)]
            if not env_files:
                continue

            out["branches"][b] = {"files": {}}
            for fp in env_files:
                try:
                    content = sh(["git", "show", f"{ref}:{fp}"], cwd=str(repo_dir), env=env)
                except subprocess.CalledProcessError:
                    continue

                keys = extract_keys_from_text(content)
                out["branches"][b]["files"][fp] = {"keys": keys, "key_count": len(keys)}

        return out


def build_unified_example(inventory: List[Dict]) -> tuple[str, List[str]]:
    all_keys = set()
    for repo in inventory:
        for bdata in (repo.get("branches") or {}).values():
            for fdata in (bdata.get("files") or {}).values():
                for k in fdata.get("keys", []) or []:
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
        raise SystemExit("Missing GH_SCAN_TOKEN or GH_OWNER")

    out_dir = pathlib.Path("out")
    out_dir.mkdir(exist_ok=True)
    env_dir = pathlib.Path("env")
    env_dir.mkdir(exist_ok=True)

    repos = list_repos(owner, token, repo_filter)
    inventory: List[Dict] = []

    for r in repos:
        full_name = r.get("full_name")
        clone_url = r.get("clone_url")
        if not full_name or not clone_url:
            continue

        print(f"[scan] {full_name}")
        try:
            inventory.append(scan_repo(full_name, clone_url, token, branch_limit, branch_allow_regex))
        except Exception as e:
            # Continue scanning other repos
            inventory.append({"repo": full_name, "error": str(e), "branches": {}})

    unified_example, unified_keys = build_unified_example(inventory)

    (out_dir / "env_inventory.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    (env_dir / ".env.unified.example").write_text(unified_example, encoding="utf-8")
    (out_dir / "env_keys_unified.json").write_text(json.dumps(unified_keys, indent=2, ensure_ascii=False), encoding="utf-8")


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
# body_sha256: TBD
# notes: Multi-repo + multi-branch env scan; keys-only; outputs inventory + unified env example.
