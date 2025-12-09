"""
Verification script for Flexible Agent Flow.
This script initializes the IAConversacionalIntegrada and runs a simulated conversation
to verify that the agentic loop and tool calling are working.
"""
import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    from ia_conversacional_integrada import IAConversacionalIntegrada
    print("✅ Successfully imported IAConversacionalIntegrada")
except ImportError as e:
    print(f"❌ Failed to import IAConversacionalIntegrada: {e}")
    sys.exit(1)

def test_flow():
    print("\n--- Starting Agentic Flow Test ---\n")
    
    # Initialize Agent
    try:
        agent = IAConversacionalIntegrada()
        print("✅ Agent initialized")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return

    # Simulate User Input (Complex request to trigger tools)
    user_msg = "Hola Superchapita, necesito precio para un techo Isodec de 50 metros cuadrados en Montevideo. Me llamo Juan Perez."
    client_id = "test_user_001"
    
    print(f"\n👤 USER: {user_msg}")
    
    # Process Message
    try:
        response = agent.procesar_mensaje(user_msg, client_id)
        
        print(f"\n🤖 AGENT RESPONSE:\n{response.mensaje}")
        print(f"\nConfianza: {response.confianza}")
        print(f"Tipo: {response.tipo_respuesta}")
        
    except Exception as e:
        print(f"\n❌ Error processing message: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_flow()
