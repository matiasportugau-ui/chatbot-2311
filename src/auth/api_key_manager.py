#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Key Manager
Handles API key generation, validation, and management
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List
from .models import APIKey, APIKeyCreate, APIKeyResponse
import logging

logger = logging.getLogger(__name__)


class APIKeyManager:
    """API key manager for webhook and external service authentication"""
    
    def __init__(self, db_connection=None):
        """
        Initialize API key manager
        
        Args:
            db_connection: Database connection (MongoDB or similar)
        """
        self.db = db_connection
        self.key_prefix = "bmc"
        self.key_length = 32
    
    def generate_api_key(self) -> str:
        """
        Generate a secure random API key
        
        Returns:
            API key string in format: bmc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        """
        random_part = secrets.token_urlsafe(self.key_length)
        api_key = f"{self.key_prefix}_{random_part}"
        return api_key
    
    def hash_api_key(self, api_key: str) -> str:
        """
        Hash API key for storage
        
        Args:
            api_key: Plain text API key
            
        Returns:
            Hashed API key (SHA256)
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    async def create_api_key(
        self,
        owner_id: str,
        key_data: APIKeyCreate
    ) -> APIKeyResponse:
        """
        Create new API key
        
        Args:
            owner_id: User ID who owns the key
            key_data: API key creation data
            
        Returns:
            APIKeyResponse with plain text key (only shown once)
        """
        # Generate API key
        plain_key = self.generate_api_key()
        hashed_key = self.hash_api_key(plain_key)
        
        # Calculate expiration
        expires_at = None
        if key_data.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
        
        # Create API key object
        api_key = APIKey(
            key=hashed_key,
            name=key_data.name,
            owner_id=owner_id,
            scopes=key_data.scopes,
            rate_limit=key_data.rate_limit,
            expires_at=expires_at,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Store in database
        if self.db:
            try:
                result = await self.db["api_keys"].insert_one(api_key.dict(exclude={"id"}))
                api_key.id = str(result.inserted_id)
                logger.info(f"Created API key: {key_data.name} for user: {owner_id}")
            except Exception as e:
                logger.error(f"Error storing API key: {e}")
                raise
        
        # Return response with plain text key (only time it's visible)
        return APIKeyResponse(
            id=api_key.id,
            key=plain_key,  # Plain text - save this!
            name=api_key.name,
            scopes=api_key.scopes,
            rate_limit=api_key.rate_limit,
            expires_at=api_key.expires_at,
            created_at=api_key.created_at
        )
    
    async def verify_api_key(self, api_key: str) -> Optional[APIKey]:
        """
        Verify API key and return key data
        
        Args:
            api_key: Plain text API key
            
        Returns:
            APIKey object if valid, None otherwise
        """
        if not api_key or not api_key.startswith(f"{self.key_prefix}_"):
            logger.warning("Invalid API key format")
            return None
        
        hashed_key = self.hash_api_key(api_key)
        
        if self.db:
            try:
                # Find key in database
                key_doc = await self.db["api_keys"].find_one({"key": hashed_key})
                
                if not key_doc:
                    logger.warning("API key not found")
                    return None
                
                api_key_obj = APIKey(**key_doc)
                
                # Check if key is active
                if not api_key_obj.is_active:
                    logger.warning(f"API key is inactive: {api_key_obj.name}")
                    return None
                
                # Check expiration
                if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
                    logger.warning(f"API key has expired: {api_key_obj.name}")
                    # Optionally deactivate expired key
                    await self.db["api_keys"].update_one(
                        {"key": hashed_key},
                        {"$set": {"is_active": False}}
                    )
                    return None
                
                # Update last used timestamp
                await self.db["api_keys"].update_one(
                    {"key": hashed_key},
                    {"$set": {"last_used_at": datetime.utcnow()}}
                )
                
                logger.debug(f"API key verified: {api_key_obj.name}")
                return api_key_obj
            
            except Exception as e:
                logger.error(f"Error verifying API key: {e}")
                return None
        
        return None
    
    async def list_api_keys(self, owner_id: str) -> List[APIKey]:
        """
        List all API keys for a user
        
        Args:
            owner_id: User ID
            
        Returns:
            List of APIKey objects (without plain text keys)
        """
        if not self.db:
            return []
        
        try:
            cursor = self.db["api_keys"].find({"owner_id": owner_id})
            keys = []
            async for doc in cursor:
                keys.append(APIKey(**doc))
            return keys
        except Exception as e:
            logger.error(f"Error listing API keys: {e}")
            return []
    
    async def revoke_api_key(self, key_id: str, owner_id: str) -> bool:
        """
        Revoke (deactivate) an API key
        
        Args:
            key_id: API key ID
            owner_id: User ID (must be owner)
            
        Returns:
            True if revoked successfully
        """
        if not self.db:
            return False
        
        try:
            result = await self.db["api_keys"].update_one(
                {"_id": key_id, "owner_id": owner_id},
                {"$set": {"is_active": False}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Revoked API key: {key_id}")
                return True
            else:
                logger.warning(f"API key not found or not owned by user: {key_id}")
                return False
        
        except Exception as e:
            logger.error(f"Error revoking API key: {e}")
            return False
    
    async def rotate_api_key(self, key_id: str, owner_id: str) -> Optional[APIKeyResponse]:
        """
        Rotate API key (create new key, deactivate old one)
        
        Args:
            key_id: Current API key ID
            owner_id: User ID (must be owner)
            
        Returns:
            New APIKeyResponse or None
        """
        if not self.db:
            return None
        
        try:
            # Get current key
            old_key_doc = await self.db["api_keys"].find_one(
                {"_id": key_id, "owner_id": owner_id}
            )
            
            if not old_key_doc:
                logger.warning(f"API key not found: {key_id}")
                return None
            
            old_key = APIKey(**old_key_doc)
            
            # Create new key with same settings
            new_key_data = APIKeyCreate(
                name=old_key.name,
                scopes=old_key.scopes,
                rate_limit=old_key.rate_limit,
                expires_in_days=None  # Calculate from old expiration
            )
            
            if old_key.expires_at:
                days_remaining = (old_key.expires_at - datetime.utcnow()).days
                if days_remaining > 0:
                    new_key_data.expires_in_days = days_remaining
            
            # Create new key
            new_key = await self.create_api_key(owner_id, new_key_data)
            
            # Deactivate old key
            await self.db["api_keys"].update_one(
                {"_id": key_id},
                {"$set": {"is_active": False}}
            )
            
            logger.info(f"Rotated API key: {key_id} -> {new_key.id}")
            return new_key
        
        except Exception as e:
            logger.error(f"Error rotating API key: {e}")
            return None


# Singleton instance
_api_key_manager = None


def get_api_key_manager(db_connection=None) -> APIKeyManager:
    """Get singleton API key manager instance"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager(db_connection)
    return _api_key_manager
