#!/usr/bin/env python3
"""Check detailed phase states to find any stuck in_progress"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.orchestrator.state_manager import StateManager

sm = StateManager()
phases = sm.state.get('phases', {})

print("=" * 80)
print("📊 ESTADO DETALLADO DE TODAS LAS FASES")
print("=" * 80)
print()

# Check for in_progress phases
in_progress_phases = []
for phase_key, phase_data in phases.items():
    status = phase_data.get('status', 'unknown')
    if status == 'in_progress':
        in_progress_phases.append((phase_key, phase_data))

if in_progress_phases:
    print("⚠️  FASES EN 'in_progress' (PODRÍAN ESTAR COLGADAS):")
    print()
    for phase_key, phase_data in in_progress_phases:
        started = phase_data.get('started_at', 'N/A')
        print(f"  Phase {phase_key}:")
        print(f"    Status: {phase_data.get('status')}")
        print(f"    Started: {started}")
        print(f"    Errors: {len(phase_data.get('errors', []))}")
        print()
else:
    print("✅ No hay fases en 'in_progress'")
    print()

# Show all phases
print("\n📋 TODAS LAS FASES:")
print("-" * 80)

# Sort phases numerically
phase_numbers = []
for k in phases.keys():
    try:
        phase_numbers.append(int(k))
    except:
        pass

for phase_num in sorted(phase_numbers):
    phase_data = phases.get(str(phase_num), {})
    status = phase_data.get('status', 'unknown')
    started = phase_data.get('started_at', 'N/A')
    completed = phase_data.get('completed_at', 'N/A')
    approved = phase_data.get('approved', False)
    
    # Format dates
    if started != 'N/A' and started:
        started_short = started[:19] if len(started) > 19 else started
    else:
        started_short = 'N/A'
    
    if completed != 'N/A' and completed:
        completed_short = completed[:19] if len(completed) > 19 else completed
    else:
        completed_short = 'N/A'
    
    status_icon = '✅' if status in ['completed', 'approved'] else '🔄' if status == 'in_progress' else '⏳' if status == 'pending' else '❌'
    
    print(f"{status_icon} Phase {phase_num:3d}: {status:12s} | Approved: {str(approved):5s} | Started: {started_short:19s} | Completed: {completed_short:19s}")

print()
print("=" * 80)
print(f"Current Phase: {sm.get_current_phase()}")
print(f"Overall Status: {sm.get_overall_status()}")
print("=" * 80)

