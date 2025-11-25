#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Proactive Agent Actions - Automated Proactive Agent Behaviors
Implements quote follow-ups, abandoned cart recovery, product recommendations, etc.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from pymongo.collection import Collection

from agent_coordinator import AgentCoordinator, TaskPriority, get_coordinator
from agent_scheduler import AgentScheduler, ScheduleType, get_scheduler
from agent_workflows import WorkflowEngine, get_workflow_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProactiveAgentActions:
    """Proactive agent actions and automation"""
    
    def __init__(self, coordinator: Optional[AgentCoordinator] = None,
                 scheduler: Optional[AgentScheduler] = None,
                 workflow_engine: Optional[WorkflowEngine] = None,
                 ia_instance: Optional[Any] = None):
        """
        Initialize proactive agent actions
        
        Args:
            coordinator: Agent coordinator instance
            scheduler: Agent scheduler instance
            workflow_engine: Workflow engine instance
            ia_instance: IA instance for intelligent actions
        """
        self.coordinator = coordinator or get_coordinator()
        self.scheduler = scheduler or get_scheduler(self.coordinator)
        self.workflow_engine = workflow_engine or get_workflow_engine(self.coordinator)
        self.ia_instance = ia_instance
        
        # MongoDB connection
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bmc_chat')
        try:
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client.get_database()
            self.conversations: Collection = self.db.conversations
            self.quotes: Collection = self.db.quotes
            self.followups: Collection = self.db.followups
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise
        
        logger.info("Proactive Agent Actions initialized")
    
    def schedule_quote_followups(self):
        """Schedule automatic quote follow-ups after 24/48/72 hours"""
        try:
            # Find quotes that need follow-up
            now = datetime.now()
            
            # 24 hours
            cutoff_24h = now - timedelta(hours=24)
            quotes_24h = list(self.quotes.find({
                "created_at": {"$lt": cutoff_24h.isoformat()},
                "followup_24h_sent": {"$ne": True},
                "status": {"$in": ["pending", "sent"]}
            }).limit(50))
            
            for quote in quotes_24h:
                self._schedule_quote_followup(quote, "24h")
            
            # 48 hours
            cutoff_48h = now - timedelta(hours=48)
            quotes_48h = list(self.quotes.find({
                "created_at": {"$lt": cutoff_48h.isoformat()},
                "followup_48h_sent": {"$ne": True},
                "status": {"$in": ["pending", "sent"]}
            }).limit(50))
            
            for quote in quotes_48h:
                self._schedule_quote_followup(quote, "48h")
            
            # 72 hours
            cutoff_72h = now - timedelta(hours=72)
            quotes_72h = list(self.quotes.find({
                "created_at": {"$lt": cutoff_72h.isoformat()},
                "followup_72h_sent": {"$ne": True},
                "status": {"$in": ["pending", "sent"]}
            }).limit(50))
            
            for quote in quotes_72h:
                self._schedule_quote_followup(quote, "72h")
            
            logger.info(f"Scheduled quote follow-ups: {len(quotes_24h)} (24h), {len(quotes_48h)} (48h), {len(quotes_72h)} (72h)")
            
        except Exception as e:
            logger.error(f"Error scheduling quote follow-ups: {e}")
    
    def _schedule_quote_followup(self, quote: Dict[str, Any], interval: str):
        """Schedule a quote follow-up"""
        try:
            quote_id = str(quote.get("_id", ""))
            cliente_telefono = quote.get("cliente", {}).get("telefono")
            
            if not cliente_telefono:
                logger.warning(f"Quote {quote_id} has no phone number")
                return
            
            # Use workflow engine to execute follow-up workflow
            execution_id = self.workflow_engine.execute_workflow(
                workflow_id="followup_workflow",
                initial_data={
                    "quote_id": quote_id,
                    "phone": cliente_telefono,
                    "interval": interval,
                    "quote_data": quote
                }
            )
            
            # Mark as scheduled
            self.quotes.update_one(
                {"_id": quote["_id"]},
                {"$set": {f"followup_{interval}_scheduled": True}}
            )
            
            logger.info(f"Scheduled {interval} follow-up for quote {quote_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling quote follow-up: {e}")
    
    def recover_abandoned_carts(self):
        """Recover abandoned carts (conversations with quote requests but no completion)"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=2)
            
            # Find conversations with quote requests but no completed quote
            abandoned = list(self.conversations.find({
                "type": "cotizacion",
                "timestamp": {"$lt": cutoff_time.isoformat()},
                "quote_completed": {"$ne": True},
                "abandoned_recovery_sent": {"$ne": True}
            }).limit(50))
            
            for conversation in abandoned:
                self._recover_abandoned_cart(conversation)
            
            logger.info(f"Processed {len(abandoned)} abandoned carts")
            
        except Exception as e:
            logger.error(f"Error recovering abandoned carts: {e}")
    
    def _recover_abandoned_cart(self, conversation: Dict[str, Any]):
        """Recover a single abandoned cart"""
        try:
            phone = conversation.get("phone")
            if not phone:
                return
            
            # Generate recovery message
            if self.ia_instance:
                message = self._generate_recovery_message_ai(conversation)
            else:
                message = (
                    "👋 Hola! Notamos que empezaste una cotización pero no la completaste.\n\n"
                    "¿Te gustaría continuar? Estoy aquí para ayudarte. 😊"
                )
            
            # Submit task to send recovery message
            task_id = self.coordinator.submit_task(
                task_type="send_message",
                payload={
                    "phone": phone,
                    "message": message,
                    "channel": "whatsapp",
                    "type": "abandoned_cart_recovery"
                },
                priority=TaskPriority.HIGH
            )
            
            # Mark as sent
            self.conversations.update_one(
                {"_id": conversation["_id"]},
                {"$set": {"abandoned_recovery_sent": True, "abandoned_recovery_at": datetime.now().isoformat()}}
            )
            
            logger.info(f"Sent abandoned cart recovery to {phone}")
            
        except Exception as e:
            logger.error(f"Error recovering abandoned cart: {e}")
    
    def _generate_recovery_message_ai(self, conversation: Dict[str, Any]) -> str:
        """Generate recovery message using AI"""
        try:
            if not self.ia_instance:
                return ""
            
            prompt = (
                f"Genera un mensaje de recuperación de carrito abandonado. "
                f"El cliente empezó una cotización pero no la completó. "
                f"El mensaje debe ser amigable, no intrusivo, y ofrecer ayuda. "
                f"Máximo 3 líneas."
            )
            
            if hasattr(self.ia_instance, 'procesar_mensaje_usuario'):
                response = self.ia_instance.procesar_mensaje_usuario(
                    mensaje=prompt,
                    telefono_cliente=conversation.get("phone", "unknown"),
                    sesion_id=f"recovery_{conversation.get('_id', 'unknown')}"
                )
                
                if isinstance(response, dict):
                    return response.get('mensaje', '')
                return str(response)
            
        except Exception as e:
            logger.warning(f"AI recovery message generation failed: {e}")
        
        return ""
    
    def recommend_products(self, conversation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommend products based on conversation history"""
        try:
            # Analyze conversation to understand customer needs
            conversation_history = conversation.get("history", [])
            last_messages = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            
            # Extract product mentions and interests
            product_keywords = {
                "isodec": ["isodec", "aislamiento", "térmico"],
                "poliestireno": ["poliestireno", "eps", "expandido"],
                "lana_roca": ["lana", "roca", "mineral"]
            }
            
            mentioned_products = []
            for msg in last_messages:
                msg_text = msg.get("content", "").lower()
                for product, keywords in product_keywords.items():
                    if any(keyword in msg_text for keyword in keywords):
                        if product not in mentioned_products:
                            mentioned_products.append(product)
            
            # Generate recommendations
            recommendations = []
            if mentioned_products:
                # Recommend mentioned products
                for product in mentioned_products:
                    recommendations.append({
                        "product": product,
                        "reason": "Mencionado en conversación",
                        "confidence": 0.8
                    })
            else:
                # Default recommendation: most popular product
                recommendations.append({
                    "product": "isodec",
                    "reason": "Producto más popular",
                    "confidence": 0.6
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating product recommendations: {e}")
            return []
    
    def send_price_drop_notifications(self):
        """Send notifications for price drops (if price tracking is implemented)"""
        # TODO: Implement price drop tracking and notifications
        logger.info("Price drop notifications not yet implemented")
        pass
    
    def send_seasonal_campaigns(self, campaign_type: str = "seasonal"):
        """Send seasonal campaign messages"""
        try:
            # Find active customers
            active_customers = list(self.conversations.find({
                "last_interaction": {"$gte": (datetime.now() - timedelta(days=90)).isoformat()}
            }).limit(100))
            
            campaign_message = self._get_campaign_message(campaign_type)
            
            for customer in active_customers:
                phone = customer.get("phone")
                if phone:
                    self.coordinator.submit_task(
                        task_type="send_message",
                        payload={
                            "phone": phone,
                            "message": campaign_message,
                            "channel": "whatsapp",
                            "type": "campaign",
                            "campaign": campaign_type
                        },
                        priority=TaskPriority.NORMAL
                    )
            
            logger.info(f"Sent {len(active_customers)} campaign messages")
            
        except Exception as e:
            logger.error(f"Error sending seasonal campaigns: {e}")
    
    def _get_campaign_message(self, campaign_type: str) -> str:
        """Get campaign message based on type"""
        messages = {
            "seasonal": (
                "🌞 ¡Hola! Con el verano acercándose, es el momento perfecto para mejorar el aislamiento térmico de tu hogar.\n\n"
                "¿Te gustaría recibir una cotización? 😊"
            ),
            "winter": (
                "❄️ ¡Hola! Prepárate para el invierno con el mejor aislamiento térmico.\n\n"
                "¿Te gustaría conocer nuestras ofertas? 😊"
            ),
            "promotion": (
                "🎉 ¡Hola! Tenemos ofertas especiales en productos de aislamiento térmico.\n\n"
                "¿Te gustaría conocer más? 😊"
            )
        }
        
        return messages.get(campaign_type, messages["seasonal"])
    
    def setup_automated_actions(self):
        """Set up all automated proactive actions"""
        try:
            # Schedule quote follow-ups (runs every hour)
            self.scheduler.schedule_task(
                task_type="schedule_quote_followups",
                payload={},
                schedule="1 hour",
                schedule_type=ScheduleType.RECURRING
            )
            
            # Schedule abandoned cart recovery (runs every 2 hours)
            self.scheduler.schedule_task(
                task_type="recover_abandoned_carts",
                payload={},
                schedule="2 hours",
                schedule_type=ScheduleType.RECURRING
            )
            
            logger.info("✅ Automated proactive actions scheduled")
            
        except Exception as e:
            logger.error(f"Error setting up automated actions: {e}")


# Global instance (singleton)
_proactive_actions_instance: Optional[ProactiveAgentActions] = None


def get_proactive_actions(coordinator: Optional[AgentCoordinator] = None,
                          scheduler: Optional[AgentScheduler] = None,
                          workflow_engine: Optional[WorkflowEngine] = None,
                          ia_instance: Optional[Any] = None) -> ProactiveAgentActions:
    """Get the global proactive actions instance (singleton)"""
    global _proactive_actions_instance
    if _proactive_actions_instance is None:
        _proactive_actions_instance = ProactiveAgentActions(coordinator, scheduler, workflow_engine, ia_instance)
    return _proactive_actions_instance


if __name__ == "__main__":
    # Example usage
    from agent_coordinator import AgentCoordinator
    from agent_scheduler import AgentScheduler
    from agent_workflows import WorkflowEngine
    
    coordinator = AgentCoordinator()
    coordinator.start()
    
    scheduler = AgentScheduler(coordinator)
    scheduler.start()
    
    workflow_engine = WorkflowEngine(coordinator)
    
    proactive = ProactiveAgentActions(coordinator, scheduler, workflow_engine)
    proactive.setup_automated_actions()
    
    # Test quote follow-ups
    proactive.schedule_quote_followups()
    
    coordinator.stop()
    scheduler.stop()

