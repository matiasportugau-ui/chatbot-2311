#!/usr/bin/env python3
"""
Script para extraer datos de WhatsApp y Mercado Libre para entrenamiento
Extrae conversaciones y solicitudes para uso en entrenamiento de modelos
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("⚠️  pymongo no está instalado. Instala con: pip install pymongo")


class ExtractorDatosEntrenamiento:
    """Extractor de datos para entrenamiento desde WhatsApp y Mercado Libre"""

    def __init__(self, mongodb_uri: Optional[str] = None):
        """
        Inicializa el extractor
        
        Args:
            mongodb_uri: URI de conexión a MongoDB (opcional, usa MONGODB_URI env var)
        """
        self.mongodb_uri = mongodb_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017/bmc_chat")
        self.client: Optional[MongoClient] = None
        self.db = None
        
    def conectar_mongodb(self) -> bool:
        """Conecta a MongoDB"""
        if not MONGODB_AVAILABLE:
            print("❌ MongoDB no disponible - pymongo no instalado")
            return False
            
        try:
            self.client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.server_info()
            
            # Extraer nombre de base de datos
            db_name = "bmc_chat"
            if "/" in self.mongodb_uri:
                parts = self.mongodb_uri.split("/")
                if len(parts) > 3:
                    potential_db = parts[-1].split("?")[0]
                    if potential_db and ":" not in potential_db:
                        db_name = potential_db
            
            self.db = self.client[db_name]
            print(f"✅ Conectado a MongoDB: {db_name}")
            return True
        except ConnectionFailure as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return False
    
    def desconectar_mongodb(self):
        """Cierra la conexión a MongoDB"""
        if self.client:
            self.client.close()
            print("✅ Desconectado de MongoDB")
    
    def extraer_whatsapp_mongodb(
        self,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limite: Optional[int] = None,
        coleccion: str = "conversations",
        incluir_context: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extrae mensajes de WhatsApp desde MongoDB
        
        Args:
            fecha_desde: Fecha desde la cual extraer (opcional)
            fecha_hasta: Fecha hasta la cual extraer (opcional)
            limite: Límite de documentos a extraer (opcional)
            coleccion: Nombre de la colección (default: "conversations")
        
        Returns:
            Lista de conversaciones en formato para entrenamiento
        """
        if not self.db:
            if not self.conectar_mongodb():
                return []
        
        try:
            collection = self.db[coleccion]
            
            # Construir query
            query = {}
            if fecha_desde or fecha_hasta:
                query["timestamp"] = {}
                if fecha_desde:
                    query["timestamp"]["$gte"] = fecha_desde
                if fecha_hasta:
                    query["timestamp"]["$lte"] = fecha_hasta
            
            # Extraer documentos
            cursor = collection.find(query).sort("timestamp", -1)
            if limite:
                cursor = cursor.limit(limite)
            
            conversaciones = []
            for doc in cursor:
                # Formatear para entrenamiento
                conversacion = {
                    "source": "whatsapp",
                    "session_id": doc.get("session_id", ""),
                    "phone": doc.get("phone", ""),
                    "timestamp": doc.get("timestamp", "").isoformat() if isinstance(doc.get("timestamp"), datetime) else str(doc.get("timestamp", "")),
                    "message": doc.get("message", ""),
                    "response": doc.get("response", ""),
                    "response_type": doc.get("response_type", ""),
                    "confidence": doc.get("confidence", 0.0),
                    "intent": doc.get("intent", ""),
                    "entities": doc.get("entities", {}),
                    "metadata": {
                        "source": doc.get("source", "api"),
                        "original_id": str(doc.get("_id", "")),
                    }
                }
                conversaciones.append(conversacion)
            
            print(f"✅ Extraídas {len(conversaciones)} conversaciones de WhatsApp desde {coleccion}")
            
            # También extraer desde context si está habilitado
            if incluir_context and coleccion == "conversations":
                try:
                    context_col = self.db["context"]
                    context_docs = context_col.find({}).limit(limite or 1000)
                    
                    for ctx_doc in context_docs:
                        messages = ctx_doc.get("messages", [])
                        for msg in messages:
                            if msg.get("role") == "user":
                                # Buscar respuesta correspondiente
                                response_msg = None
                                msg_idx = messages.index(msg)
                                if msg_idx + 1 < len(messages) and messages[msg_idx + 1].get("role") == "assistant":
                                    response_msg = messages[msg_idx + 1]
                                
                                conversacion = {
                                    "source": "whatsapp",
                                    "session_id": ctx_doc.get("session_id", ""),
                                    "phone": ctx_doc.get("user_phone", ""),
                                    "timestamp": msg.get("timestamp", ctx_doc.get("last_activity", "")).isoformat() if isinstance(msg.get("timestamp"), datetime) else str(msg.get("timestamp", "")),
                                    "message": msg.get("content", ""),
                                    "response": response_msg.get("content", "") if response_msg else "",
                                    "response_type": "text",
                                    "confidence": 0.0,
                                    "intent": ctx_doc.get("intent", ""),
                                    "entities": ctx_doc.get("entities", {}),
                                    "metadata": {
                                        "source": "context",
                                        "original_id": str(ctx_doc.get("_id", "")),
                                    }
                                }
                                conversaciones.append(conversacion)
                    
                    if conversaciones:
                        print(f"✅ Total extraídas (incluyendo context): {len(conversaciones)} conversaciones")
                except Exception as e:
                    print(f"⚠️  No se pudo extraer desde context: {e}")
            
            return conversaciones
            
        except Exception as e:
            print(f"❌ Error extrayendo WhatsApp: {e}")
            return []
    
    def extraer_whatsapp_archivo(self, archivo: str) -> List[Dict[str, Any]]:
        """
        Extrae mensajes de WhatsApp desde un archivo JSON
        
        Args:
            archivo: Ruta al archivo JSON con conversaciones
        
        Returns:
            Lista de conversaciones formateadas
        """
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            conversaciones = []
            if isinstance(datos, list):
                for item in datos:
                    conversacion = {
                        "source": "whatsapp",
                        "session_id": item.get("session_id", ""),
                        "phone": item.get("phone", ""),
                        "timestamp": item.get("timestamp", ""),
                        "message": item.get("message", ""),
                        "response": item.get("response", ""),
                        "response_type": item.get("response_type", ""),
                        "confidence": item.get("confidence", 0.0),
                        "intent": item.get("intent", ""),
                        "entities": item.get("entities", {}),
                        "metadata": {
                            "source": "file",
                            "file": archivo
                        }
                    }
                    conversaciones.append(conversacion)
            
            print(f"✅ Extraídas {len(conversaciones)} conversaciones desde archivo")
            return conversaciones
            
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {archivo}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Error leyendo JSON: {e}")
            return []
        except Exception as e:
            print(f"❌ Error extrayendo desde archivo: {e}")
            return []
    
    def extraer_mercado_libre_archivo(self, archivo: str) -> List[Dict[str, Any]]:
        """
        Extrae solicitudes de Mercado Libre desde un archivo JSON/CSV
        
        Args:
            archivo: Ruta al archivo con datos de Mercado Libre
        
        Returns:
            Lista de solicitudes formateadas
        """
        try:
            path = Path(archivo)
            
            if path.suffix.lower() == '.json':
                with open(archivo, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
            elif path.suffix.lower() == '.csv':
                import csv
                datos = []
                with open(archivo, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    datos = list(reader)
            else:
                print(f"❌ Formato no soportado: {path.suffix}")
                return []
            
            solicitudes = []
            
            # Manejar formato con estructura {interacciones: [...]}
            if isinstance(datos, dict) and "interacciones" in datos:
                datos = datos["interacciones"]
            
            if isinstance(datos, list):
                for item in datos:
                    # Formatear según estructura esperada de Mercado Libre
                    # Soporta múltiples formatos: API ML, interacciones KB, etc.
                    solicitud = {
                        "source": "mercado_libre",
                        "question_id": item.get("question_id") or item.get("id", ""),
                        "product_id": item.get("product_id") or item.get("item_id", "") or (item.get("contexto", {}).get("item_id", "") if isinstance(item.get("contexto"), dict) else ""),
                        "buyer_id": item.get("buyer_id") or item.get("user_id", "") or item.get("cliente_id", ""),
                        "timestamp": item.get("date_created") or item.get("timestamp", ""),
                        "question": item.get("text") or item.get("question", "") or item.get("mensaje_cliente", ""),
                        "answer": (
                            item.get("answer", {}).get("text", "") if isinstance(item.get("answer"), dict) 
                            else item.get("answer", "") or item.get("respuesta_agente", "")
                        ),
                        "status": item.get("status", "") or item.get("resultado", ""),
                        "product_title": item.get("product_title") or item.get("title", ""),
                        "metadata": {
                            "source": "file",
                            "file": archivo,
                            "tipo_interaccion": item.get("tipo_interaccion", ""),
                            "contexto": item.get("contexto", {})
                        }
                    }
                    solicitudes.append(solicitud)
            
            print(f"✅ Extraídas {len(solicitudes)} solicitudes de Mercado Libre")
            return solicitudes
            
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {archivo}")
            return []
        except Exception as e:
            print(f"❌ Error extrayendo Mercado Libre: {e}")
            return []
    
    def extraer_mercado_libre_api(
        self,
        access_token: str,
        seller_id: Optional[str] = None,
        limite: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Extrae solicitudes de Mercado Libre desde la API
        
        Args:
            access_token: Token de acceso de Mercado Libre
            seller_id: ID del vendedor (opcional)
            limite: Límite de solicitudes a extraer
        
        Returns:
            Lista de solicitudes formateadas
        """
        try:
            import requests
            
            solicitudes = []
            
            # Endpoint para obtener preguntas
            if seller_id:
                url = f"https://api.mercadolibre.com/questions/search"
                params = {
                    "seller_id": seller_id,
                    "status": "ANSWERED",
                    "limit": limite
                }
            else:
                # Si no hay seller_id, intentar obtener desde el token
                url = "https://api.mercadolibre.com/questions/search"
                params = {
                    "status": "ANSWERED",
                    "limit": limite
                }
            
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                
                for question in questions:
                    solicitud = {
                        "source": "mercado_libre",
                        "question_id": question.get("id", ""),
                        "product_id": question.get("item_id", ""),
                        "buyer_id": question.get("from", {}).get("id", ""),
                        "timestamp": question.get("date_created", ""),
                        "question": question.get("text", ""),
                        "answer": question.get("answer", {}).get("text", "") if question.get("answer") else "",
                        "status": question.get("status", ""),
                        "product_title": question.get("item", {}).get("title", ""),
                        "metadata": {
                            "source": "api",
                            "api_version": "v1"
                        }
                    }
                    solicitudes.append(solicitud)
                
                print(f"✅ Extraídas {len(solicitudes)} solicitudes desde API de Mercado Libre")
            else:
                print(f"❌ Error en API de Mercado Libre: {response.status_code} - {response.text}")
            
            return solicitudes
            
        except ImportError:
            print("❌ requests no está instalado. Instala con: pip install requests")
            return []
        except Exception as e:
            print(f"❌ Error extrayendo desde API: {e}")
            return []
    
    def guardar_para_entrenamiento(
        self,
        datos: List[Dict[str, Any]],
        archivo_salida: str,
        formato: str = "json"
    ):
        """
        Guarda los datos extraídos en formato para entrenamiento
        
        Args:
            datos: Lista de datos a guardar
            archivo_salida: Ruta del archivo de salida
            formato: Formato de salida ("json" o "csv")
        """
        try:
            path = Path(archivo_salida)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if formato.lower() == "json":
                with open(archivo_salida, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, ensure_ascii=False, indent=2)
                print(f"✅ Datos guardados en JSON: {archivo_salida}")
                
            elif formato.lower() == "csv":
                import csv
                
                if not datos:
                    print("⚠️  No hay datos para guardar")
                    return
                
                # Obtener todas las claves posibles
                all_keys = set()
                for item in datos:
                    all_keys.update(item.keys())
                
                # Aplanar estructuras anidadas
                flattened_data = []
                for item in datos:
                    flat_item = {}
                    for key, value in item.items():
                        if isinstance(value, (dict, list)):
                            flat_item[key] = json.dumps(value, ensure_ascii=False)
                        else:
                            flat_item[key] = value
                    flattened_data.append(flat_item)
                
                with open(archivo_salida, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                    writer.writeheader()
                    writer.writerows(flattened_data)
                
                print(f"✅ Datos guardados en CSV: {archivo_salida}")
            
            else:
                print(f"❌ Formato no soportado: {formato}")
                return
            
            print(f"📊 Total de registros guardados: {len(datos)}")
            
        except Exception as e:
            print(f"❌ Error guardando datos: {e}")
    
    def generar_resumen(self, datos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera un resumen de los datos extraídos
        
        Args:
            datos: Lista de datos extraídos
        
        Returns:
            Diccionario con estadísticas
        """
        if not datos:
            return {"total": 0}
        
        # Contar por fuente
        por_fuente = {}
        for item in datos:
            fuente = item.get("source", "unknown")
            por_fuente[fuente] = por_fuente.get(fuente, 0) + 1
        
        # Contar intents (si aplica)
        intents = {}
        for item in datos:
            intent = item.get("intent", "")
            if intent:
                intents[intent] = intents.get(intent, 0) + 1
        
        resumen = {
            "total": len(datos),
            "por_fuente": por_fuente,
            "intents": intents,
            "fecha_extraccion": datetime.now().isoformat()
        }
        
        return resumen


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extrae datos de WhatsApp y Mercado Libre para entrenamiento"
    )
    
    parser.add_argument(
        "--whatsapp-mongodb",
        action="store_true",
        help="Extraer WhatsApp desde MongoDB"
    )
    
    parser.add_argument(
        "--whatsapp-archivo",
        type=str,
        help="Extraer WhatsApp desde archivo JSON"
    )
    
    parser.add_argument(
        "--mercado-libre-archivo",
        type=str,
        help="Extraer Mercado Libre desde archivo"
    )
    
    parser.add_argument(
        "--mercado-libre-api",
        action="store_true",
        help="Extraer Mercado Libre desde API"
    )
    
    parser.add_argument(
        "--access-token",
        type=str,
        help="Token de acceso para API de Mercado Libre"
    )
    
    parser.add_argument(
        "--seller-id",
        type=str,
        help="ID del vendedor en Mercado Libre"
    )
    
    parser.add_argument(
        "--fecha-desde",
        type=str,
        help="Fecha desde (formato: YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--fecha-hasta",
        type=str,
        help="Fecha hasta (formato: YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--limite",
        type=int,
        help="Límite de registros a extraer"
    )
    
    parser.add_argument(
        "--salida",
        type=str,
        default="datos_entrenamiento.json",
        help="Archivo de salida (default: datos_entrenamiento.json)"
    )
    
    parser.add_argument(
        "--formato",
        type=str,
        choices=["json", "csv"],
        default="json",
        help="Formato de salida (default: json)"
    )
    
    args = parser.parse_args()
    
    # Crear extractor
    extractor = ExtractorDatosEntrenamiento()
    
    todos_los_datos = []
    
    # Extraer WhatsApp desde MongoDB
    if args.whatsapp_mongodb:
        fecha_desde = None
        fecha_hasta = None
        
        if args.fecha_desde:
            fecha_desde = datetime.strptime(args.fecha_desde, "%Y-%m-%d")
        if args.fecha_hasta:
            fecha_hasta = datetime.strptime(args.fecha_hasta, "%Y-%m-%d")
        
        datos_wa = extractor.extraer_whatsapp_mongodb(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limite=args.limite
        )
        todos_los_datos.extend(datos_wa)
    
    # Extraer WhatsApp desde archivo
    if args.whatsapp_archivo:
        datos_wa = extractor.extraer_whatsapp_archivo(args.whatsapp_archivo)
        todos_los_datos.extend(datos_wa)
    
    # Extraer Mercado Libre desde archivo
    if args.mercado_libre_archivo:
        datos_ml = extractor.extraer_mercado_libre_archivo(args.mercado_libre_archivo)
        todos_los_datos.extend(datos_ml)
    
    # Extraer Mercado Libre desde API
    if args.mercado_libre_api:
        if not args.access_token:
            print("❌ Se requiere --access-token para usar API de Mercado Libre")
            sys.exit(1)
        
        datos_ml = extractor.extraer_mercado_libre_api(
            access_token=args.access_token,
            seller_id=args.seller_id,
            limite=args.limite or 100
        )
        todos_los_datos.extend(datos_ml)
    
    # Guardar datos
    if todos_los_datos:
        extractor.guardar_para_entrenamiento(todos_los_datos, args.salida, args.formato)
        
        # Mostrar resumen
        resumen = extractor.generar_resumen(todos_los_datos)
        print("\n📊 RESUMEN DE EXTRACCIÓN")
        print("=" * 50)
        print(json.dumps(resumen, indent=2, ensure_ascii=False))
    else:
        print("⚠️  No se extrajeron datos. Usa --help para ver opciones.")
    
    # Cerrar conexión
    extractor.desconectar_mongodb()


if __name__ == "__main__":
    main()

