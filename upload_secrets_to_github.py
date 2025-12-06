#!/usr/bin/env python3
"""
Upload .env secrets to GitHub Repository Secrets (for Codespaces)
Automatically uploads all secrets from .env file to GitHub
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List

# Color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def load_env_file(env_file: str = ".env") -> Dict[str, str]:
    """Load environment variables from .env file"""
    env_values = {}
    env_path = Path(env_file)

    if not env_path.exists():
        print_error(f".env file not found: {env_file}")
        print_info("Run: python setup_unified_env.py first")
        sys.exit(1)

    print_info(f"Loading secrets from {env_file}...")

    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Skip if value is empty or placeholder
                if value and not value.startswith('your-') and value != 'your-secret-key-here':
                    env_values[key] = value

    print_success(f"Loaded {len(env_values)} secrets from .env file")
    return env_values

def check_gh_cli():
    """Check if GitHub CLI is installed"""
    try:
        result = subprocess.run(['gh', '--version'],
                              capture_output=True,
                              text=True,
                              check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_gh_auth():
    """Check if GitHub CLI is authenticated"""
    try:
        result = subprocess.run(['gh', 'auth', 'status'],
                              capture_output=True,
                              text=True,
                              check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_repo_info():
    """Get repository owner and name from git remote"""
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                              capture_output=True,
                              text=True,
                              check=True)
        url = result.stdout.strip()

        # Parse GitHub URL
        if 'github.com' in url:
            if url.startswith('https://'):
                parts = url.replace('https://github.com/', '').replace('.git', '').split('/')
            elif url.startswith('git@'):
                parts = url.replace('git@github.com:', '').replace('.git', '').split('/')
            else:
                return None, None

            if len(parts) >= 2:
                return parts[0], parts[1]

        return None, None
    except subprocess.CalledProcessError:
        return None, None

def upload_secret(owner: str, repo: str, secret_name: str, secret_value: str) -> bool:
    """Upload a single secret to GitHub"""
    try:
        # Use gh CLI to set secret
        # Note: gh secret set requires the secret to be passed via stdin or environment
        import base64

        # Encode secret value
        encoded_value = base64.b64encode(secret_value.encode()).decode()

        # Use gh secret set command for Codespaces
        # Use --app codespaces to make secrets available to Codespaces
        process = subprocess.Popen(
            ['gh', 'secret', 'set', secret_name, '--repo', f'{owner}/{repo}', '--app', 'codespaces'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=secret_value)

        if process.returncode == 0:
            return True
        else:
            print_error(f"Failed to upload {secret_name}: {stderr}")
            return False

    except Exception as e:
        print_error(f"Error uploading {secret_name}: {e}")
        return False

def upload_secrets_interactive(env_values: Dict[str, str]):
    """Upload secrets interactively"""
    print_header("Upload Secrets to GitHub")

    # Check prerequisites
    if not check_gh_cli():
        print_error("GitHub CLI (gh) is not installed")
        print_info("Install from: https://cli.github.com/")
        print_info("Or use manual method (see instructions below)")
        return False

    if not check_gh_auth():
        print_error("GitHub CLI is not authenticated")
        print_info("Run: gh auth login")
        return False

    # Get repository info
    owner, repo = get_repo_info()
    if not owner or not repo:
        print_error("Could not determine repository from git remote")
        print_info("Please provide repository manually")
        owner = input("Repository owner (username/organization): ").strip()
        repo = input("Repository name: ").strip()

    if not owner or not repo:
        print_error("Repository information required")
        return False

    print_success(f"Repository: {owner}/{repo}")
    print_info("This will upload secrets to: Settings → Secrets and variables → Codespaces")
    print_warning("Secrets will be encrypted and stored securely by GitHub")

    confirm = input("\nContinue? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print_info("Upload cancelled")
        return False

    # Upload secrets
    print("\nUploading secrets...")
    uploaded = 0
    failed = 0

    for secret_name, secret_value in env_values.items():
        print(f"Uploading {secret_name}...", end=' ')

        if upload_secret(owner, repo, secret_name, secret_value):
            print_success(f"{secret_name}")
            uploaded += 1
        else:
            print_error(f"{secret_name}")
            failed += 1

    print_header("Upload Complete")
    print_success(f"Uploaded: {uploaded} secrets")
    if failed > 0:
        print_warning(f"Failed: {failed} secrets")

    print("\nNext steps:")
    print("  1. Verify in GitHub: Settings → Secrets and variables → Codespaces")
    print("  2. Create Codespace - secrets will be automatically available")
    print("  3. Or run: bash .devcontainer/load-secrets.sh in Codespace\n")

    return uploaded > 0

def show_manual_instructions(env_values: Dict[str, str]):
    """Show manual instructions for uploading secrets"""
    print_header("Manual Upload Instructions")

    owner, repo = get_repo_info()
    if owner and repo:
        github_url = f"https://github.com/{owner}/{repo}/settings/secrets/codespaces"
    else:
        github_url = "https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/codespaces"

    print("To upload secrets manually:")
    print(f"\n1. Go to: {github_url}")
    print("2. Click 'New repository secret' for each secret")
    print("3. Enter the secret name and value")
    print("\nSecrets to upload:\n")

    for i, (secret_name, secret_value) in enumerate(env_values.items(), 1):
        display_value = secret_value[:20] + "..." if len(secret_value) > 20 else secret_value
        print(f"{i:2d}. {secret_name:30s} = {display_value}")

    print(f"\nTotal: {len(env_values)} secrets")
    print(f"\nOr use GitHub CLI:")
    print(f"  gh secret set SECRET_NAME --repo {owner}/{repo}")

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Upload .env secrets to GitHub")
    parser.add_argument("--env-file", default=".env",
                       help=".env file to read (default: .env)")
    parser.add_argument("--manual", action="store_true",
                       help="Show manual instructions instead of uploading")

    args = parser.parse_args()

    try:
        # Load secrets from .env
        env_values = load_env_file(args.env_file)

        if not env_values:
            print_error("No secrets found in .env file")
            sys.exit(1)

        if args.manual:
            show_manual_instructions(env_values)
        else:
            # Try automatic upload
            success = upload_secrets_interactive(env_values)

            if not success:
                print_warning("\nAutomatic upload failed or cancelled")
                print_info("Showing manual instructions instead...\n")
                show_manual_instructions(env_values)

    except KeyboardInterrupt:
        print_error("\nUpload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

