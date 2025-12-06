#!/usr/bin/env python3
"""
Script de Validación de Integración
Verifica que el conocimiento se carga correctamente y que el chatbot funciona
"""

import sys
from typing import Any


class ValidadorIntegracion:
    """Valida la integración del conocimiento"""

    def __init__(self):
        self.reporte = {"validaciones": [], "errores": [], "advertencias": [], "estadisticas": {}}

    def validar_carga_conocimiento(self) -> bool:
        """Valida que el conocimiento se carga correctamente"""
        print("🔍 Validando carga de conocimiento...")

        try:
            from base_conocimiento_dinamica import BaseConocimientoDinamica

            base = BaseConocimientoDinamica()

            # Verificar que se cargó conocimiento
            interacciones = len(base.interacciones)
            patrones = len(base.patrones_venta)
            productos = len(base.conocimiento_productos)

            self.reporte["estadisticas"]["interacciones"] = interacciones
            self.reporte["estadisticas"]["patrones"] = patrones
            self.reporte["estadisticas"]["productos"] = productos

            if base.archivo_conocimiento_cargado:
                self.reporte["validaciones"].append(
                    {
                        "tipo": "carga_conocimiento",
                        "estado": "exitoso",
                        "archivo": base.archivo_conocimiento_cargado,
                        "interacciones": interacciones,
                        "patrones": patrones,
                        "productos": productos,
                    }
                )
                print(f"  ✅ Conocimiento cargado desde: {base.archivo_conocimiento_cargado}")
                print(f"     Interacciones: {interacciones}")
                print(f"     Patrones: {patrones}")
                print(f"     Productos: {productos}")
                return True
            else:
                self.reporte["advertencias"].append(
                    {
                        "tipo": "carga_conocimiento",
                        "mensaje": "No se cargó ningún archivo de conocimiento",
                    }
                )
                print("  ⚠️  No se cargó ningún archivo de conocimiento")
                return False

        except Exception as e:
            self.reporte["errores"].append({"tipo": "carga_conocimiento", "error": str(e)})
            print(f"  ❌ Error validando carga: {e}")
            return False

    def validar_ia_conversacional(self) -> bool:
        """Valida que la IA conversacional funciona correctamente"""
        print("\n🔍 Validando IA conversacional...")

        try:
            from ia_conversacional_integrada import IAConversacionalIntegrada

            ia = IAConversacionalIntegrada()

            # Verificar que tiene base de conocimiento
            if not ia.base_conocimiento:
                self.reporte["errores"].append(
                    {"tipo": "ia_conversacional", "error": "Base de conocimiento no inicializada"}
                )
                return False

            # Verificar que tiene patrones de respuesta
            patrones = len(ia.patrones_respuesta)
            self.reporte["estadisticas"]["patrones_respuesta"] = patrones

            # Probar procesamiento de mensaje simple
            respuesta = ia.procesar_mensaje("Hola", "test_cliente", "test_sesion")

            if respuesta and respuesta.mensaje:
                self.reporte["validaciones"].append(
                    {
                        "tipo": "ia_conversacional",
                        "estado": "exitoso",
                        "patrones_respuesta": patrones,
                        "respuesta_test": respuesta.mensaje[:50] + "...",
                    }
                )
                print("  ✅ IA conversacional funcionando")
                print(f"     Patrones de respuesta: {patrones}")
                print(f"     Respuesta de prueba: {respuesta.mensaje[:50]}...")
                return True
            else:
                self.reporte["errores"].append(
                    {"tipo": "ia_conversacional", "error": "No se generó respuesta"}
                )
                return False

        except Exception as e:
            self.reporte["errores"].append({"tipo": "ia_conversacional", "error": str(e)})
            print(f"  ❌ Error validando IA: {e}")
            return False

    def validar_productos(self) -> bool:
        """Valida que los productos están integrados"""
        print("\n🔍 Validando productos...")

        try:
            from sistema_cotizaciones import SistemaCotizacionesBMC

            sistema = SistemaCotizacionesBMC()

            productos = list(sistema.productos.keys())
            productos_esperados = ["isodec", "poliestireno", "lana_roca"]

            self.reporte["estadisticas"]["productos_sistema"] = productos

            productos_faltantes = [p for p in productos_esperados if p not in productos]

            if productos_faltantes:
                self.reporte["errores"].append(
                    {"tipo": "productos", "error": f"Productos faltantes: {productos_faltantes}"}
                )
                print(f"  ❌ Productos faltantes: {productos_faltantes}")
                return False
            else:
                self.reporte["validaciones"].append(
                    {"tipo": "productos", "estado": "exitoso", "productos": productos}
                )
                print(f"  ✅ Productos integrados: {', '.join(productos)}")
                return True

        except Exception as e:
            self.reporte["errores"].append({"tipo": "productos", "error": str(e)})
            print(f"  ❌ Error validando productos: {e}")
            return False

    def validar_respuestas_usando_conocimiento(self) -> bool:
        """Valida que las respuestas usan el conocimiento cargado"""
        print("\n🔍 Validando uso de conocimiento en respuestas...")

        try:
            from ia_conversacional_integrada import IAConversacionalIntegrada

            ia = IAConversacionalIntegrada()

            # Probar preguntas que deberían usar conocimiento
            preguntas_test = [
                "Información sobre Isodec",
                "Quiero cotizar",
                "¿Qué productos tienen?",
            ]

            respuestas_mejoradas = 0
            for pregunta in preguntas_test:
                respuesta = ia.procesar_mensaje(pregunta, "test_cliente", "test_sesion")

                # Verificar que la respuesta no es genérica
                respuestas_genericas = [
                    "gracias por tu consulta",
                    "te ayudo con la información",
                    "puedo ayudarte con",
                ]

                mensaje_lower = respuesta.mensaje.lower()
                es_generica = any(gen in mensaje_lower for gen in respuestas_genericas)

                if not es_generica and len(respuesta.mensaje) > 50:
                    respuestas_mejoradas += 1

            self.reporte["estadisticas"]["respuestas_mejoradas"] = respuestas_mejoradas
            self.reporte["estadisticas"]["total_preguntas_test"] = len(preguntas_test)

            if respuestas_mejoradas >= len(preguntas_test) * 0.5:  # Al menos 50%
                self.reporte["validaciones"].append(
                    {
                        "tipo": "uso_conocimiento",
                        "estado": "exitoso",
                        "respuestas_mejoradas": respuestas_mejoradas,
                        "total": len(preguntas_test),
                    }
                )
                print(f"  ✅ {respuestas_mejoradas}/{len(preguntas_test)} respuestas mejoradas")
                return True
            else:
                self.reporte["advertencias"].append(
                    {
                        "tipo": "uso_conocimiento",
                        "mensaje": f"Solo {respuestas_mejoradas}/{len(preguntas_test)} respuestas mejoradas",
                    }
                )
                print(
                    f"  ⚠️  Solo {respuestas_mejoradas}/{len(preguntas_test)} respuestas mejoradas"
                )
                return False

        except Exception as e:
            self.reporte["errores"].append({"tipo": "uso_conocimiento", "error": str(e)})
            print(f"  ❌ Error validando uso de conocimiento: {e}")
            return False

    def validar_todo(self) -> dict[str, Any]:
        """Ejecuta todas las validaciones"""
        print("=" * 70)
        print("VALIDACIÓN DE INTEGRACIÓN")
        print("=" * 70)
        print("")

        resultados = {
            "carga_conocimiento": self.validar_carga_conocimiento(),
            "ia_conversacional": self.validar_ia_conversacional(),
            "productos": self.validar_productos(),
            "uso_conocimiento": self.validar_respuestas_usando_conocimiento(),
        }

        self.reporte["resultados"] = resultados
        self.reporte["exitoso"] = all(resultados.values())

        return self.reporte

    def generar_reporte_texto(self) -> str:
        """Genera reporte en texto"""
        reporte = []
        reporte.append("=" * 70)
        reporte.append("REPORTE DE VALIDACIÓN")
        reporte.append("=" * 70)
        reporte.append("")

        # Resultados
        resultados = self.reporte.get("resultados", {})
        reporte.append("RESULTADOS:")
        for tipo, resultado in resultados.items():
            estado = "✅" if resultado else "❌"
            reporte.append(f"  {estado} {tipo}: {'Exitoso' if resultado else 'Fallido'}")
        reporte.append("")

        # Estadísticas
        estadisticas = self.reporte.get("estadisticas", {})
        if estadisticas:
            reporte.append("ESTADÍSTICAS:")
            for key, value in estadisticas.items():
                reporte.append(f"  {key}: {value}")
            reporte.append("")

        # Errores
        if self.reporte["errores"]:
            reporte.append("ERRORES:")
            for error in self.reporte["errores"]:
                reporte.append(f"  ❌ {error['tipo']}: {error.get('error', '')}")
            reporte.append("")

        # Advertencias
        if self.reporte["advertencias"]:
            reporte.append("ADVERTENCIAS:")
            for adv in self.reporte["advertencias"]:
                reporte.append(f"  ⚠️  {adv['tipo']}: {adv.get('mensaje', '')}")
            reporte.append("")

        # Estado final
        if self.reporte.get("exitoso", False):
            reporte.append("✅ VALIDACIÓN EXITOSA")
        else:
            reporte.append("❌ VALIDACIÓN FALLIDA - Revisar errores")

        return "\n".join(reporte)

    def guardar_reporte(self, archivo: str = "reporte_validacion.json"):
        """Guarda el reporte"""
        import json

        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(self.reporte, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n✅ Reporte guardado en: {archivo}")


def main():
    """Función principal"""
    validador = ValidadorIntegracion()
    validador.validar_todo()

    print("\n" + validador.generar_reporte_texto())

    validador.guardar_reporte()

    # Guardar en texto
    with open("reporte_validacion.txt", "w", encoding="utf-8") as f:
        f.write(validador.generar_reporte_texto())
    print("✅ Reporte en texto guardado en: reporte_validacion.txt")

    # Exit code basado en resultado
    sys.exit(0 if validador.reporte.get("exitoso", False) else 1)


if __name__ == "__main__":
    main()
