#!/usr/bin/env python3
"""
State Persistence - Persistencia automática de estado.
Fase -7: Gestión de Estado y Contexto
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from state_manager import StateManager


class StatePersistence:
    """Maneja la persistencia automática y snapshots del estado."""
    
    def __init__(self, state_manager: StateManager, snapshots_dir: str = "system/context/snapshots"):
        self.state_manager = state_manager
        self.snapshots_dir = Path(snapshots_dir)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    def create_snapshot(self, snapshot_name: Optional[str] = None) -> str:
        """Crea un snapshot del estado actual."""
        if snapshot_name is None:
            snapshot_name = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        snapshot_data = {
            "name": snapshot_name,
            "timestamp": datetime.now().isoformat(),
            "state": self.state_manager.state.copy()
        }
        
        snapshot_file = self.snapshots_dir / f"{snapshot_name}.json"
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
        
        return snapshot_name
    
    def load_snapshot(self, snapshot_name: str) -> bool:
        """Carga un snapshot y restaura el estado."""
        snapshot_file = self.snapshots_dir / f"{snapshot_name}.json"
        if not snapshot_file.exists():
            return False
        
        try:
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                snapshot_data = json.load(f)
            
            self.state_manager.state = snapshot_data.get("state", {})
            self.state_manager.save_state()
            return True
        except Exception as e:
            print(f"Error loading snapshot {snapshot_name}: {e}")
            return False
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """Lista todos los snapshots disponibles."""
        snapshots = []
        for snapshot_file in self.snapshots_dir.glob("*.json"):
            try:
                with open(snapshot_file, 'r', encoding='utf-8') as f:
                    snapshot_data = json.load(f)
                    snapshots.append({
                        "name": snapshot_data.get("name"),
                        "timestamp": snapshot_data.get("timestamp"),
                        "file": str(snapshot_file)
                    })
            except Exception:
                continue
        
        return sorted(snapshots, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def auto_checkpoint(self, phase: int):
        """Crea un checkpoint automático para una fase."""
        checkpoint_name = f"phase_{phase}_checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.state_manager.create_checkpoint(checkpoint_name, {"phase": phase})
        return checkpoint_name

