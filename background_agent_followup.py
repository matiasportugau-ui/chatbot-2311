#!/usr/bin/env python3
"""
Background Agent for Follow-up Messages
Checks MongoDB for pending follow-ups and sends messages via WhatsApp
"""

import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any

import requests
from pymongo import MongoClient
from pymongo.collection import Collection

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FollowUpAgent:
    """Agent that handles follow-up messages for conversations"""

    def __init__(self):
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/bmc_chat")
        self.whatsapp_api_url = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v19.0")
        self.whatsapp_phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.whatsapp_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL_EXTERNAL")
        self.check_interval = int(os.getenv("FOLLOWUP_CHECK_INTERVAL", "3600"))  # 1 hour default

        # Connect to MongoDB
        try:
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client.get_database()
            self.conversations: Collection = self.db.conversations
            self.followups: Collection = self.db.followups
            logger.info("✅ Connected to MongoDB")
        except Exception as e:
            logger.error(f"❌ Error connecting to MongoDB: {e}")
            raise

    def find_pending_followups(self) -> list[dict[str, Any]]:
        """Find conversations that need follow-up messages"""
        try:
            # Find conversations that:
            # 1. Had a quote request but no response in 24 hours
            # 2. Had last message > 24 hours ago
            # 3. Don't have a follow-up scheduled already

            cutoff_time = datetime.now() - timedelta(hours=24)

            # Query for conversations needing follow-up
            pending = list(
                self.conversations.find(
                    {
                        "$or": [
                            {
                                "type": "cotizacion",
                                "timestamp": {"$lt": cutoff_time.isoformat()},
                                "followup_sent": {"$ne": True},
                            },
                            {
                                "timestamp": {"$lt": cutoff_time.isoformat()},
                                "followup_sent": {"$ne": True},
                                "last_interaction": {"$lt": cutoff_time.isoformat()},
                            },
                        ]
                    }
                ).limit(50)
            )

            logger.info(f"Found {len(pending)} conversations needing follow-up")
            return pending

        except Exception as e:
            logger.error(f"Error finding pending follow-ups: {e}")
            return []

    def generate_followup_message(self, conversation: dict[str, Any]) -> str:
        """Generate appropriate follow-up message based on conversation context"""

        conv_type = conversation.get("type", "general")
        last_message = conversation.get("message", "")

        if conv_type == "cotizacion":

            return (
                "👋 Hola! Te escribo para saber si tenés alguna consulta sobre la cotización que te enviamos.\n\n"
                "¿Te gustaría que te ayude con algo más o tenés alguna pregunta?\n\n"
                "Estoy aquí para ayudarte cuando lo necesites. 😊"
            )
        elif "informacion" in last_message.lower() or conv_type == "informacion":
            return (
                "👋 Hola! Te contacto para ver si la información que te compartimos fue útil.\n\n"
                "¿Tenés alguna otra consulta sobre nuestros productos de aislamiento térmico?\n\n"
                "Estoy disponible para ayudarte. 😊"
            )
        else:
            return (
                "👋 Hola! Te escribo para ver cómo puedo ayudarte.\n\n"
                "¿Tenés alguna consulta sobre nuestros productos o necesitás una cotización?\n\n"
                "Estoy aquí para ayudarte. 😊"
            )

    def send_followup_via_n8n(self, phone: str, message: str) -> bool:
        """Send follow-up message via n8n webhook"""
        try:
            if not self.n8n_webhook_url:
                logger.warning("N8N webhook URL not configured")
                return False

            payload = {
                "action": "send_message",
                "phone": phone,
                "message": message,
                "source": "followup_agent",
            }

            response = requests.post(self.n8n_webhook_url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info(f"✅ Follow-up sent via n8n to {phone}")
                return True
            else:
                logger.error(f"❌ Error sending follow-up via n8n: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Error sending follow-up via n8n: {e}")
            return False

    def send_followup_via_whatsapp(self, phone: str, message: str) -> bool:
        """Send follow-up message directly via WhatsApp API"""
        try:
            if not self.whatsapp_token or not self.whatsapp_phone_id:
                logger.warning("WhatsApp credentials not configured")
                return False

            url = f"{self.whatsapp_api_url}/{self.whatsapp_phone_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": message},
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                logger.info(f"✅ Follow-up sent via WhatsApp API to {phone}")
                return True
            else:
                logger.error(
                    f"❌ Error sending follow-up: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Error sending follow-up via WhatsApp API: {e}")
            return False

    def process_followups(self):
        """Process all pending follow-ups"""
        pending = self.find_pending_followups()

        for conversation in pending:
            try:
                phone = conversation.get("phone")
                if not phone:
                    logger.warning(
                        f"Skipping conversation without phone: {conversation.get('_id')}"
                    )
                    continue

                # Generate follow-up message
                message = self.generate_followup_message(conversation)

                # Try to send via n8n first, fallback to direct API
                success = False
                if self.n8n_webhook_url:
                    success = self.send_followup_via_n8n(phone, message)

                if not success:
                    success = self.send_followup_via_whatsapp(phone, message)

                if success:
                    # Mark as sent
                    self.conversations.update_one(
                        {"_id": conversation["_id"]},
                        {
                            "$set": {
                                "followup_sent": True,
                                "followup_sent_at": datetime.now().isoformat(),
                            }
                        },
                    )

                    # Log follow-up
                    self.followups.insert_one(
                        {
                            "conversation_id": str(conversation.get("_id")),
                            "phone": phone,
                            "message": message,
                            "sent_at": datetime.now().isoformat(),
                            "method": "n8n" if self.n8n_webhook_url else "whatsapp_api",
                        }
                    )

                    logger.info(f"✅ Follow-up processed for {phone}")
                else:
                    logger.warning(f"⚠️ Failed to send follow-up to {phone}")

            except Exception as e:
                logger.error(
                    f"❌ Error processing follow-up for conversation {conversation.get('_id')}: {e}"
                )
                continue

    def run_continuous(self):
        """Run the agent continuously"""
        logger.info(f"🚀 Starting Follow-up Agent (check interval: {self.check_interval}s)")

        while True:
            try:
                logger.info("Checking for pending follow-ups...")
                self.process_followups()
                logger.info(f"Sleeping for {self.check_interval} seconds...")
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                logger.info("Stopping Follow-up Agent...")
                break
            except Exception as e:
                logger.error(f"Error in follow-up agent loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

    def run_once(self):
        """Run the agent once and exit"""
        logger.info("Running Follow-up Agent (one-time execution)")
        self.process_followups()
        logger.info("Follow-up Agent execution completed")


def main():
    """Main entry point"""
    import sys

    agent = FollowUpAgent()

    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        agent.run_continuous()
    else:
        agent.run_once()


if __name__ == "__main__":
    main()
