#!/usr/bin/env python3
"""
Recover Phases Stuck in "in_progress"
This script finds phases that are stuck in "in_progress" state
and recovers them by marking them as failed or resetting them.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

def recover_stuck_phases(dry_run=True, timeout_hours=2):
    """Recover phases stuck in in_progress"""
    print("=" * 80)
    print("🔧 RECOVERY DE FASES COLGADAS EN 'in_progress'")
    print("=" * 80)
    print()
    
    try:
        from scripts.orchestrator.state_manager import StateManager
        sm = StateManager()
    except Exception as e:
        print(f"❌ Error cargando StateManager: {e}")
        return False
    
    phases = sm.state.get("phases", {})
    stuck_phases = []
    
    # Find stuck phases
    for phase_key, phase_data in phases.items():
        status = phase_data.get("status", "unknown")
        if status == "in_progress":
            started_at = phase_data.get("started_at")
            if started_at:
                try:
                    started = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                    now = datetime.utcnow()
                    elapsed = now - started
                    
                    if elapsed > timedelta(hours=timeout_hours):
                        stuck_phases.append({
                            "phase": int(phase_key),
                            "started_at": started_at,
                            "elapsed_hours": elapsed.total_seconds() / 3600,
                            "data": phase_data
                        })
                except Exception as e:
                    # If we can't parse the date, consider it stuck
                    stuck_phases.append({
                        "phase": int(phase_key),
                        "started_at": started_at,
                        "elapsed_hours": "unknown",
                        "data": phase_data
                    })
            else:
                # No start time, definitely stuck
                stuck_phases.append({
                    "phase": int(phase_key),
                    "started_at": None,
                    "elapsed_hours": "unknown",
                    "data": phase_data
                })
    
    if not stuck_phases:
        print("✅ No hay fases colgadas en 'in_progress'")
        print("   El sistema está limpio.")
        return True
    
    print(f"⚠️  Encontradas {len(stuck_phases)} fase(s) colgada(s):")
    print()
    for stuck in stuck_phases:
        phase = stuck["phase"]
        elapsed = stuck["elapsed_hours"]
        started = stuck["started_at"] or "N/A"
        errors = len(stuck["data"].get("errors", []))
        
        print(f"  Phase {phase:3d}:")
        print(f"    Started: {started}")
        print(f"    Elapsed: {elapsed} horas" if isinstance(elapsed, (int, float)) else f"    Elapsed: {elapsed}")
        print(f"    Errors: {errors}")
        print()
    
    if dry_run:
        print("🔍 MODO DRY-RUN: No se harán cambios")
        print()
        print("Para recuperar estas fases, ejecuta:")
        print("  python3 recover_stuck_phases.py --execute")
        return False
    
    # Ask for confirmation
    print("¿Deseas recuperar estas fases? (s/n): ", end="")
    try:
        response = input().strip().lower()
        if response not in ['s', 'si', 'y', 'yes']:
            print("❌ Operación cancelada")
            return False
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada")
        return False
    
    # Recover phases
    print()
    print("🔄 Recuperando fases...")
    recovered = []
    
    for stuck in stuck_phases:
        phase = stuck["phase"]
        try:
            # Mark as failed with recovery message
            sm.set_phase_status(phase, "failed")
            sm.add_phase_error(
                phase,
                f"Phase was stuck in 'in_progress' for {stuck['elapsed_hours']} hours and was automatically recovered on {datetime.utcnow().isoformat()}"
            )
            recovered.append(phase)
            print(f"  ✅ Phase {phase} marcada como 'failed' (recuperada)")
        except Exception as e:
            print(f"  ❌ Error recuperando Phase {phase}: {e}")
    
    print()
    print("=" * 80)
    print(f"✅ Recuperación completada: {len(recovered)} fase(s) recuperada(s)")
    print("=" * 80)
    print()
    print("Opciones:")
    print("  1. Reintentar fases recuperadas manualmente")
    print("  2. Resetear fases recuperadas a 'pending' para re-ejecución")
    print("  3. Dejarlas como 'failed' (requieren intervención manual)")
    print()
    
    return True

if __name__ == "__main__":
    dry_run = "--execute" not in sys.argv
    timeout = 2  # Default: 2 hours
    
    # Parse timeout if provided
    for arg in sys.argv:
        if arg.startswith("--timeout="):
            try:
                timeout = int(arg.split("=")[1])
            except:
                pass
    
    success = recover_stuck_phases(dry_run=dry_run, timeout_hours=timeout)
    sys.exit(0 if success else 1)

