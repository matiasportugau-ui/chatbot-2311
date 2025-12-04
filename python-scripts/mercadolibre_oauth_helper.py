#!/usr/bin/env python3
"""
Asistente interactivo para obtener y refrescar tokens OAuth de Mercado Libre.

Permite:
  • Generar la URL de autorización con los scopes configurados.
  • Intercambiar el `code` por `access_token` + `refresh_token`.
  • Refrescar un token sin repetir el flujo completo.
  • Guardar automáticamente los valores en un archivo `.env` compatible con
    los scripts del proyecto (MELI_ACCESS_TOKEN, MELI_REFRESH_TOKEN,
    MELI_SELLER_ID).
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import secrets
import sys
import textwrap
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

import requests

# IMPORTANTE: El valor por defecto es para Uruguay. Configura MERCADO_LIBRE_AUTH_URL según tu región:
# Argentina: https://auth.mercadolibre.com.ar, México: https://auth.mercadolibre.com.mx, etc.
DEFAULT_AUTH_URL = os.getenv("MERCADO_LIBRE_AUTH_URL", "https://auth.mercadolibre.com.uy")
DEFAULT_API_URL = os.getenv("MERCADO_LIBRE_API_URL", "https://api.mercadolibre.com")
DEFAULT_SCOPES = os.getenv("MERCADO_LIBRE_SCOPES", "offline_access read write")
DEFAULT_REDIRECT_URI = os.getenv(
    "MERCADO_LIBRE_REDIRECT_URI", "http://localhost:3000/api/mercado-libre/auth/callback"
)
PKCE_ENABLED = os.getenv("MERCADO_LIBRE_PKCE_ENABLED", "true").lower() == "true"


@dataclass
class OAuthTokens:
    access_token: str
    refresh_token: str | None
    expires_in: int
    user_id: str | None = None
    scope: str | None = None
    token_type: str | None = None


class MercadoLibreOAuthHelper:
    """Pequeño cliente para orquestar el flujo OAuth de Mercado Libre."""

    def __init__(
        self,
        app_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str = DEFAULT_REDIRECT_URI,
        scopes: str = DEFAULT_SCOPES,
        auth_url: str = DEFAULT_AUTH_URL,
        api_url: str = DEFAULT_API_URL,
        seller_id: str | None = None,
        pkce_enabled: bool = PKCE_ENABLED,
    ) -> None:
        self.app_id = app_id or os.getenv("MERCADO_LIBRE_APP_ID")
        self.client_secret = client_secret or os.getenv("MERCADO_LIBRE_CLIENT_SECRET")
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.auth_url = auth_url.rstrip("/")
        self.api_url = api_url.rstrip("/")
        self.token_endpoint = f"{self.api_url}/oauth/token"
        self.seller_id = seller_id or os.getenv("MERCADO_LIBRE_SELLER_ID")
        self.pkce_enabled = pkce_enabled
        self._code_verifier: str | None = None
        self._last_state: str | None = None

        if not self.app_id or not self.client_secret:
            raise RuntimeError(
                "Faltan MERCADO_LIBRE_APP_ID o MERCADO_LIBRE_CLIENT_SECRET. "
                "Defínelos en tu entorno o pásalos como argumentos."
            )

    # --------------------------------------------------------------------- URLs
    def build_authorization_url(self) -> str:
        """Genera la URL de autorización lista para abrir en el navegador."""
        state = secrets.token_urlsafe(16)
        self._last_state = state

        params = {
            "response_type": "code",
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": " ".join(self.scopes.split()),
        }

        if self.pkce_enabled:
            self._code_verifier = self._generate_code_verifier()
            params["code_challenge"] = self._generate_code_challenge(self._code_verifier)
            params["code_challenge_method"] = "S256"

        return f"{self.auth_url}/authorization?{urllib.parse.urlencode(params)}"

    # ------------------------------------------------------------------ Actions
    def exchange_code(self, code: str) -> OAuthTokens:
        """Intercambia el authorization code por tokens."""
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.app_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }

        if self.pkce_enabled and self._code_verifier:
            payload["code_verifier"] = self._code_verifier

        response = requests.post(self.token_endpoint, data=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return self._build_tokens(data)

    def refresh(self, refresh_token: str) -> OAuthTokens:
        """Obtiene un nuevo access token usando un refresh token."""
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.app_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }
        response = requests.post(self.token_endpoint, data=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return self._build_tokens(data)

    def fetch_seller_id(self, access_token: str) -> str | None:
        """Usa el token recién generado para obtener el seller_id."""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{self.api_url}/users/me", headers=headers, timeout=30)
        if response.status_code >= 400:
            return None
        data = response.json()
        return str(data.get("id") or self.seller_id or "")

    # ----------------------------------------------------------------- Helpers
    def persist_tokens(
        self, tokens: OAuthTokens, env_path: Path, include_seller: bool = True
    ) -> None:
        """Actualiza el archivo .env con los tokens más recientes."""
        updates: dict[str, str] = {"MELI_ACCESS_TOKEN": tokens.access_token}
        if tokens.refresh_token:
            updates["MELI_REFRESH_TOKEN"] = tokens.refresh_token
        if include_seller:
            seller_id = tokens.user_id or self.seller_id
            if not seller_id and tokens.access_token:
                seller_id = self.fetch_seller_id(tokens.access_token)
            if seller_id:
                updates["MELI_SELLER_ID"] = seller_id

        if not updates:
            return

        env_path = env_path.expanduser()
        existing = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
        lines = existing.splitlines()
        seen = set()
        new_lines = []

        for line in lines:
            if not line.strip() or line.strip().startswith("#") or "=" not in line:
                new_lines.append(line)
                continue
            key, value = line.split("=", 1)
            if key in updates:
                new_lines.append(f"{key}={updates[key]}")
                seen.add(key)
            else:
                new_lines.append(line)

        for key, value in updates.items():
            if key not in seen:
                if new_lines and new_lines[-1].strip():
                    new_lines.append("")
                new_lines.append(f"{key}={value}")

        env_path.write_text("\n".join(new_lines).strip() + "\n", encoding="utf-8")

    @staticmethod
    def _build_tokens(data: dict[str, object]) -> OAuthTokens:
        access_token = data.get("access_token")
        if not access_token:
            raise RuntimeError(
                "La respuesta de Mercado Libre no contiene access_token. "
                "Asegúrate de que el flujo OAuth se completó correctamente."
            )

        return OAuthTokens(
            access_token=str(access_token),
            refresh_token=str(data["refresh_token"]) if data.get("refresh_token") else None,
            expires_in=int(data.get("expires_in", 0)),
            user_id=str(data.get("user_id")) if data.get("user_id") else None,
            scope=data.get("scope"),
            token_type=data.get("token_type"),
        )

    @staticmethod
    def _generate_code_verifier(length: int = 64) -> str:
        raw = secrets.token_urlsafe(length)
        # PKCE verifier debe estar entre 43-128 chars
        return raw[:128]

    @staticmethod
    def _generate_code_challenge(verifier: str) -> str:
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


# ---------------------------------------------------------------------- CLI
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Asistente para autenticar Mercado Libre y guardar tokens en .env"
    )
    parser.add_argument("--code", help="Authorization code devuelto por Mercado Libre.")
    parser.add_argument("--refresh-token", help="Refresh token para renovar el access token.")
    parser.add_argument(
        "--redirect-uri",
        default=DEFAULT_REDIRECT_URI,
        help="Redirect URI registrado en la app (default: %(default)s)",
    )
    parser.add_argument(
        "--scopes",
        default=DEFAULT_SCOPES,
        help="Scopes separados por espacio que se incluirán en la autorización.",
    )
    parser.add_argument(
        "--output-env",
        default=".env.local",
        help="Archivo .env que se actualizará automáticamente (default: %(default)s). "
        "Usa '-' para evitar escritura.",
    )
    parser.add_argument(
        "--print-url",
        action="store_true",
        help="Solo imprime la URL de autorización y termina.",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="No intenta escribir las variables en el archivo .env aunque exista.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprime la respuesta cruda en formato JSON además del resumen.",
    )
    parser.add_argument(
        "--seller-id",
        help="Permite forzar el seller_id a guardar en el .env (opcional).",
    )
    parser.add_argument(
        "--env-file",
        help="Alias de --output-env (deprecated).",
    )
    return parser.parse_args()


def prompt_for_code(helper: MercadoLibreOAuthHelper) -> str:
    url = helper.build_authorization_url()
    instructions = textwrap.dedent(
        f"""
        1. Abre esta URL en el navegador y autoriza la app:
           {url}
        2. Tras iniciar sesión, copiarás el parámetro `code` del redirect URI configurado.
        3. Pega ese código cuando el script lo solicite.
        """
    ).strip()
    print(instructions)
    print()
    return input("Pega aquí el `code` devuelto por Mercado Libre: ").strip()


def print_summary(tokens: OAuthTokens) -> None:
    print("\n✅ Tokens obtenidos correctamente")
    print(f"   • access_token (primeros 8): {tokens.access_token[:8]}…")
    if tokens.refresh_token:
        print(f"   • refresh_token (primeros 8): {tokens.refresh_token[:8]}…")
    print(f"   • expira en: {tokens.expires_in // 60} min")
    if tokens.user_id:
        print(f"   • seller_id (user_id): {tokens.user_id}")
    if tokens.scope:
        print(f"   • scopes: {tokens.scope}")


def main() -> None:
    args = parse_args()
    output_env = args.env_file or args.output_env

    helper = MercadoLibreOAuthHelper(
        redirect_uri=args.redirect_uri,
        scopes=args.scopes,
        seller_id=args.seller_id,
    )

    if args.print_url and not args.code and not args.refresh_token:
        print(helper.build_authorization_url())
        return

    try:
        if args.refresh_token:
            tokens = helper.refresh(args.refresh_token)
        else:
            code = args.code or prompt_for_code(helper)
            tokens = helper.exchange_code(code)
    except requests.HTTPError as exc:
        print(
            f"❌ Error HTTP durante la autenticación: {exc} → {exc.response.text}", file=sys.stderr
        )
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"❌ Error de red durante la autenticación: {exc}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        sys.exit(1)

    print_summary(tokens)

    if args.json:
        print(json.dumps(tokens.__dict__, ensure_ascii=False, indent=2))

    if not args.no_save and output_env and output_env != "-":
        helper.persist_tokens(tokens, Path(output_env))
        print(f"💾 Variables actualizadas en {output_env}")
    else:
        print("ℹ️  Variables NO se guardaron automáticamente (modo --no-save o sin archivo).")


if __name__ == "__main__":
    main()
