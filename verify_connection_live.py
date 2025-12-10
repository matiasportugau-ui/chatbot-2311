from dotenv import load_dotenv
import os
from factura_express import get_token, obtener_productos

# Load environment variables from .env file
load_dotenv()

print("Testing FacturaExpress Connection...")

try:
    print("1. Acquiring Token...")
    token = get_token()
    print(f"SUCCESS: Token acquired: {token[:15]}...")

    print("2. Fetching Products (Deposito 1, Lista 1, Limit 5)...")
    # Using defaults 1 for testing as requested in prompt "ver que deposito y lista de precio quieren utilizar"
    # We will try with 1 and catch if it fails, or just list.
    products = obtener_productos(token, id_deposito=1, id_lista_precio=1, desde=0, hasta=5)
    print(f"SUCCESS: Retrieved {len(products)} products.")
    for p in products:
       print(f" - {p.get('descripcion', 'No description')} (ID: {p.get('idProducto')})")

except Exception as e:
    print(f"FAILURE: {e}")
