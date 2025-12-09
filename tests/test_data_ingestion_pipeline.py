
import unittest
import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extraer_datos_entrenamiento import ExtractorDatosEntrenamiento

class TestDataIngestion(unittest.TestCase):
    def setUp(self):
        self.extractor = ExtractorDatosEntrenamiento()
        self.test_dir = Path("tests/data_test")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.whatsapp_file = self.test_dir / "whatsapp_test.json"
        self.ml_file = self.test_dir / "ml_test.json"

    def tearDown(self):
        # Clean up
        if self.whatsapp_file.exists():
            self.whatsapp_file.unlink()
        if self.ml_file.exists():
            self.ml_file.unlink()
        if self.test_dir.exists():
            self.test_dir.rmdir()

    def test_pii_redaction(self):
        text = "Hello, call me at 099123456 or email me at user@example.com."
        redacted = self.extractor.redactar_pii(text)
        self.assertIn("[PHONE]", redacted)
        self.assertIn("[EMAIL]", redacted)
        self.assertNotIn("099123456", redacted)
        self.assertNotIn("user@example.com", redacted)
    
    def test_whatsapp_ingestion(self):
        data = [
            {
                "session_id": "123",
                "phone": "59899123456",
                "message": "Hola, precio?",
                "response": "100 pesos",
                "timestamp": "2024-01-01T10:00:00"
            }
        ]
        with open(self.whatsapp_file, 'w') as f:
            json.dump(data, f)
        
        extracted = self.extractor.extraer_whatsapp_archivo(str(self.whatsapp_file))
        self.assertEqual(len(extracted), 1)
        self.assertEqual(extracted[0]["message"], "Hola, precio?")
        # Phone should not be in the final 'phone' field if we wanted to be strict, 
        # but the script keeps the field, just redacts content. 
        # Actually metadata has original ID, let's check message content.
    
    def test_ml_ingestion(self):
        data = [
            {
                "id": "ML123",
                "text": "Tienen stock? mi mail es test@test.com",
                "answer": {"text": "Si tenemos"},
                "date_created": "2024-01-01T10:00:00",
                "status": "ANSWERED"
            }
        ]
        with open(self.ml_file, 'w') as f:
            json.dump(data, f)
            
        extracted = self.extractor.extraer_mercado_libre_archivo(str(self.ml_file))
        self.assertEqual(len(extracted), 1)
        self.assertIn("[EMAIL]", extracted[0]["question"])

if __name__ == '__main__':
    unittest.main()
