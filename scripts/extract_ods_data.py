import os
import pandas as pd
import json
import re

BASE_DIR = '/Users/matias/chatbot-2311/.agent/cotibase'
OUTPUT_FILE = '/Users/matias/chatbot-2311/scripts/extracted_products.json'

def clean_price(value):
    if pd.isna(value): return None
    if isinstance(value, (int, float)): return float(value)
    # Remove currency symbols and non-numeric chars except dot
    clean = re.sub(r'[^\d.]', '', str(value))
    try:
        return float(clean)
    except:
        return None

def clean_thickness(text):
    if not isinstance(text, str): return None
    match = re.search(r'(\d+)\s*mm', text, re.IGNORECASE)
    if match:
        return f"{match.group(1)}mm"
    return None

def extract_from_file(filepath):
    filename = os.path.basename(filepath)
    product_slug = filename.lower().replace('cotización', '').replace('base', '').replace('.ods', '').strip().replace(' ', '_').replace('-', '_')
    
    extracted_data = {
        "source_file": filename,
        "slug": product_slug,
        "products": []
    }
    
    try:
        xls = pd.ExcelFile(filepath, engine='odf')
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            
            # Find the header row (usually contains "Producto" or "Costo")
            header_row_idx = -1
            for i in range(min(20, len(df))):
                row_str = df.iloc[i].astype(str).str.lower().tolist()
                if any('producto' in s for s in row_str) and any('costo' in s for s in row_str):
                    header_row_idx = i
                    break
            
            if header_row_idx != -1:
                # Reload with correct header
                df = pd.read_excel(xls, sheet_name=sheet_name, header=header_row_idx)
                
                # Try to find "Ancho Util" in the raw dataframe (before header slicing) or in the footer
                # Re-read without header to scan for metadata
                df_raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                ancho_util = None
                
                # Scan first 100 rows for "Ancho Util"
                for r_idx in range(min(100, len(df_raw))):
                    row_data = df_raw.iloc[r_idx].astype(str).str.lower().tolist()
                    row_text = " ".join(row_data)
                    
                    if 'ancho' in row_text and ('util' in row_text or 'útil' in row_text or 'útil' in row_text):
                        # Try to extract number from this row
                        # Look for number in any cell of this row matches 0.5 - 1.5 range usually
                        for cell in row_data:
                            # Clean string to find number
                            try:
                                # regex for number like 1.12 or 1,12
                                match = re.search(r'(\d+[.,]\d+)', cell)
                                if match:
                                    val = float(match.group(1).replace(',', '.'))
                                    if 0.5 <= val <= 2.0: # Plausible width in meters
                                        ancho_util = val
                                        break
                                    elif 500 <= val <= 1300: # Plausible width in mm
                                         ancho_util = val / 1000
                                         break
                            except: continue
                    if ancho_util: break
                
                if not ancho_util:
                     # Check columns if one is named "Ancho"
                     pass 
                
                # Identify columns - map lowercase to original
                cols_map = {str(c).lower().strip(): c for c in df.columns}
                # print(f"DEBUG: Found columns in {filename} sheet {sheet_name}: {list(cols_map.keys())}")
                
                prod_col_lower = next((c for c in cols_map.keys() if 'producto' in c), None)
                price_col_m2_lower = next((c for c in cols_map.keys() if 'costo m2' in c or 'precio m2' in c), None)
                price_col_unit_lower = next((c for c in cols_map.keys() if 'costo unit' in c or 'precio unit' in c), None)
                
                if prod_col_lower and (price_col_m2_lower or price_col_unit_lower):
                    prod_col = cols_map[prod_col_lower]
                    # print(f"DEBUG: Selected prod_col: '{prod_col}'")
                    
                    for idx, row in df.iterrows():
                        try:
                            prod_name = row[prod_col]
                        except KeyError:
                             print(f"DEBUG ERROR: KeyError accessing '{prod_col}' in {filename} sheet {sheet_name}. Available keys: {list(row.index)}")
                             break

                        if pd.notna(prod_name) and isinstance(prod_name, str) and len(prod_name) > 3:
                            
                            price = 0
                            unit = 'unidad'
                            
                            try:
                                if price_col_m2_lower and pd.notna(row[cols_map[price_col_m2_lower]]):
                                    price = clean_price(row[cols_map[price_col_m2_lower]])
                                    unit = 'm2'
                                elif price_col_unit_lower and pd.notna(row[cols_map[price_col_unit_lower]]):
                                    price = clean_price(row[cols_map[price_col_unit_lower]])
                                    unit = 'unidad'
                            except Exception as e:
                                print(f"DEBUG ERROR processing row {idx}: {e}")
                                continue
                            
                            if price and price > 0:
                                extracted_data["products"].append({
                                    "sheet": sheet_name,
                                    "name": prod_name.strip(),
                                    "details": prod_name.strip(),
                                    "price": price,
                                    "unit": unit,
                                    "thickness": clean_thickness(prod_name) or clean_thickness(sheet_name),
                                    "width": ancho_util 
                                })

    except Exception as e:
        print(f"Error processing {filename}: {e}")
        
    return extracted_data

def main():
    print(f"📂 Scanning {BASE_DIR}...")
    files = [f for f in os.listdir(BASE_DIR) if f.endswith('.ods')]
    files.sort()
    
    all_products = []
    
    print(f"🔍 Found {len(files)} files. Extracting data...")
    
    for i, f in enumerate(files):
        # Skip experimental calculator
        if "Experimental" in f: continue
        
        print(f"[{i+1}/{len(files)}] {f}")
        filepath = os.path.join(BASE_DIR, f)
        data = extract_from_file(filepath)
        if data["products"]:
            all_products.append(data)
            
    # Post-processing to group by product type similar to knowledge-base structure
    structured_output = {}
    
    for item in all_products:
        # Heuristic to group similar products
        base_name = item['slug'].split('_')[0] 
        if "isodec" in item['slug']: base_name = 'isodec'
        if "isopanel" in item['slug']: base_name = 'isopanel'
        if "montfrio" in item['slug']: base_name = 'montfrio'
        if "teja" in item['slug']: base_name = 'teja'
        
        if base_name not in structured_output:
            structured_output[base_name] = {
                "nombre": base_name.capitalize().replace('_', ' '),
                "unidad": "m2", # Default, check most frequent
                "variantes": []
            }
        
        for p in item['products']:
            structured_output[base_name]["variantes"].append({
                "source": item['source_file'],
                "name": p['name'],
                "price": p['price'],
                "thickness": p['thickness'],
                "unit": p['unit'],
                "width": p.get('width')
            })

    print("📝 Saving JSON...")
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(structured_output, f, indent=2, ensure_ascii=False)
            
    print(f"✅ Extraction complete: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
