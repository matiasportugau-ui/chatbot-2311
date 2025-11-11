#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo del Sistema Completo Integrado BMC Uruguay
Demostración del sistema de cotizaciones con IA conversacional
"""

import json
import datetime
import time
from typing import Dict, List, Any, Optional
from decimal import Decimal

from base_conocimiento_dinamica import BaseConocimientoDinamica
from motor_analisis_conversiones import MotorAnalisisConversiones
from ia_conversacional_integrada import IAConversacionalIntegrada
from sistema_cotizaciones import SistemaCotizacionesBMC


class DemoSistemaCompleto:
    """Demo del sistema completo integrado"""
    
    def __init__(self):
        print("🎯 DEMO - SISTEMA COMPLETO INTEGRADO BMC URUGUAY")
        print("Sistema de Cotizaciones con IA Conversacional que Aprende y Evoluciona")
        print("=" * 80)
        
        # Inicializar componentes
        self.ia_conversacional = IAConversacionalIntegrada()
        self.sistema_cotizaciones = self.ia_conversacional.sistema_cotizaciones
        self.base_conocimiento = self.ia_conversacional.base_conocimiento
        self.motor_analisis = self.ia_conversacional.motor_analisis
        
        print("✅ Sistema inicializado correctamente")
        self._mostrar_estado_inicial()
    
    def _mostrar_estado_inicial(self):
        """Muestra el estado inicial del sistema"""
        print("\n📊 ESTADO INICIAL DEL SISTEMA")
        print("-" * 40)
        print(f"🤖 IA Conversacional: Activa")
        print(f"📚 Base de Conocimiento: {len(self.base_conocimiento.interacciones)} interacciones")
        print(f"📈 Patrones de Venta: {len(self.base_conocimiento.patrones_venta)} identificados")
        print(f"💡 Insights Automáticos: {len(self.base_conocimiento.insights_automaticos)} generados")
        print(f"🔄 Sistema de Aprendizaje: Activo")
    
    def simular_conversacion_completa(self):
        """Simula una conversación completa para demostrar el sistema"""
        print("\n🎭 SIMULACIÓN DE CONVERSACIÓN COMPLETA")
        print("=" * 50)
        
        cliente_id = "cliente_demo"
        sesion_id = f"demo_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Mensajes de simulación
        mensajes_simulados = [
            "Hola, necesito información sobre Isodec para mi casa",
            "Quiero cotizar para 10 metros por 5 metros, 100mm, blanco",
            "Perfecto, me parece bien el precio. ¿Incluye instalación?",
            "Excelente, procedo con la compra"
        ]
        
        print(f"👤 Cliente: {cliente_id}")
        print(f"🆔 Sesión: {sesion_id}")
        print()
        
        for i, mensaje in enumerate(mensajes_simulados, 1):
            print(f"📝 Mensaje {i}: {mensaje}")
            
            # Procesar mensaje
            respuesta = self.ia_conversacional.procesar_mensaje(mensaje, cliente_id, sesion_id)
            
            print(f"🤖 IA: {respuesta.mensaje}")
            print(f"   Confianza: {respuesta.confianza:.2f}")
            print(f"   Fuentes: {', '.join(respuesta.fuentes_conocimiento)}")
            print()
            time.sleep(1)  # Pausa para simular tiempo real
        
        # Mostrar métricas finales
        print("📊 MÉTRICAS FINALES DE LA SIMULACIÓN")
        print("-" * 40)
        self._mostrar_metricas_actuales()
    
    def _mostrar_metricas_actuales(self):
        """Muestra las métricas actuales del sistema"""
        metricas = self._calcular_metricas_actuales()
        for clave, valor in metricas.items():
            print(f"{clave}: {valor}")
    
    def _calcular_metricas_actuales(self) -> Dict[str, Any]:
        """Calcula las métricas actuales del sistema"""
        # Calcular satisfacción promedio
        satisfacciones = [
            i.satisfaccion_cliente for i in self.base_conocimiento.interacciones
            if i.satisfaccion_cliente
        ]
        satisfaccion_promedio = sum(satisfacciones) / len(satisfacciones) if satisfacciones else 0.0
        
        # Calcular tasa de conversión
        total_cotizaciones = len([
            i for i in self.base_conocimiento.interacciones
            if i.tipo_interaccion == "cotizacion"
        ])
        total_ventas = len([
            i for i in self.base_conocimiento.interacciones
            if i.tipo_interaccion == "venta"
        ])
        tasa_conversion = total_ventas / total_cotizaciones if total_cotizaciones > 0 else 0.0
        
        return {
            "total_interacciones": len(self.base_conocimiento.interacciones),
            "total_patrones_venta": len(self.base_conocimiento.patrones_venta),
            "total_insights": len(self.base_conocimiento.insights_automaticos),
            "conversaciones_activas": len(self.ia_conversacional.conversaciones_activas),
            "satisfaccion_promedio": f"{satisfaccion_promedio:.2f}/5",
            "tasa_conversion": f"{tasa_conversion:.2%}",
            "ultima_actualizacion": datetime.datetime.now().strftime("%H:%M:%S")
        }
    
    def mostrar_insights_automaticos(self):
        """Muestra los insights automáticos generados por el sistema"""
        print("\n💡 INSIGHTS AUTOMÁTICOS DEL SISTEMA")
        print("=" * 50)
        
        if not self.base_conocimiento.insights_automaticos:
            print("No hay insights disponibles aún.")
            return
        
        for i, insight in enumerate(self.base_conocimiento.insights_automaticos, 1):
            print(f"\n{i}. {insight.get('descripcion', 'Sin descripción')}")
            if 'recomendacion' in insight:
                print(f"   💡 Recomendación: {insight['recomendacion']}")
            if 'timestamp' in insight:
                print(f"   📅 Fecha: {insight['timestamp']}")
    
    def mostrar_patrones_venta_exitosos(self):
        """Muestra los patrones de venta exitosos identificados"""
        print("\n📈 PATRONES DE VENTA EXITOSOS")
        print("=" * 50)
        
        if not self.base_conocimiento.patrones_venta:
            print("No hay patrones identificados aún.")
            return
        
        for i, patron in enumerate(self.base_conocimiento.patrones_venta, 1):
            print(f"\n{i}. {patron.nombre}")
            print(f"   📊 Frecuencia: {patron.frecuencia}")
            print(f"   🎯 Tasa de Éxito: {patron.tasa_exito:.2%}")
            print(f"   🔑 Factores Clave: {', '.join(patron.factores_clave)}")
            print(f"   📝 Estrategia: {patron.estrategia_recomendada}")
    
    def demostrar_aprendizaje_automatico(self):
        """Demuestra cómo el sistema aprende automáticamente"""
        print("\n🧠 DEMOSTRACIÓN DE APRENDIZAJE AUTOMÁTICO")
        print("=" * 50)
        
        # Simular varias interacciones para mostrar el aprendizaje
        interacciones_demo = [
            {
                "mensaje": "El precio de Isodec es muy caro",
                "respuesta": "Entiendo tu preocupación. Te explico el valor a largo plazo...",
                "resultado": "exitoso",
                "satisfaccion": 5
            },
            {
                "mensaje": "Necesito información técnica sobre Isodec",
                "respuesta": "Isodec es un panel aislante con núcleo EPS...",
                "resultado": "exitoso",
                "satisfaccion": 4
            },
            {
                "mensaje": "¿Cuánto tiempo tarda la instalación?",
                "respuesta": "La instalación tarda entre 1-2 días dependiendo del tamaño...",
                "resultado": "exitoso",
                "satisfaccion": 4
            }
        ]
        
        print("Simulando interacciones para demostrar el aprendizaje...")
        
        for i, interaccion in enumerate(interacciones_demo, 1):
            print(f"\n📝 Interacción {i}: {interaccion['mensaje']}")
            
            # Crear interacción simulada
            from base_conocimiento_dinamica import InteraccionCliente
            interaccion_obj = InteraccionCliente(
                id=f"demo_{i}",
                timestamp=datetime.datetime.now(),
                cliente_id=f"cliente_demo_{i}",
                tipo_interaccion="consulta",
                mensaje_cliente=interaccion['mensaje'],
                respuesta_agente=interaccion['respuesta'],
                contexto={"producto": "isodec", "demo": True},
                resultado=interaccion['resultado'],
                satisfaccion_cliente=interaccion['satisfaccion']
            )
            
            # Registrar en base de conocimiento
            self.base_conocimiento.registrar_interaccion(interaccion_obj)
            
            print(f"🤖 Respuesta: {interaccion['respuesta']}")
            print(f"✅ Resultado: {interaccion['resultado']}")
            print(f"⭐ Satisfacción: {interaccion['satisfaccion']}/5")
        
        print("\n📊 MÉTRICAS DESPUÉS DEL APRENDIZAJE")
        print("-" * 40)
        self._mostrar_metricas_actuales()
    
    def exportar_conocimiento_completo(self, archivo: str = "conocimiento_completo_demo.json"):
        """Exporta todo el conocimiento del sistema"""
        print(f"\n💾 EXPORTANDO CONOCIMIENTO COMPLETO")
        print("=" * 50)
        
        try:
            # Exportar base de conocimiento
            self.base_conocimiento.exportar_conocimiento("base_conocimiento_demo.json")
            print("✅ Base de conocimiento exportada")
            
            # Exportar análisis de conversiones
            self.motor_analisis.exportar_analisis("analisis_conversiones_demo.json")
            print("✅ Análisis de conversiones exportado")
            
            # Exportar IA conversacional
            self.ia_conversacional.exportar_conocimiento_ia("ia_conversacional_demo.json")
            print("✅ IA conversacional exportada")
            
            # Exportar métricas del sistema
            metricas_completas = {
                "fecha_exportacion": datetime.datetime.now().isoformat(),
                "sistema_activo": True,
                "metricas_actuales": self._calcular_metricas_actuales(),
                "descripcion": "Demo del Sistema Completo Integrado BMC Uruguay"
            }
            
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(metricas_completas, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ Conocimiento completo exportado a {archivo}")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando conocimiento: {e}")
            return False
    
    def ejecutar_demo_completo(self):
        """Ejecuta la demostración completa del sistema"""
        print("\n🚀 INICIANDO DEMOSTRACIÓN COMPLETA")
        print("=" * 50)
        
        # 1. Simular conversación
        self.simular_conversacion_completa()
        
        # 2. Demostrar aprendizaje automático
        self.demostrar_aprendizaje_automatico()
        
        # 3. Mostrar insights
        self.mostrar_insights_automaticos()
        
        # 4. Mostrar patrones de venta
        self.mostrar_patrones_venta_exitosos()
        
        # 5. Exportar conocimiento
        self.exportar_conocimiento_completo()
        
        print("\n🎉 DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
        print("El sistema ha demostrado:")
        print("• Procesamiento de mensajes con IA")
        print("• Aprendizaje automático de interacciones")
        print("• Generación de insights inteligentes")
        print("• Identificación de patrones de venta")
        print("• Exportación de conocimiento")
        
        print("\n✅ Sistema listo para uso en producción")


def main():
    """Función principal para ejecutar el demo"""
    # Crear demo
    demo = DemoSistemaCompleto()
    
    # Ejecutar demo completo
    demo.ejecutar_demo_completo()


if __name__ == "__main__":
    main()
