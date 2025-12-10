import os
import pandas as pd
import json

BASE_DIR = '/Users/matias/chatbot-2311/.agent/cotibase'
OUTPUT_FILE = '/Users/matias/chatbot-2311/.agent/cotibase_analysis_report.md'

def analyze_file(filepath):
    filename = os.path.basename(filepath)
    stat = os.stat(filepath)
    
    analysis = {
        "filename": filename,
        "size_kb": f"{stat.st_size / 1024:.2f} KB",
        "sheets": [],
        "key_terms_found": [],
        "preview": ""
    }
    
    try:
        xls = pd.ExcelFile(filepath, engine='odf')
        analysis["sheets"] = xls.sheet_names
        
        # Analyze first sheet usually containing the quote
        if xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=0, header=None)
            
            # Create a text preview of the top 15 rows, 5 columns
            preview_df = df.iloc[:15, :6].fillna('')
            analysis["preview"] = preview_df.to_string(index=False)
            
            # Search for keywords in the entire dataframe
            text_content = df.astype(str).to_string().upper()
            keywords = ["TOTAL", "PRECIO", "CLIENTE", "FECHA", "DOLAR", "IVA", "SUBTOTAL"]
            found = [k for k in keywords if k in text_content]
            analysis["key_terms_found"] = found
            
    except Exception as e:
        analysis["error"] = str(e)
        
    return analysis

def main():
    print(f"📂 Scanning {BASE_DIR}...")
    files = [f for f in os.listdir(BASE_DIR) if f.endswith('.ods')]
    files.sort()
    
    results = []
    
    print(f"🔍 Found {len(files)} files. Analyzing...")
    
    for i, f in enumerate(files):
        print(f"[{i+1}/{len(files)}] {f}")
        filepath = os.path.join(BASE_DIR, f)
        results.append(analyze_file(filepath))
        
    # Generate Markdown Report
    print("📝 Generating Report...")
    
    with open(OUTPUT_FILE, 'w') as f:
        f.write("# 📊 Análisis de Archivos de Cotización (.agent/cotibase)\n\n")
        f.write(f"**Total Archivos:** {len(results)}\n")
        f.write(f"**Directorio:** `{BASE_DIR}`\n\n")
        f.write("---\n\n")
        
        for res in results:
            f.write(f"## 📄 {res['filename']}\n")
            f.write(f"- **Tamaño:** {res['size_kb']}\n")
            if "error" in res:
                f.write(f"- ❌ **Error:** {res['error']}\n")
            else:
                f.write(f"- **Hojas:** {', '.join(res['sheets'])}\n")
                f.write(f"- **Términos Clave:** {', '.join(res['key_terms_found'])}\n")
                f.write("\n**Vista Previa (Primeras 15 filas):**\n")
                f.write(res['preview'])
                f.write("\n\n")
            f.write("---\n")
            
    print(f"✅ Reporte generado en: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
