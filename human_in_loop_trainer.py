#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Human-in-the-Loop Training System
==================================

Sistema de entrenamiento con feedback humano:
- Detección de emoji ❌ para modo "Captura de Aprendizaje"
- Procesamiento de comandos de voz para correcciones
- "Doubt Gate" para respuestas con baja confianza
- Resolución de conflictos
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FeedbackCapture:
    """Captura de feedback del agente"""
    agent_id: str
    timestamp: str
    feedback_type: str  # 'emoji_rejection', 'voice_correction', 'text_correction'
    original_response: str
    correction: Optional[str]
    topic: Optional[str]
    confidence: float
    metadata: Dict[str, Any]


class HumanInTheLoopTrainer:
    """Sistema de entrenamiento con feedback humano"""
    
    def __init__(self, dynamic_knowledge_layer, multimodal_processor):
        """
        Inicializa el entrenador HITL
        
        Args:
            dynamic_knowledge_layer: Sistema de conocimiento dinámico
            multimodal_processor: Procesador multimodal para audio
        """
        self.dkl = dynamic_knowledge_layer
        self.multimodal = multimodal_processor
        
        # Configuración
        self.doubt_threshold = 0.8  # Umbral de confianza para "Doubt Gate"
        self.emoji_rejection = '❌'
        
        # Historial de feedback
        self.feedback_history: List[FeedbackCapture] = []
        
        # Patrones para extracción de correcciones de voz
        self.correction_patterns = [
            r"el precio es ([0-9.,]+)",
            r"son ([0-9.,]+) pesos",
            r"cuesta ([0-9.,]+)",
            r"el tiempo de entrega es ([0-9]+) días?",
            r"la entrega demora ([0-9]+) días?",
        ]
    
    def detect_feedback(self, message: str, message_type: str = 'text') -> Optional[str]:
        """
        Detecta si un mensaje contiene feedback de rechazo
        
        Args:
            message: Contenido del mensaje
            message_type: Tipo ('text', 'reaction', 'audio')
            
        Returns:
            Tipo de feedback detectado o None
        """
        if message_type == 'reaction':
            if self.emoji_rejection in message:
                return 'emoji_rejection'
        
        elif message_type == 'text':
            # Detectar palabras de rechazo
            rejection_words = ['no', 'incorrecto', 'mal', 'error', 'equivocado']
            message_lower = message.lower()
            if any(word in message_lower for word in rejection_words):
                return 'text_correction'
        
        elif message_type == 'audio':
            # El audio será procesado para extraer correcciones
            return 'voice_correction'
        
        return None
    
    def enter_learning_mode(self, agent_id: str, original_response: str,
                           rejection_type: str) -> str:
        """
        Entra en modo "Captura de Aprendizaje"
        
        Args:
            agent_id: ID del agente
            original_response: Respuesta original que fue rechazada
            rejection_type: Tipo de rechazo
            
        Returns:
            Mensaje para solicitar corrección
        """
        print(f"🎓 Entrando en modo aprendizaje para agente {agent_id}")
        
        if rejection_type == 'emoji_rejection':
            return (
                "⚠️ Parece que la información no era correcta. "
                "¿Podrías decirme cuál es la información correcta? "
                "Puedes escribirla o enviar un audio."
            )
        
        elif rejection_type in ['text_correction', 'voice_correction']:
            return (
                "📝 Entendido, voy a aprender de esto. "
                "¿Podrías confirmar cuál es la información correcta?"
            )
        
        return "¿Cuál sería la respuesta correcta?"
    
    def process_correction(self, agent_id: str, correction_input: Any,
                          input_type: str, original_response: str,
                          topic: Optional[str] = None) -> FeedbackCapture:
        """
        Procesa una corrección del agente
        
        Args:
            agent_id: ID del agente
            correction_input: Corrección (texto, audio, etc.)
            input_type: Tipo de entrada
            original_response: Respuesta original
            topic: Tema de la corrección (opcional)
            
        Returns:
            FeedbackCapture con la información procesada
        """
        correction_text = None
        metadata = {'input_type': input_type}
        
        # Procesar según tipo
        if input_type == 'text':
            correction_text = str(correction_input)
        
        elif input_type == 'audio':
            # Transcribir audio
            multimodal_result = self.multimodal.process_input(
                correction_input, 
                input_type='audio'
            )
            correction_text = multimodal_result.content
            metadata['transcription_confidence'] = multimodal_result.confidence
            metadata['processing_notes'] = multimodal_result.processing_notes
        
        # Extraer información estructurada
        extracted_data = self._extract_correction_data(correction_text)
        
        # Crear captura de feedback
        feedback = FeedbackCapture(
            agent_id=agent_id,
            timestamp=datetime.now().isoformat(),
            feedback_type=input_type + '_correction',
            original_response=original_response,
            correction=correction_text,
            topic=topic or extracted_data.get('topic'),
            confidence=0.9,
            metadata={**metadata, **extracted_data}
        )
        
        self.feedback_history.append(feedback)
        
        # Actualizar conocimiento dinámico si se extrajo información
        if extracted_data.get('value'):
            self.dkl.add_correction(
                topic=extracted_data.get('topic', 'general'),
                value=extracted_data['value'],
                corrected_by=agent_id,
                metadata={
                    'original_response': original_response,
                    'correction_text': correction_text
                }
            )
        
        return feedback
    
    def _extract_correction_data(self, text: str) -> Dict[str, Any]:
        """
        Extrae datos estructurados de una corrección
        
        Args:
            text: Texto de la corrección
            
        Returns:
            Diccionario con datos extraídos
        """
        extracted = {}
        
        # Intentar extraer precio
        for pattern in self.correction_patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = match.group(1)
                
                # Determinar tipo de corrección
                if 'precio' in pattern or 'cuesta' in pattern:
                    extracted['topic'] = 'precio'
                    extracted['value'] = value
                    extracted['value_type'] = 'currency'
                
                elif 'entrega' in pattern:
                    extracted['topic'] = 'tiempo_entrega'
                    extracted['value'] = value
                    extracted['value_type'] = 'days'
                
                break
        
        return extracted
    
    def should_ask_for_validation(self, confidence_score: float) -> bool:
        """
        Determina si se debe pedir validación (Doubt Gate)
        
        Args:
            confidence_score: Score de confianza de la respuesta
            
        Returns:
            True si se debe pedir validación
        """
        return confidence_score < self.doubt_threshold
    
    def format_doubt_gate_response(self, response: str, confidence: float) -> str:
        """
        Formatea respuesta con "Doubt Gate"
        
        Args:
            response: Respuesta original
            confidence: Nivel de confianza
            
        Returns:
            Respuesta formateada con advertencia
        """
        if self.should_ask_for_validation(confidence):
            return (
                "⚠️ Verificando con mi base de entrenamiento...\n\n"
                f"{response}\n\n"
                "Por favor, confirma si esta información es correcta. "
                "Si encuentras algún error, puedes corregirme."
            )
        return response
    
    def handle_conflict_confirmation(self, topic: str, old_value: Any, 
                                    new_value: Any, agent_id: str) -> str:
        """
        Maneja confirmación cuando hay conflicto
        
        Args:
            topic: Tema del conflicto
            old_value: Valor anterior
            new_value: Nuevo valor
            agent_id: ID del agente actual
            
        Returns:
            Mensaje de confirmación
        """
        # Buscar quién dio la corrección anterior
        previous_corrections = [
            f for f in self.feedback_history 
            if f.topic == topic and str(old_value) in str(f.correction)
        ]
        
        previous_agent = "otro agente"
        if previous_corrections:
            previous_agent = f"el agente {previous_corrections[0].agent_id}"
        
        return (
            f"⚠️ Detecto un conflicto:\n\n"
            f"• {previous_agent} dijo: {old_value}\n"
            f"• Tú dices: {new_value}\n\n"
            f"¿Quieres que actualice la información con tu valor? "
            f"Responde 'Sí' para confirmar."
        )
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de aprendizaje"""
        total_corrections = len(self.feedback_history)
        
        by_type = {}
        by_agent = {}
        by_topic = {}
        
        for feedback in self.feedback_history:
            # Por tipo
            by_type[feedback.feedback_type] = by_type.get(feedback.feedback_type, 0) + 1
            
            # Por agente
            by_agent[feedback.agent_id] = by_agent.get(feedback.agent_id, 0) + 1
            
            # Por tema
            if feedback.topic:
                by_topic[feedback.topic] = by_topic.get(feedback.topic, 0) + 1
        
        return {
            'total_corrections': total_corrections,
            'by_type': by_type,
            'by_agent': by_agent,
            'by_topic': by_topic,
            'doubt_threshold': self.doubt_threshold
        }
    
    def export_training_examples(self, output_file: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Exporta ejemplos de entrenamiento few-shot
        
        Args:
            output_file: Archivo de salida (opcional)
            
        Returns:
            Lista de ejemplos de entrenamiento
        """
        examples = []
        
        for feedback in self.feedback_history:
            if feedback.correction:
                example = {
                    'input': f"Pregunta del agente relacionada con: {feedback.topic}",
                    'incorrect_response': feedback.original_response,
                    'correct_response': feedback.correction,
                    'metadata': {
                        'agent_id': feedback.agent_id,
                        'timestamp': feedback.timestamp,
                        'confidence': feedback.confidence
                    }
                }
                examples.append(example)
        
        if output_file:
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(examples, f, indent=2, ensure_ascii=False)
            print(f"✅ Exportados {len(examples)} ejemplos de entrenamiento")
        
        return examples


# Ejemplo de uso con WhatsApp
class WhatsAppHITLIntegration:
    """Integración del HITL con WhatsApp Business"""
    
    def __init__(self, hitl_trainer: HumanInTheLoopTrainer):
        self.hitl = hitl_trainer
        self.active_learning_sessions = {}  # agent_id -> session_data
    
    def handle_message(self, agent_id: str, message: str, 
                      message_type: str = 'text') -> Dict[str, Any]:
        """
        Maneja mensaje de WhatsApp
        
        Args:
            agent_id: ID del agente de WhatsApp
            message: Contenido del mensaje
            message_type: Tipo de mensaje
            
        Returns:
            Respuesta para enviar al agente
        """
        # Verificar si hay sesión de aprendizaje activa con original_response
        if agent_id in self.active_learning_sessions and 'original_response' in self.active_learning_sessions[agent_id]:
            return self._handle_learning_session(agent_id, message, message_type)
        
        # Detectar feedback de rechazo
        feedback_type = self.hitl.detect_feedback(message, message_type)
        
        if feedback_type:
            # Obtener la última respuesta guardada
            last_response = ''
            if agent_id in self.active_learning_sessions:
                last_response = self.active_learning_sessions[agent_id].get('last_response', '')
            
            # Iniciar sesión de aprendizaje
            session = {
                'started_at': datetime.now().isoformat(),
                'feedback_type': feedback_type,
                'original_response': last_response,
                'last_response': last_response
            }
            self.active_learning_sessions[agent_id] = session
            
            response_text = self.hitl.enter_learning_mode(
                agent_id, 
                session['original_response'],
                feedback_type
            )
            
            return {
                'type': 'learning_mode',
                'message': response_text,
                'session_active': True
            }
        
        return {
            'type': 'normal',
            'message': None,
            'session_active': False
        }
    
    def _handle_learning_session(self, agent_id: str, message: str,
                                 message_type: str) -> Dict[str, Any]:
        """Maneja mensaje dentro de sesión de aprendizaje"""
        session = self.active_learning_sessions[agent_id]
        
        # Procesar corrección
        feedback = self.hitl.process_correction(
            agent_id=agent_id,
            correction_input=message,
            input_type=message_type,
            original_response=session['original_response']
        )
        
        # Cerrar sesión
        del self.active_learning_sessions[agent_id]
        
        return {
            'type': 'learning_complete',
            'message': (
                "✅ ¡Gracias! He aprendido de tu corrección. "
                "La próxima vez daré la información correcta."
            ),
            'session_active': False,
            'feedback': feedback
        }
    
    def store_last_response(self, agent_id: str, response: str):
        """Guarda la última respuesta enviada al agente"""
        if agent_id not in self.active_learning_sessions:
            self.active_learning_sessions[agent_id] = {}
        self.active_learning_sessions[agent_id]['last_response'] = response
