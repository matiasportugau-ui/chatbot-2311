"""
Cloud Runner (Autopilot Supervisor)
Wrapper script designed for Cloud Environments (Docker).
Ensures the application starts correctly and stays running.
"""

import os
import time
import sys
import logging
import subprocess
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [CloudRunner] - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CloudRunner")

def handle_sigterm(signum, frame):
    logger.info("Received SIGTERM. Performing graceful shutdown...")
    # Add logic here to safely stop agents if needed
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)

def main():
    logger.info("🚀 BMC Agent Autopilot Starting...")
    
    # 1. Check Environment
    required_vars = ["OPENAI_API_KEY", "SHEET_ID"]
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        logger.warning(f"⚠️ Missing environment variables: {missing}. Agents might degrade.")
    
    # 2. Launch Unified Launcher in Background Mode
    # We use subprocess to keep it isolated/managed
    cmd = [sys.executable, "unified_launcher.py", "--mode", "background"]
    
    restart_count = 0
    max_restarts = 5
    
    while True:
        try:
            logger.info("Starting Unified Launcher...")
            process = subprocess.Popen(
                cmd,
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            
            # Monitoring Loop
            while process.poll() is None:
                # Heartbeat or health check logic could go here
                time.sleep(10)
                
            exit_code = process.returncode
            logger.error(f"Unified Launcher exited with code {exit_code}")
            
            if exit_code != 0:
                restart_count += 1
                if restart_count > max_restarts:
                    logger.critical("Too many crashes. Autopilot stopping.")
                    sys.exit(1)
                logger.info(f"Restarting in 5 seconds... (Attempt {restart_count}/{max_restarts})")
                time.sleep(5)
            else:
                logger.info("Clean exit. Shutting down.")
                break
                
        except Exception as e:
            logger.error(f"Critical Supervisor Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
