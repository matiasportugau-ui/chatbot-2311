#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication Models
Defines User, API Key, and Token data structures
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    WEBHOOK = "webhook"
    READONLY = "readonly"


class User(BaseModel):
    """User model for authentication"""
    id: Optional[str] = Field(None, description="User ID")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="Full name")
    role: UserRole = Field(UserRole.USER, description="User role")
    is_active: bool = Field(True, description="Is user active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "role": "user",
                "is_active": True
            }
        }


class UserInDB(User):
    """User model with hashed password"""
    hashed_password: str = Field(..., description="Bcrypt hashed password")


class UserCreate(BaseModel):
    """User creation model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER


class UserLogin(BaseModel):
    """User login model"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    username: str
    email: str
    role: UserRole
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp


class Token(BaseModel):
    """Token response model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class APIKey(BaseModel):
    """API Key model for webhook authentication"""
    id: Optional[str] = Field(None, description="API Key ID")
    key: str = Field(..., description="API key value (hashed in DB)")
    name: str = Field(..., description="API key name/description")
    owner_id: str = Field(..., description="Owner user ID")
    scopes: List[str] = Field(default_factory=list, description="Allowed scopes")
    rate_limit: int = Field(100, description="Requests per minute")
    is_active: bool = Field(True, description="Is key active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = Field(None, description="Last usage timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "WhatsApp Webhook",
                "scopes": ["webhook:read", "webhook:write"],
                "rate_limit": 100,
                "is_active": True
            }
        }


class APIKeyCreate(BaseModel):
    """API Key creation model"""
    name: str = Field(..., min_length=3, max_length=100)
    scopes: List[str] = Field(default_factory=list)
    rate_limit: int = Field(100, gt=0, le=1000)
    expires_in_days: Optional[int] = Field(None, gt=0, le=365)


class APIKeyResponse(BaseModel):
    """API Key response with plain text key (only shown once)"""
    id: str
    key: str = Field(..., description="Plain text API key (save this!)")
    name: str
    scopes: List[str]
    rate_limit: int
    expires_at: Optional[datetime]
    created_at: datetime
