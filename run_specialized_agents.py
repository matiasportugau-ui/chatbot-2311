#!/usr/bin/env python3
"""
Specialized Agents Runner
=========================
Executes the specific BMC agents:
1. Sales Learning Agent (trains from Google Sheets + ODS)
2. Quotation Generator Agent (creates new ODS quotes)
"""

import os
import sys
import json
import shutil
import glob
from datetime import datetime
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Configuration
COTIBASE_DIR = ".agent/cotibase"
GENERATED_DIR = "Dropbox_AI_Mirror"
PROMPTS = {
    "learner": "bmc_sales_learning_agent_prompt.md",
    "generator": "bmc_quotation_generator_agent_prompt.md"
}

class BaseAgent:
    def __init__(self, role: str):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.role = role
        self.system_prompt = self._load_prompt(role)

    def _load_prompt(self, role: str) -> str:
        filename = PROMPTS.get(role)
        if not filename or not os.path.exists(filename):
            print(f"⚠️ Warning: Prompt file {filename} not found.")
            return "You are a helpful assistant."
        with open(filename, "r") as f:
            return f.read()

    def query(self, user_input: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

class SalesLearningAgent(BaseAgent):
    def __init__(self):
        super().__init__("learner")

# ... (Imports)
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ... (Previous code)

class GoogleSheetsClient:
    def __init__(self):
        self.sheet_id = os.getenv("GOOGLE_SHEET_ID")
        self.email = os.getenv("GOOGLE_SERVICE_ACCOUNT_EMAIL")
        self.private_key = os.getenv("GOOGLE_PRIVATE_KEY", "").replace('\\n', '\n')
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']

        if not all([self.sheet_id, self.email, self.private_key]):
             print("⚠️ Missing Google Sheets credentials in .env")
             self.service = None
        else:
            self.credentials = service_account.Credentials.from_service_account_info(
                {
                    "client_email": self.email,
                    "private_key": self.private_key,
                    "token_uri": "https://oauth2.googleapis.com/token",
                },
                scopes=self.scopes
            )
            self.service = build('sheets', 'v4', credentials=self.credentials)

    def fetch_full_data(self, tab_name="Enviados", range_name="A:M"):
        """
        Fetches full row data including indices.
        Returns: List[Dict] with keys like 'RowIdx', 'Estado', 'Consulta', etc.
        """
        if not self.service:
            return []
            
        try:
            # 1. Find correct tab
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            real_tab_name = None
            for s in sheets:
                title = s.get("properties", {}).get("title", "")
                if title.strip() == tab_name.strip():
                    real_tab_name = title
                    break
            
            if not real_tab_name:
                print(f"❌ Tab '{tab_name}' not found.")
                return []
            
            self.last_tab_name = real_tab_name # Store for updates

            # 2. Fetch data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id, 
                range=f"'{real_tab_name}'!{range_name}"
            ).execute()
            rows = result.get('values', [])
            
            if not rows:
                return []
            
            # 3. Find Headers
            header_row_idx = -1
            headers = []
            for i, row in enumerate(rows[:5]):
                row_lower = [str(c).lower().strip() for c in row]
                if "consulta" in row_lower: # Less strict check
                    header_row_idx = i
                    headers = row_lower
                    break
            
            if header_row_idx == -1:
                print("❌ Could not find header row.")
                return []
                
            data = []
            for i, row in enumerate(rows[header_row_idx+1:], start=header_row_idx+2): # 1-based index for Sheets
                item = {"RowIdx": i}
                # Map columns by index
                for h_idx, header in enumerate(headers):
                    if h_idx < len(row):
                        item[header] = row[h_idx]
                    else:
                        item[header] = ""
                data.append(item)
                
            return data

        except Exception as e:
            print(f"Error fetching full data: {e}")
            return []

    def update_cell(self, row_idx: int, col_letter: str, value: str):
        """Updates a specific cell."""
        if not self.service or not hasattr(self, 'last_tab_name'):
            print("⚠️ Service or tab name not available for update.")
            return False
            
        try:
            range_name = f"'{self.last_tab_name}'!{col_letter}{row_idx}"
            body = {'values': [[value]]}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            print(f"✅ Updated {range_name} -> {value}")
            return True
        except Exception as e:
            print(f"Error updating cell: {e}")
            return False

    def fetch_training_data(self, tab_name="Enviados", range_name="A:M"):
        """Legacy wrapper mainly for backward compatibility"""
        full_data = self.fetch_full_data(tab_name, range_name)
        pairs = []
        for x in full_data:
            # Map robust keys
            consulta = next((v for k,v in x.items() if 'consulta' in k), "")
            precio = next((v for k,v in x.items() if 'precio' in k or 'monto' in k or 'total' in k), "")
            arg = next((v for k,v in x.items() if 'arg' in k or 'asig' in k), "")
            
            if consulta:
                 pairs.append({"Arg": arg, "Consulta": consulta, "Precio": precio})
        return pairs

class SalesLearningAgent(BaseAgent):
    def __init__(self):
        super().__init__("learner")
        self.sheets_client = GoogleSheetsClient()

    def run_training_batch(self, input_source: str = "sheet"):
        """
        Analyzes data to learn sales patterns.
        input_source: 'sheet' (default) or raw CSV string
        """
        print(f"🧠 {self.role}: Starting Training Session...")
        
        data_pairs = []
        if input_source == "sheet":
            print("📊 Fetching data from Google Sheets ('Enviados')...")
            data_pairs = self.sheets_client.fetch_training_data()
        else:
            # Fallback/Manual input
            data_pairs = [{"Manual Input": input_source}]
            
        if not data_pairs:
            print("⚠️ No training data available.")
            return

        print(f"✅ Found {len(data_pairs)} valid training examples.")
        
        # Batch process to respect token limits (e.g., 5 at a time)
        batch_size = 5
        batches = [data_pairs[i:i + batch_size] for i in range(0, len(data_pairs), batch_size)]
        
        all_rules = []
        
        print(f"🔄 Processing {len(batches)} batches...")
        for i, batch in enumerate(batches):
            print(f"   Batch {i+1}/{len(batches)}...")
            
            # Format batch for LLM
            batch_text = "\n".join([f"- ID: {x.get('Arg')}\n  Input: {x.get('Consulta')}\n  Output: {x.get('Precio')}" for x in batch])
            
            prompt = (
                f"Analyze these specific examples mapping user requests to sales quotes:\n"
                f"{batch_text}\n\n"
                "Extract specific logic rules, patterns, or 'magic numbers' used by sales agents.\n"
                "Return them as a concise list of text rules."
            )
            
            analysis = self.query(prompt)
            all_rules.append(analysis)
        
        # Final Synthesis
        print("\n🧠 Synthesizing Final Training Rules...")
        final_prompt = (
            "Here are observations from multiple batches of sales data. "
            "Synthesize them into a single, cohesive 'Sales Logic' document.\n\n"
            + "\n---\n".join(all_rules)
        )
        final_logic = self.query(final_prompt)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        output_file = f"Sales_Logic_Training_{timestamp}.md"
        
        with open(output_file, "w") as f:
            f.write(final_logic)
            
        print(f"✅ Training Complete. Rules saved to: {output_file}")
        print("-----------------------")


class QuotationGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("generator")

    def generate_quote(self, request: str):
        print(f"⚡ {self.role}: Processing Request: '{request}'")
        
        # 1. Ask LLM to select template and extract data
        # We ask for a structured JSON response to automate the file copy
        templates_list = self._list_templates()
        instruction = (
            f"User Request: '{request}'.\n"
            f"Available Templates:\n{templates_list}\n"
            "Output JSON with keys: 'selected_template_path', 'new_filename_suffix', 'reasoning'.\n"
            "NOTE: 'selected_template_path' must be one of the paths provided in the list."
        )
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": instruction}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        try:
            data = json.loads(response.choices[0].message.content)
            template_path = data.get('selected_template_path')
            # 'new_filename_suffix' isn't fully used, we enforce the AI suffix logic ourselves
            reasoning = data.get('reasoning')
            
            print(f"Thinking: {reasoning}")
            
            if template_path:
                return self._execute_file_copy(template_path)
            else:
                print("❌ Could not determine template path.")
                return None
                
        except json.JSONDecodeError:
            print("❌ Failed to parse agent JSON response.")
            print(response.choices[0].message.content)
            return None

    def _list_templates(self) -> str:
        """Recursively list all .ods files in COTIBASE_DIR"""
        if not os.path.exists(COTIBASE_DIR):
            return "No templates found (directory missing)."
            
        file_list = []
        for root, dirs, files in os.walk(COTIBASE_DIR):
            for file in files:
                if file.endswith(".ods"):
                    # relative path from COTIBASE_DIR
                    rel_path = os.path.relpath(os.path.join(root, file), COTIBASE_DIR)
                    file_list.append(rel_path)
        
        return "\n".join(file_list[0:50]) # Limit to 50 for context window safety if too many

    def _execute_file_copy(self, template_rel_path: str) -> Optional[str]:
        """
        Mirrors the directory structure:
        Src: .agent/cotibase/Folder/File.ods
        Dst: Dropbox_AI_Mirror/Folder AI/File AI.ods
        Returns: Absolute path of new file or None
        """
        src_full_path = os.path.join(COTIBASE_DIR, template_rel_path)
        
        if not os.path.exists(src_full_path):
            print(f"❌ Template file not found: {src_full_path}")
            return None

        # Deconstruct path to rebuild with " AI" suffixes
        # template_rel_path might be "SubFolder/File.ods" or just "File.ods"
        path_parts = template_rel_path.split(os.sep)
        
        new_path_parts = []
        for i, part in enumerate(path_parts):
            if i == len(path_parts) - 1:
                # File: Append " AI" before extension
                name, ext = os.path.splitext(part)
                new_path_parts.append(f"{name} AI{ext}")
            else:
                # Directory: Append " AI"
                new_path_parts.append(f"{part} AI")
        
        dst_rel_path = os.path.join(*new_path_parts)
        dst_full_path = os.path.join(GENERATED_DIR, dst_rel_path)
        
        # Ensure output dir exists
        os.makedirs(os.path.dirname(dst_full_path), exist_ok=True)
        
        shutil.copy(src_full_path, dst_full_path)
        print(f"✅ Created File: {dst_full_path}")
        print(f"ℹ️  Next Step: Open {dst_full_path} and fill in the customer data.")
        
        # Check for PDF tools
        if shutil.which("soffice"):
            print("ℹ️  'soffice' found. You can export to PDF using: soffice --convert-to pdf ...")
        else:
            print("⚠️  'soffice' NOT found. Please export to PDF manually from LibreOffice/Excel.")
            
        return dst_full_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_specialized_agents.py [learn|generate] [input]")
        sys.exit(1)
        
    mode = sys.argv[1]
    input_data = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    
    if mode == "learn":
        agent = SalesLearningAgent()
        # If user passes "sheet" (or nothing), use sheets. Else use manual input.
        if not input_data or input_data == "sheet":
            agent.run_training_batch(input_source="sheet")
        else:
            agent.run_training_batch(input_source=input_data)
        
    elif mode == "generate":
        agent = QuotationGeneratorAgent()
        if not input_data:
            input_data = "Cliente: Maria, Necesito cotizar un techo isodec de 50mm para 30 metros cuadrados"
        agent.generate_quote(input_data)
        
    else:
        print(f"Unknown mode: {mode}")

if __name__ == "__main__":
    main()
