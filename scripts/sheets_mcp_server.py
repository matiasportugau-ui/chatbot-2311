#!/usr/bin/env python3
"""
MCP Server for Google Sheets CRM
Wraps the existing integracion_google_sheets.py to expose it as an MCP server.
Includes "Smart Trigger" logic to auto-calculate quotes for new leads.
"""

import sys
import os
import json
import logging
from typing import Any, Dict, List, Optional
from decimal import Decimal
from mcp.server.fastmcp import FastMCP

# Add parent directory to path to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integracion_google_sheets import IntegracionGoogleSheets
from ia_conversacional_integrada import IAConversacionalIntegrada
from sistema_cotizaciones import SistemaCotizacionesBMC, EspecificacionCotizacion, Cliente

# Initialize FastMCP
mcp = FastMCP("Google Sheets CRM")

# Global instances
sheets_integration = None
cotizaciones_system = None

def get_services():
    """Lazy loading of services"""
    global sheets_integration, cotizaciones_system
    
    if sheets_integration is None:
        # Initialize with a dummy/minimal IA
        ia = IAConversacionalIntegrada() 
        sheets_integration = IntegracionGoogleSheets(ia)
        sheets_integration.conectar_google_sheets()
        
    if cotizaciones_system is None:
        cotizaciones_system = SistemaCotizacionesBMC()
        # Ensure prices are set (in production this would load from DB/Matrix)
        cotizaciones_system.actualizar_precio_producto("isodec", Decimal("45.00")) # Example price
        cotizaciones_system.actualizar_precio_producto("poliestireno", Decimal("35.00"))
        
    return sheets_integration, cotizaciones_system

def map_extraction_to_specs(extracted_data: Dict) -> Optional[EspecificacionCotizacion]:
    """Maps extracted data dictionary to EspecificacionCotizacion dataclass"""
    try:
        # Defaults
        producto = extracted_data.get("producto") or "isodec" # Default to isodec if null
        espesor = extracted_data.get("espesor") or "100mm"
        
        # Dimensions
        dims = extracted_data.get("dimensiones", {})
        largo = Decimal("0")
        ancho = Decimal("0")
        
        if dims.get("tipo") == "paneles":
            # Heuristic: if panels, assume standard width 1m and length specified
            largo = Decimal(str(dims.get("largo", 0)))
            ancho = Decimal(str(dims.get("cantidad", 0))) # Treat qty as width multiplier ~ rough estimate
        elif dims.get("tipo") == "area":
            # Heuristic: Sqrt for square shape approximation if only area given
            area = Decimal(str(dims.get("area", 0)))
            side = area.sqrt()
            largo = side
            ancho = side
        elif dims.get("tipo") == "volumen":
            largo = Decimal(str(dims.get("largo", 0)))
            ancho = Decimal(str(dims.get("ancho", 0)))
            
        if largo == 0 or ancho == 0:
            # Fallback for pricing if no dims found
            largo = Decimal("1")
            ancho = Decimal("1")

        return EspecificacionCotizacion(
            producto=producto,
            espesor=espesor,
            relleno="EPS", # Default
            largo_metros=largo,
            ancho_metros=ancho,
            color=extracted_data.get("color", "Blanco").capitalize(),
            termina_front="Gotero", # Defaults
            termina_sup="Gotero",
            termina_lat_1="Gotero",
            termina_lat_2="Gotero",
            anclajes="Incluido",
            traslado="Incluido",
            direccion="",
            forma="MCP",
            origen="MCP"
        )
    except Exception as e:
        print(f"Error mapping specs: {e}")
        return None

@mcp.tool()
def list_pending_quotes() -> str:
    """
    List all pending quotes from the 'Admin.' sheet in the CRM.
    Returns a formatted string with the list of quotes.
    """
    try:
        sheets, _ = get_services()
        quotes = sheets.leer_cotizaciones_pendientes()
        
        if not quotes:
            return "No pending quotes found."
            
        result = "Pending Quotes:\n"
        for q in quotes:
            result += f"- [{q.get('Arg', 'N/A')}] {q.get('Cliente', 'Unknown')}: {q.get('Consulta', '')} (Status: {q.get('Estado', '')})\n"
        return result
    except Exception as e:
        return f"Error listing quotes: {str(e)}"

@mcp.tool()
def get_quote_details(arg_code: str) -> str:
    """
    Get detailed information for a specific quote by its ARG code.
    """
    try:
        sheets, _ = get_services()
        quotes = sheets.leer_cotizaciones_pendientes()
        
        for q in quotes:
            if q.get('Arg') == arg_code:
                return json.dumps(q, ensure_ascii=False, indent=2)
        
        return f"Quote with ARG code '{arg_code}' not found."
    except Exception as e:
        return f"Error getting quote details: {str(e)}"

@mcp.tool()
def add_new_lead(name: str, phone: str, inquiry: str, location: str = "") -> str:
    """
    Add a new lead to the CRM.
    TRIGGERS AUTO-QUOTATION:
    1. Adds the lead.
    2. Analyzes the inquiry text.
    3. Calculates a draft price.
    4. Updates the lead with the price and 'Borrador' status.
    """
    try:
        sheets, sistema = get_services()
        
        # 1. Analyze Inquiry
        extraction = sheets.extraer_informacion_consulta(inquiry)
        
        # 2. Calculate Price
        specs = map_extraction_to_specs(extraction)
        precio_estimado = Decimal("0")
        error_calc = ""
        
        if specs:
            try:
                precio_estimado, _ = sistema.calcular_precio_cotizacion(specs)
            except Exception as e:
                error_calc = str(e)
                print(f"Calculation error: {e}")
        
        # 3. Prepare Data
        # Append price to consultation text for visibility in Sheet
        consulta_enriquecida = inquiry
        estado_inicial = "Pendiente"
        
        if precio_estimado > 0:
            consulta_enriquecida += f" || 🤖 Auto-Quote: ${precio_estimado:,.2f}"
            estado_inicial = "Borrador" # Draft status
        elif error_calc:
             consulta_enriquecida += f" || ⚠️ Calc Error: {error_calc}"

        data = {
            "cliente": name,
            "telefono": phone,
            "consulta": consulta_enriquecida,
            "direccion": location,
            "origen": "MCP_Agent",
            "estado": estado_inicial
        }
        
        # 4. Save to Sheet
        result = sheets.guardar_cotizacion_en_sheets(data)
        
        if result.get("exito"):
            msg = f"Successfully added lead ({result.get('codigo_arg')})."
            if precio_estimado > 0:
                msg += f"\n✨ AUTOMATION TRIGGERED: Draft quote generated for ${precio_estimado:,.2f}."
            elif error_calc:
                 msg += f"\nWarning: Could not auto-quote ({error_calc})."
            else:
                 msg += "\nNote: Could not estimate price from inquiry details."
            return msg
        else:
            return f"Failed to add lead: {result.get('error')}"
            
    except Exception as e:
        return f"Error adding lead: {str(e)}"

if __name__ == "__main__":
    # check for mcp installation
    try:
        import mcp
        mcp.run()
    except ImportError:
        print("MCP library not found. Please install it: pip install mcp[cli] uvicorn")
        sys.exit(1)
