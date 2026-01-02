#!/usr/bin/env python3
"""
Chat Interactivo con IA - Agente de Cotizaciones BMC Uruguay
Usa IAConversacionalIntegrada con todos los modelos disponibles
"""

import os
import sys
from pathlib import Path

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    if os.path.exists(".env.local"):
        load_dotenv(".env.local", override=True)
    elif os.path.exists(".env"):
        load_dotenv(".env", override=True)
except ImportError:
    pass

# Importar IA Conversacional Integrada
try:
    from ia_conversacional_integrada import IAConversacionalIntegrada
    IA_AVAILABLE = True
except ImportError as e:
    print(f"❌ Error importando IA: {e}", file=sys.stderr)
    IA_AVAILABLE = False

# Importar sistema de cotizaciones para integración
try:
    from sistema_cotizaciones import Cliente, EspecificacionCotizacion, SistemaCotizacionesBMC
    from utils_cotizaciones import construir_contexto_validacion, obtener_datos_faltantes, formatear_mensaje_faltantes
    SISTEMA_COTIZACIONES_AVAILABLE = True
except ImportError:
    SISTEMA_COTIZACIONES_AVAILABLE = False


class ChatInteractivoAI:
    """Chat interactivo con IA completa"""

    def __init__(self):
        """Inicializar chat con IA"""
        print("[INFO] Inicializando chat con IA...", file=sys.stderr)

        if not IA_AVAILABLE:
            print("❌ IA no disponible. Usa chat_interactivo.py para modo básico.", file=sys.stderr)
            sys.exit(1)

        # Inicializar IA Conversacional
        self.ia = IAConversacionalIntegrada()

        if not self.ia.use_ai:
            print("⚠️  IA no habilitada. Verifica las credenciales.", file=sys.stderr)
            print("   Configura OPENAI_API_KEY, GEMINI_API_KEY, o XAI_API_KEY en .env", file=sys.stderr)

        # Inicializar sistema de cotizaciones si está disponible
        if SISTEMA_COTIZACIONES_AVAILABLE:
            self.sistema_cotizaciones = SistemaCotizacionesBMC()
        else:
            self.sistema_cotizaciones = None

        # IDs de sesión
        self.cliente_id = "chat_interactivo_user"
        self.sesion_id = f"session_{os.getpid()}"

        # Estado de conversación
        self.en_cotizacion = False
        self.datos_cotizacion = {}

        print(f"[INFO] Chat con IA inicializado", file=sys.stderr)
        if self.ia.model_integrator:
            models = self.ia.model_integrator.list_available_models()
            enabled = [m for m in models if m.get('enabled')]
            providers = set(m.get('provider') for m in enabled)
            print(f"[INFO] Modelos disponibles: {len(enabled)} de {len(providers)} proveedores", file=sys.stderr)
            print(f"[INFO] Proveedores: {', '.join(providers)}", file=sys.stderr)

    def procesar_mensaje(self, mensaje: str) -> str:
        """Procesa mensaje usando IA"""
        if not mensaje.strip():
            return "Por favor, escribe algo para que pueda ayudarte."

        try:
            # Procesar con IA
            respuesta_ia = self.ia.procesar_mensaje(
                mensaje=mensaje,
                cliente_id=self.cliente_id,
                sesion_id=self.sesion_id
            )

            # Extraer mensaje de la respuesta
            if hasattr(respuesta_ia, 'mensaje'):
                mensaje_respuesta = respuesta_ia.mensaje
                confianza = respuesta_ia.confianza

                # Si la confianza es baja, agregar contexto
                if confianza < 0.5:
                    mensaje_respuesta += "\n\n💡 Si necesitas ayuda con cotizaciones, productos o información, no dudes en preguntar."

                return mensaje_respuesta
            else:
                return str(respuesta_ia)

        except Exception as e:
            print(f"[ERROR] Error procesando mensaje: {e}", file=sys.stderr)
            return f"Lo siento, hubo un error procesando tu mensaje. Por favor, intenta de nuevo.\n\nError: {str(e)[:100]}"

    def saludar(self) -> str:
        """Saludo inicial usando IA"""
        saludo = self.procesar_mensaje(
            "Hola, soy un cliente interesado en productos de aislamiento térmico. "
            "Preséntate y dime cómo puedes ayudarme."
        )
        return saludo


def main():
    """Función principal"""
    sys.stdout.flush()
    sys.stderr.flush()

    print("=" * 80)
    print("🤖 CHAT INTERACTIVO CON IA - AGENTE DE COTIZACIONES BMC URUGUAY")
    print("=" * 80)
    print("Este chat usa IA para responder de forma inteligente y contextual")
    print("Escribe 'salir' para terminar la conversación")
    print("=" * 80)
    sys.stdout.flush()

    try:
        chat = ChatInteractivoAI()
    except Exception as e:
        print(f"❌ Error inicializando chat: {e}", file=sys.stderr)
        print("💡 Sugerencia: Verifica que las credenciales de IA estén configuradas", file=sys.stderr)
        sys.exit(1)

    # Saludo inicial
    print(f"\n🤖 Agente: {chat.saludar()}")
    sys.stdout.flush()

    while True:
        try:
            # Obtener mensaje
            sys.stdout.flush()
            mensaje = input("\n👤 Tú: ").strip()

            # Verificar salida
            if mensaje.lower() in ["salir", "exit", "chau", "adios", "bye", "quit"]:
                despedida = chat.procesar_mensaje("Despídete de forma amigable")
                print(f"\n🤖 Agente: {despedida}")
                sys.stdout.flush()
                break

            # Procesar mensaje
            if mensaje:
                respuesta = chat.procesar_mensaje(mensaje)
                print(f"\n🤖 Agente: {respuesta}")
                sys.stdout.flush()
            else:
                print("\n⚠️  Por favor, escribe algo.")
                sys.stdout.flush()

        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            sys.stdout.flush()
            break
        except Exception as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.stderr.flush()


if __name__ == "__main__":
    main()

