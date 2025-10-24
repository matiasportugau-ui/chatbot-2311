#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Completo Integrado BMC Uruguay
Sistema de cotizaciones con IA conversacional que aprende y evoluciona
"""

import json
import datetime
import threading
import time
from typing import Dict, List, Any, Optional
from decimal import Decimal

from base_conocimiento_dinamica import BaseConocimientoDinamica
from motor_analisis_conversiones import MotorAnalisisConversiones
from ia_conversacional_integrada import IAConversacionalIntegrada
from sistema_actualizacion_automatica import SistemaActualizacionAutomatica
from sistema_cotizaciones import SistemaCotizacionesBMC


class SistemaCompletoIntegrado:
    """Sistema completo que integra todos los componentes"""
    
    def __init__(self):
        print("🚀 Iniciando Sistema Completo Integrado BMC Uruguay")
        print("=" * 60)
        
        # Inicializar componentes
        self.ia_conversacional = IAConversacionalIntegrada()
        self.sistema_actualizacion = SistemaActualizacionAutomatica(self.ia_conversacional)
        self.sistema_cotizaciones = self.ia_conversacional.sistema_cotizaciones
        self.base_conocimiento = self.ia_conversacional.base_conocimiento
        self.motor_analisis = self.ia_conversacional.motor_analisis
        
        # Estado del sistema
        self.activo = False
        self.metricas_sistema = {}
        
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
        print(f"🔄 Sistema de Actualización: Listo")
    
    def iniciar_sistema_completo(self):
        """Inicia el sistema completo con todas las funcionalidades"""
        print("\n🚀 INICIANDO SISTEMA COMPLETO")
        print("=" * 50)
        
        try:
            # Iniciar sistema de actualización automática
            self.sistema_actualizacion.iniciar_sistema_actualizacion()
            print("✅ Sistema de actualización automática iniciado")
            
            # Marcar sistema como activo
            self.activo = True
            
            # Mostrar estado
            self._mostrar_estado_sistema()
            
            print("\n🎉 SISTEMA COMPLETO ACTIVO")
            print("El sistema ahora:")
            print("• Aprende de cada interacción")
            print("• Se actualiza automáticamente")
            print("• Mejora sus respuestas constantemente")
            print("• Analiza tendencias de ventas")
            print("• Genera insights automáticos")
            
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando sistema: {e}")
            return False
    
    def detener_sistema_completo(self):
        """Detiene el sistema completo"""
        print("\n🛑 DETENIENDO SISTEMA COMPLETO")
        print("=" * 50)
        
        try:
            # Detener sistema de actualización
            self.sistema_actualizacion.detener_sistema_actualizacion()
            print("✅ Sistema de actualización detenido")
            
            # Marcar sistema como inactivo
            self.activo = False
            
            print("✅ Sistema detenido correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error deteniendo sistema: {e}")
            return False
    
    def procesar_mensaje_cliente(self, mensaje: str, cliente_id: str, sesion_id: str = None) -> Dict[str, Any]:
        """Procesa un mensaje del cliente y retorna respuesta completa"""
        if not self.activo:
            return {
                "error": "Sistema no está activo",
                "mensaje": "El sistema no está funcionando. Por favor, inicia el sistema primero."
            }
        
        try:
            # Procesar mensaje con IA
            respuesta_ia = self.ia_conversacional.procesar_mensaje(mensaje, cliente_id, sesion_id)
            
            # Obtener métricas actuales
            metricas = self._obtener_metricas_actuales()
            
            # Preparar respuesta completa
            respuesta_completa = {
                "mensaje": respuesta_ia.mensaje,
                "tipo_respuesta": respuesta_ia.tipo_respuesta,
                "confianza": respuesta_ia.confianza,
                "fuentes_conocimiento": respuesta_ia.fuentes_conocimiento,
                "metricas_sistema": metricas,
                "timestamp": respuesta_ia.timestamp.isoformat(),
                "sistema_activo": self.activo
            }
            
            return respuesta_completa
            
        except Exception as e:
            return {
                "error": f"Error procesando mensaje: {e}",
                "mensaje": "Lo siento, hubo un error procesando tu mensaje. Por favor, intenta de nuevo.",
                "sistema_activo": self.activo
            }
    
    def _obtener_metricas_actuales(self) -> Dict[str, Any]:
        """Obtiene las métricas actuales del sistema"""
        return {
            "total_interacciones": len(self.base_conocimiento.interacciones),
            "total_patrones_venta": len(self.base_conocimiento.patrones_venta),
            "total_insights": len(self.base_conocimiento.insights_automaticos),
            "conversaciones_activas": len(self.ia_conversacional.conversaciones_activas),
            "satisfaccion_promedio": self._calcular_satisfaccion_promedio(),
            "tasa_conversion": self._calcular_tasa_conversion(),
            "ultima_actualizacion": datetime.datetime.now().isoformat()
        }
    
    def _calcular_satisfaccion_promedio(self) -> float:
        """Calcula la satisfacción promedio de los clientes"""
        satisfacciones = [
            i.satisfaccion_cliente for i in self.base_conocimiento.interacciones
            if i.satisfaccion_cliente
        ]
        return sum(satisfacciones) / len(satisfacciones) if satisfacciones else 0.0
    
    def _calcular_tasa_conversion(self) -> float:
        """Calcula la tasa de conversión de cotizaciones a ventas"""
        total_cotizaciones = len([
            i for i in self.base_conocimiento.interacciones
            if i.tipo_interaccion == "cotizacion"
        ])
        total_ventas = len([
            i for i in self.base_conocimiento.interacciones
            if i.tipo_interaccion == "venta"
        ])
        return total_ventas / total_cotizaciones if total_cotizaciones > 0 else 0.0
    
    def _mostrar_estado_sistema(self):
        """Muestra el estado actual del sistema"""
        print("\n📊 ESTADO ACTUAL DEL SISTEMA")
        print("-" * 40)
        metricas = self._obtener_metricas_actuales()
        print(f"🔄 Sistema: {'Activo' if self.activo else 'Inactivo'}")
        print(f"💬 Interacciones: {metricas['total_interacciones']}")
        print(f"📈 Patrones de Venta: {metricas['total_patrones_venta']}")
        print(f"💡 Insights: {metricas['total_insights']}")
        print(f"🎯 Satisfacción Promedio: {metricas['satisfaccion_promedio']:.2f}/5")
        print(f"📊 Tasa de Conversión: {metricas['tasa_conversion']:.2%}")
    
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
            respuesta = self.procesar_mensaje_cliente(mensaje, cliente_id, sesion_id)
            
            if "error" in respuesta:
                print(f"❌ Error: {respuesta['error']}")
            else:
                print(f"🤖 IA: {respuesta['mensaje']}")
                print(f"   Confianza: {respuesta['confianza']:.2f}")
                print(f"   Fuentes: {', '.join(respuesta['fuentes_conocimiento'])}")
            
            print()
            time.sleep(1)  # Pausa para simular tiempo real
        
        # Mostrar métricas finales
        print("📊 MÉTRICAS FINALES DE LA SIMULACIÓN")
        print("-" * 40)
        metricas = self._obtener_metricas_actuales()
        for clave, valor in metricas.items():
            print(f"{clave}: {valor}")
    
    def exportar_conocimiento_completo(self, archivo: str = "conocimiento_completo.json"):
        """Exporta todo el conocimiento del sistema"""
        print(f"\n💾 EXPORTANDO CONOCIMIENTO COMPLETO")
        print("=" * 50)
        
        try:
            # Exportar base de conocimiento
            self.base_conocimiento.exportar_conocimiento("base_conocimiento_exportada.json")
            print("✅ Base de conocimiento exportada")
            
            # Exportar análisis de conversiones
            self.motor_analisis.exportar_analisis("analisis_conversiones_exportado.json")
            print("✅ Análisis de conversiones exportado")
            
            # Exportar IA conversacional
            self.ia_conversacional.exportar_conocimiento_ia("ia_conversacional_exportada.json")
            print("✅ IA conversacional exportada")
            
            # Exportar métricas del sistema
            metricas_completas = {
                "fecha_exportacion": datetime.datetime.now().isoformat(),
                "sistema_activo": self.activo,
                "metricas_actuales": self._obtener_metricas_actuales(),
                "configuracion_actualizacion": self.sistema_actualizacion.configuracion,
                "estado_sistema_actualizacion": self.sistema_actualizacion.obtener_estado_sistema()
            }
            
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(metricas_completas, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ Conocimiento completo exportado a {archivo}")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando conocimiento: {e}")
            return False
    
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


def main():
    """Función principal para ejecutar el sistema completo"""
    print("🎯 SISTEMA COMPLETO INTEGRADO BMC URUGUAY")
    print("Sistema de Cotizaciones con IA Conversacional que Aprende y Evoluciona")
    print("=" * 80)
    
    # Crear sistema
    sistema = SistemaCompletoIntegrado()
    
    # Iniciar sistema
    if sistema.iniciar_sistema_completo():
        print("\n🎉 Sistema iniciado exitosamente!")
        
        # Simular conversación
        sistema.simular_conversacion_completa()
        
        # Mostrar insights
        sistema.mostrar_insights_automaticos()
        
        # Mostrar patrones de venta
        sistema.mostrar_patrones_venta_exitosos()
        
        # Exportar conocimiento
        sistema.exportar_conocimiento_completo()
        
        print("\n✅ Sistema funcionando correctamente")
        print("El sistema continuará aprendiendo y evolucionando automáticamente.")
        
        # Mantener sistema activo
        try:
            while True:
                time.sleep(60)
                print(f"⏰ Sistema activo - {datetime.datetime.now().strftime('%H:%M:%S')}")
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo sistema...")
            sistema.detener_sistema_completo()
            print("✅ Sistema detenido correctamente")
    else:
        print("❌ No se pudo iniciar el sistema")


if __name__ == "__main__":
    main()
