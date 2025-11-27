#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Example: Using Language Processor with Existing Code
Shows how to integrate the centralized language module
"""

import json
from language_processor import (
    get_language_processor,
    Intent
)
from ia_conversacional_integrada import IAConversacionalIntegrada
from chat_interactivo import AgenteInteractivo


class EnhancedIAConversacional:
    """Enhanced IA Conversacional using centralized language processor"""
    
    def __init__(self):
        self.ia_base = IAConversacionalIntegrada()
        self.language_processor = get_language_processor()
    
    def procesar_mensaje(self, mensaje: str, cliente_id: str, sesion_id: str = None):
        """Process message using centralized language processor"""
        # Use language processor for initial processing
        processed = self.language_processor.process_message(mensaje, sesion_id)
        
        # Map processed intent to IA response
        if processed.intent == Intent.SALUDO:
            return self.ia_base.procesar_mensaje(mensaje, cliente_id, sesion_id)
        elif processed.intent == Intent.COTIZACION:
            # Use extracted entities for better cotization
            return self._procesar_cotizacion_mejorada(processed, cliente_id, sesion_id)
        elif processed.intent == Intent.INFORMACION:
            return self._procesar_informacion_mejorada(processed, cliente_id, sesion_id)
        else:
            # Fallback to original IA
            return self.ia_base.procesar_mensaje(mensaje, cliente_id, sesion_id)
    
    def _procesar_cotizacion_mejorada(self, processed, cliente_id: str, sesion_id: str):
        """Enhanced cotization processing using extracted entities"""
        # Use extracted entities directly
        entities = processed.entities
        
        # Build enhanced message with extracted data
        enhanced_message = processed.original
        
        # Add extracted product if found
        if entities.get('products'):
            product = entities['products'][0]['id']
            if product not in enhanced_message.lower():
                enhanced_message += f" {product}"
        
        # Add extracted dimensions if found
        if entities.get('dimensions'):
            dims = entities['dimensions']
            if 'largo' in dims and 'ancho' in dims:
                enhanced_message += f" {dims['largo']}m x {dims['ancho']}m"
            elif 'area_m2' in dims:
                enhanced_message += f" {dims['area_m2']}m2"
        
        # Process with enhanced message
        return self.ia_base.procesar_mensaje(enhanced_message, cliente_id, sesion_id)
    
    def _procesar_informacion_mejorada(self, processed, cliente_id: str, sesion_id: str):
        """Enhanced information processing"""
        # Use extracted product entities
        entities = processed.entities
        
        if entities.get('products'):
            product = entities['products'][0]['id']
            # Direct product information request
            return self.ia_base.procesar_mensaje(
                f"informacion sobre {product}",
                cliente_id,
                sesion_id
            )
        
        return self.ia_base.procesar_mensaje(processed.original, cliente_id, sesion_id)


class EnhancedAgenteInteractivo:
    """Enhanced interactive agent using language processor"""
    
    def __init__(self):
        self.agente_base = AgenteInteractivo()
        self.language_processor = get_language_processor()
    
    def procesar_mensaje(self, mensaje: str):
        """Process message with language processor"""
        # Process with language module
        processed = self.language_processor.process_message(mensaje)
        
        # Use processed intent for routing
        if processed.intent == Intent.SALUDO:
            return self.agente_base.saludar()
        elif processed.intent == Intent.COTIZACION:
            # Use extracted entities
            return self._iniciar_cotizacion_mejorada(processed)
        elif processed.intent == Intent.INFORMACION:
            return self._responder_consulta_mejorada(processed)
        elif processed.intent == Intent.DESPEDIDA:
            return self.agente_base.despedir()
        else:
            # Fallback to original processing
            return self.agente_base.procesar_mensaje(mensaje)
    
    def _iniciar_cotizacion_mejorada(self, processed):
        """Enhanced cotization initiation"""
        entities = processed.entities
        
        # If we already have product and dimensions, skip some steps
        if entities.get('products') and entities.get('dimensions'):
            # We have enough info to start cotization directly
            producto = entities['products'][0]['id']
            dims = entities['dimensions']
            
            response = f"¡Perfecto! Veo que necesitas {producto}"
            if 'largo' in dims and 'ancho' in dims:
                response += f" para {dims['largo']}m x {dims['ancho']}m"
            elif 'area_m2' in dims:
                response += f" para {dims['area_m2']}m²"
            
            response += "\n\nSolo necesito algunos datos adicionales:\n"
            response += "1️⃣ ¿Qué espesor necesitas? (50mm, 75mm, 100mm, 125mm, 150mm)\n"
            response += "2️⃣ ¿Qué color prefieres? (Blanco, Gris, Personalizado)"
            
            return response
        
        # Otherwise, use standard flow
        return self.agente_base.iniciar_cotizacion()
    
    def _responder_consulta_mejorada(self, processed):
        """Enhanced information response"""
        entities = processed.entities
        
        if entities.get('products'):
            producto = entities['products'][0]['id']
            return self.agente_base.responder_consulta_producto(f"informacion sobre {producto}")
        
        return self.agente_base.responder_consulta_producto(processed.original)


# Example: Migrating existing code
def migrate_chat_interactivo():
    """Example of how to migrate chat_interactivo.py"""
    # OLD WAY:
    # agente = AgenteInteractivo()
    # respuesta = agente.procesar_mensaje(mensaje)
    
    # NEW WAY:
    agente = EnhancedAgenteInteractivo()
    respuesta = agente.procesar_mensaje(mensaje)
    
    return respuesta


# Example: Using in API endpoint
def api_process_message(message: str, session_id: str):
    """Example API endpoint using language processor"""
    processor = get_language_processor()
    
    # Process message
    result = processor.process_message(message, session_id)
    
    # Return structured response
    return {
        'success': True,
        'data': {
            'original': result.original,
            'normalized': result.normalized,
            'language': result.language.value,
            'intent': result.intent.value,
            'confidence': result.confidence,
            'entities': result.entities,
            'context': result.context
        }
    }


# Example: Batch processing
def batch_process_messages(messages: list, session_id: str):
    """Process multiple messages efficiently"""
    processor = get_language_processor()
    results = []
    
    for message in messages:
        result = processor.process_message(message, session_id)
        results.append({
            'message': message,
            'intent': result.intent.value,
            'confidence': result.confidence,
            'entities': result.entities
        })
    
    return results


# Example: Statistics and monitoring
def get_processing_stats():
    """Get processing statistics"""
    processor = get_language_processor()
    stats = processor.export_stats()
    
    return {
        'cache_size': stats['cache_size'],
        'active_sessions': stats['context_sessions'],
        'timestamp': stats['timestamp']
    }


if __name__ == "__main__":
    print("=" * 70)
    print("Language Processor Integration Examples")
    print("=" * 70)
    
    # Example 1: Basic usage
    print("\n1. Basic Usage:")
    processor = get_language_processor()
    result = processor.process_message(
        "Hola, necesito cotizar Isodec 100mm para 50m2",
        session_id="test_session_1"
    )
    print(f"Intent: {result.intent.value}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Entities: {result.entities}")
    
    # Example 2: Enhanced agent
    print("\n2. Enhanced Agent:")
    agente = EnhancedAgenteInteractivo()
    respuesta = agente.procesar_mensaje("Quiero cotizar Isodec para 10m x 5m")
    print(f"Response: {respuesta[:100]}...")
    
    # Example 3: API endpoint
    print("\n3. API Endpoint:")
    api_result = api_process_message("Información sobre poliestireno", "api_session")
    print(f"API Response: {json.dumps(api_result, indent=2, ensure_ascii=False)}")
    
    # Example 4: Statistics
    print("\n4. Statistics:")
    stats = get_processing_stats()
    print(f"Stats: {json.dumps(stats, indent=2)}")
