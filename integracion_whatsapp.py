#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integración WhatsApp BMC Uruguay
Sistema de cotizaciones con integración WhatsApp Business API
"""

import json
import datetime
import requests
import os
import logging
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
import threading
import time

from ia_conversacional_integrada import IAConversacionalIntegrada
from base_conocimiento_dinamica import InteraccionCliente
from utils.security.webhook_validation import WhatsAppWebhookValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory rate limiting for Flask
_flask_rate_limits = {}


def check_flask_rate_limit(client_id: str, limit: int = 60, window: int = 60) -> bool:
    """
    Simple rate limiting for Flask endpoints.
    
    Args:
        client_id: Client identifier (IP address)
        limit: Maximum requests per window
        window: Time window in seconds
        
    Returns:
        bool: True if allowed, False if rate limited
    """
    current_time = time.time()
    
    if client_id not in _flask_rate_limits:
        _flask_rate_limits[client_id] = []
    
    # Remove old entries
    _flask_rate_limits[client_id] = [
        t for t in _flask_rate_limits[client_id]
        if current_time - t < window
    ]
    
    # Check limit
    if len(_flask_rate_limits[client_id]) >= limit:
        return False
    
    _flask_rate_limits[client_id].append(current_time)
    return True


class IntegracionWhatsApp:
    """Integración con WhatsApp Business API"""
    
    def __init__(self, ia_conversacional: IAConversacionalIntegrada):
        self.ia = ia_conversacional
        self.app = Flask(__name__)
        self.configurar_rutas()
        self.webhook_verificado = False
        
        # Configuración WhatsApp desde variables de entorno
        self.whatsapp_token = os.getenv("WHATSAPP_TOKEN", "TU_WHATSAPP_TOKEN")
        self.whatsapp_phone_id = os.getenv("WHATSAPP_PHONE_ID", "TU_PHONE_ID")
        self.webhook_verify_token = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "TU_VERIFY_TOKEN")
        self.webhook_secret = os.getenv("WHATSAPP_WEBHOOK_SECRET", "")
        
        # Initialize webhook validator
        if self.webhook_secret:
            self.webhook_validator = WhatsAppWebhookValidator(self.webhook_secret)
        else:
            logger.warning("WHATSAPP_WEBHOOK_SECRET not set - signature validation disabled")
            self.webhook_validator = None
        
        # URL base de WhatsApp API
        self.whatsapp_api_url = f"https://graph.facebook.com/v18.0/{self.whatsapp_phone_id}/messages"
    
    def configurar_rutas(self):
        """Configura las rutas de la API Flask"""
        
        @self.app.route('/webhook', methods=['GET', 'POST'])
        def webhook():
            if request.method == 'GET':
                # Verificación del webhook
                return self.verificar_webhook()
            elif request.method == 'POST':
                # Procesar mensajes entrantes
                return self.procesar_mensaje_whatsapp()
        
        @self.app.route('/enviar_mensaje', methods=['POST'])
        def enviar_mensaje():
            return self.enviar_mensaje_whatsapp()
        
        @self.app.route('/estado_sistema', methods=['GET'])
        def estado_sistema():
            return self.obtener_estado_sistema()
    
    def verificar_webhook(self):
        """Verifica el webhook de WhatsApp"""
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if verify_token == self.webhook_verify_token:
            self.webhook_verificado = True
            print("✅ Webhook de WhatsApp verificado correctamente")
            return challenge
        else:
            print("❌ Error en verificación del webhook")
            return "Error", 403
    
    def procesar_mensaje_whatsapp(self):
        """Procesa mensajes entrantes de WhatsApp"""
        try:
            # Rate limiting - max 30 requests per minute per IP
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if not check_flask_rate_limit(f"whatsapp:{client_ip}", limit=30, window=60):
                logger.warning(f"Rate limit exceeded for WhatsApp webhook from {client_ip}")
                return jsonify({"status": "error", "message": "Rate limit exceeded"}), 429
            
            # Validate webhook signature if validator is configured
            if self.webhook_validator:
                signature = request.headers.get('X-Hub-Signature-256', '')
                payload = request.get_data()
                
                if not self.webhook_validator.validate(payload, signature):
                    logger.error("Invalid webhook signature")
                    return jsonify({"status": "error", "message": "Invalid signature"}), 401
            
            data = request.get_json()
            
            if not data or 'entry' not in data:
                return jsonify({"status": "error", "message": "Datos inválidos"}), 400
            
            # Extraer información del mensaje
            entry = data['entry'][0]
            changes = entry['changes'][0]
            value = changes['value']
            
            if 'messages' not in value:
                return jsonify({"status": "ok"})
            
            messages = value['messages']
            
            for message in messages:
                self.procesar_mensaje_individual(message, value)
            
            return jsonify({"status": "ok"})
            
        except Exception as e:
            logger.error(f"Error procesando mensaje WhatsApp: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def procesar_mensaje_individual(self, message: Dict, value: Dict):
        """Procesa un mensaje individual de WhatsApp"""
        try:
            # Extraer datos del mensaje
            from_number = message['from']
            message_id = message['id']
            timestamp = message['timestamp']
            
            # Extraer texto del mensaje
            if 'text' in message:
                text = message['text']['body']
            else:
                text = "Mensaje no soportado"
            
            # Extraer información del contacto
            contacts = value.get('contacts', [])
            contact_name = contacts[0]['profile']['name'] if contacts else "Cliente"
            
            print(f"📱 Mensaje recibido de {contact_name} ({from_number}): {text}")
            
            # Procesar con IA
            respuesta = self.ia.procesar_mensaje(text, from_number)
            
            # Enviar respuesta
            self.enviar_respuesta_whatsapp(from_number, respuesta.mensaje)
            
            # Registrar interacción
            self.registrar_interaccion_whatsapp(
                from_number, contact_name, text, respuesta.mensaje, message_id
            )
            
        except Exception as e:
            print(f"❌ Error procesando mensaje individual: {e}")
    
    def enviar_respuesta_whatsapp(self, to_number: str, message_text: str):
        """Envía una respuesta por WhatsApp"""
        try:
            headers = {
                'Authorization': f'Bearer {self.whatsapp_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "text",
                "text": {"body": message_text}
            }
            
            response = requests.post(
                self.whatsapp_api_url,
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                print(f"✅ Respuesta enviada a {to_number}")
            else:
                print(f"❌ Error enviando respuesta: {response.text}")
                
        except Exception as e:
            print(f"❌ Error enviando respuesta WhatsApp: {e}")
    
    def enviar_mensaje_whatsapp(self):
        """Endpoint para enviar mensajes manuales"""
        try:
            data = request.get_json()
            to_number = data.get('to')
            message_text = data.get('message')
            
            if not to_number or not message_text:
                return jsonify({"status": "error", "message": "Faltan parámetros"}), 400
            
            self.enviar_respuesta_whatsapp(to_number, message_text)
            
            return jsonify({"status": "success", "message": "Mensaje enviado"})
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def registrar_interaccion_whatsapp(self, phone: str, name: str, mensaje: str, respuesta: str, message_id: str):
        """Registra una interacción de WhatsApp en la base de conocimiento"""
        try:
            interaccion = InteraccionCliente(
                id=f"wa_{message_id}",
                timestamp=datetime.datetime.now(),
                cliente_id=phone,
                tipo_interaccion="whatsapp",
                mensaje_cliente=mensaje,
                respuesta_agente=respuesta,
                contexto={
                    "canal": "whatsapp",
                    "cliente_nombre": name,
                    "telefono": phone,
                    "message_id": message_id
                },
                resultado="exitoso"
            )
            
            self.ia.base_conocimiento.registrar_interaccion(interaccion)
            print(f"✅ Interacción registrada en base de conocimiento")
            
        except Exception as e:
            print(f"❌ Error registrando interacción: {e}")
    
    def obtener_estado_sistema(self):
        """Obtiene el estado actual del sistema"""
        try:
            metricas = {
                "sistema_activo": True,
                "webhook_verificado": self.webhook_verificado,
                "total_interacciones": len(self.ia.base_conocimiento.interacciones),
                "total_patrones": len(self.ia.base_conocimiento.patrones_venta),
                "total_insights": len(self.ia.base_conocimiento.insights_automaticos),
                "conversaciones_activas": len(self.ia.conversaciones_activas),
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            return jsonify(metricas)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def iniciar_servidor(self, host='0.0.0.0', port=5000, debug=False):
        """Inicia el servidor Flask"""
        print(f"🚀 Iniciando servidor WhatsApp en {host}:{port}")
        print(f"📱 Webhook URL: http://{host}:{port}/webhook")
        print(f"📊 Estado del sistema: http://{host}:{port}/estado_sistema")
        
        self.app.run(host=host, port=port, debug=debug)
    
    def simular_mensaje_whatsapp(self, phone: str, name: str, message: str):
        """Simula un mensaje de WhatsApp para testing"""
        print(f"\n📱 SIMULANDO MENSAJE WHATSAPP")
        print(f"De: {name} ({phone})")
        print(f"Mensaje: {message}")
        
        # Procesar con IA
        respuesta = self.ia.procesar_mensaje(message, phone)
        
        print(f"🤖 Respuesta IA: {respuesta.mensaje}")
        print(f"   Confianza: {respuesta.confianza:.2f}")
        
        # Registrar interacción
        self.registrar_interaccion_whatsapp(phone, name, message, respuesta.mensaje, f"sim_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        return respuesta


def main():
    """Función principal para ejecutar la integración WhatsApp"""
    print("📱 INTEGRACIÓN WHATSAPP BMC URUGUAY")
    print("=" * 50)
    
    # Crear IA conversacional
    ia = IAConversacionalIntegrada()
    
    # Crear integración WhatsApp
    whatsapp = IntegracionWhatsApp(ia)
    
    # Simular algunos mensajes para demostrar
    print("\n🎭 SIMULANDO CONVERSACIONES WHATSAPP")
    print("-" * 40)
    
    mensajes_simulados = [
        {
            "phone": "59899123456",
            "name": "Juan Pérez",
            "message": "Hola, necesito información sobre Isodec"
        },
        {
            "phone": "59899123456",
            "name": "Juan Pérez",
            "message": "Quiero cotizar para mi casa, 10m x 5m, 100mm"
        },
        {
            "phone": "59899765432",
            "name": "María García",
            "message": "¿Cuál es el precio de poliestireno 75mm?"
        }
    ]
    
    for mensaje in mensajes_simulados:
        whatsapp.simular_mensaje_whatsapp(
            mensaje["phone"],
            mensaje["name"],
            mensaje["message"]
        )
        print()
    
    # Mostrar estado del sistema
    print("\n📊 ESTADO DEL SISTEMA DESPUÉS DE SIMULACIÓN")
    print("-" * 40)
    estado = whatsapp.obtener_estado_sistema()
    print(json.dumps(estado.get_json(), indent=2, ensure_ascii=False))
    
    print("\n✅ Integración WhatsApp configurada correctamente")
    print("Para usar en producción:")
    print("1. Configurar tokens de WhatsApp Business API")
    print("2. Configurar webhook en Meta Developer Console")
    print("3. Ejecutar: python integracion_whatsapp.py --servidor")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--servidor":
        # Modo servidor
        ia = IAConversacionalIntegrada()
        whatsapp = IntegracionWhatsApp(ia)
        whatsapp.iniciar_servidor()
    else:
        # Modo demo
        main()
