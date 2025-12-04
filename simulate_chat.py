#!/usr/bin/env python3
"""
Simulated Chat Server
Allows testing chatbot locally without WhatsApp integration
Uses actual chatbot logic and workflows
"""

import json
import os
import uuid
from datetime import datetime
from typing import Any

import requests
from pymongo import MongoClient
from pymongo.collection import Collection

# Configuration
API_URL = os.getenv("PY_CHAT_SERVICE_URL", "http://localhost:8000")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/bmc_chat")
DEFAULT_PHONE = os.getenv("SIMULATE_DEFAULT_PHONE", "+59891234567")


class SimulatedChat:
    """Simulated chat interface that uses real chatbot logic"""

    def __init__(self, api_url: str = API_URL, mongodb_uri: str = MONGODB_URI):
        self.api_url = api_url
        self.mongodb_uri = mongodb_uri
        self.session_id = None
        self.phone = DEFAULT_PHONE
        self.conversation_history: list[dict[str, Any]] = []

        # Connect to MongoDB for knowledge base
        try:
            self.client = MongoClient(mongodb_uri)
            self.db = self.client.get_database()
            self.conversations: Collection = self.db.conversations
            self.kb_interactions: Collection = self.db.kb_interactions
            print("✅ Connected to MongoDB for knowledge base")
        except Exception as e:
            print(f"⚠️ MongoDB connection failed: {e}")
            print("   Continuing without MongoDB persistence")
            self.conversations = None
            self.kb_interactions = None

    def start_session(self, phone: str | None = None) -> str:
        """Start a new conversation session"""
        if phone:
            self.phone = phone
        self.session_id = f"sim_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.conversation_history = []
        print(f"📱 Started new session: {self.session_id}")
        print(f"   Phone: {self.phone}")
        return self.session_id

    def send_message(self, message: str) -> dict[str, Any]:
        """
        Send a message to the chatbot using real API
        Simulates WhatsApp message format but uses actual chatbot logic
        """
        if not self.session_id:
            self.start_session()

        print(f"\n👤 You: {message}")

        try:
            # Call real FastAPI endpoint
            response = requests.post(
                f"{self.api_url}/chat/process",
                json={"mensaje": message, "telefono": self.phone, "sesionId": self.session_id},
                timeout=30,
            )

            if response.status_code != 200:
                error_msg = f"❌ API Error: {response.status_code} - {response.text}"
                print(error_msg)
                return {"error": error_msg, "success": False}

            result = response.json()

            # Display response
            print(f"🤖 Bot: {result.get('mensaje', 'No response')}")
            print(f"   Tipo: {result.get('tipo', 'unknown')}")
            print(f"   Confianza: {result.get('confianza', 0):.2%}")
            if result.get("acciones"):
                print(f"   Acciones: {', '.join(result['acciones'])}")
            if result.get("necesita_datos"):
                print(f"   Necesita datos: {', '.join(result['necesita_datos'])}")

            # Store in conversation history
            self.conversation_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "user_message": message,
                    "bot_response": result,
                    "session_id": self.session_id,
                }
            )

            # Save to MongoDB if available
            if self.conversations is not None:
                try:
                    self.conversations.insert_one(
                        {
                            "session_id": self.session_id,
                            "phone": self.phone,
                            "message": message,
                            "response": result.get("mensaje", ""),
                            "type": result.get("tipo", ""),
                            "confidence": result.get("confianza", 0),
                            "timestamp": datetime.now().isoformat(),
                            "source": "simulator",
                            "metadata": result,
                        }
                    )
                except Exception as e:
                    print(f"⚠️ Could not save to MongoDB: {e}")

            return result

        except requests.exceptions.ConnectionError:
            error_msg = "❌ Cannot connect to API. Is the server running?"
            print(error_msg)
            print("   Try: python api_server.py")
            return {"error": error_msg, "success": False}
        except Exception as e:
            error_msg = f"❌ Error: {e}"
            print(error_msg)
            return {"error": error_msg, "success": False}

    def get_conversation_history(self) -> list[dict[str, Any]]:
        """Get full conversation history"""
        return self.conversation_history

    def export_conversation(self, filename: str | None = None) -> str:
        """Export conversation to JSON file"""
        if not filename:
            filename = f"conversation_{self.session_id}.json"

        data = {
            "session_id": self.session_id,
            "phone": self.phone,
            "started_at": self.conversation_history[0]["timestamp"]
            if self.conversation_history
            else None,
            "messages": self.conversation_history,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"💾 Conversation exported to: {filename}")
        return filename

    def load_conversation(self, filename: str):
        """Load conversation from JSON file"""
        with open(filename, encoding="utf-8") as f:
            data = json.load(f)

        self.session_id = data.get("session_id")
        self.phone = data.get("phone", DEFAULT_PHONE)
        self.conversation_history = data.get("messages", [])

        print(f"📂 Loaded conversation: {self.session_id}")
        print(f"   Messages: {len(self.conversation_history)}")

    def get_knowledge_base_stats(self) -> dict[str, Any]:
        """Get statistics from knowledge base"""
        if self.kb_interactions is None:
            return {"error": "MongoDB not available"}

        try:
            total = self.kb_interactions.count_documents({})
            by_type = {}
            for doc in self.kb_interactions.aggregate(
                [{"$group": {"_id": "$type", "count": {"$sum": 1}}}]
            ):
                by_type[doc["_id"]] = doc["count"]

            return {"total_interactions": total, "by_type": by_type}
        except Exception as e:
            return {"error": str(e)}


def interactive_chat():
    """Interactive chat loop"""
    print("=" * 70)
    print("🤖 BMC Chatbot Simulator")
    print("=" * 70)
    print("Type 'exit' or 'quit' to end the conversation")
    print("Type 'export' to save conversation")
    print("Type 'stats' to see knowledge base statistics")
    print("Type 'new' to start a new session")
    print("=" * 70)
    print()

    chat = SimulatedChat()
    chat.start_session()

    while True:
        try:
            message = input("\n👤 You: ").strip()

            if not message:
                continue

            if message.lower() in ["exit", "quit", "q"]:
                print("\n👋 Goodbye!")
                break

            if message.lower() == "export":
                chat.export_conversation()
                continue

            if message.lower() == "stats":
                stats = chat.get_knowledge_base_stats()
                print("\n📊 Knowledge Base Stats:")
                print(json.dumps(stats, indent=2))
                continue

            if message.lower() == "new":
                chat.start_session()
                continue

            # Send message
            chat.send_message(message)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def batch_test(scenarios_file: str):
    """Run batch test from scenarios file"""
    print(f"📋 Running batch test from: {scenarios_file}")

    with open(scenarios_file, encoding="utf-8") as f:
        scenarios = json.load(f)

    chat = SimulatedChat()
    results = []

    for scenario in scenarios:
        print(f"\n{'=' * 70}")
        print(f"Scenario: {scenario.get('name', 'Unnamed')}")
        print(f"{'=' * 70}")

        chat.start_session(scenario.get("phone", DEFAULT_PHONE))

        for message in scenario.get("messages", []):
            result = chat.send_message(message)
            results.append({"scenario": scenario.get("name"), "message": message, "result": result})

        # Export conversation
        filename = f"test_{scenario.get('name', 'scenario').replace(' ', '_')}.json"
        chat.export_conversation(filename)

    # Save results
    results_file = f"batch_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Batch test complete. Results saved to: {results_file}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        if len(sys.argv) > 2:
            batch_test(sys.argv[2])
        else:
            print("Usage: python simulate_chat.py --batch <scenarios_file.json>")
    else:
        interactive_chat()
