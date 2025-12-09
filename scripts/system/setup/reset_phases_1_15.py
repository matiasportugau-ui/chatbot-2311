#!/usr/bin/env python3
"""
Reset Phases 1-15 to pending status
Allows re-execution of phases with new executors
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from system.context.state_manager import StateManager


def main():
    """Reset phases 1-15 to pending"""
    print("Resetting phases 1-15 to 'pending' status...")

    sm = StateManager()

    for phase in range(1, 16):
        sm.set_phase_state(phase, "pending")
        print(f"  ✓ Phase {phase} reset to pending")

    print("\n✅ All phases 1-15 reset to pending")
    print("   Ready for re-execution with new executors")


if __name__ == "__main__":
    main()

