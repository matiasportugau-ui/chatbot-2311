#!/usr/bin/env python3
"""
Main Execution Script
Entry point for automated execution
"""

import sys
import os
import signal
from pathlib import Path

# Add orchestrator to path
orchestrator_dir = Path(__file__).parent
sys.path.insert(0, str(orchestrator_dir.parent))

from scripts.orchestrator.main_orchestrator import MainOrchestrator
from scripts.orchestrator.state_manager import StateManager
from scripts.orchestrator.status_reporter import StatusReporter


class ExecutionController:
    """Controls execution with signal handling"""
    
    def __init__(self):
        self.orchestrator = None
        self.interrupted = False
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        print("\n\nInterrupt received. Saving state and exiting gracefully...")
        self.interrupted = True
        
        if self.orchestrator:
            self.orchestrator.state_manager.set_overall_status("interrupted")
            self.orchestrator.status_reporter.save_status_report()
            print("State saved. Execution can be resumed later.")
        
        sys.exit(0)
    
    def run(self, mode: str = "automated", resume: bool = False):
        """Run execution"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Initialize orchestrator
        self.orchestrator = MainOrchestrator()
        
        # Check if can resume
        if resume and self.orchestrator.state_manager.can_resume():
            print("Resuming from saved state...")
            current_phase = self.orchestrator.state_manager.get_current_phase()
            print(f"Resuming from Phase {current_phase}")
        else:
            print("Starting new execution...")
        
        # Run execution
        try:
            success = self.orchestrator.run()
            
            if success:
                print("\n✅ Execution completed successfully!")
                return 0
            else:
                print("\n❌ Execution failed or was interrupted")
                return 1
        
        except KeyboardInterrupt:
            self.signal_handler(None, None)
            return 1
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated Consolidation Execution")
    parser.add_argument(
        "--mode",
        choices=["automated", "manual", "dry-run"],
        default="automated",
        help="Execution mode"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from saved state"
    )
    
    args = parser.parse_args()
    
    controller = ExecutionController()
    exit_code = controller.run(mode=args.mode, resume=args.resume)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

