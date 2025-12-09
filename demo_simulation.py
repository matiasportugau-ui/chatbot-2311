#!/usr/bin/env python3
"""
Simulación de Chatbot con IA Real (Modo Demo)
Este script simula una conversación donde el USUARIO está guionado
pero el AGENTE es la IA real del sistema (IAConversacionalIntegrada).
"""
import sys
import time
import os

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ia_conversacional_integrada import IAConversacionalIntegrada
except ImportError as e:
    print(f"Error: No se pudo importar IAConversacionalIntegrada: {e}")
    sys.exit(1)

class DemoSimulationAI:
    def __init__(self):
        print("⏳ Inicializando IA Conversacional...")
        try:
            self.ia = IAConversacionalIntegrada()
            self.session_id = f"demo_sim_{int(time.time())}"
            self.client_id = "simulated_user_01"
            print("✅ IA Inicializada correctamente")
        except Exception as e:
            print(f"❌ Error inicializando IA: {e}")
            sys.exit(1)

    def print_agent(self, msg):
        print(f"\n🤖 AGENTE (IA): {msg}")
        # Small delay to simulate reading/thinking time
        time.sleep(1.5)

    def print_user(self, msg):
        print(f"\n👤 USUARIO (Simulado): {msg}")
        time.sleep(1)

    def run_simulation(self):
        print("="*60)
        print(" INICIANDO SIMULACIÓN CON IA REAL")
        print("="*60)
        print(f"Sesión ID: {self.session_id}")
        
        # Guion del usuario (User Script)
        # Diseñado para fluir naturalmente con la IA
        conversation_flow = [
            "Hola buenas",
            "Quisiera cotizar Isodec",
            "Necesito cubrir 50 metros cuadrados. Son 10 metros de largo por 5 de ancho.",
            "En 100mm de espesor",
            "Color Blanco",
            "Terminación con Gotero",
            "Me llamo Juan Pérez",
            "Mi celular es 099123456",
            "Sí, confirmar cotización"
        ]

        # Mensaje inicial del sistema (si lo hubiera) o iniciamos con el usuario
        
        for user_msg in conversation_flow:
            self.print_user(user_msg)
            
            try:
                # Get real response from AI
                # procesar_mensaje returns a RespuestaIA object
                start_time = time.time()
                response_obj = self.ia.procesar_mensaje(
                    mensaje=user_msg,
                    cliente_id=self.client_id,
                    sesion_id=self.session_id
                )
                duration = time.time() - start_time
                
                # The response object has .mensaje attribute
                if hasattr(response_obj, 'mensaje'):
                    ai_msg = response_obj.mensaje
                    
                    # Optional: Print metadata if useful for debugging/demo
                    # print(f"[DEBUG] Intención: {getattr(response_obj, 'tipo_respuesta', 'unknown')} | Confianza: {getattr(response_obj, 'confianza', 0.0):.2f} | Tiempo: {duration:.2f}s")
                    
                    self.print_agent(ai_msg)
                else:
                    print(f"\n⚠️ Error: Respuesta de IA sin mensaje: {response_obj}")
            
            except Exception as e:
                print(f"\n❌ Error procesando mensaje '{user_msg}': {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "="*60)
        print(" FIN DE LA SIMULACIÓN")
        print("="*60)

if __name__ == "__main__":
    sim = DemoSimulationAI()
    sim.run_simulation()
