from dotenv import load_dotenv
import os
import sys
from factura_express import get_token, obtener_productos

# Explicitly load .env
load_dotenv()

print("--- FacturaExpress Verification Script ---")
print(f"Env Loaded: {os.path.exists('.env')}")
print(f"Emitter ID: {os.getenv('FE_EMISOR_ID')}")

try:
    print("\n1. Testing Authentication...")
    token = get_token()
    print(f"SUCCESS: Token obtained: {token[:20]}...")
    
    print("\n2. Testing Product Retrieval...")
    # Using small range
    products = obtener_productos(token, id_deposito=1, id_lista_precio=1, desde=0, hasta=5)
    print(f"SUCCESS: Retrieved {len(products)} products.")
    for p in products:
        print(f" - {p.get('descripcion', 'N/A')} (ID: {p.get('idProducto')})")
        
except Exception as e:
    print(f"\nFAILURE: {e}")
    print("Please check your credentials in .env and ensure your IP is whitelisted if applicable.")
    sys.exit(1)
