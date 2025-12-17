#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Training & Evaluation System for ChatBot
Allows real-time corrections and knowledge improvements during training mode
"""

import json
import datetime
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import re


class BotMode(Enum):
    """Bot operation modes"""
    PRODUCTION = "production"
    TRAINING = "training"


class CorrectionTrigger(Enum):
    """Correction trigger characters/emojis"""
    CORRECTION_EMOJI = "✏️"  # Pencil emoji for corrections
    CORRECTION_ALT = "🔧"  # Wrench emoji as alternative
    CORRECTION_PREFIX = "CORREGIR:"  # Text prefix for corrections
    FEEDBACK_EMOJI = "💡"  # Light bulb for feedback/suggestions


@dataclass
class CorrectionRequest:
    """A correction request from a user/agent"""
    id: str
    timestamp: datetime.datetime
    session_id: str
    user_id: str
    original_query: str
    original_response: str
    correction_text: str
    correction_type: str  # response_error, missing_info, tone_issue, etc.
    priority: int  # 1-5, 5 being highest


@dataclass
class ReformulatedResponse:
    """Bot's reformulated response after correction"""
    correction_id: str
    timestamp: datetime.datetime
    new_response: str
    reasoning: str
    changes_made: List[str]
    confidence: float
    requires_approval: bool


@dataclass
class TrainingSession:
    """A training session with the bot"""
    session_id: str
    user_id: str
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime]
    mode: BotMode
    corrections_made: int
    responses_approved: int
    responses_rejected: int
    topics_covered: List[str]


@dataclass
class KnowledgeUpdate:
    """A knowledge base update from training"""
    id: str
    timestamp: datetime.datetime
    correction_id: str
    update_type: str  # new_pattern, improved_response, new_fact, etc.
    category: str  # product_info, pricing, process, etc.
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    applied: bool
    approved_by: str


class TrainingEvaluationSystem:
    """Main system for training and evaluation"""
    
    def __init__(self, knowledge_base_path: str = "data/training"):
        """
        Initialize the training/evaluation system
        
        Args:
            knowledge_base_path: Path to store training data
        """
        self.knowledge_base_path = Path(knowledge_base_path)
        self.knowledge_base_path.mkdir(parents=True, exist_ok=True)
        
        # Session tracking
        self.active_sessions: Dict[str, TrainingSession] = {}
        self.session_modes: Dict[str, BotMode] = {}
        
        # Correction tracking
        self.pending_corrections: Dict[str, CorrectionRequest] = {}
        self.reformulated_responses: Dict[str, ReformulatedResponse] = {}
        
        # Knowledge updates
        self.knowledge_updates: List[KnowledgeUpdate] = []
        
        # Load existing data
        self._load_training_data()
        
    def _load_training_data(self):
        """Load existing training data from disk"""
        corrections_file = self.knowledge_base_path / "corrections.json"
        knowledge_file = self.knowledge_base_path / "knowledge_updates.json"
        
        if corrections_file.exists():
            with open(corrections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Load corrections (simplified for now)
                
        if knowledge_file.exists():
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Load knowledge updates
    
    def _save_training_data(self):
        """Save training data to disk"""
        # Save corrections
        corrections_file = self.knowledge_base_path / "corrections.json"
        with open(corrections_file, 'w', encoding='utf-8') as f:
            data = {
                'corrections': [asdict(c) for c in self.pending_corrections.values()],
                'reformulated': [asdict(r) for r in self.reformulated_responses.values()]
            }
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        # Save knowledge updates
        knowledge_file = self.knowledge_base_path / "knowledge_updates.json"
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            data = {
                'updates': [asdict(u) for u in self.knowledge_updates]
            }
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def set_session_mode(self, session_id: str, user_id: str, mode: BotMode) -> Dict[str, Any]:
        """
        Set the operation mode for a session
        
        Args:
            session_id: Unique session identifier
            user_id: User/agent identifier
            mode: BotMode (PRODUCTION or TRAINING)
            
        Returns:
            Confirmation message with session details
        """
        self.session_modes[session_id] = mode
        
        if mode == BotMode.TRAINING:
            # Create training session
            session = TrainingSession(
                session_id=session_id,
                user_id=user_id,
                start_time=datetime.datetime.now(),
                end_time=None,
                mode=mode,
                corrections_made=0,
                responses_approved=0,
                responses_rejected=0,
                topics_covered=[]
            )
            self.active_sessions[session_id] = session
            
            return {
                "success": True,
                "mode": mode.value,
                "message": f"✅ Modo de entrenamiento activado. Usa {CorrectionTrigger.CORRECTION_EMOJI.value} o '{CorrectionTrigger.CORRECTION_PREFIX.value}' para hacer correcciones.",
                "instructions": self._get_training_instructions()
            }
        else:
            return {
                "success": True,
                "mode": mode.value,
                "message": "✅ Modo de producción activado. El bot responderá normalmente."
            }
    
    def _get_training_instructions(self) -> str:
        """Get training mode instructions"""
        return f"""
🎓 **Instrucciones de Modo Entrenamiento:**

1. **Hacer una corrección:** Envía {CorrectionTrigger.CORRECTION_EMOJI.value} seguido de tu corrección
   Ejemplo: "{CorrectionTrigger.CORRECTION_EMOJI.value} La respuesta debe mencionar el precio actualizado"

2. **Dar feedback:** Usa {CorrectionTrigger.FEEDBACK_EMOJI.value} para sugerencias
   Ejemplo: "{CorrectionTrigger.FEEDBACK_EMOJI.value} Sería mejor usar un tono más profesional"

3. **Aprobar respuesta reformulada:** Responde "APROBAR" o "✅"

4. **Rechazar reformulación:** Responde "RECHAZAR" o "❌" con razón

5. **Ver estadísticas:** Envía "ESTADÍSTICAS" o "📊"

6. **Salir del modo entrenamiento:** Envía "SALIR ENTRENAMIENTO" o "FIN"
"""
    
    def detect_correction(self, message: str, session_id: str) -> Tuple[bool, Optional[str]]:
        """
        Detect if a message contains a correction
        
        Args:
            message: User message
            session_id: Session identifier
            
        Returns:
            Tuple of (is_correction, correction_text)
        """
        # Check if session is in training mode
        if self.session_modes.get(session_id) != BotMode.TRAINING:
            return False, None
        
        # Check for correction triggers
        correction_text = None
        
        # Check emoji triggers
        if CorrectionTrigger.CORRECTION_EMOJI.value in message:
            correction_text = message.split(CorrectionTrigger.CORRECTION_EMOJI.value, 1)[1].strip()
        elif CorrectionTrigger.CORRECTION_ALT.value in message:
            correction_text = message.split(CorrectionTrigger.CORRECTION_ALT.value, 1)[1].strip()
        elif message.upper().startswith(CorrectionTrigger.CORRECTION_PREFIX.value):
            correction_text = message[len(CorrectionTrigger.CORRECTION_PREFIX.value):].strip()
        
        return correction_text is not None, correction_text
    
    def create_correction_request(
        self,
        session_id: str,
        user_id: str,
        original_query: str,
        original_response: str,
        correction_text: str,
        correction_type: str = "general"
    ) -> CorrectionRequest:
        """
        Create a correction request
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            original_query: Original user query
            original_response: Bot's original response
            correction_text: Correction instruction
            correction_type: Type of correction
            
        Returns:
            CorrectionRequest object
        """
        correction_id = hashlib.md5(
            f"{session_id}{datetime.datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        correction = CorrectionRequest(
            id=correction_id,
            timestamp=datetime.datetime.now(),
            session_id=session_id,
            user_id=user_id,
            original_query=original_query,
            original_response=original_response,
            correction_text=correction_text,
            correction_type=correction_type,
            priority=3  # Default priority
        )
        
        self.pending_corrections[correction_id] = correction
        
        # Update session stats
        if session_id in self.active_sessions:
            self.active_sessions[session_id].corrections_made += 1
        
        self._save_training_data()
        
        return correction
    
    def generate_reformulated_response(
        self,
        correction: CorrectionRequest,
        bot_generate_func: callable
    ) -> ReformulatedResponse:
        """
        Generate a reformulated response based on correction
        
        Args:
            correction: CorrectionRequest object
            bot_generate_func: Function to generate new response
            
        Returns:
            ReformulatedResponse object
        """
        # Create prompt for reformulation
        reformulation_prompt = f"""
Tarea: Reformular respuesta basándote en la corrección proporcionada.

**Consulta original del cliente:**
{correction.original_query}

**Respuesta original del bot:**
{correction.original_response}

**Corrección solicitada:**
{correction.correction_text}

Por favor:
1. Genera una respuesta mejorada que incorpore la corrección
2. Explica qué cambios hiciste y por qué
3. Lista los puntos específicos que cambiaste

Formato de respuesta:
RESPUESTA_MEJORADA: [tu respuesta mejorada aquí]
RAZONAMIENTO: [explica los cambios]
CAMBIOS: [lista de cambios específicos, uno por línea]
"""
        
        # Generate reformulated response using bot's AI
        reformulated = bot_generate_func(reformulation_prompt)
        
        # Parse the response
        new_response, reasoning, changes = self._parse_reformulation(reformulated)
        
        # Create reformulated response object
        reformulated_obj = ReformulatedResponse(
            correction_id=correction.id,
            timestamp=datetime.datetime.now(),
            new_response=new_response,
            reasoning=reasoning,
            changes_made=changes,
            confidence=0.8,  # Can be calculated based on various factors
            requires_approval=True
        )
        
        self.reformulated_responses[correction.id] = reformulated_obj
        self._save_training_data()
        
        return reformulated_obj
    
    def _parse_reformulation(self, reformulated_text: str) -> Tuple[str, str, List[str]]:
        """Parse reformulated response into components"""
        new_response = ""
        reasoning = ""
        changes = []
        
        # Simple parsing (can be improved with better prompt engineering)
        if "RESPUESTA_MEJORADA:" in reformulated_text:
            parts = reformulated_text.split("RAZONAMIENTO:")
            response_part = parts[0].split("RESPUESTA_MEJORADA:")[1].strip()
            new_response = response_part
            
            if len(parts) > 1:
                reasoning_parts = parts[1].split("CAMBIOS:")
                reasoning = reasoning_parts[0].strip()
                
                if len(reasoning_parts) > 1:
                    changes_text = reasoning_parts[1].strip()
                    changes = [c.strip() for c in changes_text.split('\n') if c.strip()]
        else:
            # Fallback if format not followed
            new_response = reformulated_text
            reasoning = "Respuesta reformulada"
            changes = ["Respuesta general mejorada"]
        
        return new_response, reasoning, changes
    
    def approve_reformulation(
        self,
        correction_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Approve a reformulated response and update knowledge base
        
        Args:
            correction_id: Correction identifier
            user_id: User approving the change
            
        Returns:
            Status dictionary
        """
        if correction_id not in self.reformulated_responses:
            return {
                "success": False,
                "message": "Reformulación no encontrada"
            }
        
        reformulated = self.reformulated_responses[correction_id]
        correction = self.pending_corrections.get(correction_id)
        
        if not correction:
            return {
                "success": False,
                "message": "Corrección original no encontrada"
            }
        
        # Create knowledge update
        update = KnowledgeUpdate(
            id=hashlib.md5(f"{correction_id}{datetime.datetime.now()}".encode()).hexdigest()[:12],
            timestamp=datetime.datetime.now(),
            correction_id=correction_id,
            update_type="improved_response",
            category=self._categorize_update(correction, reformulated),
            before_state={
                "query": correction.original_query,
                "response": correction.original_response
            },
            after_state={
                "query": correction.original_query,
                "response": reformulated.new_response,
                "reasoning": reformulated.reasoning,
                "changes": reformulated.changes_made
            },
            applied=True,
            approved_by=user_id
        )
        
        self.knowledge_updates.append(update)
        
        # Update session stats
        session_id = correction.session_id
        if session_id in self.active_sessions:
            self.active_sessions[session_id].responses_approved += 1
        
        # Remove from pending
        if correction_id in self.pending_corrections:
            del self.pending_corrections[correction_id]
        if correction_id in self.reformulated_responses:
            del self.reformulated_responses[correction_id]
        
        self._save_training_data()
        self._apply_knowledge_update(update)
        
        return {
            "success": True,
            "message": "✅ Respuesta aprobada y conocimiento actualizado",
            "update_id": update.id,
            "details": {
                "category": update.category,
                "changes_count": len(reformulated.changes_made)
            }
        }
    
    def reject_reformulation(
        self,
        correction_id: str,
        user_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Reject a reformulated response
        
        Args:
            correction_id: Correction identifier
            user_id: User rejecting the change
            reason: Reason for rejection
            
        Returns:
            Status dictionary
        """
        if correction_id not in self.reformulated_responses:
            return {
                "success": False,
                "message": "Reformulación no encontrada"
            }
        
        correction = self.pending_corrections.get(correction_id)
        
        # Update session stats
        if correction:
            session_id = correction.session_id
            if session_id in self.active_sessions:
                self.active_sessions[session_id].responses_rejected += 1
        
        # Keep in pending for retry
        return {
            "success": True,
            "message": f"❌ Respuesta rechazada. Razón: {reason}",
            "next_action": "Por favor, proporciona más detalles sobre cómo mejorar la respuesta."
        }
    
    def _categorize_update(
        self,
        correction: CorrectionRequest,
        reformulated: ReformulatedResponse
    ) -> str:
        """Categorize the knowledge update"""
        # Simple categorization based on keywords (can be improved with ML)
        text = f"{correction.correction_text} {reformulated.reasoning}".lower()
        
        if any(word in text for word in ["precio", "costo", "cotización"]):
            return "pricing"
        elif any(word in text for word in ["producto", "característica", "especificación"]):
            return "product_info"
        elif any(word in text for word in ["proceso", "pasos", "cómo"]):
            return "process"
        elif any(word in text for word in ["tono", "forma", "manera"]):
            return "communication_style"
        else:
            return "general"
    
    def _apply_knowledge_update(self, update: KnowledgeUpdate):
        """
        Apply knowledge update to the bot's knowledge base
        
        This integrates with the existing knowledge base system
        """
        # Export to a format that can be ingested by the main bot
        update_file = self.knowledge_base_path / "pending_updates.jsonl"
        
        with open(update_file, 'a', encoding='utf-8') as f:
            json.dump(asdict(update), f, ensure_ascii=False, default=str)
            f.write('\n')
    
    def _calculate_approval_rate(self, approved: int, rejected: int) -> float:
        """Calculate approval rate percentage"""
        total = approved + rejected
        if total == 0:
            return 0.0
        return (approved / total) * 100
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a training session"""
        if session_id not in self.active_sessions:
            return {
                "success": False,
                "message": "Sesión no encontrada"
            }
        
        session = self.active_sessions[session_id]
        
        duration = datetime.datetime.now() - session.start_time
        
        return {
            "success": True,
            "session_id": session_id,
            "mode": session.mode.value,
            "duration_minutes": int(duration.total_seconds() / 60),
            "corrections_made": session.corrections_made,
            "responses_approved": session.responses_approved,
            "responses_rejected": session.responses_rejected,
            "approval_rate": self._calculate_approval_rate(
                session.responses_approved,
                session.responses_rejected
            ),
            "topics_covered": session.topics_covered
        }
    
    def end_training_session(self, session_id: str) -> Dict[str, Any]:
        """End a training session"""
        if session_id not in self.active_sessions:
            return {
                "success": False,
                "message": "Sesión no encontrada"
            }
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.datetime.now()
        
        # Get statistics before removing from active
        stats = self.get_session_statistics(session_id)
        
        # Archive session
        sessions_file = self.knowledge_base_path / "training_sessions.json"
        sessions_data = []
        
        if sessions_file.exists():
            with open(sessions_file, 'r', encoding='utf-8') as f:
                sessions_data = json.load(f)
        
        sessions_data.append(asdict(session))
        
        with open(sessions_file, 'w', encoding='utf-8') as f:
            json.dump(sessions_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Remove from active
        del self.active_sessions[session_id]
        if session_id in self.session_modes:
            del self.session_modes[session_id]
        
        # Return flattened statistics structure
        return {
            "success": True,
            "message": "✅ Sesión de entrenamiento finalizada",
            "session_id": stats.get("session_id"),
            "duration_minutes": stats.get("duration_minutes", 0),
            "corrections_made": stats.get("corrections_made", 0),
            "responses_approved": stats.get("responses_approved", 0),
            "responses_rejected": stats.get("responses_rejected", 0),
            "approval_rate": stats.get("approval_rate", 0),
            # Keep nested statistics for backward compatibility
            "statistics": {
                "session_id": stats.get("session_id"),
                "duration_minutes": stats.get("duration_minutes", 0),
                "corrections_made": stats.get("corrections_made", 0),
                "responses_approved": stats.get("responses_approved", 0),
                "responses_rejected": stats.get("responses_rejected", 0),
                "approval_rate": stats.get("approval_rate", 0)
            }
        }


# Integration helper functions

def format_correction_response(reformulated: ReformulatedResponse) -> str:
    """Format a reformulated response for display"""
    response = f"""
🔄 **Respuesta Reformulada:**

{reformulated.new_response}

---
💭 **Razonamiento:**
{reformulated.reasoning}

---
📝 **Cambios Realizados:**
"""
    for i, change in enumerate(reformulated.changes_made, 1):
        response += f"\n{i}. {change}"
    
    response += f"""

---
🎯 **Confianza:** {reformulated.confidence * 100:.1f}%

¿Aprobas esta respuesta? Responde:
- ✅ "APROBAR" para aceptar y actualizar el conocimiento
- ❌ "RECHAZAR [razón]" para rechazar y pedir otra versión
"""
    
    return response
