#!/usr/bin/env python3
"""
Motor de Análisis de Conversiones BMC Uruguay
Analiza conversiones de cotizaciones a ventas y genera insights
"""

import datetime
import json
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any


@dataclass
class ConversionAnalisis:
    """Análisis de conversión de cotización a venta"""

    cotizacion_id: str
    cliente_id: str
    producto: str
    valor_cotizacion: Decimal
    valor_venta: Decimal
    tiempo_conversion: int  # días
    factores_exito: list[str]
    canales_efectivos: list[str]
    objeciones_superadas: list[str]
    satisfaccion_cliente: int
    fecha_analisis: datetime.datetime


@dataclass
class TendenciaVentas:
    """Tendencia de ventas identificada"""

    periodo: str
    producto: str
    tendencia: str  # creciente, decreciente, estable
    cambio_porcentual: float
    factores_influencia: list[str]
    prediccion: dict[str, Any]
    confianza: float
    fecha_identificacion: datetime.datetime


@dataclass
class PerfilClienteExitoso:
    """Perfil de cliente con alta probabilidad de conversión"""

    caracteristicas: dict[str, Any]
    probabilidad_conversion: float
    productos_preferidos: list[str]
    canales_preferidos: list[str]
    patrones_comportamiento: list[str]
    recomendaciones_venta: list[str]
    casos_exitosos: int
    valor_promedio_venta: Decimal


class MotorAnalisisConversiones:
    """Motor para analizar conversiones y generar insights"""

    def __init__(self, base_conocimiento):
        self.base_conocimiento = base_conocimiento
        self.conversiones_analizadas = []
        self.tendencias_identificadas = []
        self.perfiles_clientes_exitosos = []
        self.metricas_conversion = {}
        self.insights_ventas = []

    def analizar_conversion(self, cotizacion_id: str, venta_id: str) -> ConversionAnalisis:
        """Analiza una conversión específica de cotización a venta"""
        # Buscar interacciones relacionadas
        interacciones_cotizacion = [
            i
            for i in self.base_conocimiento.interacciones
            if cotizacion_id in i.contexto.get("cotizacion_id", "")
        ]

        interacciones_venta = [
            i
            for i in self.base_conocimiento.interacciones
            if venta_id in i.contexto.get("venta_id", "")
        ]

        if not interacciones_cotizacion or not interacciones_venta:
            return None

        # Calcular métricas de conversión
        cotizacion = interacciones_cotizacion[0]
        venta = interacciones_venta[0]

        tiempo_conversion = (venta.timestamp - cotizacion.timestamp).days

        # Identificar factores de éxito
        factores_exito = self._identificar_factores_exito(
            interacciones_cotizacion, interacciones_venta
        )

        # Identificar canales efectivos
        canales_efectivos = self._identificar_canales_efectivos(interacciones_cotizacion)

        # Identificar objeciones superadas
        objeciones_superadas = self._identificar_objeciones_superadas(
            interacciones_cotizacion, interacciones_venta
        )

        analisis = ConversionAnalisis(
            cotizacion_id=cotizacion_id,
            cliente_id=cotizacion.cliente_id,
            producto=cotizacion.contexto.get("producto", ""),
            valor_cotizacion=cotizacion.valor_cotizacion or Decimal("0"),
            valor_venta=venta.valor_venta or Decimal("0"),
            tiempo_conversion=tiempo_conversion,
            factores_exito=factores_exito,
            canales_efectivos=canales_efectivos,
            objeciones_superadas=objeciones_superadas,
            satisfaccion_cliente=venta.satisfaccion_cliente or 0,
            fecha_analisis=datetime.datetime.now(),
        )

        self.conversiones_analizadas.append(analisis)
        return analisis

    def _identificar_factores_exito(
        self, interacciones_cotizacion: list, interacciones_venta: list
    ) -> list[str]:
        """Identifica factores que contribuyeron al éxito de la conversión"""
        factores = []

        # Análisis de satisfacción
        satisfacciones = [
            i.satisfaccion_cliente for i in interacciones_venta if i.satisfaccion_cliente
        ]
        if satisfacciones and statistics.mean(satisfacciones) >= 4:
            factores.append("alta_satisfaccion_cliente")

        # Análisis de tiempo de respuesta
        tiempos_respuesta = []
        for i in range(1, len(interacciones_cotizacion)):
            tiempo = (
                interacciones_cotizacion[i].timestamp - interacciones_cotizacion[i - 1].timestamp
            ).seconds
            tiempos_respuesta.append(tiempo)

        if tiempos_respuesta and statistics.mean(tiempos_respuesta) < 3600:  # Menos de 1 hora
            factores.append("respuesta_rapida")

        # Análisis de personalización
        respuestas_personalizadas = [
            i
            for i in interacciones_cotizacion
            if len(i.respuesta_agente) > 100 and i.cliente_id in i.respuesta_agente
        ]
        if len(respuestas_personalizadas) > len(interacciones_cotizacion) * 0.5:
            factores.append("respuesta_personalizada")

        # Análisis de seguimiento
        if len(interacciones_cotizacion) > 3:
            factores.append("seguimiento_activo")

        return factores

    def _identificar_canales_efectivos(self, interacciones: list) -> list[str]:
        """Identifica canales de comunicación efectivos"""
        canales = []

        for interaccion in interacciones:
            canal = interaccion.contexto.get("canal", "desconocido")
            if canal != "desconocido":
                canales.append(canal)

        # Retornar canales más frecuentes
        canal_counts = Counter(canales)
        return [canal for canal, count in canal_counts.most_common(3)]

    def _identificar_objeciones_superadas(
        self, interacciones_cotizacion: list, interacciones_venta: list
    ) -> list[str]:
        """Identifica objeciones que fueron superadas exitosamente"""
        objeciones = []

        # Buscar objeciones en interacciones de cotización
        for interaccion in interacciones_cotizacion:
            mensaje_lower = interaccion.mensaje_cliente.lower()

            if "caro" in mensaje_lower or "costoso" in mensaje_lower:
                objeciones.append("objeccion_precio")
            elif "no estoy seguro" in mensaje_lower or "dudar" in mensaje_lower:
                objeciones.append("objeccion_incertidumbre")
            elif "no es urgente" in mensaje_lower:
                objeciones.append("objeccion_urgencia")
            elif "ya tengo proveedor" in mensaje_lower:
                objeciones.append("objeccion_competencia")

        return list(set(objeciones))

    def analizar_tendencias_ventas(self, periodo_dias: int = 30) -> list[TendenciaVentas]:
        """Analiza tendencias de ventas en un período"""
        fecha_limite = datetime.datetime.now() - datetime.timedelta(days=periodo_dias)

        # Filtrar ventas del período
        ventas_periodo = [
            i
            for i in self.base_conocimiento.interacciones
            if (i.tipo_interaccion == "venta" and i.timestamp >= fecha_limite and i.valor_venta)
        ]

        # Agrupar por producto
        ventas_por_producto = defaultdict(list)
        for venta in ventas_periodo:
            producto = venta.contexto.get("producto", "desconocido")
            ventas_por_producto[producto].append(venta)

        tendencias = []

        for producto, ventas in ventas_por_producto.items():
            if len(ventas) < 3:  # Necesitamos al menos 3 ventas para analizar tendencia
                continue

            # Ordenar por fecha
            ventas_ordenadas = sorted(ventas, key=lambda x: x.timestamp)

            # Calcular tendencia
            valores = [float(v.valor_venta) for v in ventas_ordenadas]
            tendencia, cambio_porcentual = self._calcular_tendencia(valores)

            # Identificar factores de influencia
            factores_influencia = self._identificar_factores_influencia(ventas_ordenadas)

            # Generar predicción
            prediccion = self._generar_prediccion_ventas(valores, tendencia)

            # Calcular confianza
            confianza = self._calcular_confianza_tendencia(valores, tendencia)

            tendencia_obj = TendenciaVentas(
                periodo=f"{periodo_dias} días",
                producto=producto,
                tendencia=tendencia,
                cambio_porcentual=cambio_porcentual,
                factores_influencia=factores_influencia,
                prediccion=prediccion,
                confianza=confianza,
                fecha_identificacion=datetime.datetime.now(),
            )

            tendencias.append(tendencia_obj)

        self.tendencias_identificadas.extend(tendencias)
        return tendencias

    def _calcular_tendencia(self, valores: list[float]) -> tuple[str, float]:
        """Calcula la tendencia de una serie de valores"""
        if len(valores) < 2:
            return "insuficiente_datos", 0.0

        # Calcular cambio porcentual
        valor_inicial = valores[0]
        valor_final = valores[-1]
        cambio_porcentual = ((valor_final - valor_inicial) / valor_inicial) * 100

        # Determinar tendencia
        if cambio_porcentual > 10:
            return "creciente", cambio_porcentual
        elif cambio_porcentual < -10:
            return "decreciente", cambio_porcentual
        else:
            return "estable", cambio_porcentual

    def _identificar_factores_influencia(self, ventas: list) -> list[str]:
        """Identifica factores que influyen en las ventas"""
        factores = []

        # Análisis de estacionalidad
        meses = [v.timestamp.month for v in ventas]
        if len(set(meses)) > 1:
            factores.append("estacionalidad")

        # Análisis de satisfacción
        satisfacciones = [v.satisfaccion_cliente for v in ventas if v.satisfaccion_cliente]
        if satisfacciones and statistics.mean(satisfacciones) >= 4:
            factores.append("alta_satisfaccion")

        # Análisis de canales
        canales = [v.contexto.get("canal", "") for v in ventas]
        canal_counts = Counter(canales)
        if len(canal_counts) > 1:
            factores.append("multi_canal")

        return factores

    def _generar_prediccion_ventas(self, valores: list[float], tendencia: str) -> dict[str, Any]:
        """Genera predicción de ventas futuras"""
        if len(valores) < 3:
            return {"prediccion": "insuficiente_datos", "confianza": 0.0}

        # Predicción simple basada en tendencia
        valor_promedio = statistics.mean(valores)
        valor_ultimo = valores[-1]

        if tendencia == "creciente":
            prediccion_valor = valor_ultimo * 1.1  # 10% de crecimiento
        elif tendencia == "decreciente":
            prediccion_valor = valor_ultimo * 0.9  # 10% de decrecimiento
        else:
            prediccion_valor = valor_promedio

        return {
            "prediccion": prediccion_valor,
            "tendencia": tendencia,
            "valor_actual": valor_ultimo,
            "valor_promedio": valor_promedio,
        }

    def _calcular_confianza_tendencia(self, valores: list[float], tendencia: str) -> float:
        """Calcula la confianza en la tendencia identificada"""
        if len(valores) < 3:
            return 0.0

        # Calcular desviación estándar
        desviacion = statistics.stdev(valores)
        promedio = statistics.mean(valores)

        # Coeficiente de variación (menor = mayor confianza)
        cv = desviacion / promedio if promedio > 0 else 1.0

        # Confianza basada en consistencia
        confianza = max(0.0, 1.0 - cv)

        # Ajustar por número de datos
        factor_datos = min(1.0, len(valores) / 10.0)
        confianza *= factor_datos

        return round(confianza, 2)

    def generar_perfiles_clientes_exitosos(self) -> list[PerfilClienteExitoso]:
        """Genera perfiles de clientes con alta probabilidad de conversión"""
        # Agrupar conversiones por cliente
        conversiones_por_cliente = defaultdict(list)
        for conversion in self.conversiones_analizadas:
            conversiones_por_cliente[conversion.cliente_id].append(conversion)

        perfiles = []

        for cliente_id, conversiones in conversiones_por_cliente.items():
            if len(conversiones) < 2:  # Necesitamos al menos 2 conversiones
                continue

            # Calcular probabilidad de conversión
            total_interacciones = len(
                [i for i in self.base_conocimiento.interacciones if i.cliente_id == cliente_id]
            )
            probabilidad_conversion = (
                len(conversiones) / total_interacciones if total_interacciones > 0 else 0
            )

            if probabilidad_conversion < 0.5:  # Solo clientes con alta probabilidad
                continue

            # Extraer características del cliente
            caracteristicas = self._extraer_caracteristicas_cliente(cliente_id)

            # Productos preferidos
            productos_preferidos = list(set(c.producto for c in conversiones))

            # Canales preferidos
            canales_preferidos = []
            for conversion in conversiones:
                canales_preferidos.extend(conversion.canales_efectivos)
            canales_preferidos = list(set(canales_preferidos))

            # Patrones de comportamiento
            patrones = self._identificar_patrones_comportamiento(cliente_id)

            # Recomendaciones de venta
            recomendaciones = self._generar_recomendaciones_cliente(conversiones)

            # Valor promedio de venta
            valor_promedio = statistics.mean([float(c.valor_venta) for c in conversiones])

            perfil = PerfilClienteExitoso(
                caracteristicas=caracteristicas,
                probabilidad_conversion=probabilidad_conversion,
                productos_preferidos=productos_preferidos,
                canales_preferidos=canales_preferidos,
                patrones_comportamiento=patrones,
                recomendaciones_venta=recomendaciones,
                casos_exitosos=len(conversiones),
                valor_promedio_venta=Decimal(str(valor_promedio)),
            )

            perfiles.append(perfil)

        self.perfiles_clientes_exitosos = perfiles
        return perfiles

    def _extraer_caracteristicas_cliente(self, cliente_id: str) -> dict[str, Any]:
        """Extrae características de un cliente específico"""
        interacciones_cliente = [
            i for i in self.base_conocimiento.interacciones if i.cliente_id == cliente_id
        ]

        if not interacciones_cliente:
            return {}

        # Características básicas
        caracteristicas = {
            "total_interacciones": len(interacciones_cliente),
            "satisfaccion_promedio": 0,
            "tiempo_promedio_respuesta": 0,
            "canales_utilizados": [],
            "productos_interesados": [],
        }

        # Satisfacción promedio
        satisfacciones = [
            i.satisfaccion_cliente for i in interacciones_cliente if i.satisfaccion_cliente
        ]
        if satisfacciones:
            caracteristicas["satisfaccion_promedio"] = statistics.mean(satisfacciones)

        # Canales utilizados
        canales = [
            i.contexto.get("canal", "") for i in interacciones_cliente if i.contexto.get("canal")
        ]
        caracteristicas["canales_utilizados"] = list(set(canales))

        # Productos de interés
        productos = [
            i.contexto.get("producto", "")
            for i in interacciones_cliente
            if i.contexto.get("producto")
        ]
        caracteristicas["productos_interesados"] = list(set(productos))

        return caracteristicas

    def _identificar_patrones_comportamiento(self, cliente_id: str) -> list[str]:
        """Identifica patrones de comportamiento de un cliente"""
        patrones = []

        interacciones_cliente = [
            i for i in self.base_conocimiento.interacciones if i.cliente_id == cliente_id
        ]

        if len(interacciones_cliente) < 3:
            return patrones

        # Patrón de frecuencia de interacción
        fechas = [i.timestamp for i in interacciones_cliente]
        fechas_ordenadas = sorted(fechas)

        intervalos = []
        for i in range(1, len(fechas_ordenadas)):
            intervalo = (fechas_ordenadas[i] - fechas_ordenadas[i - 1]).days
            intervalos.append(intervalo)

        if intervalos:
            intervalo_promedio = statistics.mean(intervalos)
            if intervalo_promedio < 7:
                patrones.append("cliente_frecuente")
            elif intervalo_promedio > 30:
                patrones.append("cliente_esporadico")

        # Patrón de horarios
        horas = [i.timestamp.hour for i in interacciones_cliente]
        if horas:
            hora_promedio = statistics.mean(horas)
            if 9 <= hora_promedio <= 17:
                patrones.append("horario_laboral")
            else:
                patrones.append("horario_no_laboral")

        return patrones

    def _generar_recomendaciones_cliente(self, conversiones: list[ConversionAnalisis]) -> list[str]:
        """Genera recomendaciones específicas para un cliente"""
        recomendaciones = []

        # Recomendación basada en productos exitosos
        productos_exitosos = [c.producto for c in conversiones]
        if productos_exitosos:
            producto_mas_exitoso = Counter(productos_exitosos).most_common(1)[0][0]
            recomendaciones.append(f"Enfocarse en {producto_mas_exitoso} - historial exitoso")

        # Recomendación basada en canales efectivos
        canales_efectivos = []
        for c in conversiones:
            canales_efectivos.extend(c.canales_efectivos)

        if canales_efectivos:
            canal_mas_efectivo = Counter(canales_efectivos).most_common(1)[0][0]
            recomendaciones.append(f"Usar canal {canal_mas_efectivo} - mayor efectividad")

        # Recomendación basada en objeciones superadas
        objeciones_superadas = []
        for c in conversiones:
            objeciones_superadas.extend(c.objeciones_superadas)

        if objeciones_superadas:
            objecion_comun = Counter(objeciones_superadas).most_common(1)[0][0]
            recomendaciones.append(f"Preparar respuesta para {objecion_comun}")

        return recomendaciones

    def generar_insights_ventas(self) -> list[dict[str, Any]]:
        """Genera insights automáticos sobre ventas"""
        insights = []

        # Insight sobre tasa de conversión general
        total_cotizaciones = len(
            [i for i in self.base_conocimiento.interacciones if i.tipo_interaccion == "cotizacion"]
        )

        total_ventas = len(
            [i for i in self.base_conocimiento.interacciones if i.tipo_interaccion == "venta"]
        )

        if total_cotizaciones > 0:
            tasa_conversion = total_ventas / total_cotizaciones
            insights.append(
                {
                    "tipo": "tasa_conversion",
                    "descripcion": f"Tasa de conversión general: {tasa_conversion:.2%}",
                    "valor": tasa_conversion,
                    "recomendacion": "Mejorar proceso de seguimiento"
                    if tasa_conversion < 0.3
                    else "Mantener estrategia actual",
                }
            )

        # Insight sobre productos más exitosos
        if self.conversiones_analizadas:
            productos_exitosos = [c.producto for c in self.conversiones_analizadas]
            producto_mas_exitoso = Counter(productos_exitosos).most_common(1)[0]

            insights.append(
                {
                    "tipo": "producto_exitoso",
                    "descripcion": f"Producto más exitoso: {producto_mas_exitoso[0]} ({producto_mas_exitoso[1]} conversiones)",
                    "valor": producto_mas_exitoso[1],
                    "recomendacion": f"Promocionar {producto_mas_exitoso[0]} como producto estrella",
                }
            )

        # Insight sobre tiempo de conversión
        if self.conversiones_analizadas:
            tiempos_conversion = [c.tiempo_conversion for c in self.conversiones_analizadas]
            tiempo_promedio = statistics.mean(tiempos_conversion)

            insights.append(
                {
                    "tipo": "tiempo_conversion",
                    "descripcion": f"Tiempo promedio de conversión: {tiempo_promedio:.1f} días",
                    "valor": tiempo_promedio,
                    "recomendacion": "Acelerar proceso de seguimiento"
                    if tiempo_promedio > 14
                    else "Proceso optimizado",
                }
            )

        self.insights_ventas = insights
        return insights

    def exportar_analisis(self, archivo: str):
        """Exporta todo el análisis a un archivo JSON"""
        analisis_exportar = {
            "conversiones_analizadas": [asdict(c) for c in self.conversiones_analizadas],
            "tendencias_identificadas": [asdict(t) for t in self.tendencias_identificadas],
            "perfiles_clientes_exitosos": [asdict(p) for p in self.perfiles_clientes_exitosos],
            "insights_ventas": self.insights_ventas,
            "fecha_exportacion": datetime.datetime.now().isoformat(),
        }

        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(analisis_exportar, f, ensure_ascii=False, indent=2, default=str)


def main():
    """Función principal para demostrar el motor de análisis"""
    from base_conocimiento_dinamica import BaseConocimientoDinamica

    # Crear base de conocimiento
    base = BaseConocimientoDinamica()

    # Crear motor de análisis
    motor = MotorAnalisisConversiones(base)

    # Simular algunas conversiones
    print("Motor de Análisis de Conversiones BMC Uruguay")
    print("=" * 50)

    # Generar insights
    insights = motor.generar_insights_ventas()
    print("\nInsights generados:")
    for insight in insights:
        print(f"- {insight['descripcion']}")
        print(f"  Recomendación: {insight['recomendacion']}")

    # Exportar análisis
    motor.exportar_analisis("analisis_conversiones.json")
    print("\nAnálisis exportado a analisis_conversiones.json")


if __name__ == "__main__":
    main()
