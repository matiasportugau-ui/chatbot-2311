#!/usr/bin/env python3
"""
Shared Context Service for Multi-Agent System
Provides unified MongoDB-based context management for all agents
"""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Try to import MongoDB service
try:
    import sys
    from pathlib import Path

    # Add parent directory to path to import mongodb_service
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

    from mongodb_service import ensure_mongodb_connected, get_mongodb_service

    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    logger.warning("mongodb_service not available, using in-memory fallback")


class SharedContextService:
    """Unified context service for all agents"""

    def __init__(self):
        self._in_memory_sessions = {}
        self._in_memory_contexts = {}

    def get_context(self, session_id: str, user_phone: str) -> dict[str, Any] | None:
        """
        Retrieve full conversation context for a session

        Args:
            session_id: Session identifier
            user_phone: User phone number

        Returns:
            Context dictionary or None if not found
        """
        try:
            if MONGODB_AVAILABLE and ensure_mongodb_connected():
                mongodb = get_mongodb_service()
                if mongodb is not None:
                    context_col = mongodb.get_collection("context")
                    context_doc = context_col.find_one(
                        {"session_id": session_id, "user_phone": user_phone}
                    )

                    if context_doc:
                        # Convert MongoDB document to dict, remove _id
                        context_dict = dict(context_doc)
                        context_dict.pop("_id", None)
                        return context_dict

            # Fallback to in-memory
            key = f"{user_phone}_{session_id}"
            return self._in_memory_contexts.get(key)

        except Exception as e:
            logger.warning(f"Error getting context from MongoDB: {e}, using in-memory")
            key = f"{user_phone}_{session_id}"
            return self._in_memory_contexts.get(key)

    def save_context(self, session_id: str, context: dict[str, Any]) -> bool:
        """
        Save/update conversation context

        Args:
            session_id: Session identifier
            context: Context dictionary (must include user_phone)

        Returns:
            True if successful, False otherwise
        """
        try:
            user_phone = context.get("user_phone") or context.get("cliente_id")
            if not user_phone:
                logger.error("Context must include user_phone or cliente_id")
                return False

            if MONGODB_AVAILABLE and ensure_mongodb_connected():
                mongodb = get_mongodb_service()
                if mongodb is not None:
                    context_col = mongodb.get_collection("context")
                    # Prepare document
                    context_doc = {
                        "session_id": session_id,
                        "user_phone": user_phone,
                        "last_updated": datetime.now(),
                        **context,
                    }

                    # Update or insert
                    context_col.update_one(
                        {"session_id": session_id, "user_phone": user_phone},
                        {"$set": context_doc},
                        upsert=True,
                    )
                    return True

            # Fallback to in-memory
            key = f"{user_phone}_{session_id}"
            self._in_memory_contexts[key] = context
            return True

        except Exception as e:
            logger.error(f"Error saving context to MongoDB: {e}")
            # Fallback to in-memory
            user_phone = context.get("user_phone") or context.get("cliente_id")
            if user_phone:
                key = f"{user_phone}_{session_id}"
                self._in_memory_contexts[key] = context
            return False

    def add_message(
        self,
        session_id: str,
        message: str,
        role: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Add message to conversation history

        Args:
            session_id: Session identifier
            message: Message content
            role: 'user' | 'assistant' | 'system'
            metadata: Optional message metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            if MONGODB_AVAILABLE and ensure_mongodb_connected():
                mongodb = get_mongodb_service()
                if mongodb is not None:
                    context_col = mongodb.get_collection("context")
                    message_entry = {
                        "role": role,
                        "content": message,
                        "timestamp": datetime.now(),
                        "metadata": metadata or {},
                    }

                    context_col.update_one(
                        {"session_id": session_id},
                        {
                            "$push": {"messages": message_entry},
                            "$set": {"last_updated": datetime.now()},
                        },
                    )
                    return True

            # Fallback: update in-memory context
            for key, context in self._in_memory_contexts.items():
                if context.get("session_id") == session_id:
                    if "messages" not in context:
                        context["messages"] = []
                    context["messages"].append(
                        {
                            "role": role,
                            "content": message,
                            "timestamp": datetime.now().isoformat(),
                            "metadata": metadata or {},
                        }
                    )
                    return True

            return False

        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return False

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """
        Get session metadata

        Args:
            session_id: Session identifier

        Returns:
            Session dictionary or None if not found
        """
        try:
            if MONGODB_AVAILABLE and ensure_mongodb_connected():
                mongodb = get_mongodb_service()
                if mongodb is not None:
                    sessions_col = mongodb.get_collection("sessions")
                    session_doc = sessions_col.find_one({"session_id": session_id})
                    if session_doc:
                        session_dict = dict(session_doc)
                        session_dict.pop("_id", None)
                        return session_dict

            # Fallback to in-memory
            return self._in_memory_sessions.get(session_id)

        except Exception as e:
            logger.warning(f"Error getting session from MongoDB: {e}")
            return self._in_memory_sessions.get(session_id)

    def create_session(
        self,
        user_phone: str,
        initial_message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Create new session

        Args:
            user_phone: User phone number
            initial_message: Optional initial message
            metadata: Optional session metadata

        Returns:
            Session ID
        """
        import uuid

        session_id = f"sess_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"

        session_data = {
            "session_id": session_id,
            "user_phone": user_phone,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "status": "active",
            "metadata": metadata or {},
        }

        try:
            if MONGODB_AVAILABLE and ensure_mongodb_connected():
                mongodb = get_mongodb_service()
                if mongodb is not None:
                    sessions_col = mongodb.get_collection("sessions")
                    sessions_col.insert_one(session_data)

                    # Create initial context if message provided
                    if initial_message:
                        self.add_message(session_id, initial_message, "user")

                    return session_id

            # Fallback to in-memory
            self._in_memory_sessions[session_id] = session_data
            if initial_message:
                self.add_message(session_id, initial_message, "user")

            return session_id

        except Exception as e:
            logger.warning(f"Error creating session in MongoDB: {e}, using in-memory")
            self._in_memory_sessions[session_id] = session_data
            if initial_message:
                self.add_message(session_id, initial_message, "user")
            return session_id

    def list_sessions(self, user_phone: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """
        List sessions for a user or all sessions

        Args:
            user_phone: Optional user phone to filter by
            limit: Maximum number of sessions to return

        Returns:
            List of session dictionaries
        """
        try:
            if MONGODB_AVAILABLE and ensure_mongodb_connected():
                mongodb = get_mongodb_service()
                if mongodb is not None:
                    sessions_col = mongodb.get_collection("sessions")
                    query = {}
                    if user_phone:
                        query["user_phone"] = user_phone

                    sessions = list(sessions_col.find(query).sort("last_activity", -1).limit(limit))

                    # Convert to dicts and remove _id
                    result = []
                    for session in sessions:
                        session_dict = dict(session)
                        session_dict.pop("_id", None)
                        result.append(session_dict)

                    return result

            # Fallback to in-memory
            result = []
            for session in self._in_memory_sessions.values():
                if not user_phone or session.get("user_phone") == user_phone:
                    result.append(session)

            # Sort by last_activity
            result.sort(key=lambda x: x.get("last_activity", datetime.min), reverse=True)
            return result[:limit]

        except Exception as e:
            logger.warning(f"Error listing sessions from MongoDB: {e}")
            # Return in-memory sessions
            result = []
            for session in self._in_memory_sessions.values():
                if not user_phone or session.get("user_phone") == user_phone:
                    result.append(session)
            result.sort(key=lambda x: x.get("last_activity", datetime.min), reverse=True)
            return result[:limit]


# Singleton instance
_shared_context_service = None


def get_shared_context_service() -> SharedContextService:
    """Get singleton instance of shared context service"""
    global _shared_context_service
    if _shared_context_service is None:
        _shared_context_service = SharedContextService()
    return _shared_context_service
