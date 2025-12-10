import os
import re
import json
import difflib
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None
    Credentials = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuoteMatcher")

# Configuration
DATA_DIR = Path("data/quotes")
SHEET_ID = "1-c834pOUNnUWn7Q-Bc4kDHJGCQo0LKI05dXaLgqcXgI" # Updated Sheet ID
SHEET_NAME = "Admin."

class QuoteMatcher:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.quotes_index = []
        self.sheet_client = None
        self.sheet = None

    def index_local_files(self):
        """
        Scans DATA_DIR recursively to build an index of available quotes.
        Parses filenames to extract: Date, Client, Context.
        Expected format example: "Cotización 08032022 Margarita Econopanel 0,40mm ML.ods"
        """
        logger.info(f"Indexing files in {DATA_DIR}...")
        
        # Regex to capture Date (DDMMYYYY) and the rest of the filename
        # Pattern: "Cotizaci" + wildcard + "n" + space + Date + space + Rest
        # This handles "Cotización", "Cotizacion", "Cotización" (decomposed), etc.
        pattern = re.compile(r"Cotizaci.*n\s+(\d{8})\s+(.*)\.(ods|pdf|xlsx|xls)", re.IGNORECASE)

        for path in DATA_DIR.rglob("*"):
            if path.is_file() and not path.name.startswith('.'):
                # Normalized name for regex (optional, but regex with .* is effective enough usually)
                match = pattern.search(path.name)
                if match:
                    date_str = match.group(1)
                    rest_str = match.group(2)
                    
                    # Try to parse date
                    try:
                        date_obj = datetime.strptime(date_str, "%d%m%Y")
                        date_formatted = date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        date_formatted = date_str

                    # Heuristic to separate Client Name from Details
                    # Usually: "Client Name" + "Product Info"
                    # We'll just keep the full 'rest_str' as 'raw_details' for fuzzy matching
                    # and try to extract the first 2-3 words as possible name
                    
                    self.quotes_index.append({
                        "path": str(path),
                        "filename": path.name,
                        "date": date_formatted,
                        "raw_info": rest_str, # Contains Client + Product
                        "ext": match.group(3)
                    })
        
        logger.info(f"Indexed {len(self.quotes_index)} quote files.")

    def connect_sheets(self):
        """
        Connects to Google Sheets using simulated or real credentials.
        """
        if not gspread:
            logger.error("gspread library not installed.")
            return False

        try:
            # Try to load credentials from environment or file
            # This logic mirrors integracion_google_sheets.py
            # For this script, we assume we might need to rely on env vars or local file
            
            # TODO: Add specific credential loading if needed. 
            # For now, we will try to find a nice way to get the client.
            # If running locally, maybe the user has a 'credentials.json'
            
            creds_file = 'credentials.json' # Placeholder
            if os.path.exists(creds_file):
                 scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                 creds = Credentials.from_service_account_file(creds_file, scopes=scope)
                 self.sheet_client = gspread.authorize(creds)
                 self.sheet = self.sheet_client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
                 logger.info("Connected to Google Sheet.")
                 return True
            else:
                 logger.warning("No credentials.json found. Cannot connect to real sheet.")
                 return False

        except Exception as e:
            import traceback
            logger.error(f"Failed to connect to sheets: {e}")
            logger.error(traceback.format_exc())
            return False

    def find_best_match(self, client_name: str, target_date: Optional[str] = None) -> Optional[Dict]:
        """
        Finds the best matching quote file for a given client name (and optionally date).
        """
        if not client_name:
            return None
        
        best_ratio = 0.0
        best_match = None

        # Clean client name
        client_name_clean = client_name.lower().strip()

        for quote in self.quotes_index:
            # Check date match if provided (e.g., same month/year or exact)
            # This step can be strict or loose. For now, loose.
            
            # Match Name in 'raw_info'
            # We look for the client name inside the filename's info part
            info_lower = quote['raw_info'].lower()
            
            # Simple substring check first
            if client_name_clean in info_lower:
                ratio = 1.0 # Exact substring match
            else:
                # Fuzzy match
                ratio = difflib.SequenceMatcher(None, client_name_clean, info_lower).ratio()
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = quote

        # Threshold for accepting a match
        if best_ratio > 0.4:  # Adjust threshold as needed
            return best_match
        
        return None

    def run(self):
        self.index_local_files()
        
        connected = self.connect_sheets()
        
        if not connected:
            logger.info("Running with MOCK data as sheet connection failed.")
            sheet_rows = [
                {"Arg": "1", "Cliente": "Margarita", "Fecha": "08-03", "Consulta": "", "Estado": "Pendiente"},
                {"Arg": "2", "Cliente": "Julian Tol", "Fecha": "15-03", "Consulta": "Pendiente de cotizar", "Estado": "Pendiente"},
                {"Arg": "3", "Cliente": "Jorge Piriz", "Fecha": "26-03", "Consulta": "", "Estado": "Pendiente"},
            ]
        else:
            # get_all_records fails if there are duplicate or empty headers
            # We use get_all_values and manually construct dictionaries
            all_values = self.sheet.get_all_values()
            if not all_values:
                logger.warning("Sheet is empty.")
                sheet_rows = []
            else:
                # Automatic header detection
                header_row_index = 0
                for i, row in enumerate(all_values):
                    # Check if any cell matches "Cliente" (fuzzy or stripped)
                    if any("cliente" in str(cell).lower() for cell in row):
                        header_row_index = i
                        break
                
                headers = [str(h).strip() for h in all_values[header_row_index]]
                logger.info(f"Using Header Row {header_row_index} found with 'Cliente' column.")

                sheet_rows = []
                for row_idx, row in enumerate(all_values[header_row_index+1:]):
                    # row is a list of strings
                    row_dict = {}
                    for col_idx, cell_value in enumerate(row):
                        if col_idx < len(headers):
                            header = headers[col_idx].strip()
                            if header: # Only map if header is not empty
                                row_dict[header] = cell_value
                    
                    # Store row index (1-based, starting after header) -> actual sheet row is row_idx + 2
                    row_dict['_row_index'] = row_idx + 2 
                    sheet_rows.append(row_dict)

        logger.info(f"Processing {len(sheet_rows)} rows from Sheet...")

        matches_found = 0
        for i, row in enumerate(sheet_rows):
            client = row.get("Cliente", "")
            # Phone could be useful too if it's in the filename, but currently only seeing Names
            
            if not client:
                continue
                
            match = self.find_best_match(client)
            
            if match:
                matches_found += 1
                logger.info(f"MATCH FOUND: Client '{client}' -> File '{match['filename']}'")
                
                new_consulta = f"MATCHED: {match['filename']} ({match['date']})"
                
                if self.dry_run:
                    logger.info(f"  [DRY RUN] Would update row {i+2} 'Consulta' to: {new_consulta}")
                else:
                    if connected:
                        # Update the cell. 'Consulta' column index needs to be found or hardcoded
                        # Assuming 'Consulta' is column H (8) based on previous files, but safer to find it
                        # For now, just logging the intent
                        try:
                            # self.sheet.update_cell(i+2, col_index, new_consulta)
                            pass 
                        except Exception as e:
                            logger.error(f"Error updating sheet: {e}")

        logger.info(f"Total matches found: {matches_found}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Match Dropbox Quotes to Google Sheets")
    parser.add_argument("--live", action="store_true", help="Perform actual updates to Google Sheet")
    args = parser.parse_args()

    matcher = QuoteMatcher(dry_run=not args.live)
    matcher.run()
