#!/usr/bin/env python3
"""
Base de Conocimiento Dinámica BMC Uruguay
Sistema que evoluciona constantemente basado en interacciones y ventas
"""

import datetime
import json
import statistics
from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any


@dataclass
class InteraccionCliente:
    """Registro de interacción con cliente"""

    id: str
    timestamp: datetime.datetime
    cliente_id: str
    tipo_interaccion: str  # consulta, cotizacion, venta, seguimiento
    mensaje_cliente: str
    respuesta_agente: str
    contexto: dict[str, Any]
    resultado: str  # exitoso, fallido, pendiente
    valor_cotizacion: Decimal | None = None
    valor_venta: Decimal | None = None
    satisfaccion_cliente: int | None = None  # 1-5
    lecciones_aprendidas: list[str] = None


@dataclass
class PatronVenta:
    """Patrón identificado en ventas exitosas"""

    id: str
    nombre: str
    descripcion: str
    frecuencia: int
    tasa_exito: float
    factores_clave: list[str]
    productos_asociados: list[str]
    perfil_cliente: dict[str, Any]
    palabras_clave: list[str]
    estrategia_recomendada: str
    fecha_creacion: datetime.datetime
    fecha_ultima_actualizacion: datetime.datetime


@dataclass
class ConocimientoProducto:
    """Conocimiento evolutivo sobre productos"""

    producto_id: str
    nombre: str
    caracteristicas_base: dict[str, Any]
    caracteristicas_aprendidas: dict[str, Any]
    objeciones_comunes: list[str]
    respuestas_efectivas: list[str]
    casos_uso_exitosos: list[str]
    precios_competitivos: dict[str, Decimal]
    tendencias_demanda: list[dict[str, Any]]
    recomendaciones_venta: list[str]
    fecha_ultima_actualizacion: datetime.datetime


class BaseConocimientoDinamica:
    """Base de conocimiento que evoluciona automáticamente"""

    def __init__(self):
        self.interacciones = []
        self.patrones_venta = []
        self.conocimiento_productos = {}
        self.metricas_evolucion = {}
        self.insights_automaticos = []
        self.cargar_conocimiento_inicial()

    def cargar_conocimiento_inicial(self):
        """Carga el conocimiento inicial del sistema"""
        # Conocimiento base de productos
        self.conocimiento_productos = {
            "isodec": ConocimientoProducto(
                producto_id="isodec",
                nombre="Isodec",
                caracteristicas_base={
                    "tipo": "Panel aislante térmico",
                    "nucleo": "EPS",
                    "conductividad_termica": "0.035 W/mK",
                    "densidad": "15-20 kg/m³",
                },
                caracteristicas_aprendidas={},
                objeciones_comunes=[],
                respuestas_efectivas=[],
                casos_uso_exitosos=[],
                precios_competitivos={},
                tendencias_demanda=[],
                recomendaciones_venta=[],
                fecha_ultima_actualizacion=datetime.datetime.now(),
            )
        }

        # Patrones de venta iniciales
        self.patrones_venta = [
            PatronVenta(
                id="patron_1",
                nombre="Cliente Técnico",
                descripcion="Clientes que preguntan especificaciones técnicas detalladas",
                frecuencia=0,
                tasa_exito=0.0,
                factores_clave=["especificaciones_tecnicas", "certificaciones", "durabilidad"],
                productos_asociados=["isodec"],
                perfil_cliente={"nivel_tecnico": "alto", "decisor": "técnico"},
                palabras_clave=["conductividad", "resistencia", "certificación", "durabilidad"],
                estrategia_recomendada="Enfocarse en especificaciones técnicas y beneficios a largo plazo",
                fecha_creacion=datetime.datetime.now(),
                fecha_ultima_actualizacion=datetime.datetime.now(),
            )
        ]

    def registrar_interaccion(self, interaccion: InteraccionCliente):
        """Registra una nueva interacción"""
        self.interacciones.append(interaccion)
        self.analizar_interaccion(interaccion)
        self.actualizar_conocimiento()

    def analizar_interaccion(self, interaccion: InteraccionCliente):
        """Analiza una interacción para extraer conocimiento"""
        # Extraer palabras clave del mensaje
        palabras_clave = self._extraer_palabras_clave(interaccion.mensaje_cliente)

        # Identificar tipo de consulta
        tipo_consulta = self._identificar_tipo_consulta(interaccion.mensaje_cliente)

        # Analizar efectividad de la respuesta
        efectividad = self._evaluar_efectividad_respuesta(interaccion)

        # Actualizar patrones de venta
        if interaccion.tipo_interaccion == "venta" and interaccion.valor_venta:
            self._actualizar_patrones_venta_exitosos(interaccion, palabras_clave)

        # Actualizar conocimiento de productos
        self._actualizar_conocimiento_productos(interaccion, palabras_clave)

        # Generar insights automáticos
        self._generar_insights_automaticos(interaccion)

    def _extraer_palabras_clave(self, texto: str) -> list[str]:
        """Extrae palabras clave de un texto"""
        # Palabras técnicas
        palabras_tecnicas = [
            "conductividad",
            "resistencia",
            "durabilidad",
            "aislamiento",
            "térmico",
            "acústico",
            "fuego",
            "humedad",
            "instalación",
        ]

        # Palabras de negocio
        palabras_negocio = [
            "precio",
            "costo",
            "presupuesto",
            "oferta",
            "descuento",
            "entrega",
            "instalación",
            "garantía",
            "servicio",
        ]

        # Palabras emocionales
        palabras_emocionales = [
            "urgente",
            "importante",
            "necesito",
            "quiero",
            "mejor",
            "calidad",
            "confianza",
            "seguridad",
            "garantía",
        ]

        texto_lower = texto.lower()
        palabras_encontradas = []

        for categoria, palabras in [
            ("tecnico", palabras_tecnicas),
            ("negocio", palabras_negocio),
            ("emocional", palabras_emocionales),
        ]:
            for palabra in palabras:
                if palabra in texto_lower:
                    palabras_encontradas.append(f"{categoria}:{palabra}")

        return palabras_encontradas

    def _identificar_tipo_consulta(self, mensaje: str) -> str:
        """Identifica el tipo de consulta del cliente"""
        mensaje_lower = mensaje.lower()

        if any(palabra in mensaje_lower for palabra in ["precio", "costo", "cuanto"]):
            return "precio"
        elif any(
            palabra in mensaje_lower for palabra in ["especificacion", "caracteristica", "tecnico"]
        ):
            return "tecnico"
        elif any(palabra in mensaje_lower for palabra in ["instalacion", "montaje", "colocacion"]):
            return "instalacion"
        elif any(palabra in mensaje_lower for palabra in ["garantia", "servicio", "soporte"]):
            return "servicio"
        else:
            return "general"

    def _evaluar_efectividad_respuesta(self, interaccion: InteraccionCliente) -> float:
        """Evalúa la efectividad de la respuesta del agente"""
        if interaccion.resultado == "exitoso":
            return 1.0
        elif interaccion.resultado == "fallido":
            return 0.0
        elif interaccion.satisfaccion_cliente:
            return interaccion.satisfaccion_cliente / 5.0
        else:
            return 0.5  # Neutral

    def _actualizar_patrones_venta_exitosos(
        self, interaccion: InteraccionCliente, palabras_clave: list[str]
    ):
        """Actualiza patrones de venta exitosos"""
        # Buscar patrón existente similar
        patron_existente = None
        for patron in self.patrones_venta:
            if any(palabra in patron.palabras_clave for palabra in palabras_clave):
                patron_existente = patron
                break

        if patron_existente:
            # Actualizar patrón existente
            patron_existente.frecuencia += 1
            patron_existente.tasa_exito = self._calcular_tasa_exito_patron(patron_existente)
            patron_existente.fecha_ultima_actualizacion = datetime.datetime.now()
        else:
            # Crear nuevo patrón
            nuevo_patron = PatronVenta(
                id=f"patron_{len(self.patrones_venta) + 1}",
                nombre=f"Patrón {len(self.patrones_venta) + 1}",
                descripcion=f"Patrón identificado en venta de {interaccion.timestamp.strftime('%Y-%m-%d')}",
                frecuencia=1,
                tasa_exito=1.0,
                factores_clave=palabras_clave,
                productos_asociados=[interaccion.contexto.get("producto", "")],
                perfil_cliente=interaccion.contexto,
                palabras_clave=palabras_clave,
                estrategia_recomendada="Estrategia basada en interacción exitosa",
                fecha_creacion=datetime.datetime.now(),
                fecha_ultima_actualizacion=datetime.datetime.now(),
            )
            self.patrones_venta.append(nuevo_patron)

    def _calcular_tasa_exito_patron(self, patron: PatronVenta) -> float:
        """Calcula la tasa de éxito de un patrón"""
        interacciones_patron = [
            i
            for i in self.interacciones
            if any(palabra in i.mensaje_cliente.lower() for palabra in patron.palabras_clave)
        ]

        if not interacciones_patron:
            return 0.0

        exitosas = sum(1 for i in interacciones_patron if i.resultado == "exitoso")
        return exitosas / len(interacciones_patron)

    def _actualizar_conocimiento_productos(
        self, interaccion: InteraccionCliente, palabras_clave: list[str]
    ):
        """Actualiza el conocimiento sobre productos"""
        producto = interaccion.contexto.get("producto", "")
        if not producto or producto not in self.conocimiento_productos:
            return

        conocimiento = self.conocimiento_productos[producto]

        # Actualizar objeciones comunes
        if interaccion.resultado == "fallido":
            objecion = self._extraer_objecion(interaccion.mensaje_cliente)
            if objecion and objecion not in conocimiento.objeciones_comunes:
                conocimiento.objeciones_comunes.append(objecion)

        # Actualizar respuestas efectivas
        if interaccion.resultado == "exitoso":
            if interaccion.respuesta_agente not in conocimiento.respuestas_efectivas:
                conocimiento.respuestas_efectivas.append(interaccion.respuesta_agente)

        # Actualizar casos de uso exitosos
        if interaccion.tipo_interaccion == "venta":
            caso_uso = self._extraer_caso_uso(interaccion)
            if caso_uso and caso_uso not in conocimiento.casos_uso_exitosos:
                conocimiento.casos_uso_exitosos.append(caso_uso)

        # Actualizar recomendaciones de venta
        if interaccion.satisfaccion_cliente and interaccion.satisfaccion_cliente >= 4:
            recomendacion = self._generar_recomendacion_venta(interaccion)
            if recomendacion and recomendacion not in conocimiento.recomendaciones_venta:
                conocimiento.recomendaciones_venta.append(recomendacion)

        conocimiento.fecha_ultima_actualizacion = datetime.datetime.now()

    def _extraer_objecion(self, mensaje: str) -> str | None:
        """Extrae objeciones del mensaje del cliente"""
        objeciones_comunes = [
            "muy caro",
            "muy costoso",
            "no tengo presupuesto",
            "no estoy seguro",
            "necesito pensarlo",
            "no es urgente",
            "ya tengo proveedor",
            "no me convence",
        ]

        mensaje_lower = mensaje.lower()
        for objecion in objeciones_comunes:
            if objecion in mensaje_lower:
                return objecion

        return None

    def _extraer_caso_uso(self, interaccion: InteraccionCliente) -> str | None:
        """Extrae caso de uso exitoso de la interacción"""
        contexto = interaccion.contexto
        if "aplicacion" in contexto:
            return contexto["aplicacion"]
        elif "proyecto" in contexto:
            return contexto["proyecto"]
        else:
            return f"Venta exitosa de {contexto.get('producto', 'producto')} por ${interaccion.valor_venta}"

    def _generar_recomendacion_venta(self, interaccion: InteraccionCliente) -> str | None:
        """Genera recomendación de venta basada en interacción exitosa"""
        if interaccion.satisfaccion_cliente >= 4:
            return f"Estrategia exitosa: {interaccion.respuesta_agente[:100]}..."
        return None

    def _generar_insights_automaticos(self, interaccion: InteraccionCliente):
        """Genera insights automáticos basados en la interacción"""
        insight = {
            "timestamp": interaccion.timestamp,
            "tipo": "interaccion",
            "descripcion": f"Interacción {interaccion.tipo_interaccion} con resultado {interaccion.resultado}",
            "valor": float(interaccion.valor_venta) if interaccion.valor_venta else 0,
            "satisfaccion": interaccion.satisfaccion_cliente,
            "palabras_clave": self._extraer_palabras_clave(interaccion.mensaje_cliente),
        }

        self.insights_automaticos.append(insight)

    def actualizar_conocimiento(self):
        """Actualiza el conocimiento general del sistema"""
        self._actualizar_metricas_evolucion()
        self._limpiar_conocimiento_obsoleto()
        self._generar_recomendaciones_sistema()

    def _actualizar_metricas_evolucion(self):
        """Actualiza métricas de evolución del sistema"""
        ahora = datetime.datetime.now()

        # Métricas de interacciones
        interacciones_hoy = [i for i in self.interacciones if i.timestamp.date() == ahora.date()]

        interacciones_semana = [i for i in self.interacciones if (ahora - i.timestamp).days <= 7]

        # Métricas de ventas
        ventas_hoy = [i for i in interacciones_hoy if i.tipo_interaccion == "venta"]
        ventas_semana = [i for i in interacciones_semana if i.tipo_interaccion == "venta"]

        # Métricas de satisfacción
        satisfacciones = [
            i.satisfaccion_cliente for i in self.interacciones if i.satisfaccion_cliente
        ]
        satisfaccion_promedio = statistics.mean(satisfacciones) if satisfacciones else 0

        self.metricas_evolucion = {
            "fecha_actualizacion": ahora.isoformat(),
            "interacciones_hoy": len(interacciones_hoy),
            "interacciones_semana": len(interacciones_semana),
            "ventas_hoy": len(ventas_hoy),
            "ventas_semana": len(ventas_semana),
            "satisfaccion_promedio": satisfaccion_promedio,
            "total_interacciones": len(self.interacciones),
            "total_patrones": len(self.patrones_venta),
            "total_insights": len(self.insights_automaticos),
        }

    def _limpiar_conocimiento_obsoleto(self):
        """Limpia conocimiento obsoleto o poco relevante"""
        # Limpiar patrones con baja frecuencia y tasa de éxito
        patrones_validos = []
        for patron in self.patrones_venta:
            if patron.frecuencia >= 3 and patron.tasa_exito >= 0.3:
                patrones_validos.append(patron)

        self.patrones_venta = patrones_validos

        # Limpiar insights antiguos (más de 30 días)
        ahora = datetime.datetime.now()
        insights_validos = [
            i for i in self.insights_automaticos if (ahora - i["timestamp"]).days <= 30
        ]
        self.insights_automaticos = insights_validos

    def _generar_recomendaciones_sistema(self):
        """Genera recomendaciones para mejorar el sistema"""
        recomendaciones = []

        # Recomendación basada en patrones exitosos
        patrones_exitosos = [p for p in self.patrones_venta if p.tasa_exito >= 0.7]
        if patrones_exitosos:
            recomendaciones.append(
                {
                    "tipo": "patron_exitoso",
                    "descripcion": f"Usar estrategias de {len(patrones_exitosos)} patrones exitosos identificados",
                    "prioridad": "alta",
                }
            )

        # Recomendación basada en satisfacción
        if self.metricas_evolucion.get("satisfaccion_promedio", 0) < 4.0:
            recomendaciones.append(
                {
                    "tipo": "mejora_satisfaccion",
                    "descripcion": "Mejorar respuestas para aumentar satisfacción del cliente",
                    "prioridad": "alta",
                }
            )

        # Recomendación basada en objeciones comunes
        for producto_id, conocimiento in self.conocimiento_productos.items():
            if len(conocimiento.objeciones_comunes) >= 3:
                recomendaciones.append(
                    {
                        "tipo": "objeciones_frecuentes",
                        "descripcion": f"Desarrollar respuestas para objeciones comunes de {producto_id}",
                        "prioridad": "media",
                    }
                )

        return recomendaciones

    def obtener_respuesta_inteligente(self, mensaje_cliente: str, contexto: dict[str, Any]) -> str:
        """Genera respuesta inteligente basada en el conocimiento acumulado"""
        palabras_clave = self._extraer_palabras_clave(mensaje_cliente)
        tipo_consulta = self._identificar_tipo_consulta(mensaje_cliente)

        # Buscar patrones similares exitosos
        patrones_similares = []
        for patron in self.patrones_venta:
            similitud = len(set(palabras_clave) & set(patron.palabras_clave))
            if similitud > 0:
                patrones_similares.append((patron, similitud))

        # Ordenar por similitud y tasa de éxito
        patrones_similares.sort(key=lambda x: (x[1], x[0].tasa_exito), reverse=True)

        if patrones_similares:
            mejor_patron = patrones_similares[0][0]
            return self._generar_respuesta_basada_en_patron(mejor_patron, mensaje_cliente, contexto)

        # Buscar respuestas efectivas similares
        respuestas_efectivas = []
        for interaccion in self.interacciones:
            if interaccion.resultado == "exitoso" and any(
                palabra in interaccion.mensaje_cliente.lower() for palabra in palabras_clave
            ):
                respuestas_efectivas.append(interaccion.respuesta_agente)

        if respuestas_efectivas:
            return respuestas_efectivas[0]  # Usar la primera respuesta efectiva encontrada

        # Respuesta por defecto
        return self._generar_respuesta_por_defecto(mensaje_cliente, contexto)

    def _generar_respuesta_basada_en_patron(
        self, patron: PatronVenta, mensaje: str, contexto: dict[str, Any]
    ) -> str:
        """Genera respuesta basada en patrón exitoso"""
        return f"Basándome en experiencias exitosas similares: {patron.estrategia_recomendada}"

    def _generar_respuesta_por_defecto(self, mensaje: str, contexto: dict[str, Any]) -> str:
        """Genera respuesta por defecto cuando no hay conocimiento específico"""
        return "Gracias por tu consulta. Te ayudo con la información que necesitas."

    def exportar_conocimiento(self, archivo: str):
        """Exporta todo el conocimiento a un archivo JSON"""
        conocimiento_exportar = {
            "interacciones": [asdict(i) for i in self.interacciones],
            "patrones_venta": [asdict(p) for p in self.patrones_venta],
            "conocimiento_productos": {
                k: asdict(v) for k, v in self.conocimiento_productos.items()
            },
            "metricas_evolucion": self.metricas_evolucion,
            "insights_automaticos": self.insights_automaticos,
            "fecha_exportacion": datetime.datetime.now().isoformat(),
        }

        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(conocimiento_exportar, f, ensure_ascii=False, indent=2, default=str)

    def importar_conocimiento(self, archivo: str):
        """Importa conocimiento desde un archivo JSON"""
        with open(archivo, encoding="utf-8") as f:
            conocimiento = json.load(f)

        # Importar interacciones
        for i in conocimiento.get("interacciones", []):
            interaccion = InteraccionCliente(**i)
            interaccion.timestamp = datetime.datetime.fromisoformat(i["timestamp"])
            self.interacciones.append(interaccion)

        # Importar patrones de venta
        for p in conocimiento.get("patrones_venta", []):
            patron = PatronVenta(**p)
            patron.fecha_creacion = datetime.datetime.fromisoformat(p["fecha_creacion"])
            patron.fecha_ultima_actualizacion = datetime.datetime.fromisoformat(
                p["fecha_ultima_actualizacion"]
            )
            self.patrones_venta.append(patron)

        # Importar conocimiento de productos
        for k, v in conocimiento.get("conocimiento_productos", {}).items():
            conocimiento_prod = ConocimientoProducto(**v)
            conocimiento_prod.fecha_ultima_actualizacion = datetime.datetime.fromisoformat(
                v["fecha_ultima_actualizacion"]
            )
            self.conocimiento_productos[k] = conocimiento_prod

        self.metricas_evolucion = conocimiento.get("metricas_evolucion", {})
        self.insights_automaticos = conocimiento.get("insights_automaticos", [])


def main():
    """Función principal para demostrar la base de conocimiento"""
    base = BaseConocimientoDinamica()

    # Simular algunas interacciones
    interacciones_simuladas = [
        InteraccionCliente(
            id="int_1",
            timestamp=datetime.datetime.now(),
            cliente_id="cliente_1",
            tipo_interaccion="consulta",
            mensaje_cliente="Necesito información sobre Isodec para mi casa",
            respuesta_agente="Isodec es un panel aislante térmico con núcleo EPS...",
            contexto={"producto": "isodec", "aplicacion": "residencial"},
            resultado="exitoso",
            satisfaccion_cliente=4,
        ),
        InteraccionCliente(
            id="int_2",
            timestamp=datetime.datetime.now(),
            cliente_id="cliente_2",
            tipo_interaccion="venta",
            mensaje_cliente="El precio de Isodec es muy caro",
            respuesta_agente="Entiendo tu preocupación. Te explico el valor a largo plazo...",
            contexto={"producto": "isodec", "objecion": "precio"},
            resultado="exitoso",
            valor_venta=Decimal("5000.00"),
            satisfaccion_cliente=5,
        ),
    ]

    for interaccion in interacciones_simuladas:
        base.registrar_interaccion(interaccion)

    # Mostrar métricas
    print("Métricas de evolución:")
    print(json.dumps(base.metricas_evolucion, indent=2, default=str))

    # Exportar conocimiento
    base.exportar_conocimiento("base_conocimiento.json")
    print("\nConocimiento exportado a base_conocimiento.json")


if __name__ == "__main__":
    main()
