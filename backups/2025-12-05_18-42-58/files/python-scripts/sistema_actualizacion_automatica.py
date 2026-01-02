#!/usr/bin/env python3
"""
Sistema de Actualización Automática BMC Uruguay
Actualiza constantemente el conocimiento basado en interacciones y ventas
"""

import datetime
import json
import logging
import statistics
import threading
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any

import schedule

from ia_conversacional_integrada import IAConversacionalIntegrada


@dataclass
class ActualizacionSistema:
    """Registro de actualización del sistema"""

    timestamp: datetime.datetime
    tipo_actualizacion: str
    elementos_actualizados: int
    nuevos_insights: int
    metricas_mejoradas: dict[str, Any]
    recomendaciones_generadas: list[str]
    estado_sistema: str


class SistemaActualizacionAutomatica:
    """Sistema que actualiza automáticamente el conocimiento"""

    def __init__(self, ia_conversacional: IAConversacionalIntegrada):
        self.ia = ia_conversacional
        self.base_conocimiento = ia_conversacional.base_conocimiento
        self.motor_analisis = ia_conversacional.motor_analisis
        self.actualizaciones_realizadas = []
        self.configuracion = self._cargar_configuracion()
        self.logger = self._configurar_logging()
        self.ejecutando = False

    def _cargar_configuracion(self) -> dict[str, Any]:
        """Carga la configuración del sistema de actualización"""
        return {
            "frecuencia_actualizacion_minutos": 30,
            "frecuencia_analisis_horas": 6,
            "frecuencia_limpieza_dias": 1,
            "frecuencia_exportacion_horas": 12,
            "umbral_satisfaccion_minimo": 3.0,
            "umbral_confianza_respuesta": 0.7,
            "max_interacciones_por_cliente": 100,
            "dias_retencion_datos": 90,
            "archivos_exportacion": {
                "base_conocimiento": "base_conocimiento_actualizada.json",
                "analisis_conversiones": "analisis_conversiones_actualizado.json",
                "ia_conversacional": "ia_conversacional_actualizada.json",
                "metricas_sistema": "metricas_sistema.json",
            },
        }

    def _configurar_logging(self) -> logging.Logger:
        """Configura el sistema de logging"""
        logger = logging.getLogger("SistemaActualizacion")
        logger.setLevel(logging.INFO)

        # Crear handler para archivo
        handler = logging.FileHandler("sistema_actualizacion.log")
        handler.setLevel(logging.INFO)

        # Crear formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        return logger

    def iniciar_sistema_actualizacion(self):
        """Inicia el sistema de actualización automática"""
        self.logger.info("Iniciando sistema de actualización automática")
        self.ejecutando = True

        # Programar tareas
        schedule.every(self.configuracion["frecuencia_actualizacion_minutos"]).minutes.do(
            self._actualizar_conocimiento
        )
        schedule.every(self.configuracion["frecuencia_analisis_horas"]).hours.do(
            self._analizar_tendencias
        )
        schedule.every(self.configuracion["frecuencia_limpieza_dias"]).days.do(
            self._limpiar_datos_obsoletos
        )
        schedule.every(self.configuracion["frecuencia_exportacion_horas"]).hours.do(
            self._exportar_conocimiento
        )

        # Ejecutar tareas en hilo separado
        hilo_actualizacion = threading.Thread(target=self._ejecutar_tareas_programadas)
        hilo_actualizacion.daemon = True
        hilo_actualizacion.start()

        self.logger.info("Sistema de actualización iniciado correctamente")

    def detener_sistema_actualizacion(self):
        """Detiene el sistema de actualización automática"""
        self.logger.info("Deteniendo sistema de actualización automática")
        self.ejecutando = False
        schedule.clear()

    def _ejecutar_tareas_programadas(self):
        """Ejecuta las tareas programadas"""
        while self.ejecutando:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto

    def _actualizar_conocimiento(self):
        """Actualiza el conocimiento del sistema"""
        try:
            self.logger.info("Iniciando actualización de conocimiento")

            # Actualizar base de conocimiento
            self.base_conocimiento.actualizar_conocimiento()

            # Actualizar patrones de respuesta de la IA
            self._actualizar_patrones_respuesta()

            # Generar nuevos insights
            nuevos_insights = self._generar_nuevos_insights()

            # Actualizar métricas
            metricas = self._calcular_metricas_actualizadas()

            # Registrar actualización
            actualizacion = ActualizacionSistema(
                timestamp=datetime.datetime.now(),
                tipo_actualizacion="conocimiento",
                elementos_actualizados=len(self.base_conocimiento.interacciones),
                nuevos_insights=nuevos_insights,
                metricas_mejoradas=metricas,
                recomendaciones_generadas=self._generar_recomendaciones(),
                estado_sistema="activo",
            )

            self.actualizaciones_realizadas.append(actualizacion)

            self.logger.info(f"Actualización completada: {nuevos_insights} nuevos insights")

        except Exception as e:
            self.logger.error(f"Error en actualización de conocimiento: {e}")

    def _actualizar_patrones_respuesta(self):
        """Actualiza los patrones de respuesta de la IA"""
        # Analizar respuestas exitosas recientes
        interacciones_recientes = [
            i
            for i in self.base_conocimiento.interacciones
            if (datetime.datetime.now() - i.timestamp).days <= 7
        ]

        respuestas_exitosas = [
            i
            for i in interacciones_recientes
            if i.resultado == "exitoso" and i.satisfaccion_cliente and i.satisfaccion_cliente >= 4
        ]

        # Agrupar por tipo de respuesta
        respuestas_por_tipo = defaultdict(list)
        for interaccion in respuestas_exitosas:
            tipo = self._clasificar_tipo_respuesta(interaccion.respuesta_agente)
            respuestas_por_tipo[tipo].append(interaccion.respuesta_agente)

        # Actualizar patrones
        for tipo, respuestas in respuestas_por_tipo.items():
            if tipo not in self.ia.patrones_respuesta:
                self.ia.patrones_respuesta[tipo] = []

            # Agregar respuestas exitosas que no estén ya en los patrones
            for respuesta in respuestas:
                if respuesta not in self.ia.patrones_respuesta[tipo]:
                    self.ia.patrones_respuesta[tipo].append(respuesta)

    def _clasificar_tipo_respuesta(self, respuesta: str) -> str:
        """Clasifica el tipo de respuesta"""
        respuesta_lower = respuesta.lower()

        if any(palabra in respuesta_lower for palabra in ["hola", "buenos", "buenas"]):
            return "saludo"
        elif any(palabra in respuesta_lower for palabra in ["gracias", "chau", "adios"]):
            return "despedida"
        elif any(palabra in respuesta_lower for palabra in ["cotización", "precio", "costo"]):
            return "cotizacion"
        elif any(palabra in respuesta_lower for palabra in ["información", "características"]):
            return "informacion"
        elif any(palabra in respuesta_lower for palabra in ["producto", "isodec", "poliestireno"]):
            return "producto"
        else:
            return "general"

    def _generar_nuevos_insights(self) -> int:
        """Genera nuevos insights basados en datos recientes"""
        insights_generados = 0

        # Insight sobre satisfacción del cliente
        satisfacciones_recientes = [
            i.satisfaccion_cliente
            for i in self.base_conocimiento.interacciones
            if (i.satisfaccion_cliente and (datetime.datetime.now() - i.timestamp).days <= 7)
        ]

        if satisfacciones_recientes:
            satisfaccion_promedio = statistics.mean(satisfacciones_recientes)
            if satisfaccion_promedio < self.configuracion["umbral_satisfaccion_minimo"]:
                insight = {
                    "tipo": "satisfaccion_baja",
                    "descripcion": f"Satisfacción promedio reciente: {satisfaccion_promedio:.2f}",
                    "recomendacion": "Revisar respuestas y mejorar atención al cliente",
                    "timestamp": datetime.datetime.now().isoformat(),
                }
                self.base_conocimiento.insights_automaticos.append(insight)
                insights_generados += 1

        # Insight sobre productos más consultados
        consultas_recientes = [
            i
            for i in self.base_conocimiento.interacciones
            if (
                i.tipo_interaccion == "consulta"
                and (datetime.datetime.now() - i.timestamp).days <= 7
            )
        ]

        productos_consultados = []
        for consulta in consultas_recientes:
            if consulta.contexto.get("producto"):
                productos_consultados.append(consulta.contexto["producto"])

        if productos_consultados:
            producto_mas_consultado = Counter(productos_consultados).most_common(1)[0]
            insight = {
                "tipo": "producto_popular",
                "descripcion": f"Producto más consultado: {producto_mas_consultado[0]} ({producto_mas_consultado[1]} consultas)",
                "recomendacion": f"Promocionar {producto_mas_consultado[0]} como producto estrella",
                "timestamp": datetime.datetime.now().isoformat(),
            }
            self.base_conocimiento.insights_automaticos.append(insight)
            insights_generados += 1

        return insights_generados

    def _calcular_metricas_actualizadas(self) -> dict[str, Any]:
        """Calcula métricas actualizadas del sistema"""
        ahora = datetime.datetime.now()

        # Métricas de interacciones
        interacciones_hoy = [
            i for i in self.base_conocimiento.interacciones if i.timestamp.date() == ahora.date()
        ]

        interacciones_semana = [
            i for i in self.base_conocimiento.interacciones if (ahora - i.timestamp).days <= 7
        ]

        # Métricas de satisfacción
        satisfacciones = [
            i.satisfaccion_cliente
            for i in self.base_conocimiento.interacciones
            if i.satisfaccion_cliente
        ]
        satisfaccion_promedio = statistics.mean(satisfacciones) if satisfacciones else 0

        # Métricas de conversión
        total_cotizaciones = len(
            [i for i in self.base_conocimiento.interacciones if i.tipo_interaccion == "cotizacion"]
        )
        total_ventas = len(
            [i for i in self.base_conocimiento.interacciones if i.tipo_interaccion == "venta"]
        )
        tasa_conversion = total_ventas / total_cotizaciones if total_cotizaciones > 0 else 0

        return {
            "interacciones_hoy": len(interacciones_hoy),
            "interacciones_semana": len(interacciones_semana),
            "satisfaccion_promedio": satisfaccion_promedio,
            "tasa_conversion": tasa_conversion,
            "total_interacciones": len(self.base_conocimiento.interacciones),
            "total_patrones": len(self.base_conocimiento.patrones_venta),
            "total_insights": len(self.base_conocimiento.insights_automaticos),
        }

    def _generar_recomendaciones(self) -> list[str]:
        """Genera recomendaciones para mejorar el sistema"""
        recomendaciones = []

        # Recomendación basada en satisfacción
        metricas = self._calcular_metricas_actualizadas()
        if metricas["satisfaccion_promedio"] < self.configuracion["umbral_satisfaccion_minimo"]:
            recomendaciones.append(
                "Mejorar calidad de respuestas para aumentar satisfacción del cliente"
            )

        # Recomendación basada en tasa de conversión
        if metricas["tasa_conversion"] < 0.3:
            recomendaciones.append("Implementar estrategias de seguimiento para mejorar conversión")

        # Recomendación basada en patrones exitosos
        patrones_exitosos = [
            p for p in self.base_conocimiento.patrones_venta if p.tasa_exito >= 0.7
        ]
        if patrones_exitosos:
            recomendaciones.append(
                f"Replicar estrategias de {len(patrones_exitosos)} patrones exitosos identificados"
            )

        return recomendaciones

    def _analizar_tendencias(self):
        """Analiza tendencias de ventas y comportamiento"""
        try:
            self.logger.info("Iniciando análisis de tendencias")

            # Analizar tendencias de ventas
            tendencias = self.motor_analisis.analizar_tendencias_ventas(periodo_dias=30)

            # Generar perfiles de clientes exitosos
            perfiles = self.motor_analisis.generar_perfiles_clientes_exitosos()

            # Generar insights de ventas
            insights_ventas = self.motor_analisis.generar_insights_ventas()

            self.logger.info(
                f"Análisis completado: {len(tendencias)} tendencias, {len(perfiles)} perfiles"
            )

        except Exception as e:
            self.logger.error(f"Error en análisis de tendencias: {e}")

    def _limpiar_datos_obsoletos(self):
        """Limpia datos obsoletos del sistema"""
        try:
            self.logger.info("Iniciando limpieza de datos obsoletos")

            fecha_limite = datetime.datetime.now() - datetime.timedelta(
                days=self.configuracion["dias_retencion_datos"]
            )

            # Limpiar interacciones antiguas
            interacciones_validas = [
                i for i in self.base_conocimiento.interacciones if i.timestamp >= fecha_limite
            ]

            interacciones_eliminadas = len(self.base_conocimiento.interacciones) - len(
                interacciones_validas
            )
            self.base_conocimiento.interacciones = interacciones_validas

            # Limpiar insights antiguos
            insights_validos = [
                i
                for i in self.base_conocimiento.insights_automaticos
                if datetime.datetime.fromisoformat(i["timestamp"]) >= fecha_limite
            ]

            insights_eliminados = len(self.base_conocimiento.insights_automaticos) - len(
                insights_validos
            )
            self.base_conocimiento.insights_automaticos = insights_validos

            self.logger.info(
                f"Limpieza completada: {interacciones_eliminadas} interacciones, {insights_eliminados} insights eliminados"
            )

        except Exception as e:
            self.logger.error(f"Error en limpieza de datos: {e}")

    def _exportar_conocimiento(self):
        """Exporta el conocimiento actualizado"""
        try:
            self.logger.info("Iniciando exportación de conocimiento")

            # Exportar base de conocimiento
            self.base_conocimiento.exportar_conocimiento(
                self.configuracion["archivos_exportacion"]["base_conocimiento"]
            )

            # Exportar análisis de conversiones
            self.motor_analisis.exportar_analisis(
                self.configuracion["archivos_exportacion"]["analisis_conversiones"]
            )

            # Exportar IA conversacional
            self.ia.exportar_conocimiento_ia(
                self.configuracion["archivos_exportacion"]["ia_conversacional"]
            )

            # Exportar métricas del sistema
            self._exportar_metricas_sistema()

            self.logger.info("Exportación completada correctamente")

        except Exception as e:
            self.logger.error(f"Error en exportación: {e}")

    def _exportar_metricas_sistema(self):
        """Exporta métricas del sistema"""
        metricas = {
            "fecha_exportacion": datetime.datetime.now().isoformat(),
            "metricas_actuales": self._calcular_metricas_actualizadas(),
            "actualizaciones_realizadas": len(self.actualizaciones_realizadas),
            "configuracion": self.configuracion,
            "estado_sistema": "activo" if self.ejecutando else "inactivo",
        }

        with open(
            self.configuracion["archivos_exportacion"]["metricas_sistema"], "w", encoding="utf-8"
        ) as f:
            json.dump(metricas, f, ensure_ascii=False, indent=2, default=str)

    def obtener_estado_sistema(self) -> dict[str, Any]:
        """Obtiene el estado actual del sistema"""
        return {
            "ejecutando": self.ejecutando,
            "ultima_actualizacion": self.actualizaciones_realizadas[-1].timestamp.isoformat()
            if self.actualizaciones_realizadas
            else None,
            "total_actualizaciones": len(self.actualizaciones_realizadas),
            "metricas_actuales": self._calcular_metricas_actualizadas(),
            "configuracion": self.configuracion,
        }

    def forzar_actualizacion(self):
        """Fuerza una actualización inmediata del sistema"""
        self.logger.info("Forzando actualización del sistema")
        self._actualizar_conocimiento()
        self._analizar_tendencias()
        self._exportar_conocimiento()


def main():
    """Función principal para demostrar el sistema de actualización"""
    print("Sistema de Actualización Automática BMC Uruguay")
    print("=" * 50)

    # Crear IA conversacional
    from ia_conversacional_integrada import IAConversacionalIntegrada

    ia = IAConversacionalIntegrada()

    # Crear sistema de actualización
    sistema_actualizacion = SistemaActualizacionAutomatica(ia)

    # Mostrar estado inicial
    estado = sistema_actualizacion.obtener_estado_sistema()
    print(f"Estado del sistema: {'Activo' if estado['ejecutando'] else 'Inactivo'}")
    print(f"Total de interacciones: {estado['metricas_actuales']['total_interacciones']}")
    print(f"Total de patrones: {estado['metricas_actuales']['total_patrones']}")

    # Iniciar sistema
    sistema_actualizacion.iniciar_sistema_actualizacion()
    print("\nSistema de actualización iniciado")
    print("Presiona Ctrl+C para detener")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        sistema_actualizacion.detener_sistema_actualizacion()
        print("\nSistema detenido")


if __name__ == "__main__":
    main()
