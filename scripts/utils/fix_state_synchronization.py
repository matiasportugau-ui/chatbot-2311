#!/usr/bin/env python3
"""
Fix State Synchronization Issues
- Syncs Phase 0 status between state managers
- Resets current phase to proper starting point
- Validates state consistency
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def fix_state_sync():
    """Fix state synchronization issues"""
    print("=" * 80)
    print("🔧 FIXING STATE SYNCHRONIZATION")
    print("=" * 80)
    
    # Fix orchestrator state
    print("\n1. Fixing Orchestrator State...")
    try:
        from scripts.orchestrator.state_manager import StateManager as OrchestratorStateManager
        osm = OrchestratorStateManager()
        
        # Check current state
        current_phase = osm.get_current_phase()
        phase_0_status = osm.get_phase_status(0)
        
        print(f"   Current phase: {current_phase}")
        print(f"   Phase 0 status: {phase_0_status}")
        
        # Fix Phase 0 if needed
        if phase_0_status != "completed":
            print("   ⚠️  Phase 0 not marked as completed. Fixing...")
            osm.set_phase_status(0, "completed")
            osm.set_phase_approved(0, True, True)
            # Add Phase 0 outputs if they exist
            phase_0_outputs = [
                "consolidation/discovery/workspace_analysis.json",
                "consolidation/discovery/bmc_inventory.json",
                "consolidation/discovery/integrations_status.json",
                "consolidation/discovery/quotation_assessment.json",
                "consolidation/discovery/production_baseline.json"
            ]
            for output in phase_0_outputs:
                if Path(output).exists():
                    osm.add_phase_output(0, output)
            print("   ✅ Phase 0 marked as completed")
        else:
            print("   ✅ Phase 0 already marked as completed")
        
        # Fix current phase if needed
        if current_phase > 15 or current_phase < -8:
            print(f"   ⚠️  Current phase ({current_phase}) is out of range. Resetting to -8...")
            osm.set_current_phase(-8)
            print("   ✅ Current phase reset to -8")
        elif current_phase == 16:
            # Phase 0 is completed, so start from Phase 1
            print(f"   ⚠️  Current phase is 16. Setting to 1 (Phase 0 already completed)...")
            osm.set_current_phase(1)
            print("   ✅ Current phase set to 1")
        else:
            print(f"   ✅ Current phase ({current_phase}) is valid")
        
    except Exception as e:
        print(f"   ❌ Error fixing orchestrator state: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Verify system context state
    print("\n2. Verifying System Context State...")
    try:
        from system.context.state_manager import StateManager as SystemStateManager
        ssm = SystemStateManager()
        
        phases = ssm.get_all_phases()
        print(f"   System context tracks {len(phases)} phases")
        
        phase_0_state = None
        for phase_data in phases.values():
            if phase_data.get("phase") == 0:
                phase_0_state = phase_data.get("state")
                break
        
        if phase_0_state == "completed":
            print("   ✅ Phase 0 marked as completed in system context")
        else:
            print(f"   ⚠️  Phase 0 state in system context: {phase_0_state}")
            
    except Exception as e:
        print(f"   ⚠️  Could not verify system context state: {e}")
    
    # Final verification
    print("\n3. Final Verification...")
    try:
        from scripts.orchestrator.state_manager import StateManager as OrchestratorStateManager
        osm = OrchestratorStateManager()
        
        current_phase = osm.get_current_phase()
        phase_0_status = osm.get_phase_status(0)
        completed_phases = osm.get_completed_phases()
        
        print(f"   Current phase: {current_phase}")
        print(f"   Phase 0 status: {phase_0_status}")
        print(f"   Completed phases: {len(completed_phases)} phases")
        print(f"   Phase 0 in completed list: {0 in completed_phases}")
        
        if phase_0_status == "completed" and 0 in completed_phases:
            print("\n   ✅ State synchronization fixed successfully!")
            return True
        else:
            print("\n   ⚠️  State synchronization may still have issues")
            return False
            
    except Exception as e:
        print(f"   ❌ Error in verification: {e}")
        return False

if __name__ == "__main__":
    success = fix_state_sync()
    sys.exit(0 if success else 1)

