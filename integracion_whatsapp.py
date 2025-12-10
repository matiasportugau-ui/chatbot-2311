#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integración WhatsApp BMC Uruguay
Sistema de cotizaciones con integración WhatsApp Business API
"""

import json
import datetime
import requests
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
import threading
import time

from ia_conversacional_integrada import IAConversacionalIntegrada
from base_conocimiento_dinamica import InteraccionCliente


class IntegracionWhatsApp:
    """Integración con WhatsApp Business API"""
    
    def __init__(self, ia_conversacional: IAConversacionalIntegrada):
        self.ia = ia_conversacional
        self.app = Flask(__name__)
        self.configurar_rutas()
        self.webhook_verificado = False
        
        # Configuración WhatsApp
        self.whatsapp_token = "TU_WHATSAPP_TOKEN"  # Reemplazar con token real
        self.whatsapp_phone_id = "TU_PHONE_ID"     # Reemplazar con phone ID real
        self.webhook_verify_token = "TU_VERIFY_TOKEN"  # Reemplazar con token de verificación
        
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
            # Verify signature if secret is present
            if self.webhook_verify_token and request.headers.get('X-Hub-Signature-256'):
                from utils.security.webhook_validation import validate_webhook_request
                is_valid, error = validate_webhook_request(request, service='whatsapp')
                if not is_valid:
                    print(f"❌ Firma inválida: {error}")
                    return jsonify({"status": "error", "message": "Invalid signature"}), 403

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
            print(f"❌ Error procesando mensaje WhatsApp: {e}")
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
