"""
Stuck Phase Recovery Implementation
Automatically recovers phases stuck in 'in_progress' state
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path


class StuckPhaseRecovery:
    """Recover phases stuck in in_progress state"""
    
    def __init__(self, state_manager, timeout_hours: int = 2):
        """
        Initialize recovery system
        
        Args:
            state_manager: StateManager instance
            timeout_hours: Hours after which a phase is considered stuck
        """
        self.state_manager = state_manager
        self.timeout_hours = timeout_hours
    
    def find_stuck_phases(self) -> List[Dict[str, Any]]:
        """
        Find phases stuck in in_progress state
        
        Returns:
            List of stuck phase information dictionaries
        """
        phases = self.state_manager.state.get("phases", {})
        stuck_phases = []
        timeout_delta = timedelta(hours=self.timeout_hours)
        
        for phase_key, phase_data in phases.items():
            status = phase_data.get("status", "unknown")
            
            if status == "in_progress":
                started_at = phase_data.get("started_at")
                
                if started_at:
                    try:
                        # Parse timestamp (handle both with and without timezone)
                        started_str = started_at.replace('Z', '+00:00')
                        if '+' not in started_str and 'T' in started_str:
                            # No timezone, assume UTC
                            started = datetime.fromisoformat(started_str)
                        else:
                            started = datetime.fromisoformat(started_str)
                        
                        elapsed = datetime.utcnow() - started
                        
                        if elapsed > timeout_delta:
                            stuck_phases.append({
                                "phase": int(phase_key),
                                "started_at": started_at,
                                "elapsed_hours": elapsed.total_seconds() / 3600,
                                "phase_data": phase_data
                            })
                    except Exception as e:
                        # If we can't parse the date, consider it stuck
                        stuck_phases.append({
                            "phase": int(phase_key),
                            "started_at": started_at,
                            "elapsed_hours": "unknown",
                            "error": str(e),
                            "phase_data": phase_data
                        })
                else:
                    # No start time, definitely stuck
                    stuck_phases.append({
                        "phase": int(phase_key),
                        "started_at": None,
                        "elapsed_hours": "unknown",
                        "phase_data": phase_data
                    })
        
        return stuck_phases
    
    def recover_stuck_phases(self, dry_run: bool = False) -> List[int]:
        """
        Recover all stuck phases
        
        Args:
            dry_run: If True, only report stuck phases without recovering
        
        Returns:
            List of recovered phase numbers
        """
        stuck_phases = self.find_stuck_phases()
        
        if not stuck_phases:
            return []
        
        if dry_run:
            return [p["phase"] for p in stuck_phases]
        
        recovered = []
        
        for stuck_info in stuck_phases:
            phase = stuck_info["phase"]
            elapsed = stuck_info.get("elapsed_hours", "unknown")
            
            try:
                # Mark as failed with recovery message
                self.state_manager.set_phase_status(phase, "failed")
                
                recovery_message = (
                    f"Phase was stuck in 'in_progress' for {elapsed} hours "
                    f"and was automatically recovered on {datetime.utcnow().isoformat()}"
                )
                
                self.state_manager.add_phase_error(phase, recovery_message)
                recovered.append(phase)
                
            except Exception as e:
                print(f"❌ Error recovering Phase {phase}: {e}")
        
        return recovered
    
    def get_recovery_summary(self) -> Dict[str, Any]:
        """Get summary of stuck phases"""
        stuck_phases = self.find_stuck_phases()
        
        return {
            "stuck_count": len(stuck_phases),
            "timeout_hours": self.timeout_hours,
            "stuck_phases": [
                {
                    "phase": p["phase"],
                    "elapsed_hours": p.get("elapsed_hours", "unknown"),
                    "started_at": p.get("started_at")
                }
                for p in stuck_phases
            ]
        }

