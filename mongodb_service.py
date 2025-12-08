#!/usr/bin/env python3
"""
MongoDB Service Module
Provides centralized MongoDB connection management for the BMC Chatbot system
"""

import logging
import os

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

# Global connection instances
_client: MongoClient | None = None
_db: Database | None = None


def ensure_mongodb_connected() -> bool:
    """
    Ensure MongoDB connection is established

    Returns:
        True if connection is successful, False otherwise
    """
    global _client, _db

    try:
        if _client is None:
            default_uri = "mongodb://localhost:27017/bmc_chat"
            mongodb_uri = os.getenv("MONGODB_URI", default_uri)
            # Log connection without credentials
            if "@" in mongodb_uri:
                log_uri = mongodb_uri.split("@")[-1]
            else:
                log_uri = mongodb_uri
            logger.info(f"Connecting to MongoDB: {log_uri}")

            # Parse database name from URI
            # MongoDB URI format:
            # mongodb://[username:password@]host[:port][/database][?options]
            # Extract database name if present, otherwise use default
            db_name = "bmc_chat"  # Default database name

            # Find the database name part (after the last / and before ?)
            if "/" in mongodb_uri:
                # Split by / to get parts
                parts = mongodb_uri.split("/")
                # Database name would be in the last part (before query params)
                # Format: mongodb://host:port/dbname or
                # mongodb://user:pass@host:port/dbname
                if len(parts) > 3:
                    # Remove query params
                    potential_db = parts[-1].split("?")[0]
                    # Check if this looks like a database name (not host:port)
                    # Database name shouldn't contain : (indicates host:port)
                    if potential_db and ":" not in potential_db:
                        db_name = potential_db

            # Create connection with timeout
            _client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)

            # Test connection
            _client.server_info()

            # Get database
            _db = _client[db_name]

            logger.info(f"✅ MongoDB connection established to database: {db_name}")
            return True
        else:
            # Connection already exists, verify it's still alive
            _client.server_info()
            return True

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        _client = None
        _db = None
        return False
    except Exception as e:
        error_msg = f"❌ Unexpected error connecting to MongoDB: {e}"
        logger.error(error_msg)
        _client = None
        _db = None
        return False


class MongoDBService:
    """
    MongoDB Service wrapper class
    Provides a get_collection() method for compatibility with
    shared_context_service
    """

    def __init__(self, db: Database):
        self.db = db

    def get_collection(self, collection_name: str):
        """
        Get a collection from the database

        Args:
            collection_name: Name of the collection

        Returns:
            Collection object
        """
        return self.db[collection_name]

    def get_database(self) -> Database:
        """Get the database object"""
        return self.db


def get_mongodb_service() -> MongoDBService | None:
    """
    Get MongoDB service with get_collection() method support

    Returns:
        MongoDBService wrapper if connected, None otherwise
    """
    global _db

    if _db is None and not ensure_mongodb_connected():
        return None

    if _db is None:
        return None

    return MongoDBService(_db)
