import unittest
import os
import sys
import json
from unittest.mock import MagicMock

from ai_agents.watcher_agent import watcher
from scripts.ingest_history import ingest_csv_history

class TestObservationalMode(unittest.TestCase):

    def test_watcher_correlation(self):
        print("\n--- Testing Watcher Agent Correlation ---")
        
        # 1. Simulate Chat Interaction
        user_phone = "59899123456"
        watcher.observe_chat(user_id=user_phone, message="Quiero cotizar Isodec 50mm", role="user")
        
        # 2. Simulate Sheet Row Update (Success)
        row_data = {
            "Fecha": "2025-12-06",
            "Telefono": "099123456", # Matching phone (normalized)
            "Producto": "Isodec",
            "Espesor": "50mm",
            "Estado": "Calificado"
        }
        
        # Watcher should find the correlation
        # We'll mock the internal _learn_pattern to verify it was called
        watcher._learn_pattern = MagicMock()
        watcher.observe_sheet_update(row_data)
        
        watcher._learn_pattern.assert_called_once()
        print("✅ Watcher correctly correlated Chat <-> Sheet update")

    def test_history_ingestion(self):
        print("\n--- Testing History Ingestion ---")
        # Create a dummy history file
        dummy_csv = "test_history.csv"
        with open(dummy_csv, "w") as f:
            f.write("Date,Customer,Product,Price\n2023-01-01,Juan,Isodec,100")
            
        try:
            ingest_csv_history(dummy_csv)
            self.assertTrue(os.path.exists("pricing_matrix_learned.json"))
            print("✅ Ingestion script generated learned pricing matrix")
        finally:
            if os.path.exists(dummy_csv):
                os.remove(dummy_csv)
            if os.path.exists("pricing_matrix_learned.json"):
                os.remove("pricing_matrix_learned.json")

if __name__ == "__main__":
    unittest.main()
