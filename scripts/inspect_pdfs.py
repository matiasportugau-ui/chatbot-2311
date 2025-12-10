import pdfplumber
import os
import re

PDF_DIR = '.agent/pdf_productos'

def search_width(text):
    text = text.lower()
    matches = []
    
    # 1. Explicit Ancho Util patterns
    # Matches: ancho util: 1000mm, ancho util 1.12m, ancho útil 1120 mm
    regex_explicit = r'ancho\s*(?:ú|ú|u)til[:\s]*(\d+(?:[.,]\d+)?)\s*(mm|cm|m)?'
    
    found = re.findall(regex_explicit, text)
    for f in found:
        matches.append(f"Explicit: {f[0]}{f[1] if f[1] else ''}")

    # 2. Look for common widths 1.12, 1000, 1150 in context of "ancho"
    # Matches: ancho ... 1.12, ancho ... 1000
    # User mentioned "1.12 ej."
    regex_implicit = r'ancho.*?(\d+(?:[.,]\d+)?)\s*(mm|cm|m|mts)'
    
    # Search line by line for better context
    lines = text.split('\n')
    for line in lines:
        if 'ancho' in line:
            # Look for numbers in this line
            nums = re.findall(r'(\d+(?:[.,]\d+)?)', line)
            for n in nums:
                # filter plausible widths: 0.8-1.5m, 800-1200mm
                try:
                    val = float(n.replace(',', '.'))
                    if (0.5 <= val <= 2.0) or (500 <= val <= 1300):
                         matches.append(f"Context: {line.strip()} -> {val}")
                except: pass

    return list(set(matches))

def main():
    print(f"🔍 Searching for 'Ancho Útil' in PDFs under {PDF_DIR}...")
    
    count = 0
    for root, dirs, files in os.walk(PDF_DIR):
        for file in files:
            if file.lower().endswith('.pdf'):
                path = os.path.join(root, file)
                try:
                    with pdfplumber.open(path) as pdf:
                        text = ""
                        for page in pdf.pages:
                            text += page.extract_text() or ""
                        
                        widths = search_width(text)
                        if widths:
                            print(f"\n📄 {file}:")
                            for w in widths:
                                print(f"   found: {w}")
                            count += 1
                except Exception as e:
                    print(f"⚠️ Error reading {file}: {e}")

    print(f"\n✅ Finished. Found potential width info in {count} files.")

if __name__ == "__main__":
    main()
