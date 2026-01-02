#!/usr/bin/env python3
"""
Script de Pruebas de Respuestas del Chatbot
Ejecuta preguntas de prueba y compara respuestas antes/después de la integración
"""

import json
from datetime import datetime
from typing import Any


class TesterRespuestas:
    """Prueba las respuestas del chatbot"""

    def __init__(self):
        self.preguntas_test = [
            {"categoria": "saludo", "pregunta": "Hola", "esperado": ["saludo", "hola", "ayuda"]},
            {
                "categoria": "informacion_producto",
                "pregunta": "Información sobre Isodec",
                "esperado": ["isodec", "panel", "aislante", "térmico"],
            },
            {
                "categoria": "cotizacion",
                "pregunta": "Quiero cotizar",
                "esperado": ["cotizar", "datos", "precio"],
            },
            {
                "categoria": "productos",
                "pregunta": "¿Qué productos tienen?",
                "esperado": ["producto", "isodec", "poliestireno", "lana"],
            },
            {
                "categoria": "precio",
                "pregunta": "¿Cuánto cuesta Isodec?",
                "esperado": ["precio", "costo", "isodec"],
            },
            {
                "categoria": "especificaciones",
                "pregunta": "¿Qué espesores tienen disponibles?",
                "esperado": ["espesor", "50mm", "75mm", "100mm"],
            },
        ]

        self.resultados = {
            "fecha_prueba": datetime.now().isoformat(),
            "preguntas": [],
            "resumen": {},
        }

    def probar_pregunta(self, pregunta_data: dict[str, Any]) -> dict[str, Any]:
        """Prueba una pregunta específica"""
        try:
            from ia_conversacional_integrada import IAConversacionalIntegrada

            ia = IAConversacionalIntegrada()

            pregunta = pregunta_data["pregunta"]
            respuesta = ia.procesar_mensaje(pregunta, "test_cliente", "test_sesion")

            # Analizar respuesta
            mensaje_lower = respuesta.mensaje.lower()
            palabras_esperadas = [e.lower() for e in pregunta_data["esperado"]]

            palabras_encontradas = [p for p in palabras_esperadas if p in mensaje_lower]
            cobertura = (
                len(palabras_encontradas) / len(palabras_esperadas) if palabras_esperadas else 0
            )

            # Verificar si es genérica
            respuestas_genericas = [
                "gracias por tu consulta",
                "te ayudo con la información",
                "puedo ayudarte con",
            ]
            es_generica = any(gen in mensaje_lower for gen in respuestas_genericas)

            # Calcular satisfacción
            satisfaccion = 0.0
            if cobertura >= 0.5:
                satisfaccion += 0.3
            if not es_generica:
                satisfaccion += 0.3
            if len(respuesta.mensaje) > 50:
                satisfaccion += 0.2
            if respuesta.confianza > 0.7:
                satisfaccion += 0.2

            resultado = {
                "categoria": pregunta_data["categoria"],
                "pregunta": pregunta,
                "respuesta": respuesta.mensaje,
                "cobertura": cobertura,
                "palabras_encontradas": palabras_encontradas,
                "es_generica": es_generica,
                "longitud": len(respuesta.mensaje),
                "confianza": respuesta.confianza,
                "satisfaccion": satisfaccion,
                "tipo_respuesta": respuesta.tipo_respuesta,
                "fuentes": respuesta.fuentes_conocimiento,
            }

            return resultado

        except Exception as e:
            return {
                "categoria": pregunta_data["categoria"],
                "pregunta": pregunta_data["pregunta"],
                "error": str(e),
                "satisfaccion": 0.0,
            }

    def ejecutar_todas_las_pruebas(self) -> dict[str, Any]:
        """Ejecuta todas las pruebas"""
        print("🧪 Ejecutando pruebas de respuestas...")
        print("")

        resultados = []
        for pregunta_data in self.preguntas_test:
            print(f"  Probando: {pregunta_data['pregunta']}")
            resultado = self.probar_pregunta(pregunta_data)
            resultados.append(resultado)

            if "error" in resultado:
                print(f"    ❌ Error: {resultado['error']}")
            else:
                estado = "✅" if resultado["satisfaccion"] >= 0.7 else "⚠️"
                print(f"    {estado} Satisfacción: {resultado['satisfaccion']:.2f}")

        self.resultados["preguntas"] = resultados

        # Calcular resumen
        satisfacciones = [r["satisfaccion"] for r in resultados if "error" not in r]
        promedio = sum(satisfacciones) / len(satisfacciones) if satisfacciones else 0.0

        satisfactorias = len([s for s in satisfacciones if s >= 0.7])
        total = len(satisfacciones)

        self.resultados["resumen"] = {
            "total_preguntas": len(self.preguntas_test),
            "preguntas_exitosas": satisfactorias,
            "preguntas_fallidas": total - satisfactorias,
            "satisfaccion_promedio": promedio,
            "tasa_exito": satisfactorias / total if total > 0 else 0.0,
        }

        return self.resultados

    def generar_reporte_texto(self) -> str:
        """Genera reporte en texto"""
        reporte = []
        reporte.append("=" * 70)
        reporte.append("REPORTE DE PRUEBAS DE RESPUESTAS")
        reporte.append("=" * 70)
        reporte.append(f"Fecha: {self.resultados['fecha_prueba']}")
        reporte.append("")

        # Resumen
        resumen = self.resultados["resumen"]
        reporte.append("RESUMEN:")
        reporte.append(f"  Total preguntas: {resumen['total_preguntas']}")
        reporte.append(f"  Preguntas exitosas: {resumen['preguntas_exitosas']}")
        reporte.append(f"  Preguntas fallidas: {resumen['preguntas_fallidas']}")
        reporte.append(f"  Satisfacción promedio: {resumen['satisfaccion_promedio']:.2f}")
        reporte.append(f"  Tasa de éxito: {resumen['tasa_exito']:.1%}")
        reporte.append("")

        # Detalles
        reporte.append("DETALLES POR PREGUNTA:")
        for resultado in self.resultados["preguntas"]:
            if "error" in resultado:
                reporte.append(f"  ❌ {resultado['categoria']}: {resultado['pregunta']}")
                reporte.append(f"     Error: {resultado['error']}")
            else:
                estado = "✅" if resultado["satisfaccion"] >= 0.7 else "⚠️"
                reporte.append(f"  {estado} {resultado['categoria']}: {resultado['pregunta']}")
                reporte.append(f"     Satisfacción: {resultado['satisfaccion']:.2f}")
                reporte.append(f"     Cobertura: {resultado['cobertura']:.1%}")
                reporte.append(f"     Confianza: {resultado['confianza']:.2f}")
                reporte.append(f"     Fuentes: {', '.join(resultado['fuentes'])}")
                if resultado["es_generica"]:
                    reporte.append("     ⚠️  Respuesta genérica")
            reporte.append("")

        return "\n".join(reporte)

    def guardar_reporte(self, archivo: str = "reporte_pruebas_respuestas.json"):
        """Guarda el reporte"""
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(self.resultados, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ Reporte guardado en: {archivo}")


def main():
    """Función principal"""
    tester = TesterRespuestas()
    tester.ejecutar_todas_las_pruebas()

    print("\n" + tester.generar_reporte_texto())

    tester.guardar_reporte()

    # Guardar en texto
    with open("reporte_pruebas_respuestas.txt", "w", encoding="utf-8") as f:
        f.write(tester.generar_reporte_texto())
    print("✅ Reporte en texto guardado en: reporte_pruebas_respuestas.txt")


if __name__ == "__main__":
    main()
