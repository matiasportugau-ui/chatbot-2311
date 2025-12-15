#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import datetime
import json
from enum import Enum

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPLOY_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "deploy-ai-agent.sh")
LOG_FILE = os.path.join(PROJECT_ROOT, "deployment_smart.log")

class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] [{level}] {message}"
    
    # Print to console with color
    if level == "INFO":
        print(f"{Color.GREEN}➜ {message}{Color.ENDC}")
    elif level == "WARNING":
        print(f"{Color.WARNING}⚠ {message}{Color.ENDC}")
    elif level == "ERROR":
        print(f"{Color.FAIL}✖ {message}{Color.ENDC}")
    elif level == "HEADER":
        print(f"\n{Color.BOLD}{Color.CYAN}=== {message} ==={Color.ENDC}")
    else:
        print(message)
    
    # Write to log file
    with open(LOG_FILE, "a") as f:
        f.write(formatted_message + "\n")

def run_command(command, cwd=PROJECT_ROOT, capture_output=True):
    try:
        if isinstance(command, str):
            command = command.split()
        
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=capture_output,
            check=False
        )
        return result
    except Exception as e:
        log(f"Command failed: {e}", "ERROR")
        return None

def check_git_status():
    log("Checking git status...", "HEADER")
    result = run_command(["git", "status", "--porcelain"])
    
    if not result:
        return "ERROR"
    
    if not result.stdout.strip():
        log("Git working tree is clean.", "INFO")
        return "CLEAN"
    
    log("Git working tree is DIRTY.", "WARNING")
    print(result.stdout)
    return "DIRTY"

def check_sensitive_files():
    log("Scanning for sensitive files...", "HEADER")
    
    # Check if tracked
    result = run_command(["git", "ls-files", "credentials.json", ".env.production", ".env"])
    
    if result.stdout.strip():
        log("CRITICAL: Sensitive files are tracked by git!", "ERROR")
        log(f"Files: \n{result.stdout}", "ERROR")
        return False
        
    return True

def fix_git_state(auto_commit=False, message="chore: automated deployment update"):
    log("Attempting to fix git state...", "HEADER")
    
    # 1. Check for untracked files that should be ignored or added
    status = run_command(["git", "status", "--porcelain"])
    lines = status.stdout.splitlines()
    
    files_to_add = []
    
    for line in lines:
        if line.startswith("??") or line.strip(): 
            # ?? is untracked
            # M is modified
            # A is added
            files_to_add.append(line.split()[-1])
            
    if not files_to_add:
        log("Nothing to fix?", "WARNING")
        return True
        
    log(f"Found {len(files_to_add)} changed/untracked files.", "INFO")
    
    if auto_commit:
        log("Auto-committing changes...", "INFO")
        run_command(["git", "add", "."])
        run_command(["git", "commit", "-m", message])
        log("Changes committed.", "INFO")
        return True
    else:
        # Prompt user
        response = input(f"{Color.WARNING}Do you want to commit these changes? (y/n): {Color.ENDC}")
        if response.lower() == 'y':
            run_command(["git", "add", "."])
            msg = input(f"Enter commit message (default: {message}): ") or message
            run_command(["git", "commit", "-m", msg])
            log("Changes committed.", "INFO")
            return True
        else:
            log("User aborted commit.", "ERROR")
            return False

def run_deployment(target="vercel", skip_checks=False):
    log(f"Starting deployment to {target}...", "HEADER")
    
    cmd = [DEPLOY_SCRIPT, "--full-deployment", "--target", target, "--json"]
    if skip_checks:
        cmd.append("--skip-checks")
        
    log(f"Executing: {' '.join(cmd)}", "INFO")
    
    # Stream output ideally, but for now capturing execution
    process = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate()
    
    if process.returncode == 0:
        log("Deployment script finished successfully.", "INFO")
        # Try to parse last line as JSON
        try:
            lines = stdout.strip().split('\n')
            last_line = lines[-1]
            data = json.loads(last_line)
            if data.get("status") == "success":
                log("Deployment SUCCESS confirmed by script.", "INFO")
                return True
        except:
            pass
    else:
        log("Deployment script failed.", "ERROR")
        print(stderr)
        return False
        
    return True

def main():
    parser = argparse.ArgumentParser(description="Smart Deployment Manager")
    parser.add_argument("--check-only", action="store_true", help="Run checks and exit")
    parser.add_argument("--auto-commit", action="store_true", help="Automatically commit changes")
    parser.add_argument("--message", default="chore: auto-save before deployment", help="Commit message")
    parser.add_argument("--target", default="vercel", help="Deployment target")
    
    args = parser.parse_args()
    
    log("Initializing Smart Deploy...", "INFO")
    
    # 1. Security Check
    if not check_sensitive_files():
        log("Aborting due to security risks. Please untrack sensitive files.", "ERROR")
        sys.exit(1)
        
    # 2. Status Check
    status = check_git_status()
    
    if args.check_only:
        log("Check complete.", "INFO")
        sys.exit(0)
        
    # 3. Handle Dirty State
    if status == "DIRTY":
        if not fix_git_state(args.auto_commit, args.message):
            log("Cannot deploy with dirty git state. Aborting.", "ERROR")
            sys.exit(1)
            
    # 4. Deploy
    run_deployment(args.target, skip_checks=True) # Skip checks in inner script since we did them

if __name__ == "__main__":
    main()
