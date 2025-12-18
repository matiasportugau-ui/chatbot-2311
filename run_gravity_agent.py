#!/usr/bin/env python3
"""
Launcher for Gravity Agent Mode
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from agents.gravity.gravity_agent import GravityAgent
    
    if __name__ == "__main__":
        agent = GravityAgent()
        agent.run_gravity_mode()
        
except ImportError as e:
    print(f"Error importing Gravity Agent: {e}")
    sys.exit(1)
