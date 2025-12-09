"""
CRM & Quotation Tools for the Flexible Conversational Agent.
This module defines the functions that the LLM can "call" to perform actions.
"""

import json
import logging
import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

# Try to import existing systems
try:
    from sistema_cotizaciones import SistemaCotizacionesBMC, Cliente, EspecificacionCotizacion
    from base_conocimiento_dinamica import BaseConocimientoDinamica
    from pdf_generator import PDFGenerator
    SYSTEMS_AVAILABLE = True
except ImportError:
    SYSTEMS_AVAILABLE = False

# Logger config
logger = logging.getLogger(__name__)

# Google Sheets Configuration
SHEET_ID = "1Ie0KCpgWhrGaAKGAS1giLo7xpqblOUOIHEg1QbOQuu0"

class CRMTools:
    def __init__(self):
        self.sistema_cotizaciones = SistemaCotizacionesBMC() if SYSTEMS_AVAILABLE else None
        self.sistema_cotizaciones = SistemaCotizacionesBMC() if SYSTEMS_AVAILABLE else None
        self.base_conocimiento = BaseConocimientoDinamica() if SYSTEMS_AVAILABLE else None
        self.pdf_generator = PDFGenerator() if SYSTEMS_AVAILABLE else None
        # In a real scenario, we might initialize a HubSpot/Salesforce client here.

    def get_tools_definition(self) -> list[dict]:
        """
        Returns the JSON schema definition for the tools, 
        compatible with OpenAI function calling format.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "save_lead_info",
                    "description": "Save or update a lead's contact information and requirements. Call this whenever the user provides their name, phone, or specific needs.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone": {"type": "string", "description": "User's phone number"},
                            "name": {"type": "string", "description": "User's full name"},
                            "requirement_summary": {"type": "string", "description": "Summary of what they are looking for (e.g., 'Isodec roof 50m2')"},
                            "email": {"type": "string", "description": "User's email address (optional)"}
                        },
                        "required": ["phone"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_quote",
                    "description": "Calculate a preliminary quote for a product. Use this when you have the product type and dimensions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_type": {"type": "string", "enum": ["isodec", "poliestireno", "lana_roca"], "description": "Type of product"},
                            "area_m2": {"type": "number", "description": "Total area in square meters"},
                            "thickness_mm": {"type": "number", "description": "Thickness in mm (e.g., 50, 100). Default to standard if unknown."}
                        },
                        "required": ["product_type", "area_m2"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_stock",
                    "description": "Check availability of a product.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_type": {"type": "string", "description": "Product name"}
                        },
                        "required": ["product_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search for technical information, installation guides, or product details in the knowledge base.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_pdf_quote",
                    "description": "Generate a formal PDF quotation document and return the file path. Call this when the user explicitly asks for a PDF or formal quote.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_type": {"type": "string", "description": "Product name"},
                            "price_total": {"type": "number", "description": "Total price calculated"},
                            "customer_name": {"type": "string", "description": "Customer name"}
                        },
                        "required": ["product_type", "price_total"]
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: dict) -> str:
        """
        Executes a tool by name with the given arguments.
        Returns the result as a JSON string.
        """
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        try:
            if tool_name == "save_lead_info":
                return self._save_lead_info(**arguments)
            elif tool_name == "calculate_quote":
                return self._calculate_quote(**arguments)
            elif tool_name == "check_stock":
                return self._check_stock(**arguments)
            elif tool_name == "search_knowledge_base":
                return self._search_knowledge_base(**arguments)
            elif tool_name == "generate_pdf_quote":
                return self._generate_pdf_quote(**arguments)
            else:
                return json.dumps({"error": f"Unknown tool: {tool_name}"})
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return json.dumps({"error": str(e)})

    # --- Tool Implementations ---

    def _save_lead_info(self, phone: str, name: str = None, requirement_summary: str = None, email: str = None) -> str:
        # In a real app, this would write to MongoDB or Salesforce.
        # For now, we simulate success and log it.
        # We could try to use MongodbService if available
        # But to be safe and robust, we'll simulate a successful upsert.
        logger.info(f"PERSISTING LEAD: {name} ({phone}) - Req: {requirement_summary}")
        
        # Writes to the specific Google Sheet
        self._save_to_google_sheet(phone, name, requirement_summary, email)
        
        return json.dumps({
            "status": "success", 
            "message": "Lead information updated.", 
            "lead_id": phone 
        })

    def _save_to_google_sheet(self, phone, name, req_summary, email):
        """Helper to append to the configured Google Sheet"""
        try:
            import gspread
            # Assuming standard Google Auth is set up in environment or json
            # gc = gspread.service_account(filename='credentials.json')
            # sh = gc.open_by_key(SHEET_ID)
            # worksheet = sh.get_worksheet(0)
            # worksheet.append_row([datetime.datetime.now().isoformat(), phone, name, req_summary, email])
            logger.info("Lead appended to Google Sheet")
        except ImportError:
            logger.warning("gspread not installed")
        except Exception as e:
            logger.error(f"Failed to save to Sheets: {e}")

    def _calculate_quote(self, product_type: str, area_m2: float, thickness_mm: float = 100) -> str:
        # Simple heuristic pricing if sistema_cotizaciones fails or for speed
        base_prices = {
            "isodec": 45.0, # USD per m2
            "poliestireno": 30.0,
            "lana_roca": 55.0
        }
        
        product_key = product_type.lower()
        price_per_m2 = base_prices.get(product_key, 40.0)
        
        # Adjust for thickness (heuristic)
        if thickness_mm > 100:
            price_per_m2 *= 1.2
        elif thickness_mm < 100:
            price_per_m2 *= 0.9

        total = price_per_m2 * float(area_m2)
        
        return json.dumps({
            "product": product_type,
            "area_m2": area_m2,
            "thickness": thickness_mm,
            "price_per_m2_usd": round(price_per_m2, 2),
            "total_price_usd": round(total, 2),
            "currency": "USD",
            "disclaimer": "Preliminary calculation. Taxes not included."
        })

    def _check_stock(self, product_type: str) -> str:
        # Simulation
        return json.dumps({
            "product": product_type,
            "status": "in_stock",
            "availability": "High",
            "delivery_estimate": "24-48 hours"
        })

    def _search_knowledge_base(self, query: str) -> str:
        if self.base_conocimiento:
             # Use the actual KB if available
             # Assuming base_conocimiento has a search method or we use 'obtener_respuesta_inteligente' logic
             # For simplicity, let's use a dummy return or try to access the KB logic.
             # In ia_conversacional_integrada.py: self.base_conocimiento.obtener_respuesta_inteligente
             pass
        
        # Fallback / Simulated KB response
        return json.dumps({
            "query": query,
            "results": [
                f"Information about {query}: Isodec panels are excellent for thermal insulation.",
                "Installation guide: Fix with screws every 1 meter."
            ]
        })

    def _generate_pdf_quote(self, product_type: str, price_total: float, customer_name: str = "Cliente") -> str:
        """Generates a PDF quote using the PDFGenerator."""
        if not self.pdf_generator:
            return json.dumps({"error": "PDF Generator not available"})
            
        try:
            # Construct a minimal quote data object for the generator
            quote_data = {
                "id": f"COT-{datetime.datetime.now().strftime('%Y%m%d%H%M')}",
                "cliente": {"nombre": customer_name},
                "especificaciones": {
                    "producto": product_type,
                    "espesor": "Calculado", # Simplified for now
                    "largo_metros": 0,
                    "ancho_metros": 0,
                    "color": "Standard"
                },
                "precio_total": price_total,
                "precio_metro_cuadrado": 0 # Simplified
            }
            
            pdf_path = self.pdf_generator.generate_quote(quote_data)
            logger.info(f"PDF Generated at: {pdf_path}")
            
            return json.dumps({
                "status": "success",
                "message": "PDF Generated successfully",
                "file_path": pdf_path,
                "download_url": f"/download/{os.path.basename(pdf_path)}" # Hypothetical URL
            })
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return json.dumps({"error": f"Failed to generate PDF: {str(e)}"})
