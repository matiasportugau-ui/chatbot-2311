#!/usr/bin/env python3
"""
Script de Análisis de Escenarios de Prueba
Analiza todos los escenarios en test_scenarios/ y genera un reporte
"""

import glob
import json
import os
from datetime import datetime
from typing import Any


class AnalizadorEscenarios:
    """Analiza escenarios de prueba del chatbot"""

    def __init__(self, directorio: str = "test_scenarios"):
        self.directorio = directorio
        self.reporte = {
            "fecha_analisis": datetime.now().isoformat(),
            "escenarios": [],
            "resumen": {},
            "cobertura": {},
            "productos_mencionados": set(),
            "casos_uso": [],
        }

    def encontrar_escenarios(self) -> list[str]:
        """Encuentra todos los archivos JSON de escenarios"""
        if not os.path.exists(self.directorio):
            return []

        patron = os.path.join(self.directorio, "*.json")
        return sorted(glob.glob(patron))

    def analizar_escenario(self, ruta_archivo: str) -> dict[str, Any]:
        """Analiza un archivo de escenario"""
        try:
            with open(ruta_archivo, encoding="utf-8") as f:
                datos = json.load(f)

            # Manejar tanto escenarios individuales como listas
            escenarios = datos if isinstance(datos, list) else [datos]

            analisis = {
                "archivo": ruta_archivo,
                "nombre": os.path.basename(ruta_archivo),
                "numero_escenarios": len(escenarios),
                "escenarios": [],
            }

            productos_en_archivo = set()
            tipos_conversacion = set()
            casos_uso = []

            for escenario in escenarios:
                esc_analisis = {
                    "nombre": escenario.get("name", "Sin nombre"),
                    "descripcion": escenario.get("description", ""),
                    "mensajes": len(escenario.get("messages", [])),
                    "productos": [],
                    "tipo": escenario.get("type", "general"),
                    "intencion": escenario.get("intent", "unknown"),
                }

                # Extraer productos mencionados
                mensajes = escenario.get("messages", [])
                for msg in mensajes:
                    contenido = msg.get("content", "").lower()
                    if "isodec" in contenido:
                        productos_en_archivo.add("isodec")
                        if "isodec" not in esc_analisis["productos"]:
                            esc_analisis["productos"].append("isodec")
                    if "poliestireno" in contenido:
                        productos_en_archivo.add("poliestireno")
                        if "poliestireno" not in esc_analisis["productos"]:
                            esc_analisis["productos"].append("poliestireno")
                    if "lana" in contenido or "lana_roca" in contenido:
                        productos_en_archivo.add("lana_roca")
                        if "lana_roca" not in esc_analisis["productos"]:
                            esc_analisis["productos"].append("lana_roca")

                tipos_conversacion.add(esc_analisis["tipo"])
                casos_uso.append(esc_analisis["nombre"])

                analisis["escenarios"].append(esc_analisis)

            analisis["productos_mencionados"] = list(productos_en_archivo)
            analisis["tipos_conversacion"] = list(tipos_conversacion)

            return analisis

        except json.JSONDecodeError as e:
            return {"archivo": ruta_archivo, "error": f"Error parseando JSON: {str(e)}"}
        except Exception as e:
            return {"archivo": ruta_archivo, "error": f"Error analizando archivo: {str(e)}"}

    def analizar_todos(self) -> dict[str, Any]:
        """Analiza todos los escenarios"""
        archivos = self.encontrar_escenarios()

        if not archivos:
            print(f"⚠️  No se encontraron escenarios en {self.directorio}")
            return self.reporte

        print(f"📊 Encontrados {len(archivos)} archivos de escenarios")

        analisis_archivos = []
        todos_productos = set()
        todos_tipos = set()
        todos_casos = []

        for archivo in archivos:
            print(f"  Analizando: {os.path.basename(archivo)}")
            analisis = self.analizar_escenario(archivo)
            analisis_archivos.append(analisis)

            if "error" not in analisis:
                todos_productos.update(analisis.get("productos_mencionados", []))
                todos_tipos.update(analisis.get("tipos_conversacion", []))
                todos_casos.extend([s["nombre"] for s in analisis.get("escenarios", [])])

        # Calcular estadísticas
        total_escenarios = sum(
            a.get("numero_escenarios", 0) for a in analisis_archivos if "error" not in a
        )
        total_mensajes = sum(
            sum(s.get("mensajes", 0) for s in a.get("escenarios", []))
            for a in analisis_archivos
            if "error" not in a
        )

        self.reporte["escenarios"] = analisis_archivos
        self.reporte["resumen"] = {
            "total_archivos": len(archivos),
            "total_escenarios": total_escenarios,
            "total_mensajes": total_mensajes,
            "productos_unicos": len(todos_productos),
            "tipos_conversacion_unicos": len(todos_tipos),
        }

        self.reporte["cobertura"] = {
            "productos_mencionados": sorted(list(todos_productos)),
            "tipos_conversacion": sorted(list(todos_tipos)),
            "casos_uso": todos_casos,
        }

        return self.reporte

    def generar_reporte_texto(self) -> str:
        """Genera un reporte en texto legible"""
        reporte = []
        reporte.append("=" * 70)
        reporte.append("REPORTE DE ANÁLISIS DE ESCENARIOS")
        reporte.append("=" * 70)
        reporte.append(f"Fecha: {self.reporte['fecha_analisis']}")
        reporte.append("")

        # Resumen
        resumen = self.reporte["resumen"]
        reporte.append("RESUMEN GENERAL:")
        reporte.append(f"  Total archivos: {resumen['total_archivos']}")
        reporte.append(f"  Total escenarios: {resumen['total_escenarios']}")
        reporte.append(f"  Total mensajes: {resumen['total_mensajes']}")
        reporte.append(f"  Productos únicos mencionados: {resumen['productos_unicos']}")
        reporte.append(f"  Tipos de conversación únicos: {resumen['tipos_conversacion_unicos']}")
        reporte.append("")

        # Cobertura
        cobertura = self.reporte["cobertura"]
        reporte.append("COBERTURA:")
        reporte.append(f"  Productos mencionados: {', '.join(cobertura['productos_mencionados'])}")
        reporte.append(f"  Tipos de conversación: {', '.join(cobertura['tipos_conversacion'])}")
        reporte.append("")

        # Detalles por archivo
        reporte.append("DETALLES POR ARCHIVO:")
        for analisis in self.reporte["escenarios"]:
            if "error" in analisis:
                reporte.append(f"  ❌ {os.path.basename(analisis['archivo'])}: {analisis['error']}")
            else:
                reporte.append(f"  ✅ {analisis['nombre']}:")
                reporte.append(f"     Escenarios: {analisis['numero_escenarios']}")
                reporte.append(
                    f"     Productos: {', '.join(analisis.get('productos_mencionados', []))}"
                )
                reporte.append(f"     Tipos: {', '.join(analisis.get('tipos_conversacion', []))}")
                for esc in analisis.get("escenarios", [])[:3]:  # Mostrar primeros 3
                    reporte.append(f"       - {esc['nombre']}: {esc['mensajes']} mensajes")
        reporte.append("")

        return "\n".join(reporte)

    def guardar_reporte(self, archivo_salida: str = "reporte_analisis_escenarios.json"):
        """Guarda el reporte en JSON"""
        # Convertir set a list para JSON
        reporte_serializable = json.loads(json.dumps(self.reporte, default=str))
        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(reporte_serializable, f, ensure_ascii=False, indent=2)
        print(f"✅ Reporte guardado en: {archivo_salida}")


def main():
    """Función principal"""
    print("🔍 Iniciando análisis de escenarios de prueba...")
    print("")

    analizador = AnalizadorEscenarios()
    analizador.analizar_todos()

    # Mostrar reporte
    print(analizador.generar_reporte_texto())

    # Guardar reporte
    analizador.guardar_reporte()

    # Guardar reporte en texto
    with open("reporte_analisis_escenarios.txt", "w", encoding="utf-8") as f:
        f.write(analizador.generar_reporte_texto())
    print("✅ Reporte en texto guardado en: reporte_analisis_escenarios.txt")


if __name__ == "__main__":
    main()
