#!/usr/bin/env python3
"""
Full Sales Training Cycle
=========================
1. Fetches real historic quote requests from Google Sheets.
2. Runs the AI Agent to generate quotes for those same requests.
3. Compares the AI's output with the real human quote.
4. Generates a training report with lessons learned.
"""

import sys
import os
import datetime
import re
from typing import List, Dict, Any

# Ensure we can import properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run_specialized_agents import SalesLearningAgent, BaseAgent
from ia_conversacional_integrada import IAConversacionalIntegrada

def extract_price(text: str) -> float:
    """Extracts the first major price number from text."""
    # Look for patterns like $150, 150 USD, 150.00
    # Simplified regex for demo purposes
    matches = re.findall(r'\$?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', text)
    if not matches:
        return 0.0
    
    # Take the largest number found that looks like a total price? 
    # Or just the first one? Let's take the first one usually.
    try:
        # Normalize: remove dots if they are thousands separators, replace comma with dot
        val_str = matches[0].replace(',', '.')
        return float(val_str)
    except:
        return 0.0

class FullCycleTrainer(BaseAgent):
    def __init__(self):
        super().__init__("learner") # Use learner role for analysis
        self.sales_agent = SalesLearningAgent()
        self.ia = IAConversacionalIntegrada()
        self.ia.use_ai = True # Ensure AI is on for simulation

    def run_cycle(self, max_items=10):
        print("🚀 Starting Advanced Training Cycle...")
        
        # 1. Fetch Data
        print("📊 Fetching full historical data...")
        data = self.sales_agent.sheets_client.fetch_full_data()
        
        if not data:
            print("❌ No data found to train on.")
            return
            
        # Filter for 'Enviado' (ignoring case/whitespace)
        enviados = [
            row for row in data 
            if "enviado" in str(row.get('estado', '')).lower() 
            or "enviado" in str(row.get('Enviado', '')).lower()
        ]

        print(f"✅ Loaded {len(data)} rows. Found {len(enviados)} 'Enviado' items. Processing top {max_items}...")
        
        from run_specialized_agents import QuotationGeneratorAgent
        pdf_generator = QuotationGeneratorAgent()
        
        results = []
        
        for i, item in enumerate(enviados[:max_items]):
            # Robust key retrieval
            def get_val(keys_list):
                for k in keys_list:
                    val = next((v for key,v in item.items() if k in key.lower()), None)
                    if val is not None: return val
                return ""

            arg_id = get_val(['arg', 'asig'])
            consulta = get_val(['consulta'])
            real_price = get_val(['precio', 'monto', 'total'])
            
            # Context fields
            cliente_nombre = get_val(['cliente'])
            telefono = get_val(['telefono'])
            fecha = get_val(['fecha'])
            
            row_idx = item.get('RowIdx')
            
            print(f"\nExample {i+1}: [{arg_id}] Row {row_idx}")
            print(f"User: {cliente_nombre} ({telefono}) - '{consulta[:50]}...'")
            
            # 2. Simulate AI
            session_id = f"train_{arg_id}_{datetime.datetime.now().timestamp()}"
            client_id = telefono if telefono else "099123456"
            
            try:
                # We prepend context to the message to help the AI (simulating past messages or context injection)
                # But here we just pass the query. The AI should ask for details if missing.
                # However, for 'Enviado' quotes, the user probably already gave details.
                response = self.ia.procesar_mensaje(consulta, client_id, session_id)
                ai_response_text = response.mensaje
                
                # Check if AI gathered enough info to quote (internally state would be 'cotizacion_completada' or similar)
                # For this simulation, we force the Generator if AI response looks promising or just always try?
                # User asked to "leave the quote link". 
                
                # Let's generate a quote file based on the SIMULATED AI knowledge + Inquiry
                # We use the QuotationGeneratorAgent
                # We construct a prompt for it based on the row data
                
                gen_request = f"Cliente: {cliente_nombre}, Telefono: {telefono}, Consulta: {consulta}"
                # We capture the output of generate_quote via stdout capture? Or modifying the agent?
                # The agent prints the path. Let's make it return the path.
                # We need to modify QuotationGeneratorAgent to return path. 
                # For now, let's assume we can't modify it easily without breaking other things, 
                # so we will use a workaround or just update it quickly in next step.
                # Actually, let's just instantiate it and use internal methods or better yet,
                # UPDATE QuotationGeneratorAgent to return path first? 
                # Strategy: I'll assume I update QuotationGeneratorAgent in next step or use a wrapper.
                # Let's assume it returns the path now (I will update it).
                
                quote_path = pdf_generator.generate_quote(gen_request) 
                
            except Exception as e:
                ai_response_text = f"Error: {e}"
                quote_path = None
                
            print(f"AI Quote Text: {ai_response_text[:100]}...")
            if quote_path:
                print(f"AI File: {quote_path}")
                # Write to Column I (Index 8 -> 'I')
                self.sales_agent.sheets_client.update_cell(row_idx, 'I', quote_path)
            
            # 3. Compare
            comparison = {
                "id": arg_id,
                "input": consulta,
                "human_output": real_price,
                "ai_output": ai_response_text,
                "human_val": extract_price(real_price),
                "ai_val": extract_price(ai_response_text)
            }
            results.append(comparison)
            
        # 4. Analyze & Report
        self._generate_report(results)

    def _generate_report(self, results: List[Dict]):
        print("\n🧠 Analyzing results and generating report...")
        
        # Prepare content for LLM analysis
        analysis_prompt = (
            "Analyze the performance of an AI Sales Agent vs a Human Agent.\n"
            "Below are paired examples. Identify why the AI might have quoted differently.\n\n"
        )
        
        for res in results:
            diff = abs(res['human_val'] - res['ai_val'])
            analysis_prompt += (
                f"--- Request ID: {res['id']} ---\n"
                f"Customer: {res['input']}\n"
                f"Human Quote: {res['human_output']}\n"
                f"AI Quote: {res['ai_output']}\n"
                f"Price Diff Approx: {diff}\n\n"
            )
            
        analysis_prompt += (
            "\nProduce a 'Training Report' in Markdown.\n"
            "1. Summary of accuracy.\n"
            "2. Key discrepancies (e.g. AI missed installation cost, or used wrong base price).\n"
            "3. Actionable knowledge updates (Rules to add to the system)."
        )
        
        report_content = self.query(analysis_prompt)
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"TRAINING_REPORT_{timestamp}.md"
        
        with open(filename, "w") as f:
            f.write(report_content)
            
        print(f"✅ Report generated: {filename}")
        print("Please review the report to identify necessary knowledge base updates.")

def main():
    trainer = FullCycleTrainer()
    trainer.run_cycle(max_items=5) # Start small

if __name__ == "__main__":
    main()
