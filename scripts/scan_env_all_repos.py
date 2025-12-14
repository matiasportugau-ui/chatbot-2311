#!/usr/bin/env python3
"""Scan all repos + all branches, keys-only.

SECURITY GUARANTEE:
- Never prints or stores secret VALUES
- Only extracts variable KEYS (left side of KEY=...)

Outputs:
- out/env_inventory.json
- out/env_keys_unified.json
- env/.env.unified.example (placeholders)
"""

import json
import os
import pathlib
import re
import subprocess
import tempfile
from typing import Any

import requests

ENV_PATH_RE = re.compile(r"(^|/)(\.env(\..*)?|.*\.env|\.envrc)$")
KEY_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")
API = "https://api.github.com"


def sh(cmd: list[str], cwd: str | None = None, extra_env: dict[str, str] | None = None) -> str:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    r = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True, env=env)
    return r.stdout


def gh_get(url: str, token: str, params: dict[str, Any] | None = None) -> Any:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def is_org(owner: str, token: str) -> bool:
    # Lightweight detection: orgs/{owner} exists -> org
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    r = requests.get(f"{API}/orgs/{owner}", headers=headers, timeout=15)
    if r.status_code == 200:
        return True
    if r.status_code in (404, 401, 403):
        return False
    r.raise_for_status()
    return False


def list_repos(owner: str, token: str, repo_filter: str | None) -> list[dict]:
    repos: list[dict] = []
    page = 1

    base = f"{API}/orgs/{owner}/repos" if is_org(owner, token) else f"{API}/users/{owner}/repos"

    while True:
        data = gh_get(base, token, params={"per_page": 100, "page": page, "type": "all"})
        if not data:
            break
        for r in data:
            name = r["name"]
            if repo_filter and repo_filter.lower() not in name.lower():
                continue
            repos.append(r)
        page += 1
    return repos


def extract_keys_from_text(txt: str) -> list[str]:
    keys: set[str] = set()
    for line in txt.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = KEY_RE.match(line)
        if m:
            keys.add(m.group(1))
    return sorted(keys)


def _git_with_auth(cmd: list[str], token: str, cwd: str | None = None) -> str:
    # Avoid embedding token in URL; use per-command header.
    # Token still lives in process argv (as header value) but is never printed.
    auth_header = f"AUTHORIZATION: bearer {token}"
    return sh(["git", "-c", f"http.https://github.com/.extraheader={auth_header}", *cmd], cwd=cwd)


def scan_repo(
    full_name: str,
    clone_url: str,
    token: str,
    branch_limit: int,
    branch_allow_regex: str | None,
) -> dict:
    allow = re.compile(branch_allow_regex) if branch_allow_regex else None

    with tempfile.TemporaryDirectory() as tmp:
        repo_dir = pathlib.Path(tmp) / full_name.replace("/", "__")

        # Clone liviano (sin blobs; sin checkout)
        _git_with_auth(["clone", "--no-checkout", "--filter=blob:none", clone_url, str(repo_dir)], token)

        # Fetch todas las branches remotas
        _git_with_auth(["fetch", "origin", "+refs/heads/*:refs/remotes/origin/*"], token, cwd=str(repo_dir))

        refs = sh(
            ["git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin"],
            cwd=str(repo_dir),
        ).splitlines()
        branches = [r.replace("origin/", "") for r in refs if r.startswith("origin/")]

        if allow:
            branches = [b for b in branches if allow.search(b)]
        branches = sorted(set(branches))
        if branch_limit > 0:
            branches = branches[:branch_limit]

        out: dict[str, Any] = {"repo": full_name, "branches": {}}

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


def build_unified_example(inventory: list[dict]) -> tuple[str, list[str]]:
    all_keys: set[str] = set()
    for repo in inventory:
        for bdata in repo.get("branches", {}).values():
            for fdata in bdata.get("files", {}).values():
                for k in fdata.get("keys", []):
                    all_keys.add(k)
    keys_sorted = sorted(all_keys)
    example = "\n".join([f"{k}=__REQUIRED__" for k in keys_sorted]) + ("\n" if keys_sorted else "")
    return example, keys_sorted


def main() -> None:
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
    inventory: list[dict] = []

    for r in repos:
        full_name = r["full_name"]
        clone_url = r["clone_url"]
        print(f"[scan] {full_name}")
        inventory.append(
            scan_repo(
                full_name=full_name,
                clone_url=clone_url,
                token=token,
                branch_limit=branch_limit,
                branch_allow_regex=branch_allow_regex,
            )
        )

    unified_example, unified_keys = build_unified_example(inventory)

    (out_dir / "env_inventory.json").write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (env_dir / ".env.unified.example").write_text(unified_example, encoding="utf-8")
    (out_dir / "env_keys_unified.json").write_text(
        json.dumps(unified_keys, indent=2, ensure_ascii=False), encoding="utf-8"
    )


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
