#!/usr/bin/env python3
"""
Main entry point for Phase 0: BMC Discovery & Assessment
Runs all Phase 0 discovery tasks using DiscoveryAgent
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from discovery.discovery_agent import DiscoveryAgent


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Phase 0: BMC Discovery & Assessment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Phase 0 with default settings
  python run_phase_0.py
  
  # Run with custom workspace and output directory
  python run_phase_0.py --workspace /path/to/workspace --output-dir consolidation/discovery
        """
    )
    
    parser.add_argument(
        "--workspace", "-w",
        default="/Users/matias/chatbot2511/chatbot-2311",
        help="Workspace path to analyze"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        default="consolidation/discovery",
        help="Output directory for discovery results"
    )
    
    args = parser.parse_args()
    
    # Create and execute DiscoveryAgent
    print("🚀 Starting Phase 0: BMC Discovery & Assessment")
    print(f"   Workspace: {args.workspace}")
    print(f"   Output: {args.output_dir}")
    print()
    
    agent = DiscoveryAgent(
        workspace_path=args.workspace,
        output_dir=args.output_dir
    )
    
    # Execute Phase 0
    results = agent.execute_phase_0()
    
    # Return appropriate exit code
    if results.get("status") == "completed":
        print("\n✅ Phase 0 completed successfully!")
        return 0
    elif results.get("status") == "partial":
        print("\n⚠️  Phase 0 completed with some issues")
        return 1
    else:
        print("\n❌ Phase 0 failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

