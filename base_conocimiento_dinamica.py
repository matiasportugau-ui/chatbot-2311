#!/usr/bin/env python3
"""
Base de Conocimiento Dinámica BMC Uruguay
Sistema que evoluciona constantemente basado en interacciones y ventas
"""

import datetime
import hashlib
import json
import os
import statistics
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
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
        self.directorio_base = Path(__file__).resolve().parent
        self.config_conocimiento = self._cargar_configuracion_conocimiento()
        self.archivo_conocimiento_cargado = None
        self.cargar_conocimiento_inicial()
        
        # Initialize OpenAI for Embeddings (Real-time Learning)
        self.openai_client = None
        try:
            # Check env var directly to avoid waiting for load_dotenv if not called
            if os.getenv("OPENAI_API_KEY"):
                from openai import OpenAI
                self.openai_client = OpenAI()
        except ImportError:
            print("⚠️ OpenAI not installed, vector embeddings disabled.")
        except Exception as e:
            print(f"⚠️ OpenAI init failed: {e}")

        self.cargar_conocimiento_entrenado()

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

    def _cargar_configuracion_conocimiento(self) -> dict[str, Any]:
        """Carga la configuración de conocimiento desde archivo"""
        config_default = {
            "carga_conocimiento": {
                "habilitada": True,
                "archivos_prioridad": [
                    "conocimiento_consolidado.json",
                    "base_conocimiento_final.json",
                    "conocimiento_completo.json",
                    "base_conocimiento_exportada.json",
                    "base_conocimiento_demo.json",
                    "conocimiento_completo_demo.json",
                ],
                "cargar_primer_archivo_encontrado": True,
                "intentar_mongodb": True,
                "mongodb_uri": "mongodb://localhost:27017/bmc_chat",
            },
            "consolidacion": {
                "habilitada": False,
                "archivo_salida": "conocimiento_consolidado.json",
                "evitar_duplicados": True,
                "combinar_productos": True,
            },
            "logging": {"nivel": "INFO", "mostrar_carga": True, "mostrar_estadisticas": True},
            "validacion": {
                "validar_al_cargar": True,
                "verificar_integridad": True,
                "advertencias_duplicados": True,
            },
        }

        config_path = self.directorio_base / "config_conocimiento.json"
        if not config_path.exists():
            return config_default

        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)
            return self._deep_merge_dicts(config_default, data)
        except Exception as e:
            print(f"⚠️  Error cargando config_conocimiento.json: {e}")
            return config_default

    def _deep_merge_dicts(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Realiza un merge profundo entre dos diccionarios"""
        resultado = dict(base)
        for clave, valor in override.items():
            if (
                clave in resultado
                and isinstance(resultado[clave], dict)
                and isinstance(valor, dict)
            ):
                resultado[clave] = self._deep_merge_dicts(resultado[clave], valor)
            else:
                resultado[clave] = valor
        return resultado

    def _resolver_ruta_archivo(self, archivo: str) -> Path:
        """Resuelve la ruta absoluta de un archivo de conocimiento"""
        if not archivo:
            return self.directorio_base
        ruta = Path(archivo)
        if not ruta.is_absolute():
            ruta = self.directorio_base / archivo
        return ruta

    def cargar_conocimiento_entrenado(self) -> bool:
        """Carga conocimiento entrenado desde archivos o MongoDB"""
        config_carga = self.config_conocimiento.get("carga_conocimiento", {})
        config_logging = self.config_conocimiento.get("logging", {})
        # PRIORIDAD: Intentar MongoDB primero (Estrategia unificada)
        if config_carga.get("intentar_mongodb", True):
            if self._cargar_desde_mongodb(config_carga.get("mongodb_uri")):
                return True

        if not config_carga.get("habilitada", True):
            return False

        archivos_prioridad = config_carga.get("archivos_prioridad", [])
        cargar_primer_archivo = config_carga.get("cargar_primer_archivo_encontrado", True)
        conocimiento_cargado = False

        for archivo in archivos_prioridad:
            ruta = self._resolver_ruta_archivo(archivo)
            if ruta.exists():
                try:
                    self.importar_conocimiento(str(ruta))
                    self.archivo_conocimiento_cargado = str(ruta)
                    conocimiento_cargado = True
                    if config_logging.get("mostrar_carga", True):
                        print(f"✅ Conocimiento cargado desde: {ruta.name}")
                    if cargar_primer_archivo:
                        return True
                except Exception as e:
                    print(f"⚠️  Error cargando {ruta.name}: {e}")

        return conocimiento_cargado

    def _cargar_desde_mongodb(self, uri: str | None) -> bool:
        """Carga conocimiento desde MongoDB si está disponible"""
        if not uri:
            return False

        try:
            from pymongo import MongoClient
        except ImportError:
            print("⚠️  pymongo no está instalado. Omitiendo carga desde MongoDB.")
            return False

        client = None
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")

            db_name = uri.rsplit("/", 1)[-1] if "/" in uri else "bmc_chat"
            db_name = db_name.split("?")[0] if db_name else "bmc_chat"
            db = client.get_database(db_name or "bmc_chat")
            coleccion = db.get_collection("kb_interactions")

            documentos = list(coleccion.find().limit(500))
            if not documentos:
                print("⚠️  No se encontraron interacciones en MongoDB.")
                return False

            interacciones = []
            for doc in documentos:
                interacciones.append(
                    {
                        "id": str(doc.get("_id")),
                        "timestamp": doc.get("timestamp"),
                        "cliente_id": doc.get("cliente_id", "desconocido"),
                        "tipo_interaccion": doc.get("tipo_interaccion", "consulta"),
                        "mensaje_cliente": doc.get("mensaje_cliente", ""),
                        "respuesta_agente": doc.get("respuesta_agente", ""),
                        "contexto": doc.get("contexto", {}),
                        "resultado": doc.get("resultado", "pendiente"),
                        "valor_cotizacion": doc.get("valor_cotizacion"),
                        "valor_venta": doc.get("valor_venta"),
                        "satisfaccion_cliente": doc.get("satisfaccion_cliente"),
                        "lecciones_aprendidas": doc.get("lecciones_aprendidas", []),
                    }
                )

            self._importar_interacciones(interacciones)
            self.archivo_conocimiento_cargado = "mongodb"
            print("✅ Conocimiento cargado desde MongoDB")
            return True

        except Exception as e:
            print(f"⚠️  Error cargando desde MongoDB: {e}")
            return False
        finally:
            if client:
                client.close()

    def registrar_interaccion(self, interaccion: InteraccionCliente):
        """Registra una nueva interacción"""
        self.interacciones.append(interaccion)
        
        # Persist to MongoDB with Vector Embedding (Real-time RAG)
        self._persistir_interaccion_mongo(interaccion)
        
        self.analizar_interaccion(interaccion)
        self.actualizar_conocimiento()

    def analizar_interaccion(self, interaccion: InteraccionCliente):
        """Analiza una interacción para extraer conocimiento"""
        # Extraer palabras clave del mensaje
        palabras_clave = self._extraer_palabras_clave(interaccion.mensaje_cliente)

        # Identificar tipo de consulta
        _tipo_consulta = self._identificar_tipo_consulta(interaccion.mensaje_cliente)

        # Analizar efectividad de la respuesta
        _efectividad = self._evaluar_efectividad_respuesta(interaccion)

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

    def _persistir_interaccion_mongo(self, interaccion: InteraccionCliente):
        """Guarda la interacción en MongoDB con embedding vectorial"""
        try:
            config_carga = self.config_conocimiento.get("carga_conocimiento", {})
            uri = config_carga.get("mongodb_uri")
            if not uri:
                return

            from pymongo import MongoClient
            client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            db_name = uri.rsplit("/", 1)[-1] if "/" in uri else "bmc_chat"
            db_name = db_name.split("?")[0]
            db = client.get_database(db_name)
            col = db["kb_interactions"]

            # Generate Embedding
            embedding = []
            if self.openai_client and interaccion.mensaje_cliente:
                try:
                    text = interaccion.mensaje_cliente.replace("\n", " ")
                    embedding = self.openai_client.embeddings.create(
                        input=[text], 
                        model="text-embedding-3-small"
                    ).data[0].embedding
                except Exception as e:
                    print(f"⚠️ Embedding generation failed: {e}")

            doc = asdict(interaccion)
            doc["embedding"] = embedding
            
            # Upsert
            col.replace_one({"id": interaccion.id}, doc, upsert=True)
            client.close()
        except Exception as e:
             # Fail silently to not impact main flow
            print(f"⚠️ Failed to persist interaction to Mongo: {e}")

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

        self._importar_interacciones(conocimiento.get("interacciones", []))
        self._importar_patrones(conocimiento.get("patrones_venta", []))
        self._importar_productos(conocimiento.get("conocimiento_productos", {}))

        if conocimiento.get("metricas_evolucion"):
            self._fusionar_metricas_evolucion(conocimiento["metricas_evolucion"])
        if conocimiento.get("insights_automaticos"):
            nuevos_insights = self._importar_insights(conocimiento["insights_automaticos"])
            if nuevos_insights:
                self.insights_automaticos.extend(nuevos_insights)

    def _importar_interacciones(self, interacciones: list[dict[str, Any]]):
        """Importa interacciones desde una lista de diccionarios"""
        for datos in interacciones:
            interaccion = self._crear_interaccion_desde_dict(datos)
            if interaccion:
                self.interacciones.append(interaccion)

    def _importar_patrones(self, patrones: list[dict[str, Any]]):
        """Importa patrones de venta desde una lista"""
        config_consolidacion = self.config_conocimiento.get("consolidacion", {})
        evitar_duplicados = config_consolidacion.get("evitar_duplicados", True)

        for datos in patrones:
            patron = self._crear_patron_desde_dict(datos)
            if patron:
                if evitar_duplicados:
                    # Buscar si ya existe un patrón con el mismo ID
                    indice_existente = None
                    for i, patron_existente in enumerate(self.patrones_venta):
                        if patron_existente.id == patron.id:
                            indice_existente = i
                            break

                    if indice_existente is not None:
                        # Reemplazar el patrón existente con el nuevo (más actualizado)
                        self.patrones_venta[indice_existente] = patron
                    else:
                        # No existe, agregar nuevo patrón
                        self.patrones_venta.append(patron)
                else:
                    # Si no se evitan duplicados, simplemente agregar
                    self.patrones_venta.append(patron)

    def _importar_productos(self, productos: dict[str, Any]):
        """Importa conocimiento de productos"""
        for producto_id, datos in productos.items():
            producto = self._crear_conocimiento_producto(producto_id, datos)
            if producto:
                self.conocimiento_productos[producto_id] = producto

    def _importar_insights(self, insights: list[Any]) -> list[dict[str, Any]]:
        """Convierte la lista de insights asegurando tipos consistentes"""
        resultado = []
        for insight in insights:
            if isinstance(insight, dict):
                insight_copia = dict(insight)
                timestamp_valor = insight_copia.get("timestamp")
                if timestamp_valor:
                    try:
                        insight_copia["timestamp"] = self._parse_datetime(timestamp_valor)
                    except ValueError:
                        print(f"⚠️  Insight descartado por timestamp inválido: {timestamp_valor}")
                        continue
                else:
                    print("⚠️  Insight descartado por no incluir timestamp.")
                    continue
                resultado.append(insight_copia)
            else:
                print(f"⚠️  Insight no es un dict y se descartará: {insight}")
        return resultado

    def _fusionar_metricas_evolucion(self, nuevas_metricas: dict[str, Any]):
        """Mantiene las métricas más recientes al importar múltiples archivos"""
        if not nuevas_metricas:
            return
        if not self.metricas_evolucion:
            self.metricas_evolucion = nuevas_metricas
            return

        fecha_actual = self.metricas_evolucion.get("fecha_actualizacion")
        fecha_nueva = nuevas_metricas.get("fecha_actualizacion")

        try:
            dt_actual = self._parse_datetime(fecha_actual) if fecha_actual else None
        except ValueError:
            dt_actual = None
        try:
            dt_nueva = self._parse_datetime(fecha_nueva) if fecha_nueva else None
        except ValueError:
            dt_nueva = None

        if dt_nueva and (not dt_actual or dt_nueva > dt_actual):
            self.metricas_evolucion = nuevas_metricas

    def _crear_interaccion_desde_dict(self, datos: dict[str, Any]) -> InteraccionCliente | None:
        """Crea una interaccion a partir de un diccionario"""
        if not isinstance(datos, dict):
            return None

        try:
            timestamp = self._parse_datetime(datos.get("timestamp"))
        except ValueError as e:
            print(f"⚠️  Interacción descartada por timestamp inválido: {e}")
            return None
        valor_cotizacion = self._parse_decimal(datos.get("valor_cotizacion"))
        valor_venta = self._parse_decimal(datos.get("valor_venta"))

        interaccion_id = datos.get("id") or self._generar_id_interaccion(
            datos.get("mensaje_cliente", ""), timestamp
        )

        try:
            interaccion = InteraccionCliente(
                id=interaccion_id,
                timestamp=timestamp,
                cliente_id=datos.get("cliente_id", "desconocido"),
                tipo_interaccion=datos.get("tipo_interaccion", "consulta"),
                mensaje_cliente=datos.get("mensaje_cliente", ""),
                respuesta_agente=datos.get("respuesta_agente", ""),
                contexto=self._normalizar_contexto(datos.get("contexto", {})),
                resultado=datos.get("resultado", "pendiente"),
                valor_cotizacion=valor_cotizacion,
                valor_venta=valor_venta,
                satisfaccion_cliente=datos.get("satisfaccion_cliente"),
                lecciones_aprendidas=datos.get("lecciones_aprendidas") or [],
            )
            return interaccion
        except Exception as e:
            print(f"⚠️  Error importando interacción: {e}")
            return None

    def _crear_patron_desde_dict(self, datos: dict[str, Any]) -> PatronVenta | None:
        """Crea un patrón de venta desde un diccionario"""
        if not isinstance(datos, dict):
            return None

        try:
            try:
                fecha_creacion = self._parse_datetime(datos.get("fecha_creacion"))
                fecha_actualizacion = self._parse_datetime(datos.get("fecha_ultima_actualizacion"))
            except ValueError as e:
                print(f"⚠️  Patrón descartado por timestamp inválido: {e}")
                return None

            patron = PatronVenta(
                id=datos.get("id", f"patron_{len(self.patrones_venta) + 1}"),
                nombre=datos.get("nombre", "Patrón identificado"),
                descripcion=datos.get("descripcion", ""),
                frecuencia=datos.get("frecuencia", 0),
                tasa_exito=float(datos.get("tasa_exito", 0.0)),
                factores_clave=datos.get("factores_clave", []),
                productos_asociados=datos.get("productos_asociados", []),
                perfil_cliente=datos.get("perfil_cliente", {}),
                palabras_clave=datos.get("palabras_clave", []),
                estrategia_recomendada=datos.get("estrategia_recomendada", ""),
                fecha_creacion=fecha_creacion,
                fecha_ultima_actualizacion=fecha_actualizacion,
            )
            return patron
        except Exception as e:
            print(f"⚠️  Error importando patrón de venta: {e}")
            return None

    def _crear_conocimiento_producto(
        self, producto_id: str, datos: dict[str, Any]
    ) -> ConocimientoProducto | None:
        """Crea un objeto ConocimientoProducto desde diccionario"""
        if not isinstance(datos, dict):
            return None

        try:
            try:
                fecha_actualizacion = self._parse_datetime(datos.get("fecha_ultima_actualizacion"))
            except ValueError as e:
                print(f"⚠️  Producto {producto_id} descartado por timestamp inválido: {e}")
                return None
            precios = {
                k: self._parse_decimal(v) or Decimal("0")
                for k, v in (datos.get("precios_competitivos", {}) or {}).items()
            }

            conocimiento = ConocimientoProducto(
                producto_id=producto_id,
                nombre=datos.get("nombre", producto_id.title()),
                caracteristicas_base=datos.get("caracteristicas_base", {}),
                caracteristicas_aprendidas=datos.get("caracteristicas_aprendidas", {}),
                objeciones_comunes=datos.get("objeciones_comunes", []),
                respuestas_efectivas=datos.get("respuestas_efectivas", []),
                casos_uso_exitosos=datos.get("casos_uso_exitosos", []),
                precios_competitivos=precios,
                tendencias_demanda=datos.get("tendencias_demanda", []),
                recomendaciones_venta=datos.get("recomendaciones_venta", []),
                fecha_ultima_actualizacion=fecha_actualizacion,
            )
            return conocimiento
        except Exception as e:
            print(f"⚠️  Error importando conocimiento de producto {producto_id}: {e}")
            return None

    def _parse_datetime(self, valor: Any) -> datetime.datetime:
        """Convierte diferentes formatos de fecha a datetime"""
        if isinstance(valor, datetime.datetime):
            return valor
        if isinstance(valor, str):
            # Try Python's built-in fromisoformat first (Python 3.7+)
            # Handles ISO 8601 with timezone (e.g., 2025-11-26T08:06:23.479649+00:00)
            try:
                # Normalize Z to +00:00 for fromisoformat
                valor_normalized = valor.replace("Z", "+00:00")
                # Handle +00 as +00:00
                if valor_normalized.endswith("+00") and not valor_normalized.endswith("+00:00"):
                    valor_normalized = valor_normalized.replace("+00", "+00:00")
                return datetime.datetime.fromisoformat(valor_normalized)
            except (ValueError, AttributeError):
                # fromisoformat not available or format not supported, try manual parsing
                pass

            # Remove timezone indicators for manual parsing
            valor_clean = valor.replace("Z", "").replace("+00:00", "").replace("+00", "")

            formatos = (
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
            )
            for formato in formatos:
                try:
                    return datetime.datetime.strptime(valor_clean, formato)
                except ValueError:
                    continue
        raise ValueError(f"Formato de fecha inválido: {valor}")

    def _parse_decimal(self, valor: Any) -> Decimal | None:
        """Convierte un valor a Decimal"""
        if valor is None or valor == "":
            return None
        if isinstance(valor, Decimal):
            return valor
        try:
            return Decimal(str(valor))
        except Exception:
            return None

    def _normalizar_contexto(self, contexto: Any) -> dict[str, Any]:
        """Asegura que el contexto sea un diccionario"""
        if isinstance(contexto, dict):
            return contexto
        return {}

    def _generar_id_interaccion(self, mensaje: str, timestamp: datetime.datetime) -> str:
        """Genera un ID único para interacciones sin identificador"""
        contenido = f"{mensaje}{timestamp.isoformat()}"
        return hashlib.sha1(contenido.encode("utf-8")).hexdigest()


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
