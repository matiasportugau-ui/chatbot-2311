#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapeador de Productos con Enlaces Web BMC Uruguay
Mapea productos del sistema con sus enlaces en bmcuruguay.com.uy
"""

import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import time

class MapeadorProductosWeb:
    """Mapeador de productos con enlaces web"""
    
    def __init__(self):
        self.base_url = "https://bmcuruguay.com.uy"
        self.productos_mapeados = {}
        self.enlaces_disponibles = {}
        self.cargar_enlaces_base()
    
    def cargar_enlaces_base(self):
        """Carga los enlaces base de productos conocidos"""
        self.enlaces_base = {
            "isodec": {
                "url": f"{self.base_url}/productos/isodec",
                "categoria": "paneles-aislantes",
                "descripcion": "Panel aislante térmico con núcleo de EPS"
            },
            "poliestireno": {
                "url": f"{self.base_url}/productos/poliestireno",
                "categoria": "aislantes-termicos",
                "descripcion": "Aislante térmico de poliestireno expandido"
            },
            "lana_roca": {
                "url": f"{self.base_url}/productos/lana-roca",
                "categoria": "aislantes-termicos",
                "descripcion": "Aislante térmico y acústico de lana de roca"
            },
            "poliuretano": {
                "url": f"{self.base_url}/productos/poliuretano",
                "categoria": "aislantes-termicos",
                "descripcion": "Aislante térmico de poliuretano"
            },
            "fibra_vidrio": {
                "url": f"{self.base_url}/productos/fibra-vidrio",
                "categoria": "aislantes-termicos",
                "descripcion": "Aislante térmico de fibra de vidrio"
            }
        }
    
    def obtener_informacion_producto(self, codigo_producto: str) -> Optional[Dict]:
        """
        Obtiene información detallada de un producto desde la web
        
        Args:
            codigo_producto: Código del producto a buscar
            
        Returns:
            Diccionario con información del producto o None si no se encuentra
        """
        if codigo_producto not in self.enlaces_base:
            return None
        
        url = self.enlaces_base[codigo_producto]["url"]
        
        try:
            # Hacer petición HTTP con headers para evitar bloqueos
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer información del producto
            producto_info = {
                'codigo': codigo_producto,
                'url': url,
                'categoria': self.enlaces_base[codigo_producto]["categoria"],
                'descripcion': self.enlaces_base[codigo_producto]["descripcion"],
                'titulo': self._extraer_titulo(soup),
                'precio': self._extraer_precio(soup),
                'especificaciones': self._extraer_especificaciones(soup),
                'imagenes': self._extraer_imagenes(soup),
                'disponibilidad': self._extraer_disponibilidad(soup),
                'fecha_actualizacion': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return producto_info
            
        except requests.RequestException as e:
            print(f"Error obteniendo información de {codigo_producto}: {e}")
            return None
        except Exception as e:
            print(f"Error procesando {codigo_producto}: {e}")
            return None
    
    def _extraer_titulo(self, soup: BeautifulSoup) -> str:
        """Extrae el título del producto"""
        # Buscar en diferentes selectores comunes
        selectores_titulo = [
            'h1.product-title',
            'h1.title',
            '.product-name h1',
            'h1',
            '.product-title'
        ]
        
        for selector in selectores_titulo:
            elemento = soup.select_one(selector)
            if elemento:
                return elemento.get_text().strip()
        
        return "Título no encontrado"
    
    def _extraer_precio(self, soup: BeautifulSoup) -> str:
        """Extrae el precio del producto"""
        selectores_precio = [
            '.price',
            '.product-price',
            '.price-current',
            '[class*="price"]',
            '.cost'
        ]
        
        for selector in selectores_precio:
            elemento = soup.select_one(selector)
            if elemento:
                precio_texto = elemento.get_text().strip()
                # Limpiar el texto del precio
                precio_limpio = ''.join(c for c in precio_texto if c.isdigit() or c in '.,$')
                return precio_limpio
        
        return "Precio no disponible"
    
    def _extraer_especificaciones(self, soup: BeautifulSoup) -> Dict:
        """Extrae las especificaciones técnicas del producto"""
        especificaciones = {}
        
        # Buscar tablas de especificaciones
        tablas = soup.find_all('table')
        for tabla in tablas:
            filas = tabla.find_all('tr')
            for fila in filas:
                celdas = fila.find_all(['td', 'th'])
                if len(celdas) == 2:
                    clave = celdas[0].get_text().strip()
                    valor = celdas[1].get_text().strip()
                    especificaciones[clave] = valor
        
        # Buscar listas de especificaciones
        listas = soup.find_all(['ul', 'ol'], class_=lambda x: x and 'spec' in x.lower())
        for lista in listas:
            items = lista.find_all('li')
            for item in items:
                texto = item.get_text().strip()
                if ':' in texto:
                    clave, valor = texto.split(':', 1)
                    especificaciones[clave.strip()] = valor.strip()
        
        return especificaciones
    
    def _extraer_imagenes(self, soup: BeautifulSoup) -> List[str]:
        """Extrae las URLs de las imágenes del producto"""
        imagenes = []
        
        # Buscar imágenes del producto
        selectores_imagen = [
            '.product-image img',
            '.product-gallery img',
            '.product-photos img',
            'img[alt*="producto"]',
            'img[src*="product"]'
        ]
        
        for selector in selectores_imagen:
            elementos = soup.select(selector)
            for elemento in elementos:
                src = elemento.get('src')
                if src:
                    # Convertir URL relativa a absoluta
                    if src.startswith('/'):
                        src = self.base_url + src
                    elif not src.startswith('http'):
                        src = f"{self.base_url}/{src}"
                    imagenes.append(src)
        
        return list(set(imagenes))  # Eliminar duplicados
    
    def _extraer_disponibilidad(self, soup: BeautifulSoup) -> str:
        """Extrae información de disponibilidad del producto"""
        selectores_disponibilidad = [
            '.availability',
            '.stock',
            '.in-stock',
            '.out-of-stock',
            '[class*="stock"]',
            '[class*="available"]'
        ]
        
        for selector in selectores_disponibilidad:
            elemento = soup.select_one(selector)
            if elemento:
                return elemento.get_text().strip()
        
        return "Disponibilidad no especificada"
    
    def mapear_todos_los_productos(self) -> Dict:
        """Mapea todos los productos disponibles"""
        print("Iniciando mapeo de productos...")
        
        for codigo_producto in self.enlaces_base.keys():
            print(f"Procesando {codigo_producto}...")
            
            info_producto = self.obtener_informacion_producto(codigo_producto)
            if info_producto:
                self.productos_mapeados[codigo_producto] = info_producto
                print(f"✓ {codigo_producto} mapeado correctamente")
            else:
                print(f"✗ Error mapeando {codigo_producto}")
            
            # Pausa entre peticiones para no sobrecargar el servidor
            time.sleep(1)
        
        return self.productos_mapeados
    
    def buscar_productos_por_categoria(self, categoria: str) -> List[Dict]:
        """Busca productos por categoría"""
        productos_categoria = []
        
        for codigo, info in self.productos_mapeados.items():
            if info.get('categoria', '').lower() == categoria.lower():
                productos_categoria.append(info)
        
        return productos_categoria
    
    def buscar_productos_por_palabra_clave(self, palabra_clave: str) -> List[Dict]:
        """Busca productos por palabra clave en título o descripción"""
        productos_encontrados = []
        palabra_lower = palabra_clave.lower()
        
        for codigo, info in self.productos_mapeados.items():
            titulo = info.get('titulo', '').lower()
            descripcion = info.get('descripcion', '').lower()
            
            if palabra_lower in titulo or palabra_lower in descripcion:
                productos_encontrados.append(info)
        
        return productos_encontrados
    
    def exportar_mapeo(self, archivo: str):
        """Exporta el mapeo de productos a un archivo JSON"""
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(self.productos_mapeados, f, ensure_ascii=False, indent=2)
        
        print(f"Mapeo exportado a {archivo}")
    
    def generar_reporte_mapeo(self) -> str:
        """Genera un reporte del mapeo de productos"""
        reporte = f"""
=== REPORTE DE MAPEO DE PRODUCTOS BMC URUGUAY ===
Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}
Total de productos mapeados: {len(self.productos_mapeados)}

"""
        
        for codigo, info in self.productos_mapeados.items():
            reporte += f"""
PRODUCTO: {codigo.upper()}
Título: {info.get('titulo', 'N/A')}
URL: {info.get('url', 'N/A')}
Categoría: {info.get('categoria', 'N/A')}
Precio: {info.get('precio', 'N/A')}
Disponibilidad: {info.get('disponibilidad', 'N/A')}
Imágenes: {len(info.get('imagenes', []))}
Especificaciones: {len(info.get('especificaciones', {}))}
---
"""
        
        return reporte
    
    def actualizar_matriz_precios_con_enlaces(self, archivo_matriz: str):
        """Actualiza la matriz de precios con los enlaces obtenidos"""
        try:
            with open(archivo_matriz, 'r', encoding='utf-8') as f:
                matriz = json.load(f)
            
            # Actualizar productos con enlaces
            for codigo_producto, info_mapeada in self.productos_mapeados.items():
                if codigo_producto in matriz['productos']:
                    matriz['productos'][codigo_producto]['link_web'] = info_mapeada['url']
                    matriz['productos'][codigo_producto]['titulo_web'] = info_mapeada['titulo']
                    matriz['productos'][codigo_producto]['precio_web'] = info_mapeada['precio']
                    matriz['productos'][codigo_producto]['disponibilidad'] = info_mapeada['disponibilidad']
                    matriz['productos'][codigo_producto]['imagenes'] = info_mapeada['imagenes']
                    matriz['productos'][codigo_producto]['especificaciones_web'] = info_mapeada['especificaciones']
                    matriz['productos'][codigo_producto]['fecha_actualizacion_web'] = info_mapeada['fecha_actualizacion']
            
            # Guardar matriz actualizada
            with open(archivo_matriz, 'w', encoding='utf-8') as f:
                json.dump(matriz, f, ensure_ascii=False, indent=2)
            
            print(f"Matriz de precios actualizada con enlaces web")
            
        except FileNotFoundError:
            print(f"Archivo {archivo_matriz} no encontrado")
        except Exception as e:
            print(f"Error actualizando matriz: {e}")

def main():
    """Función principal para demostrar el mapeador"""
    mapeador = MapeadorProductosWeb()
    
    print("=== MAPEADOR DE PRODUCTOS BMC URUGUAY ===")
    print("Mapeando productos con enlaces web...")
    
    # Mapear todos los productos
    productos_mapeados = mapeador.mapear_todos_los_productos()
    
    if productos_mapeados:
        # Generar reporte
        print("\n" + mapeador.generar_reporte_mapeo())
        
        # Exportar mapeo
        mapeador.exportar_mapeo('productos_mapeados.json')
        
        # Actualizar matriz de precios
        mapeador.actualizar_matriz_precios_con_enlaces('matriz_precios.json')
        
        print("\n✓ Mapeo completado exitosamente")
    else:
        print("\n✗ No se pudieron mapear productos")

if __name__ == "__main__":
    main()
