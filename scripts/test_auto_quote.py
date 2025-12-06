#!/usr/bin/env python3
"""
Test script for Auto-Quotation Logic in MCP Server
"""

import sys
import os
import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

# Add parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import sheets_mcp_server
from sistema_cotizaciones import EspecificacionCotizacion

class TestAutoQuote(unittest.TestCase):
    
    @patch('scripts.sheets_mcp_server.get_services')
    def test_add_lead_triggers_quote(self, mock_get_services):
        print("\nTesting Auto-Quote Trigger...")
        
        # Mock Services
        mock_sheets = MagicMock()
        mock_system = MagicMock()
        mock_get_services.return_value = (mock_sheets, mock_system)
        
        # Mock Extraction
        mock_sheets.extraer_informacion_consulta.return_value = {
            "producto": "isodec",
            "espesor": "100mm",
            "dimensiones": {"tipo": "area", "area": 100},
            "color": "Blanco"
        }
        
        # Mock Calculation
        mock_system.calcular_precio_cotizacion.return_value = (Decimal("1500.00"), Decimal("15.00"))
        
        # Mock Save
        mock_sheets.guardar_cotizacion_en_sheets.return_value = {
            "exito": True,
            "codigo_arg": "AUTO001"
        }
        
        # Action
        result = sheets_mcp_server.add_new_lead(
            "Test Client", 
            "555-9999", 
            "I need Isodec 100mm for 100m2 roof"
        )
        
        # Assertions
        print(f"Result: {result}")
        self.assertIn("AUTO001", result)
        self.assertIn("Draft quote generated", result)
        self.assertIn("$1,500.00", result)
        
        # Verify Save called with Enriched Data
        mock_sheets.guardar_cotizacion_en_sheets.assert_called_once()
        args, _ = mock_sheets.guardar_cotizacion_en_sheets.call_args
        saved_data = args[0]
        
        self.assertIn("Auto-Quote: $1,500.00", saved_data["consulta"])
        self.assertEqual(saved_data["estado"], "Borrador")
        print("[OK] Lead saved with Price and Draft status")

if __name__ == '__main__':
    unittest.main()
