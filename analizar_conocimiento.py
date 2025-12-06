#!/usr/bin/env python3
"""
Script de Análisis de Archivos de Conocimiento
Analiza todos los archivos JSON de conocimiento y genera un reporte detallado
"""

import glob
import json
import os
from collections import defaultdict
from datetime import datetime
from typing import Any


class AnalizadorConocimiento:
    """Analiza archivos de conocimiento del chatbot"""

    def __init__(self):
        self.archivos_analizados = []
        self.reporte = {
            "fecha_analisis": datetime.now().isoformat(),
            "archivos": [],
            "resumen": {},
            "comparacion": {},
            "duplicados": [],
            "conflictos": [],
        }

    def encontrar_archivos_conocimiento(self) -> list[str]:
        """Encuentra todos los archivos JSON de conocimiento"""
        patrones = [
            "*conocimiento*.json",
            "*base_conocimiento*.json",
            "*ia_conversacional*.json",
            "*analisis_conversiones*.json",
        ]

        archivos = []
        for patron in patrones:
            archivos.extend(glob.glob(patron))

        # Filtrar archivos que no son de conocimiento
        archivos_filtrados = []
        for archivo in archivos:
            nombre = os.path.basename(archivo).lower()
            # Excluir archivos de configuración o resultados
            if not any(excluir in nombre for excluir in ["config", "result", "test"]):
                archivos_filtrados.append(archivo)

        return sorted(set(archivos_filtrados))

    def analizar_archivo(self, ruta_archivo: str) -> dict[str, Any]:
        """Analiza un archivo de conocimiento"""
        try:
            with open(ruta_archivo, encoding="utf-8") as f:
                datos = json.load(f)

            analisis = {
                "archivo": ruta_archivo,
                "tamaño_bytes": os.path.getsize(ruta_archivo),
                "fecha_modificacion": datetime.fromtimestamp(
                    os.path.getmtime(ruta_archivo)
                ).isoformat(),
                "interacciones": 0,
                "patrones_venta": 0,
                "conocimiento_productos": 0,
                "insights": 0,
                "metricas": {},
                "estructura": {},
            }

            # Analizar interacciones
            if "interacciones" in datos:
                interacciones = datos["interacciones"]
                analisis["interacciones"] = len(interacciones)
                analisis["estructura"]["tiene_interacciones"] = True

                # Analizar tipos de interacción
                tipos = defaultdict(int)
                resultados = defaultdict(int)
                for inter in interacciones:
                    if isinstance(inter, dict):
                        tipos[inter.get("tipo_interaccion", "desconocido")] += 1
                        resultados[inter.get("resultado", "desconocido")] += 1

                analisis["metricas"]["tipos_interaccion"] = dict(tipos)
                analisis["metricas"]["resultados"] = dict(resultados)
            else:
                analisis["estructura"]["tiene_interacciones"] = False

            # Analizar patrones de venta
            if "patrones_venta" in datos:
                patrones = datos["patrones_venta"]
                analisis["patrones_venta"] = len(patrones)
                analisis["estructura"]["tiene_patrones"] = True

                # Analizar productos asociados
                productos_patrones = set()
                for patron in patrones:
                    if isinstance(patron, dict):
                        productos = patron.get("productos_asociados", [])
                        productos_patrones.update(productos)

                analisis["metricas"]["productos_en_patrones"] = list(productos_patrones)
            else:
                analisis["estructura"]["tiene_patrones"] = False

            # Analizar conocimiento de productos
            if "conocimiento_productos" in datos:
                productos = datos["conocimiento_productos"]
                analisis["conocimiento_productos"] = len(productos)
                analisis["estructura"]["tiene_productos"] = True
                analisis["metricas"]["productos"] = list(productos.keys())
            else:
                analisis["estructura"]["tiene_productos"] = False

            # Analizar insights
            if "insights_automaticos" in datos:
                insights = datos["insights_automaticos"]
                analisis["insights"] = len(insights)
                analisis["estructura"]["tiene_insights"] = True
            else:
                analisis["estructura"]["tiene_insights"] = False

            # Analizar métricas de evolución
            if "metricas_evolucion" in datos:
                analisis["estructura"]["tiene_metricas"] = True
                analisis["metricas"]["evolucion"] = datos["metricas_evolucion"]
            else:
                analisis["estructura"]["tiene_metricas"] = False

            # Fecha de exportación
            if "fecha_exportacion" in datos:
                analisis["fecha_exportacion"] = datos["fecha_exportacion"]

            return analisis

        except json.JSONDecodeError as e:
            return {"archivo": ruta_archivo, "error": f"Error parseando JSON: {str(e)}"}
        except Exception as e:
            return {"archivo": ruta_archivo, "error": f"Error analizando archivo: {str(e)}"}

    def comparar_archivos(self, analisis_archivos: list[dict[str, Any]]) -> dict[str, Any]:
        """Compara archivos para identificar el más completo"""
        comparacion = {
            "archivo_mas_completo": None,
            "max_interacciones": 0,
            "max_patrones": 0,
            "max_productos": 0,
            "puntuacion_completitud": {},
        }

        for analisis in analisis_archivos:
            if "error" in analisis:
                continue

            # Calcular puntuación de completitud
            puntuacion = 0
            puntuacion += analisis.get("interacciones", 0) * 1
            puntuacion += analisis.get("patrones_venta", 0) * 10
            puntuacion += analisis.get("conocimiento_productos", 0) * 5
            puntuacion += analisis.get("insights", 0) * 2

            comparacion["puntuacion_completitud"][analisis["archivo"]] = puntuacion

            # Actualizar máximos
            if analisis.get("interacciones", 0) > comparacion["max_interacciones"]:
                comparacion["max_interacciones"] = analisis["interacciones"]

            if analisis.get("patrones_venta", 0) > comparacion["max_patrones"]:
                comparacion["max_patrones"] = analisis["patrones_venta"]

            if analisis.get("conocimiento_productos", 0) > comparacion["max_productos"]:
                comparacion["max_productos"] = analisis["conocimiento_productos"]

        # Identificar archivo más completo
        if comparacion["puntuacion_completitud"]:
            archivo_mas_completo = max(
                comparacion["puntuacion_completitud"].items(), key=lambda x: x[1]
            )[0]
            comparacion["archivo_mas_completo"] = archivo_mas_completo

        return comparacion

    def detectar_duplicados(self, analisis_archivos: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Detecta archivos duplicados o con contenido similar"""
        duplicados = []

        # Agrupar por número de interacciones
        por_interacciones = defaultdict(list)
        for analisis in analisis_archivos:
            if "error" not in analisis:
                num_inter = analisis.get("interacciones", 0)
                por_interacciones[num_inter].append(analisis["archivo"])

        # Identificar grupos con mismo número de interacciones
        for num_inter, archivos in por_interacciones.items():
            if num_inter > 0 and len(archivos) > 1:
                duplicados.append(
                    {
                        "tipo": "mismo_numero_interacciones",
                        "numero": num_inter,
                        "archivos": archivos,
                    }
                )

        return duplicados

    def analizar_todos(self) -> dict[str, Any]:
        """Analiza todos los archivos de conocimiento"""
        archivos = self.encontrar_archivos_conocimiento()

        print(f"📊 Encontrados {len(archivos)} archivos de conocimiento")

        analisis_archivos = []
        for archivo in archivos:
            print(f"  Analizando: {os.path.basename(archivo)}")
            analisis = self.analizar_archivo(archivo)
            analisis_archivos.append(analisis)

        # Generar resumen
        total_interacciones = sum(
            a.get("interacciones", 0) for a in analisis_archivos if "error" not in a
        )
        total_patrones = sum(
            a.get("patrones_venta", 0) for a in analisis_archivos if "error" not in a
        )
        total_productos = sum(
            a.get("conocimiento_productos", 0) for a in analisis_archivos if "error" not in a
        )
        total_insights = sum(a.get("insights", 0) for a in analisis_archivos if "error" not in a)

        self.reporte["archivos"] = analisis_archivos
        self.reporte["resumen"] = {
            "total_archivos": len(archivos),
            "total_interacciones": total_interacciones,
            "total_patrones_venta": total_patrones,
            "total_conocimiento_productos": total_productos,
            "total_insights": total_insights,
        }

        # Comparar archivos
        self.reporte["comparacion"] = self.comparar_archivos(analisis_archivos)

        # Detectar duplicados
        self.reporte["duplicados"] = self.detectar_duplicados(analisis_archivos)

        return self.reporte

    def generar_reporte_texto(self) -> str:
        """Genera un reporte en texto legible"""
        reporte = []
        reporte.append("=" * 70)
        reporte.append("REPORTE DE ANÁLISIS DE CONOCIMIENTO")
        reporte.append("=" * 70)
        reporte.append(f"Fecha: {self.reporte['fecha_analisis']}")
        reporte.append("")

        # Resumen
        resumen = self.reporte["resumen"]
        reporte.append("RESUMEN GENERAL:")
        reporte.append(f"  Total archivos analizados: {resumen['total_archivos']}")
        reporte.append(f"  Total interacciones: {resumen['total_interacciones']}")
        reporte.append(f"  Total patrones de venta: {resumen['total_patrones_venta']}")
        reporte.append(f"  Total conocimiento productos: {resumen['total_conocimiento_productos']}")
        reporte.append(f"  Total insights: {resumen['total_insights']}")
        reporte.append("")

        # Archivo más completo
        comparacion = self.reporte["comparacion"]
        if comparacion.get("archivo_mas_completo"):
            reporte.append("ARCHIVO MÁS COMPLETO:")
            reporte.append(f"  {comparacion['archivo_mas_completo']}")
            reporte.append("")

        # Detalles por archivo
        reporte.append("DETALLES POR ARCHIVO:")
        for analisis in self.reporte["archivos"]:
            if "error" in analisis:
                reporte.append(f"  ❌ {os.path.basename(analisis['archivo'])}: {analisis['error']}")
            else:
                reporte.append(f"  ✅ {os.path.basename(analisis['archivo'])}:")
                reporte.append(f"     Interacciones: {analisis['interacciones']}")
                reporte.append(f"     Patrones: {analisis['patrones_venta']}")
                reporte.append(f"     Productos: {analisis['conocimiento_productos']}")
                reporte.append(f"     Insights: {analisis['insights']}")
        reporte.append("")

        # Duplicados
        if self.reporte["duplicados"]:
            reporte.append("DUPLICADOS DETECTADOS:")
            for dup in self.reporte["duplicados"]:
                reporte.append(
                    f"  {dup['tipo']}: {', '.join(os.path.basename(a) for a in dup['archivos'])}"
                )
            reporte.append("")

        return "\n".join(reporte)

    def guardar_reporte(self, archivo_salida: str = "reporte_analisis_conocimiento.json"):
        """Guarda el reporte en JSON"""
        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(self.reporte, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ Reporte guardado en: {archivo_salida}")


def main():
    """Función principal"""
    print("🔍 Iniciando análisis de archivos de conocimiento...")
    print("")

    analizador = AnalizadorConocimiento()
    analizador.analizar_todos()

    # Mostrar reporte
    print(analizador.generar_reporte_texto())

    # Guardar reporte
    analizador.guardar_reporte()

    # Guardar reporte en texto
    with open("reporte_analisis_conocimiento.txt", "w", encoding="utf-8") as f:
        f.write(analizador.generar_reporte_texto())
    print("✅ Reporte en texto guardado en: reporte_analisis_conocimiento.txt")


if __name__ == "__main__":
    main()
