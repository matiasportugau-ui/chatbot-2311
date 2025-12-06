#!/usr/bin/env python3
"""
Test script to verify the Custom MCP Server logic.
This does NOT start the MCP server, but tests the underlying tool functions.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the module to be tested
try:
    from scripts import sheets_mcp_server
    print("[OK] Successfully imported sheets_mcp_server")
except ImportError as e:
    print(f"[FAIL] Could not import sheets_mcp_server: {e}")
    sys.exit(1)

class TestGoogleSheetsMCP(unittest.TestCase):
    
    @patch('scripts.sheets_mcp_server.get_sheets_integration')
    def test_list_pending_quotes(self, mock_get_integration):
        """Test listing quotes with mocked backend"""
        print("\nTesting list_pending_quotes...")
        
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.leer_cotizaciones_pendientes.return_value = [
            {"Arg": "TEST001", "Cliente": "John Doe", "Consulta": "Test Inquiry", "Estado": "Pendiente"}
        ]
        mock_get_integration.return_value = mock_instance
        
        # Run function
        result = sheets_mcp_server.list_pending_quotes()
        
        # Verify
        self.assertIn("TEST001", result)
        self.assertIn("John Doe", result)
        print("[OK] list_pending_quotes returned valid data")

    @patch('scripts.sheets_mcp_server.get_sheets_integration')
    def test_add_new_lead(self, mock_get_integration):
        """Test adding a lead with mocked backend"""
        print("\nTesting add_new_lead...")
        
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.guardar_cotizacion_en_sheets.return_value = {
            "exito": True,
            "codigo_arg": "NEW001"
        }
        mock_get_integration.return_value = mock_instance
        
        # Run function
        result = sheets_mcp_server.add_new_lead("Jane Doe", "555-0100", "New Inquiry")
        
        # Verify
        self.assertIn("Successfully added lead", result)
        self.assertIn("NEW001", result)
        print("[OK] add_new_lead returned success")

if __name__ == '__main__':
    try:
        import mcp
        print("[OK] mcp library is installed")
    except ImportError:
        print("[FAIL] mcp library is NOT installed")
    
    # Run tests
    unittest.main()
