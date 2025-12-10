import os
import hashlib
import requests
from typing import List, Dict, Any, Optional

API_BASE = "https://cliente.facturaexpress.com.uy/StockApiRest/v1/"

def _hash_password(password: str) -> str:
    """Hash the plain password using SHA-256 as required by the API."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_token() -> str:
    """Obtain an authentication token from FacturaExpress.
    Reads credentials from environment variables:
        FE_EMISOR_ID, FE_USERNAME, FE_PASSWORD_HASH
    Returns the token string.
    """
    emitter_id = os.getenv("FE_EMISOR_ID")
    username = os.getenv("FE_USERNAME")
    password_hash = os.getenv("FE_PASSWORD_HASH")
    if not all([emitter_id, username, password_hash]):
        raise EnvironmentError("Missing FacturaExpress credentials in environment variables.")
    payload = {"idEmisor": emitter_id, "usuario": username, "clave": password_hash}
    resp = requests.post(f"{API_BASE}login", json=payload)
    if resp.status_code != 200:
        print(f"Error Status: {resp.status_code}")
        print(f"Error Body: {resp.text}")
    resp.raise_for_status()
    try:
        data = resp.json()
    except Exception as e:
        print(f"JSON Decode Error Body: {resp.text}")
        raise e
    token = data.get("token")
    if not token:
        raise RuntimeError("Token not found in response.")
    return token

def obtener_productos(
    token: str,
    id_deposito: int,
    id_lista_precio: int,
    desde: int = 0,
    hasta: int = 2000,
    fecha_modificacion: Optional[str] = None,
    hora_modificacion: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fetch products from the API with pagination.
    Returns a list of product dictionaries.
    """
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "idDeposito": id_deposito,
        "idListaPrecio": id_lista_precio,
        "desde": desde,
        "hasta": hasta,
    }
    if fecha_modificacion:
        params["fechaModificacion"] = fecha_modificacion
    if hora_modificacion:
        params["horaModificacion"] = hora_modificacion
    resp = requests.get(f"{API_BASE}obtenerProductos", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get("productos", [])
