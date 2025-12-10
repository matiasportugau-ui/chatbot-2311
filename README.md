# FacturaExpress Integration

This module provides an interface to the FacturaExpress API for authentication and product retrieval.

## Files
- `factura_express.py`: Core logic for token acquisition and API calls.
- `test_factura_express.py`: Unit tests.

## Installation
Requires `requests`.
```bash
pip install requests
```

## Configuration
Set the following environment variables:
- `FE_EMISOR_ID`
- `FE_USERNAME`
- `FE_PASSWORD_HASH` (SHA-256 hash)

## Usage
```python
from factura_express import get_token, obtener_productos

token = get_token()
products = obtener_productos(token, id_deposito=1, id_lista_precio=1)
```

## Testing
Run unit tests:
```bash
python -m unittest test_factura_express.py
```
