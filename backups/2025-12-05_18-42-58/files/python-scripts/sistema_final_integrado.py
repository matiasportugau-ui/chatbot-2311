#!/usr/bin/env python3
"""
Sistema Final Integrado BMC Uruguay
Sistema completo de cotizaciones con IA conversacional, WhatsApp y Google Sheets
"""

import argparse
import datetime
import json
import time
from typing import Any

from ia_conversacional_integrada import IAConversacionalIntegrada
from integracion_google_sheets import IntegracionGoogleSheets
from integracion_whatsapp import IntegracionWhatsApp


class SistemaFinalIntegrado:
    """Sistema final integrado con todas las funcionalidades"""

    def __init__(self):
        print("🎯 SISTEMA FINAL INTEGRADO BMC URUGUAY")
        print("Sistema Completo de Cotizaciones con IA Conversacional")
        print("=" * 80)

        # Inicializar componentes principales
        self.ia_conversacional = IAConversacionalIntegrada()
        self.base_conocimiento = self.ia_conversacional.base_conocimiento
        self.motor_analisis = self.ia_conversacional.motor_analisis

        # Inicializar integraciones
        self.whatsapp = IntegracionWhatsApp(self.ia_conversacional)
        self.google_sheets = IntegracionGoogleSheets(self.ia_conversacional)

        # Estado del sistema
        self.activo = False
        self.modo_demo = True

        print("✅ Sistema inicializado correctamente")
        self._mostrar_estado_inicial()

    def _mostrar_estado_inicial(self):
        """Muestra el estado inicial del sistema"""
        print("\n📊 ESTADO INICIAL DEL SISTEMA")
        print("-" * 50)
        print("🤖 IA Conversacional: Activa")
        print("📱 Integración WhatsApp: Configurada")
        print("📊 Integración Google Sheets: Configurada")
        print(f"📚 Base de Conocimiento: {len(self.base_conocimiento.interacciones)} interacciones")
        print(f"📈 Patrones de Venta: {len(self.base_conocimiento.patrones_venta)} identificados")
        print(
            f"💡 Insights Automáticos: {len(self.base_conocimiento.insights_automaticos)} generados"
        )
        print("🔄 Sistema de Aprendizaje: Activo")

    def ejecutar_demo_completo(self):
        """Ejecuta una demostración completa del sistema"""
        print("\n🎭 DEMOSTRACIÓN COMPLETA DEL SISTEMA")
        print("=" * 60)

        # 1. Demo de IA Conversacional
        self._demo_ia_conversacional()

        # 2. Demo de integración WhatsApp
        self._demo_whatsapp()

        # 3. Demo de integración Google Sheets
        self._demo_google_sheets()

        # 4. Demo de análisis y métricas
        self._demo_analisis_metricas()

        # 5. Exportar todo el conocimiento
        self._exportar_conocimiento_completo()

        print("\n🎉 DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
        print("El sistema ha demostrado todas sus funcionalidades:")
        print("• IA Conversacional inteligente")
        print("• Integración con WhatsApp Business")
        print("• Sincronización con Google Sheets")
        print("• Análisis automático de conversiones")
        print("• Aprendizaje continuo y evolución")
        print("• Exportación de conocimiento")

    def _demo_ia_conversacional(self):
        """Demo de la IA conversacional"""
        print("\n🤖 DEMO - IA CONVERSACIONAL")
        print("-" * 40)

        cliente_id = "demo_cliente"
        sesion_id = f"demo_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        mensajes_demo = [
            "Hola, necesito información sobre Isodec para mi casa",
            "Quiero cotizar para 10 metros por 5 metros, 100mm, blanco",
            "El precio me parece caro, ¿hay descuentos?",
            "Perfecto, procedo con la compra",
        ]

        for i, mensaje in enumerate(mensajes_demo, 1):
            print(f"👤 Cliente: {mensaje}")
            respuesta = self.ia_conversacional.procesar_mensaje(mensaje, cliente_id, sesion_id)
            print(f"🤖 IA: {respuesta.mensaje}")
            print(f"   Confianza: {respuesta.confianza:.2f}")
            print()
            time.sleep(0.5)

    def _demo_whatsapp(self):
        """Demo de integración WhatsApp"""
        print("\n📱 DEMO - INTEGRACIÓN WHATSAPP")
        print("-" * 40)

        mensajes_whatsapp = [
            {
                "phone": "59899123456",
                "name": "Juan Pérez",
                "message": "Hola, necesito cotizar Isodec para mi casa",
            },
            {
                "phone": "59899765432",
                "name": "María García",
                "message": "¿Cuál es el precio de poliestireno 75mm?",
            },
        ]

        for mensaje in mensajes_whatsapp:
            print(f"📱 WhatsApp - {mensaje['name']}: {mensaje['message']}")
            respuesta = self.whatsapp.simular_mensaje_whatsapp(
                mensaje["phone"], mensaje["name"], mensaje["message"]
            )
            print(f"🤖 Respuesta: {respuesta.mensaje}")
            print()

    def _demo_google_sheets(self):
        """Demo de integración Google Sheets"""
        print("\n📊 DEMO - INTEGRACIÓN GOOGLE SHEETS")
        print("-" * 40)

        # Sincronizar cotizaciones
        self.google_sheets.sincronizar_cotizaciones()

        # Generar reporte
        reporte = self.google_sheets.generar_reporte_cotizaciones()
        print(f"📈 Reporte generado: {reporte['total_cotizaciones']} cotizaciones")

    def _demo_analisis_metricas(self):
        """Demo de análisis y métricas"""
        print("\n📊 DEMO - ANÁLISIS Y MÉTRICAS")
        print("-" * 40)

        # Mostrar métricas actuales
        metricas = self._calcular_metricas_completas()
        print("📈 Métricas del Sistema:")
        for clave, valor in metricas.items():
            print(f"   {clave}: {valor}")

        # Mostrar insights
        print(f"\n💡 Insights Generados: {len(self.base_conocimiento.insights_automaticos)}")
        for i, insight in enumerate(self.base_conocimiento.insights_automaticos[:3], 1):
            print(f"   {i}. {insight.get('descripcion', 'Sin descripción')}")

        # Mostrar patrones de venta
        print(f"\n📈 Patrones de Venta: {len(self.base_conocimiento.patrones_venta)}")
        for i, patron in enumerate(self.base_conocimiento.patrones_venta[:3], 1):
            print(f"   {i}. {patron.nombre} (Éxito: {patron.tasa_exito:.2%})")

    def _calcular_metricas_completas(self) -> dict[str, Any]:
        """Calcula métricas completas del sistema"""
        # Métricas básicas
        total_interacciones = len(self.base_conocimiento.interacciones)
        total_patrones = len(self.base_conocimiento.patrones_venta)
        total_insights = len(self.base_conocimiento.insights_automaticos)

        # Satisfacción promedio
        satisfacciones = [
            i.satisfaccion_cliente
            for i in self.base_conocimiento.interacciones
            if i.satisfaccion_cliente
        ]
        satisfaccion_promedio = sum(satisfacciones) / len(satisfacciones) if satisfacciones else 0.0

        # Tasa de conversión
        total_cotizaciones = len(
            [i for i in self.base_conocimiento.interacciones if i.tipo_interaccion == "cotizacion"]
        )
        total_ventas = len(
            [i for i in self.base_conocimiento.interacciones if i.tipo_interaccion == "venta"]
        )
        tasa_conversion = total_ventas / total_cotizaciones if total_cotizaciones > 0 else 0.0

        # Conversaciones activas
        conversaciones_activas = len(self.ia_conversacional.conversaciones_activas)

        return {
            "total_interacciones": total_interacciones,
            "total_patrones_venta": total_patrones,
            "total_insights": total_insights,
            "conversaciones_activas": conversaciones_activas,
            "satisfaccion_promedio": f"{satisfaccion_promedio:.2f}/5",
            "tasa_conversion": f"{tasa_conversion:.2%}",
            "sistema_activo": self.activo,
            "modo_demo": self.modo_demo,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        }

    def _exportar_conocimiento_completo(self):
        """Exporta todo el conocimiento del sistema"""
        print("\n💾 EXPORTANDO CONOCIMIENTO COMPLETO")
        print("-" * 40)

        try:
            # Exportar base de conocimiento
            self.base_conocimiento.exportar_conocimiento("base_conocimiento_final.json")
            print("✅ Base de conocimiento exportada")

            # Exportar análisis de conversiones
            self.motor_analisis.exportar_analisis("analisis_conversiones_final.json")
            print("✅ Análisis de conversiones exportado")

            # Exportar IA conversacional
            self.ia_conversacional.exportar_conocimiento_ia("ia_conversacional_final.json")
            print("✅ IA conversacional exportada")

            # Exportar métricas del sistema
            metricas = self._calcular_metricas_completas()
            with open("metricas_sistema_final.json", "w", encoding="utf-8") as f:
                json.dump(metricas, f, ensure_ascii=False, indent=2, default=str)
            print("✅ Métricas del sistema exportadas")

            print("✅ Conocimiento completo exportado exitosamente")

        except Exception as e:
            print(f"❌ Error exportando conocimiento: {e}")

    def iniciar_sistema_produccion(self):
        """Inicia el sistema en modo producción"""
        print("\n🚀 INICIANDO SISTEMA EN MODO PRODUCCIÓN")
        print("=" * 60)

        try:
            self.activo = True
            self.modo_demo = False

            print("✅ Sistema iniciado en modo producción")
            print("📱 Servidor WhatsApp: http://localhost:5000")
            print("📊 Estado del sistema: http://localhost:5000/estado_sistema")
            print("🔄 Sincronización Google Sheets: Activa")
            print("🤖 IA Conversacional: Activa")

            # Iniciar servidor WhatsApp
            self.whatsapp.iniciar_servidor()

        except Exception as e:
            print(f"❌ Error iniciando sistema: {e}")

    def mostrar_menu_principal(self):
        """Muestra el menú principal del sistema"""
        print("\n🎯 MENÚ PRINCIPAL - SISTEMA BMC URUGUAY")
        print("=" * 50)
        print("1. Ejecutar Demo Completo")
        print("2. Iniciar Sistema Producción")
        print("3. Mostrar Estado del Sistema")
        print("4. Exportar Conocimiento")
        print("5. Salir")
        print("-" * 50)

    def ejecutar_menu_interactivo(self):
        """Ejecuta el menú interactivo del sistema"""
        while True:
            self.mostrar_menu_principal()

            try:
                opcion = input("Selecciona una opción (1-5): ").strip()

                if opcion == "1":
                    self.ejecutar_demo_completo()
                elif opcion == "2":
                    self.iniciar_sistema_produccion()
                elif opcion == "3":
                    self._mostrar_estado_sistema()
                elif opcion == "4":
                    self._exportar_conocimiento_completo()
                elif opcion == "5":
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción inválida. Intenta de nuevo.")

                input("\nPresiona Enter para continuar...")

            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def _mostrar_estado_sistema(self):
        """Muestra el estado actual del sistema"""
        print("\n📊 ESTADO ACTUAL DEL SISTEMA")
        print("=" * 50)

        metricas = self._calcular_metricas_completas()
        for clave, valor in metricas.items():
            print(f"{clave}: {valor}")


def main():
    """Función principal del sistema"""
    parser = argparse.ArgumentParser(description="Sistema Final Integrado BMC Uruguay")
    parser.add_argument("--demo", action="store_true", help="Ejecutar demo completo")
    parser.add_argument("--produccion", action="store_true", help="Iniciar en modo producción")
    parser.add_argument("--interactivo", action="store_true", help="Modo interactivo")

    args = parser.parse_args()

    # Crear sistema
    sistema = SistemaFinalIntegrado()

    if args.demo:
        # Modo demo
        sistema.ejecutar_demo_completo()
    elif args.produccion:
        # Modo producción
        sistema.iniciar_sistema_produccion()
    elif args.interactivo:
        # Modo interactivo
        sistema.ejecutar_menu_interactivo()
    else:
        # Modo por defecto - demo
        print("Ejecutando demo por defecto...")
        sistema.ejecutar_demo_completo()


if __name__ == "__main__":
    main()
