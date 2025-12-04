#!/usr/bin/env python3
"""
Auto-Start Script for Orchestrator
Automatically runs orchestrator on session start
"""

import sys
import os
from pathlib import Path
import json
import subprocess
from datetime import datetime

# Get repository root
REPO_ROOT = Path(__file__).parent.parent.parent
ORCHESTRATOR_DIR = Path(__file__).parent
CONFIG_FILE = ORCHESTRATOR_DIR / "config" / "auto_start_config.json"

def load_config():
    """Load auto-start configuration"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "enabled": True,
        "mode": "automated",
        "resume": True,
        "check_interval": 300,  # 5 minutes
        "auto_restart": True,
        "log_file": "consolidation/logs/auto_start.log"
    }

def ensure_log_dir():
    """Ensure log directory exists"""
    log_file = Path(load_config().get("log_file", "consolidation/logs/auto_start.log"))
    log_file.parent.mkdir(parents=True, exist_ok=True)
    return log_file

def log(message: str):
    """Log message to file and console"""
    log_file = ensure_log_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}\n"
    
    with open(log_file, 'a') as f:
        f.write(log_message)
    
    print(log_message.strip())

def check_if_running():
    """Check if orchestrator is already running"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "run_automated_execution.py"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def start_orchestrator(config):
    """Start orchestrator process"""
    script_path = ORCHESTRATOR_DIR / "run_automated_execution.py"
    
    if not script_path.exists():
        log(f"ERROR: Orchestrator script not found: {script_path}")
        return False
    
    mode = config.get("mode", "automated")
    resume = config.get("resume", True)
    
    cmd = [sys.executable, str(script_path)]
    
    if mode == "manual":
        cmd.append("--mode")
        cmd.append("manual")
    elif mode == "dry-run":
        cmd.append("--mode")
        cmd.append("dry-run")
    
    if resume:
        cmd.append("--resume")
    
    try:
        log(f"Starting orchestrator: {' '.join(cmd)}")
        
        # Start in background
        process = subprocess.Popen(
            cmd,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        log(f"Orchestrator started with PID: {process.pid}")
        return True
        
    except Exception as e:
        log(f"ERROR: Failed to start orchestrator: {e}")
        return False

def main():
    """Main auto-start function"""
    log("=" * 60)
    log("Auto-Start Orchestrator")
    log("=" * 60)
    
    config = load_config()
    
    if not config.get("enabled", True):
        log("Auto-start is disabled in configuration")
        return 0
    
    if check_if_running():
        log("Orchestrator is already running, skipping start")
        return 0
    
    log("Orchestrator not running, starting...")
    
    if start_orchestrator(config):
        log("Orchestrator started successfully")
        return 0
    else:
        log("Failed to start orchestrator")
        return 1

if __name__ == "__main__":
    sys.exit(main())

