#!/usr/bin/env python3
"""
Human-in-the-Loop Training System
Implements emoji-based feedback protocol and voice command corrections
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from dynamic_knowledge_manager import DynamicKnowledgeManager, KnowledgeQuery
from multimodal_processor import MultimodalProcessor


@dataclass
class FeedbackSession:
    """Feedback session for training"""
    session_id: str
    agent_id: str
    original_query: str
    bot_response: str
    feedback_type: str  # "emoji", "voice", "text"
    feedback_content: str
    correction_data: Optional[dict[str, Any]]
    timestamp: str
    status: str  # "pending", "approved", "rejected"


class HumanInLoopTrainer:
    """Human-in-the-loop training system"""
    
    # Emoji triggers
    CORRECTION_EMOJIS = ["❌", "✏️", "🔧", "⚠️"]
    APPROVAL_EMOJIS = ["✅", "👍", "✔️"]
    DOUBT_EMOJIS = ["❓", "🤔", "⁉️"]
    
    # Voice command patterns
    CORRECTION_PATTERNS = [
        r"no,?\s*(?:el\s+)?precio\s+es\s+(\d+)",
        r"corregir:?\s*(.+)",
        r"en\s+realidad\s+es\s+(.+)",
        r"debería\s+ser\s+(.+)"
    ]
    
    def __init__(self, knowledge_manager: DynamicKnowledgeManager):
        self.knowledge_manager = knowledge_manager
        self.multimodal_processor = MultimodalProcessor()
        
        self.active_sessions = {}
        self.training_mode_agents = set()  # Agents in training mode
        
        print("✅ Human-in-the-Loop Trainer initialized")
    
    def activate_training_mode(self, agent_id: str):
        """Activate training mode for an agent"""
        self.training_mode_agents.add(agent_id)
        print(f"🎓 Training mode activated for agent: {agent_id}")
    
    def deactivate_training_mode(self, agent_id: str):
        """Deactivate training mode for an agent"""
        if agent_id in self.training_mode_agents:
            self.training_mode_agents.remove(agent_id)
            print(f"✅ Training mode deactivated for agent: {agent_id}")
    
    def is_training_mode(self, agent_id: str) -> bool:
        """Check if agent is in training mode"""
        return agent_id in self.training_mode_agents
    
    def process_message(
        self,
        agent_id: str,
        message: str,
        message_type: str = "text",
        previous_response: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Process a message from an agent
        
        Returns:
            Dictionary with action, response, and metadata
        """
        # Check for training mode commands
        if "MODO ENTRENAMIENTO" in message.upper() or "TRAINING MODE" in message.upper():
            self.activate_training_mode(agent_id)
            return {
                "action": "training_activated",
                "response": "🎓 Modo de entrenamiento activado. Puedes corregir mis respuestas usando ❌ o diciéndome la información correcta.",
                "metadata": {}
            }
        
        if "MODO PRODUCCIÓN" in message.upper() or "PRODUCTION MODE" in message.upper():
            self.deactivate_training_mode(agent_id)
            return {
                "action": "training_deactivated",
                "response": "✅ Modo de producción activado. Las respuestas serán finales sin solicitar correcciones.",
                "metadata": {}
            }
        
        # Check for correction emojis
        if any(emoji in message for emoji in self.CORRECTION_EMOJIS):
            return self._handle_emoji_correction(agent_id, message, previous_response)
        
        # Check for approval emojis
        if any(emoji in message for emoji in self.APPROVAL_EMOJIS):
            return self._handle_approval(agent_id, message)
        
        # Check for voice corrections (process audio first if needed)
        if message_type == "audio":
            return self._handle_voice_correction(agent_id, message, previous_response)
        
        # Check for text-based corrections
        correction_match = self._extract_correction_from_text(message)
        if correction_match and self.is_training_mode(agent_id):
            return self._handle_text_correction(agent_id, message, correction_match, previous_response)
        
        # Normal message - not a correction
        return {
            "action": "normal_response",
            "response": None,  # Will be handled by main bot logic
            "metadata": {}
        }
    
    def _handle_emoji_correction(
        self,
        agent_id: str,
        message: str,
        previous_response: Optional[str]
    ) -> dict[str, Any]:
        """Handle emoji-based correction"""
        # Extract the correction text (everything after the emoji)
        correction_text = message
        for emoji in self.CORRECTION_EMOJIS:
            correction_text = correction_text.replace(emoji, "").strip()
        
        if not correction_text:
            return {
                "action": "request_correction",
                "response": "⚠️ He detectado que quieres hacer una corrección. ¿Cuál es la información correcta?",
                "metadata": {"awaiting_correction": True}
            }
        
        # Create feedback session
        session_id = f"session_{agent_id}_{datetime.now().timestamp()}"
        session = FeedbackSession(
            session_id=session_id,
            agent_id=agent_id,
            original_query="",  # Will be filled from context
            bot_response=previous_response or "",
            feedback_type="emoji",
            feedback_content=correction_text,
            correction_data=None,
            timestamp=datetime.now().isoformat(),
            status="pending"
        )
        
        self.active_sessions[session_id] = session
        
        # Parse the correction
        parsed_correction = self._parse_correction(correction_text)
        
        return {
            "action": "correction_received",
            "response": f"📝 Corrección recibida:\n\n{correction_text}\n\n¿Deseas que actualice mi base de conocimiento con esta información? Responde ✅ para aprobar o ❌ para cancelar.",
            "metadata": {
                "session_id": session_id,
                "parsed_correction": parsed_correction,
                "awaiting_approval": True
            }
        }
    
    def _handle_voice_correction(
        self,
        agent_id: str,
        audio_message: str,
        previous_response: Optional[str]
    ) -> dict[str, Any]:
        """Handle voice-based correction"""
        # Process audio using multimodal processor
        multimodal_input = self.multimodal_processor.process_input(audio_message, "audio")
        transcribed_text = multimodal_input.content
        
        # Check if it's a correction command
        correction_match = self._extract_correction_from_text(transcribed_text)
        if correction_match:
            return self._handle_text_correction(agent_id, transcribed_text, correction_match, previous_response)
        
        return {
            "action": "voice_processed",
            "response": f"🎤 Transcripción: {transcribed_text}",
            "metadata": {"transcription": transcribed_text}
        }
    
    def _handle_text_correction(
        self,
        agent_id: str,
        message: str,
        correction_match: dict[str, Any],
        previous_response: Optional[str]
    ) -> dict[str, Any]:
        """Handle text-based correction"""
        session_id = f"session_{agent_id}_{datetime.now().timestamp()}"
        session = FeedbackSession(
            session_id=session_id,
            agent_id=agent_id,
            original_query="",
            bot_response=previous_response or "",
            feedback_type="text",
            feedback_content=message,
            correction_data=correction_match,
            timestamp=datetime.now().isoformat(),
            status="pending"
        )
        
        self.active_sessions[session_id] = session
        
        return {
            "action": "correction_received",
            "response": f"📝 Corrección identificada:\n\n{correction_match.get('summary', message)}\n\n¿Deseas que actualice mi base de conocimiento? Responde ✅ para aprobar.",
            "metadata": {
                "session_id": session_id,
                "correction": correction_match,
                "awaiting_approval": True
            }
        }
    
    def _handle_approval(self, agent_id: str, message: str) -> dict[str, Any]:
        """Handle approval of correction"""
        # Find the most recent session for this agent
        agent_sessions = [s for s in self.active_sessions.values() if s.agent_id == agent_id and s.status == "pending"]
        
        if not agent_sessions:
            return {
                "action": "no_pending_correction",
                "response": "No hay correcciones pendientes de aprobar.",
                "metadata": {}
            }
        
        # Get the most recent session
        session = max(agent_sessions, key=lambda s: s.timestamp)
        
        # Apply the correction
        success = self._apply_correction(session)
        
        if success:
            session.status = "approved"
            return {
                "action": "correction_applied",
                "response": "✅ ¡Perfecto! He actualizado mi base de conocimiento con esta corrección. Gracias por ayudarme a mejorar.",
                "metadata": {"session_id": session.session_id}
            }
        else:
            return {
                "action": "correction_failed",
                "response": "❌ Hubo un problema al aplicar la corrección. Por favor, intenta nuevamente.",
                "metadata": {"session_id": session.session_id}
            }
    
    def _extract_correction_from_text(self, text: str) -> Optional[dict[str, Any]]:
        """Extract correction data from text using patterns"""
        text_lower = text.lower()
        
        # Check for price corrections
        price_match = re.search(r"precio\s+es\s+(\d+(?:[.,]\d+)?)", text_lower)
        if price_match:
            return {
                "type": "price",
                "value": float(price_match.group(1).replace(",", ".")),
                "summary": f"Precio: {price_match.group(1)}"
            }
        
        # Check for specification corrections
        spec_match = re.search(r"(?:la|el)\s+(\w+)\s+(?:es|son)\s+(.+?)(?:\.|$)", text_lower)
        if spec_match:
            return {
                "type": "specification",
                "attribute": spec_match.group(1),
                "value": spec_match.group(2).strip(),
                "summary": f"{spec_match.group(1)}: {spec_match.group(2)}"
            }
        
        # Generic correction
        if any(keyword in text_lower for keyword in ["corregir", "en realidad", "debería ser"]):
            return {
                "type": "general",
                "content": text,
                "summary": text[:100]
            }
        
        return None
    
    def _parse_correction(self, correction_text: str) -> dict[str, Any]:
        """Parse correction text into structured data"""
        return self._extract_correction_from_text(correction_text) or {
            "type": "general",
            "content": correction_text,
            "summary": correction_text[:100]
        }
    
    def _apply_correction(self, session: FeedbackSession) -> bool:
        """Apply a correction to the knowledge base"""
        correction_data = session.correction_data or self._parse_correction(session.feedback_content)
        
        if not correction_data:
            return False
        
        # Determine correction type and ID
        correction_type = correction_data.get("type", "responses")
        correction_id = f"{session.agent_id}_{datetime.now().timestamp()}"
        
        # Map to knowledge manager categories
        category_map = {
            "price": "prices",
            "specification": "technical_specs",
            "general": "responses"
        }
        
        category = category_map.get(correction_type, "responses")
        
        # Prepare correction data
        kb_correction = {
            "original_response": session.bot_response,
            "correction": session.feedback_content,
            "parsed_data": correction_data,
            "agent_id": session.agent_id,
            "timestamp": session.timestamp,
            "keywords": self._extract_keywords(session.feedback_content)
        }
        
        # Add to knowledge base
        return self.knowledge_manager.add_correction(
            correction_type=category,
            correction_id=correction_id,
            correction_data=kb_correction,
            source_agent=session.agent_id
        )
    
    def _extract_keywords(self, text: str) -> list[str]:
        """Extract keywords from text"""
        # Simple keyword extraction (can be improved with NLP)
        words = text.lower().split()
        # Filter out common words
        stopwords = {"el", "la", "los", "las", "de", "del", "a", "en", "por", "para", "con", "es", "son"}
        keywords = [w for w in words if len(w) > 3 and w not in stopwords]
        return keywords[:10]  # Limit to top 10
    
    def calculate_confidence_score(self, query: str, response: str, context: dict[str, Any]) -> float:
        """
        Calculate confidence score for a response
        
        Args:
            query: User query
            response: Bot response
            context: Additional context
        
        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.5  # Base confidence
        
        # Check if response is from dynamic knowledge (higher confidence)
        if context.get("source") == "dynamic":
            confidence += 0.3
        
        # Check if response has specific data (prices, specs)
        if any(keyword in response.lower() for keyword in ["precio", "uyu", "$", "m²", "mm"]):
            confidence += 0.1
        
        # Check response length (not too short, not generic)
        if 50 < len(response) < 500:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def should_trigger_doubt_gate(self, confidence: float) -> bool:
        """Check if doubt gate should be triggered"""
        return confidence < 0.8


def main():
    """Test human-in-the-loop trainer"""
    from pathlib import Path
    
    knowledge_manager = DynamicKnowledgeManager(Path(__file__).parent)
    trainer = HumanInLoopTrainer(knowledge_manager)
    
    # Test training mode activation
    print("\n=== Test Training Mode ===")
    result = trainer.process_message("agent_001", "MODO ENTRENAMIENTO")
    print(f"Action: {result['action']}")
    print(f"Response: {result['response']}")
    
    # Test emoji correction
    print("\n=== Test Emoji Correction ===")
    result = trainer.process_message(
        "agent_001",
        "❌ El precio del Isodec 100mm es 1500 UYU por m²",
        previous_response="El precio del Isodec es 1200 UYU por m²"
    )
    print(f"Action: {result['action']}")
    print(f"Response: {result['response']}")
    
    # Test approval
    print("\n=== Test Approval ===")
    result = trainer.process_message("agent_001", "✅")
    print(f"Action: {result['action']}")
    print(f"Response: {result['response']}")
    
    print("\n✅ Human-in-the-Loop Trainer test completed")


if __name__ == "__main__":
    main()
