#!/usr/bin/env python3
"""
Interactive CLI for Simulated Chat
Enhanced command-line interface with more features
"""

import json
import os

from simulate_chat import API_URL, SimulatedChat


class EnhancedCLI:
    """Enhanced CLI with more features"""

    def __init__(self):
        self.chat = SimulatedChat()
        self.running = True
        self.commands = {
            "help": self.show_help,
            "new": self.new_session,
            "phone": self.set_phone,
            "history": self.show_history,
            "export": self.export_conversation,
            "load": self.load_conversation,
            "stats": self.show_stats,
            "clear": self.clear_screen,
            "exit": self.exit_chat,
            "quit": self.exit_chat,
        }

    def show_help(self):
        """Show available commands"""
        print("\n📖 Available Commands:")
        print("  /help          - Show this help")
        print("  /new           - Start new session")
        print("  /phone <num>   - Set phone number")
        print("  /history       - Show conversation history")
        print("  /export        - Export conversation to JSON")
        print("  /load <file>   - Load conversation from JSON")
        print("  /stats         - Show knowledge base statistics")
        print("  /clear         - Clear screen")
        print("  /exit, /quit   - Exit chat")
        print("\n💡 Just type a message to chat with the bot!")

    def new_session(self):
        """Start new session"""
        self.chat.start_session()
        print("✅ New session started")

    def set_phone(self, phone: str = None):
        """Set phone number"""
        if not phone:
            phone = input("Enter phone number: ").strip()
        if phone:
            self.chat.phone = phone
            print(f"✅ Phone set to: {phone}")

    def show_history(self):
        """Show conversation history"""
        history = self.chat.get_conversation_history()
        if not history:
            print("📝 No conversation history")
            return

        print(f"\n📝 Conversation History ({len(history)} messages):")
        print("-" * 70)
        for i, msg in enumerate(history, 1):
            print(f"\n{i}. {msg['timestamp']}")
            print(f"   👤 You: {msg['user_message']}")
            print(f"   🤖 Bot: {msg['bot_response'].get('mensaje', '')}")
            print(
                f"      Tipo: {msg['bot_response'].get('tipo', '')} | "
                f"Confianza: {msg['bot_response'].get('confianza', 0):.2%}"
            )

    def export_conversation(self):
        """Export conversation"""
        if not self.chat.conversation_history:
            print("❌ No conversation to export")
            return
        self.chat.export_conversation()

    def load_conversation(self, filename: str = None):
        """Load conversation"""
        if not filename:
            filename = input("Enter filename: ").strip()
        if filename:
            try:
                self.chat.load_conversation(filename)
                print("✅ Conversation loaded")
            except Exception as e:
                print(f"❌ Error loading conversation: {e}")

    def show_stats(self):
        """Show knowledge base statistics"""
        stats = self.chat.get_knowledge_base_stats()
        print("\n📊 Knowledge Base Statistics:")
        print(json.dumps(stats, indent=2))

    def clear_screen(self):
        """Clear screen"""
        os.system("clear" if os.name != "nt" else "cls")

    def exit_chat(self):
        """Exit chat"""
        self.running = False
        print("\n👋 Goodbye!")

    def process_command(self, input_text: str):
        """Process command or message"""
        input_text = input_text.strip()

        if not input_text:
            return

        # Check if it's a command
        if input_text.startswith("/"):
            parts = input_text[1:].split(" ", 1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else None

            if cmd in self.commands:
                if arg:
                    self.commands[cmd](arg)
                else:
                    self.commands[cmd]()
            else:
                print(f"❌ Unknown command: /{cmd}")
                print("   Type /help for available commands")
        else:
            # It's a message, send it
            self.chat.send_message(input_text)

    def run(self):
        """Run interactive CLI"""
        print("=" * 70)
        print("🤖 BMC Chatbot Simulator - Enhanced CLI")
        print("=" * 70)
        print(f"API: {API_URL}")
        print(f"Phone: {self.chat.phone}")
        print("\nType /help for commands or just start chatting!")
        print("=" * 70)

        # Check API connection
        try:
            import requests

            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server is running")
            else:
                print("⚠️ API server may not be running properly")
        except Exception:
            print("❌ Cannot connect to API server")
            print(f"   Make sure it's running at: {API_URL}")
            print("   Start it with: python api_server.py")

        print()

        # Start session
        self.chat.start_session()

        # Main loop
        while self.running:
            try:
                user_input = input("\n👤 You: ")
                self.process_command(user_input)
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    cli = EnhancedCLI()
    cli.run()
