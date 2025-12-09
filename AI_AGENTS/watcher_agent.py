"""
Watcher Agent (Observational Mode)
Monitors WhatsApp interactions and correlates them with Google Sheets updates
to learn how the team qualifies leads.
"""

import json
import logging
import time
from typing import Dict, Any, List
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WatcherAgent")

class WatcherAgent:
    def __init__(self, sheets_client=None):
        self.sheets_client = sheets_client
        self.observation_log = []
        self.learning_pairs = []

    def observe_chat(self, user_id: str, message: str, role: str):
        """
        Logs a chat interaction.
        """
        event = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "chat",
            "user_id": user_id,
            "role": role,
            "content": message
        }
        self.observation_log.append(event)
        # In a real system, we might flush this to a DB or file
        
    def observe_sheet_update(self, row_data: Dict[str, Any]):
        """
        Called when a new row is detected in the Google Sheet.
        Attempts to correlate with recent chat history.
        """
        logger.info(f"👀 Observed Sheet Update: {row_data}")
        
        # Simple heuristic correlation algorithm
        # 1. Find chat logs from the last 30 minutes
        # 2. Look for matching phone numbers or names
        
        correlation = self._find_correlation(row_data)
        if correlation:
            logger.info("✨ DISCOVERY: Correlated Chat -> Sheet Entry")
            self._learn_pattern(correlation, row_data)
            
    def _find_correlation(self, row_data: Dict[str, Any]) -> List[Dict]:
        """
        Tries to match row data (e.g. phone) with chat logs.
        """
        phone = row_data.get("Telefono", "")
        if not phone:
            return []
            
        # Clean phone
        phone_clean = ''.join(filter(str.isdigit, str(phone)))
        
        if not phone_clean:
            return []
            
        # Heuristic: Match last 8 digits (ignoring country code/leading zero diffs)
        phone_core = phone_clean[-8:] if len(phone_clean) >= 8 else phone_clean
        
        # Look back in logs
        relevant_chats = []
        for event in reversed(self.observation_log):
            user_id_clean = ''.join(filter(str.isdigit, str(event["user_id"])))
            
            if event["type"] == "chat":
                print(f"DEBUG: Comparing core '{phone_core}' with user '{user_id_clean}'")
                if phone_core in user_id_clean:
                    relevant_chats.insert(0, event)
        
        print(f"DEBUG: Found {len(relevant_chats)} matches")
        return relevant_chats

    def _learn_pattern(self, chat_history: List[Dict], sheet_outcome: Dict[str, Any]):
        """
        Generates a training example from the correlation.
        """
        training_example = {
            "input_dialog": [c["content"] for c in chat_history if c["role"] == "user"],
            "output_qualification": sheet_outcome
        }
        self.learning_pairs.append(training_example)
        
        # Save to training data file
        try:
            with open("learned_patterns.jsonl", "a") as f:
                f.write(json.dumps(training_example, ensure_ascii=False) + "\n")
            logger.info("✅ Saved new training pattern")
        except Exception as e:
            logger.error(f"Failed to save pattern: {e}")

# Singleton / Global instance
watcher = WatcherAgent()
