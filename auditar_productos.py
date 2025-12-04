#!/usr/bin/env python3
"""
Script de Auditoría de Productos
Identifica todos los productos que deberían estar integrados en el sistema
"""

import json
import os
import re
from typing import Any


class AuditorProductos:
    """Audita productos en el sistema"""

    def __init__(self):
        self.reporte = {
            "productos_en_sistema": set(),
            "productos_en_matriz_precios": set(),
            "productos_en_conocimiento": set(),
            "productos_en_escenarios": set(),
            "productos_faltantes": [],
            "productos_adicionales": [],
        }

    def auditar_sistema_cotizaciones(self) -> set[str]:
        """Audita productos en sistema_cotizaciones.py"""
        productos = set()

        try:
            with open("sistema_cotizaciones.py", encoding="utf-8") as f:
                contenido = f.read()

            # Buscar definiciones de productos
            # Patrón: "codigo": "nombre_producto"
            patrones = [
                r'"codigo":\s*"([^"]+)"',
                r'codigo="([^"]+)"',
                r'producto\s*=\s*["\']([^"\']+)["\']',
                r'"producto":\s*"([^"]+)"',
            ]

            for patron in patrones:
                matches = re.findall(patron, contenido, re.IGNORECASE)
                productos.update(matches)

            # Buscar productos hardcodeados
            productos_hardcodeados = ["isodec", "poliestireno", "lana_roca", "lana roca"]
            for producto in productos_hardcodeados:
                if producto.lower() in contenido.lower():
                    productos.add(producto.lower().replace(" ", "_"))

        except FileNotFoundError:
            print("⚠️  Archivo sistema_cotizaciones.py no encontrado")
        except Exception as e:
            print(f"⚠️  Error leyendo sistema_cotizaciones.py: {e}")

        return productos

    def auditar_matriz_precios(self) -> set[str]:
        """Audita productos en matriz_precios.json"""
        productos = set()

        try:
            with open("matriz_precios.json", encoding="utf-8") as f:
                datos = json.load(f)

            if "productos" in datos:
                productos.update(datos["productos"].keys())

        except FileNotFoundError:
            print("⚠️  Archivo matriz_precios.json no encontrado")
        except Exception as e:
            print(f"⚠️  Error leyendo matriz_precios.json: {e}")

        return productos

    def auditar_conocimiento(self) -> set[str]:
        """Audita productos mencionados en archivos de conocimiento"""
        productos = set()

        archivos_conocimiento = [
            "conocimiento_completo.json",
            "base_conocimiento_final.json",
            "base_conocimiento_exportada.json",
        ]

        for archivo in archivos_conocimiento:
            if not os.path.exists(archivo):
                continue

            try:
                with open(archivo, encoding="utf-8") as f:
                    datos = json.load(f)

                # Buscar en interacciones
                if "interacciones" in datos:
                    for inter in datos["interacciones"]:
                        mensaje = inter.get("mensaje_cliente", "").lower()
                        contexto = inter.get("contexto", {})

                        # Buscar productos en mensajes
                        if "isodec" in mensaje:
                            productos.add("isodec")
                        if "poliestireno" in mensaje:
                            productos.add("poliestireno")
                        if "lana" in mensaje and "roca" in mensaje:
                            productos.add("lana_roca")

                        # Buscar en contexto
                        if "producto" in contexto:
                            prod = str(contexto["producto"]).lower()
                            productos.add(prod)

                # Buscar en patrones de venta
                if "patrones_venta" in datos:
                    for patron in datos["patrones_venta"]:
                        productos_asoc = patron.get("productos_asociados", [])
                        productos.update([p.lower() for p in productos_asoc])

                # Buscar en conocimiento de productos
                if "conocimiento_productos" in datos:
                    productos.update(datos["conocimiento_productos"].keys())

            except Exception as e:
                print(f"⚠️  Error leyendo {archivo}: {e}")

        return productos

    def auditar_escenarios(self) -> set[str]:
        """Audita productos mencionados en escenarios de prueba"""
        productos = set()

        if not os.path.exists("test_scenarios"):
            return productos

        import glob

        archivos = glob.glob("test_scenarios/*.json")

        for archivo in archivos:
            try:
                with open(archivo, encoding="utf-8") as f:
                    datos = json.load(f)

                escenarios = datos if isinstance(datos, list) else [datos]

                for escenario in escenarios:
                    mensajes = escenario.get("messages", [])
                    for msg in mensajes:
                        contenido = msg.get("content", "").lower()
                        if "isodec" in contenido:
                            productos.add("isodec")
                        if "poliestireno" in contenido:
                            productos.add("poliestireno")
                        if "lana" in contenido and "roca" in contenido:
                            productos.add("lana_roca")

            except Exception as e:
                print(f"⚠️  Error leyendo {archivo}: {e}")

        return productos

    def normalizar_producto(self, producto: str) -> str:
        """Normaliza el nombre de un producto"""
        producto = producto.lower().strip()
        # Normalizaciones comunes
        producto = producto.replace(" ", "_")
        producto = producto.replace("-", "_")
        if "lana" in producto and "roca" in producto:
            return "lana_roca"
        return producto

    def auditar_todos(self) -> dict[str, Any]:
        """Realiza auditoría completa"""
        print("🔍 Iniciando auditoría de productos...")
        print("")

        # Auditar cada fuente
        print("  Auditing sistema_cotizaciones.py...")
        productos_sistema = self.auditar_sistema_cotizaciones()
        self.reporte["productos_en_sistema"] = productos_sistema

        print("  Auditing matriz_precios.json...")
        productos_matriz = self.auditar_matriz_precios()
        self.reporte["productos_en_matriz_precios"] = productos_matriz

        print("  Auditing archivos de conocimiento...")
        productos_conocimiento = self.auditar_conocimiento()
        self.reporte["productos_en_conocimiento"] = productos_conocimiento

        print("  Auditing escenarios de prueba...")
        productos_escenarios = self.auditar_escenarios()
        self.reporte["productos_en_escenarios"] = productos_escenarios

        # Normalizar todos los productos
        todos_productos = set()
        todos_productos.update([self.normalizar_producto(p) for p in productos_sistema])
        todos_productos.update([self.normalizar_producto(p) for p in productos_matriz])
        todos_productos.update([self.normalizar_producto(p) for p in productos_conocimiento])
        todos_productos.update([self.normalizar_producto(p) for p in productos_escenarios])

        # Identificar productos faltantes
        productos_base = {"isodec", "poliestireno", "lana_roca"}

        # Productos que están en otras fuentes pero no en el sistema base
        productos_faltantes = []
        for producto in todos_productos:
            if producto not in productos_base and producto:
                productos_faltantes.append(
                    {
                        "producto": producto,
                        "en_matriz_precios": producto
                        in [self.normalizar_producto(p) for p in productos_matriz],
                        "en_conocimiento": producto
                        in [self.normalizar_producto(p) for p in productos_conocimiento],
                        "en_escenarios": producto
                        in [self.normalizar_producto(p) for p in productos_escenarios],
                    }
                )

        self.reporte["productos_faltantes"] = productos_faltantes

        # Productos adicionales (más allá de los 3 base)
        productos_adicionales = todos_productos - productos_base
        self.reporte["productos_adicionales"] = sorted(list(productos_adicionales))

        return self.reporte

    def generar_reporte_texto(self) -> str:
        """Genera un reporte en texto legible"""
        reporte = []
        reporte.append("=" * 70)
        reporte.append("REPORTE DE AUDITORÍA DE PRODUCTOS")
        reporte.append("=" * 70)
        reporte.append("")

        # Productos en cada fuente
        reporte.append("PRODUCTOS ENCONTRADOS POR FUENTE:")
        reporte.append(f"  Sistema de cotizaciones: {sorted(self.reporte['productos_en_sistema'])}")
        reporte.append(
            f"  Matriz de precios: {sorted(self.reporte['productos_en_matriz_precios'])}"
        )
        reporte.append(
            f"  Archivos de conocimiento: {sorted(self.reporte['productos_en_conocimiento'])}"
        )
        reporte.append(f"  Escenarios de prueba: {sorted(self.reporte['productos_en_escenarios'])}")
        reporte.append("")

        # Productos base
        reporte.append("PRODUCTOS BASE INTEGRADOS:")
        reporte.append("  - isodec")
        reporte.append("  - poliestireno")
        reporte.append("  - lana_roca")
        reporte.append("")

        # Productos faltantes
        if self.reporte["productos_faltantes"]:
            reporte.append("PRODUCTOS FALTANTES (mencionados pero no integrados):")
            for prod in self.reporte["productos_faltantes"]:
                reporte.append(f"  - {prod['producto']}")
                if prod["en_matriz_precios"]:
                    reporte.append("    ✓ En matriz de precios")
                if prod["en_conocimiento"]:
                    reporte.append("    ✓ En conocimiento")
                if prod["en_escenarios"]:
                    reporte.append("    ✓ En escenarios")
            reporte.append("")
        else:
            reporte.append("✅ No se encontraron productos faltantes")
            reporte.append("")

        # Productos adicionales
        if self.reporte["productos_adicionales"]:
            reporte.append("PRODUCTOS ADICIONALES DETECTADOS:")
            for prod in self.reporte["productos_adicionales"]:
                reporte.append(f"  - {prod}")
            reporte.append("")

        return "\n".join(reporte)

    def guardar_reporte(self, archivo_salida: str = "reporte_auditoria_productos.json"):
        """Guarda el reporte en JSON"""
        # Convertir sets a lists para JSON
        reporte_serializable = {
            "productos_en_sistema": sorted(list(self.reporte["productos_en_sistema"])),
            "productos_en_matriz_precios": sorted(
                list(self.reporte["productos_en_matriz_precios"])
            ),
            "productos_en_conocimiento": sorted(list(self.reporte["productos_en_conocimiento"])),
            "productos_en_escenarios": sorted(list(self.reporte["productos_en_escenarios"])),
            "productos_faltantes": self.reporte["productos_faltantes"],
            "productos_adicionales": self.reporte["productos_adicionales"],
        }

        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(reporte_serializable, f, ensure_ascii=False, indent=2)
        print(f"✅ Reporte guardado en: {archivo_salida}")


def main():
    """Función principal"""
    auditor = AuditorProductos()
    auditor.auditar_todos()

    # Mostrar reporte
    print(auditor.generar_reporte_texto())

    # Guardar reporte
    auditor.guardar_reporte()

    # Guardar reporte en texto
    with open("reporte_auditoria_productos.txt", "w", encoding="utf-8") as f:
        f.write(auditor.generar_reporte_texto())
    print("✅ Reporte en texto guardado en: reporte_auditoria_productos.txt")


if __name__ == "__main__":
    main()
