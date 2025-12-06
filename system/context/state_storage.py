#!/usr/bin/env python3
"""
State Storage - Almacenamiento persistente de estado.
Fase -7: Gestión de Estado y Contexto
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class StateStorage:
    """Maneja el almacenamiento persistente del estado."""
    
    def __init__(self, storage_dir: str = "system/context/storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, key: str, data: Dict[str, Any]) -> bool:
        """Guarda datos con una clave específica."""
        try:
            file_path = self.storage_dir / f"{key}.json"
            data["_saved_at"] = datetime.now().isoformat()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving {key}: {e}")
            return False
    
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Carga datos por clave."""
        try:
            file_path = self.storage_dir / f"{key}.json"
            if not file_path.exists():
                return None
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Elimina datos por clave."""
        try:
            file_path = self.storage_dir / f"{key}.json"
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting {key}: {e}")
            return False
    
    def list_keys(self) -> list:
        """Lista todas las claves almacenadas."""
        try:
            return [f.stem for f in self.storage_dir.glob("*.json")]
        except Exception:
            return []

