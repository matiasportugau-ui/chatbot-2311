import os
import hashlib
import requests
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    # If the stored value is not a SHA-256 hash, hash it now
    if len(password_hash) != 64 or not all(c in "0123456789abcdef" for c in password_hash.lower()):
        logger.info("Password appears to be plain text; hashing with SHA-256.")
        password_hash = hashlib.sha256(password_hash.encode("utf-8")).hexdigest()
    if not all([emitter_id, username, password_hash]):
        raise EnvironmentError("Missing FacturaExpress credentials in environment variables.")
    
    payload = {"idEmisor": emitter_id, "usuario": username, "clave": password_hash}
    
    # Optional: Log attempt (masking sensitive data)
    logger.info(f"Authenticating to FacturaExpress (Emisor: {emitter_id}, User: {username})")

    last_error = None

    # Attempt 1: JSON login
    try:
        logger.info("Attempting login with JSON payload...")
        headers = {"Accept": "application/json"}
        resp = requests.post(f"{API_BASE}login", json=payload, headers=headers, timeout=10)
        logger.info(f"JSON login response status: {resp.status_code}")
        resp.raise_for_status()
        try:
            data = resp.json()
            token = data.get("token")
            if token:
                logger.info("Successfully obtained token via JSON login.")
                return token
            else:
                logger.warning("JSON login successful, but token not found in response. Trying form-encoded.")
                last_error = RuntimeError("Token not found in JSON response.")
        except Exception as e:
            logger.warning(f"Failed to parse JSON from JSON login response: {e}. Body: '{resp.text}'. Trying form-encoded.")
            last_error = RuntimeError(f"Invalid JSON response from JSON login: {e}")
    except Exception as e:
        logger.warning(f"JSON login failed: {e}. Trying form-encoded login.")
        last_error = e

    # Attempt 2: Form-encoded login
    try:
        logger.info("Attempting login with form-encoded payload...")
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        resp = requests.post(f"{API_BASE}login", data=payload, headers=headers, timeout=10)
        logger.info(f"Form-encoded login response status: {resp.status_code}")
        resp.raise_for_status()
        try:
            data = resp.json()
            token = data.get("token")
            if token:
                logger.info("Successfully obtained token via form-encoded login.")
                return token
            else:
                logger.error("Form-encoded login successful, but token not found in response.")
                raise RuntimeError("Token not found in response after form-encoded attempt.")
        except Exception as e:
            logger.error(f"Failed to parse JSON from form-encoded login response: {e}. Body: '{resp.text}'")
            raise RuntimeError(f"Invalid JSON response from form-encoded login: {e}")
    except Exception as e:
        logger.error(f"Form-encoded login also failed: {e}")
        if last_error:
            raise RuntimeError(f"All login attempts failed. JSON attempt error: {last_error}; Form-encoded attempt error: {e}")
        else:
            raise RuntimeError(f"All login attempts failed. Form-encoded attempt error: {e}")

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
    
    try:
        resp = requests.get(f"{API_BASE}obtenerProductos", headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json().get("productos", [])
    except Exception as e:
        logger.error(f"Error yielding products: {e}")
        raise
