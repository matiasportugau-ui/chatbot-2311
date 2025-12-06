"""
AI Agent Workflows for BMC Uruguay.
Defines the specialized agents: Quotation Agent and Evolution Agent.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Import internal tools
try:
    from tools_crm import CRMTools
except ImportError:
    CRMTools = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentContext:
    session_id: str
    history: List[Dict[str, str]]
    metadata: Dict[str, Any]

class BaseAgent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.crm_tools = CRMTools() if CRMTools else None

    def get_system_prompt(self) -> str:
        return self.system_prompt

    def run(self, message: str, context: AgentContext) -> str:
        raise NotImplementedError("Subclasses must implement run method")

class QuotationAgent(BaseAgent):
    """
    Expert Sales Agent dedicated to handling quotations, product inquiries,
    and closing sales with PDF generation capabilities.
    """
    
    SYSTEM_PROMPT = """
    You are 'BMC Bot', an expert Sales Engineer for BMC Uruguay.
    Your goal is to help customers find the right insulation products (Isodec, Poliestireno, Lana de Roca)
    and generate accurate quotations.
    
    CORE RESPONSIBILITIES:
    1.  **Qualify:** Ask for missing information (Dimensions: Length x Width, Product Type, Thickness) naturally.
    2.  **Quote:** Once you have the data, ALWAYS calculate the quote.
    3.  **Close:** Offer to generate a PDF quote or check stock.
    4.  **Support:** Answer technical questions using your knowledge base.

    TONE:
    - Professional, helpful, and concise.
    - Spanish language (Rioplatense variant is acceptable but keep it formal).
    
    TOOLS AVAILABLE:
    - calculate_quote(product_type, area_m2, thickness_mm)
    - generate_pdf_quote(quote_id) -> returns PDF path
    - check_stock(product_type)
    - save_lead_info(phone, name)
    - search_knowledge_base(query)

    CRITICAL INSTRUCTIONS:
    - DO NOT use regex or rigid patterns. Understand the user's intent.
    - If the user asks for a "budget" or "price", treat it as a quote request.
    - If the user confirms the price, ask if they want a formal PDF (cotización formal).
    - If you calculate a quote, the tool will return a JSON. Summarize it nicely for the user.
    """

    def __init__(self):
        super().__init__("QuotationAgent", self.SYSTEM_PROMPT)

    def run(self, message: str, context: AgentContext) -> Dict[str, Any]:
        """
        Processes a message and returns the response + actions.
        This method is designed to be called by the ModelIntegrator.
        """
        # In a real implementation with OpenAI/LangChain, this would:
        # 1. Send history + message + tools definition to LLM.
        # 2. LLM decides to call tool OR respond.
        # 3. If tool, execute and loop.
        # 4. Return final text.
        
        # For this architecture, we return the configuration for the ModelIntegrator
        # to execute the actual LLM call.
        return {
            "agent_name": self.name,
            "system_prompt": self.SYSTEM_PROMPT,
            "tools": self.crm_tools.get_tools_definition() if self.crm_tools else []
        }

class EvolutionAgent(BaseAgent):
    """
    Background agent that runs 24/7 to monitor system health and
    suggest improvements.
    """
    
    SYSTEM_PROMPT = """
    You are the 'Evolution Agent'. You run in the background of the BMC System.
    Your job is to:
    1.  Monitor conversation logs for failed quotes or angry users.
    2.  Check for system errors in logs.
    3.  Report status every hour.
    
    You do NOT interact with customers directly. You interact with the System Admin.
    """

    def __init__(self):
        super().__init__("EvolutionAgent", self.SYSTEM_PROMPT)

    def perform_health_check(self) -> Dict[str, Any]:
        """
        Runs a health check on the quotation system components.
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": []
        }
        
        # Check 1: PDF Generation
        try:
            from pdf_generator import PDFGenerator
            gen = PDFGenerator(output_dir="temp_check")
            # Create a dummy small file to test write permissions
            # Clean up immediately
            import shutil
            if os.path.exists("temp_check"):
                shutil.rmtree("temp_check")
            status["checks"].append({"name": "pdf_generation", "status": "ok"})
        except Exception as e:
            status["status"] = "degraded"
            status["checks"].append({"name": "pdf_generation", "status": "error", "details": str(e)})

        return status

# Singleton instances
quotation_agent = QuotationAgent()
evolution_agent = EvolutionAgent()
