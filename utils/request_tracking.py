#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Request Tracking Utility
Generates and manages request IDs for OpenAI API calls and system-wide request tracking.
Implements X-Client-Request-Id header support per OpenAI API best practices.
"""

import uuid
import threading
import time
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import re


@dataclass
class RequestMetadata:
    """Metadata for a tracked request"""
    request_id: str
    client_request_id: Optional[str]
    timestamp: datetime
    model: Optional[str] = None
    provider: Optional[str] = None
    endpoint: Optional[str] = None
    status: str = "pending"  # pending, completed, failed
    response_time: Optional[float] = None
    error: Optional[str] = None


class RequestTracker:
    """
    Thread-safe request tracking service.
    Generates unique request IDs and manages request metadata.
    """

    def __init__(self):
        self._requests: Dict[str, RequestMetadata] = {}
        self._lock = threading.Lock()
        self._max_stored_requests = 1000  # Reduced from 10000 to prevent memory issues (target: <500MB)

    def generate_request_id(self) -> str:
        """
        Generate a unique request ID (UUID format).

        Returns:
            UUID string in standard format
        """
        return str(uuid.uuid4())

    def validate_client_request_id(self, client_request_id: str) -> bool:
        """
        Validate X-Client-Request-Id header value.

        Requirements per OpenAI API:
        - Must contain only ASCII characters
        - Must be no more than 512 characters long

        Args:
            client_request_id: The client-provided request ID

        Returns:
            True if valid, False otherwise
        """
        if not client_request_id:
            return False

        # Check length
        if len(client_request_id) > 512:
            return False

        # Check ASCII only
        try:
            client_request_id.encode('ascii')
        except UnicodeEncodeError:
            return False

        return True

    def create_request_metadata(
        self,
        client_request_id: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> RequestMetadata:
        """
        Create request metadata with validation.

        Args:
            client_request_id: Optional client-provided request ID
            model: Model name being used
            provider: Provider name (openai, groq, etc.)
            endpoint: API endpoint being called

        Returns:
            RequestMetadata object
        """
        # Generate server-side request ID
        request_id = self.generate_request_id()

        # Validate client request ID if provided
        if client_request_id and not self.validate_client_request_id(client_request_id):
            # If invalid, log warning but continue with server-generated ID
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Invalid X-Client-Request-Id provided: {client_request_id[:50]}... "
                f"(must be ASCII and <= 512 chars). Using server-generated ID."
            )
            client_request_id = None

        metadata = RequestMetadata(
            request_id=request_id,
            client_request_id=client_request_id,
            timestamp=datetime.now(),
            model=model,
            provider=provider,
            endpoint=endpoint,
            status="pending"
        )

        # Store metadata
        with self._lock:
            # Clean up old requests if we're at the limit
            if len(self._requests) >= self._max_stored_requests:
                # Remove oldest 10% of requests
                sorted_requests = sorted(
                    self._requests.items(),
                    key=lambda x: x[1].timestamp
                )
                to_remove = len(sorted_requests) // 10
                for req_id, _ in sorted_requests[:to_remove]:
                    del self._requests[req_id]

            self._requests[request_id] = metadata
            if client_request_id:
                # Also store by client request ID for lookup
                self._requests[client_request_id] = metadata

        return metadata

    def update_request(
        self,
        request_id: str,
        status: Optional[str] = None,
        response_time: Optional[float] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        Update request metadata.

        Args:
            request_id: Request ID to update
            status: New status (completed, failed)
            response_time: Response time in seconds
            error: Error message if failed

        Returns:
            True if request was found and updated, False otherwise
        """
        with self._lock:
            if request_id in self._requests:
                metadata = self._requests[request_id]
                if status:
                    metadata.status = status
                if response_time is not None:
                    metadata.response_time = response_time
                if error:
                    metadata.error = error
                return True
        return False

    def get_request(self, request_id: str) -> Optional[RequestMetadata]:
        """
        Retrieve request metadata by ID.

        Args:
            request_id: Request ID or client request ID

        Returns:
            RequestMetadata if found, None otherwise
        """
        with self._lock:
            return self._requests.get(request_id)

    def get_request_dict(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve request metadata as dictionary.

        Args:
            request_id: Request ID or client request ID

        Returns:
            Dictionary representation of RequestMetadata if found, None otherwise
        """
        metadata = self.get_request(request_id)
        if metadata:
            return asdict(metadata)
        return None

    def cleanup_old_requests(self, max_age_seconds: int = 3600):
        """
        Remove requests older than specified age.

        Args:
            max_age_seconds: Maximum age in seconds (default 1 hour)
        """
        current_time = datetime.now()
        with self._lock:
            to_remove = []
            for req_id, metadata in self._requests.items():
                age = (current_time - metadata.timestamp).total_seconds()
                if age > max_age_seconds:
                    to_remove.append(req_id)

            for req_id in to_remove:
                del self._requests[req_id]


# Global request tracker instance
_request_tracker: Optional[RequestTracker] = None
_tracker_lock = threading.Lock()


def get_request_tracker() -> RequestTracker:
    """
    Get or create the global request tracker instance.

    Returns:
        RequestTracker instance
    """
    global _request_tracker
    if _request_tracker is None:
        with _tracker_lock:
            if _request_tracker is None:
                _request_tracker = RequestTracker()
    return _request_tracker


# Thread-local storage for request context
_context = threading.local()


def set_request_context(request_id: str, client_request_id: Optional[str] = None):
    """
    Set request context for current thread.

    Args:
        request_id: Server-generated request ID
        client_request_id: Optional client-provided request ID
    """
    _context.request_id = request_id
    _context.client_request_id = client_request_id


def get_request_context() -> Optional[Dict[str, str]]:
    """
    Get request context for current thread.

    Returns:
        Dictionary with request_id and client_request_id, or None
    """
    request_id = getattr(_context, 'request_id', None)
    client_request_id = getattr(_context, 'client_request_id', None)

    if request_id:
        return {
            'request_id': request_id,
            'client_request_id': client_request_id
        }
    return None


def clear_request_context():
    """Clear request context for current thread."""
    if hasattr(_context, 'request_id'):
        delattr(_context, 'request_id')
    if hasattr(_context, 'client_request_id'):
        delattr(_context, 'client_request_id')

