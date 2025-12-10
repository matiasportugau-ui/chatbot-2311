#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincroniza el catálogo de productos públicos del sitio Shopify
bmcuruguay.com.uy y lo transforma en archivos reutilizables por la
consolidación de conocimiento del chatbot.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


SHOPIFY_STORE_URL = "https://bmcuruguay.com.uy"
DEFAULT_MAX_AGE_MINUTES = 60
ADMIN_API_VERSION = "2024-10"


def _int_from_env(var_name: str, default: int) -> int:
    """Obtiene enteros seguros desde variables de entorno."""
    value = os.getenv(var_name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass
class ShopifyVariant:
    """Representa una variante de producto de Shopify."""

    id: int
    title: str
    sku: str
    price: str
    available: bool
    weight: float
    weight_unit: str
    inventory_quantity: int = 0



@dataclass
class ShopifyProduct:
    """Producto de Shopify con metadatos limpios."""

    id: int
    handle: str
    title: str
    vendor: str
    product_type: str
    tags: List[str]
    url: str
    description: str
    variants: List[ShopifyVariant]
    options: List[Dict[str, Any]]
    images: List[str]
    published_at: Optional[str]
    updated_at: Optional[str]


class ShopifyProductSync:
    """Cliente simple para extraer y transformar productos Shopify públicos."""

    def __init__(
        self,
        per_page: int = 250,
        output_dir: Path | None = None,
        knowledge_filename: str = "conocimiento_shopify.json",
    ):
        self.per_page = per_page
        self.output_dir = output_dir or Path("data/shopify")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_path = Path(knowledge_filename)
        self.raw_path = self.output_dir / "shopify_products_raw.json"
        self.max_age_minutes = _int_from_env(
            "SHOPIFY_SYNC_MAX_AGE_MINUTES", DEFAULT_MAX_AGE_MINUTES
        )
        self.force_sync = os.getenv("SHOPIFY_FORCE_SYNC", "").lower() in {"1", "true", "yes"}
        
        # Admin API Config
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        self.shop_domain = os.getenv("SHOPIFY_SHOP_DOMAIN", "bmcuruguay.myshopify.com")
        self.use_admin_api = bool(self.access_token)

    def run(self) -> None:
        """Ejecuta la descarga y genera los archivos necesarios."""
        if self._should_skip_sync():
            print(
                "♻️  Catálogo Shopify reciente: omitiendo sincronización remota "
                f"(max {self.max_age_minutes} min)."
            )
            return

        products = self._fetch_all_products()
        normalized = [self._normalize_product(prod) for prod in products]
        timestamp = datetime.now(timezone.utc).isoformat()

        raw_payload = {
            "metadata": {
                "source": "admin_api" if self.use_admin_api else "public_api",
                "generated_at": timestamp,
                "total_products": len(products),
            },
            "products": products,
        }
        self._write_json(self.raw_path, raw_payload)

        knowledge_payload = self._build_knowledge_payload(normalized, timestamp)
        self._write_json(self.knowledge_path, knowledge_payload)

        print(
            f"✅ Shopify sync completado: {len(products)} productos → "
            f"{self.raw_path} / {self.knowledge_path}"
        )

    def _fetch_all_products(self) -> List[Dict[str, Any]]:
        """Orquesta la descarga dependiendo del modo (Admin vs Public)."""
        if self.use_admin_api:
            return self._fetch_admin_products()
        return self._fetch_public_products()

    def _fetch_public_products(self) -> List[Dict[str, Any]]:
        """Recorre todas las páginas del endpoint público de Shopify."""
        print("🌍 Modo Público: Usando endpoint products.json (sin inventario real)")
        url = f"{SHOPIFY_STORE_URL}/products.json"
        page = 1
        products: List[Dict[str, Any]] = []

        with requests.Session() as session:
            session.headers.update(
                {
                    "User-Agent": "BMC-ShopifySync/1.0 (+https://bmcuruguay.com.uy)",
                    "Accept": "application/json",
                }
            )
            while True:
                params = {"limit": self.per_page, "page": page}
                response = session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                chunk = data.get("products", [])
                if not chunk:
                    break
                products.extend(chunk)
                print(f"  • Página {page}: {len(chunk)} productos")
                page += 1

        return products

    def _fetch_admin_products(self) -> List[Dict[str, Any]]:
        """Usa la Admin API para obtener productos con datos privados (inventario)."""
        print(f"🔐 Modo Admin: Conectando a {self.shop_domain} (con inventario)")
        url = f"https://{self.shop_domain}/admin/api/{ADMIN_API_VERSION}/products.json"
        products: List[Dict[str, Any]] = []
        
        # Paginación basada en since_id es más robusta para scripts simples
        last_id = 0
        
        with requests.Session() as session:
            session.headers.update(
                {
                    "X-Shopify-Access-Token": self.access_token,
                    "Content-Type": "application/json",
                }
            )
            while True:
                params = {"limit": self.per_page, "since_id": last_id}
                response = session.get(url, params=params, timeout=30)
                if response.status_code == 401:
                    raise Exception("Error de autenticación: Token de Shopify inválido")
                response.raise_for_status()
                
                data = response.json()
                chunk = data.get("products", [])
                if not chunk:
                    break
                
                products.extend(chunk)
                last_id = chunk[-1]["id"]
                print(f"  • Lote recibido: {len(chunk)} productos (Total: {len(products)})")

        return products

    def _normalize_product(self, product: Dict[str, Any]) -> ShopifyProduct:
        """Convierte el producto bruto en una estructura tipada."""
        description_html = product.get("body_html") or ""
        soup = BeautifulSoup(description_html, "html.parser")
        description_text = soup.get_text(" ", strip=True)

        variants = [
            ShopifyVariant(
                id=variant.get("id"),
                title=variant.get("title", ""),
                sku=variant.get("sku") or "",
                price=variant.get("price") or "",
                available=variant.get("available", False),
                weight=float(variant.get("grams", 0) or 0) / 1000.0,
                weight_unit="kg",
                inventory_quantity=variant.get("inventory_quantity", 0),
            )
            for variant in product.get("variants", [])
        ]

        images = [image.get("src") for image in product.get("images", []) if image.get("src")]

        raw_tags = product.get("tags") or []
        if isinstance(raw_tags, str):
            tags = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
        else:
            tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()]

        return ShopifyProduct(
            id=product.get("id"),
            handle=product.get("handle") or str(product.get("id")),
            title=product.get("title", "").strip(),
            vendor=product.get("vendor") or "",
            product_type=product.get("product_type") or "",
            tags=tags,
            url=f"{SHOPIFY_STORE_URL}/products/{product.get('handle')}",
            description=description_text,
            variants=variants,
            options=product.get("options", []),
            images=images,
            published_at=product.get("published_at"),
            updated_at=product.get("updated_at"),
        )

    def _build_knowledge_payload(
        self, products: List[ShopifyProduct], timestamp: str
    ) -> Dict[str, Any]:
        """Crea el archivo de conocimiento compatible con el consolidado."""
        conocimiento_productos = {}
        for product in products:
            producto_id = product.handle.replace(" ", "_").lower()

            caracteristicas_base = {
                "descripcion": product.description,
                "tipo_producto": product.product_type,
                "vendor": product.vendor,
                "tags": product.tags,
                "opciones": product.options,
                "imagenes": product.images,
                "url_producto": product.url,
                "variantes": [asdict(variant) for variant in product.variants],
            }

            precios_competitivos = {}
            for variant in product.variants:
                key = f"{product.title} - {variant.title}".strip(" -")
                precios_competitivos[key] = variant.price

            conocimiento_productos[producto_id] = {
                "nombre": product.title or producto_id.title(),
                "caracteristicas_base": caracteristicas_base,
                "caracteristicas_aprendidas": {},
                "objeciones_comunes": [],
                "respuestas_efectivas": [],
                "casos_uso_exitosos": [],
                "precios_competitivos": precios_competitivos,
                "inventario": {
                     v.title: v.inventory_quantity for v in product.variants
                } if self.use_admin_api else {},
                "tendencias_demanda": [],
                "recomendaciones_venta": [
                    "Destacar disponibilidad a medida y fabricación nacional",
                    "Resaltar opciones de espesor y terminaciones",
                ],
                "fecha_ultima_actualizacion": timestamp,
            }

        return {
            "fuente": "shopify_public_api",
            "descripcion": "Catálogo sincronizado desde bmcuruguay.com.uy",
            "fecha_exportacion": timestamp,
            "conocimiento_productos": conocimiento_productos,
        }

    def _should_skip_sync(self) -> bool:
        """Determina si se puede reutilizar la data local para ahorrar requests."""
        if self.force_sync:
            return False
        if self.max_age_minutes <= 0:
            return False
        freshest_path = self.knowledge_path if self.knowledge_path.exists() else self.raw_path
        if not freshest_path.exists():
            return False
        last_modified = datetime.fromtimestamp(freshest_path.stat().st_mtime, timezone.utc)
        age_minutes = (datetime.now(timezone.utc) - last_modified).total_seconds() / 60
        return age_minutes < self.max_age_minutes

    @staticmethod
    def _write_json(path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)


def main() -> None:
    try:
        per_page = int(os.getenv("SHOPIFY_PAGE_SIZE", "250"))
    except ValueError:
        per_page = 250

    syncer = ShopifyProductSync(per_page=per_page)
    try:
        syncer.run()
    except requests.HTTPError as exc:
        print(f"❌ Error HTTP al consultar Shopify: {exc}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"❌ Error de red al consultar Shopify: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

