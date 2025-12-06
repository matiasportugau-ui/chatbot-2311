"""
Integration Test for BMC AI Team
Verifies:
1. PDF Generation
2. Quotation Agent Configuration
3. Evolution Agent Health Check
"""

import sys
import os
import unittest
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_generator import PDFGenerator
from agent_workflows import quotation_agent, evolution_agent, AgentContext

class TestAITeam(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = "test_output"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_pdf_generation(self):
        print("\n--- Testing PDF Generation ---")
        generator = PDFGenerator(output_dir=self.test_dir)
        data = {
            "id": "TEST-QUOTE-001",
            "cliente": {"nombre": "Test User", "telefono": "12345678"},
            "especificaciones": {
                "producto": "Isodec",
                "espesor": "100mm",
                "color": "White",
                "largo_metros": 10,
                "ancho_metros": 5
            },
            "precio_total": 5000.00,
            "precio_metro_cuadrado": 100.00
        }
        path = generator.generate_quote(data)
        self.assertTrue(os.path.exists(path))
        print(f"✅ PDF generated at: {path}")

    def test_quotation_agent(self):
        print("\n--- Testing Quotation Agent ---")
        context = AgentContext(
            session_id="test_session",
            history=[],
            metadata={}
        )
        config = quotation_agent.run("Quiero cotizar un techo", context)
        
        self.assertEqual(config["agent_name"], "QuotationAgent")
        self.assertIn("BMC Bot", config["system_prompt"])
        self.assertTrue(len(config["tools"]) > 0)
        
        # Check if PDF tool is available
        tool_names = [t["function"]["name"] for t in config["tools"]]
        self.assertIn("generate_pdf_quote", tool_names)
        print(f"✅ Agent configured with tools: {tool_names}")

    def test_evolution_agent(self):
        print("\n--- Testing Evolution Agent ---")
        status = evolution_agent.perform_health_check()
        if status["status"] != "healthy":
            print(f"❌ Evolution Agent Status Details: {status}")
        self.assertEqual(status["status"], "healthy")
        print(f"✅ Health Check Status: {status}")

if __name__ == '__main__':
    unittest.main()
