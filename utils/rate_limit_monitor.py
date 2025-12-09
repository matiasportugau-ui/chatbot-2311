#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rate Limit Monitor
Tracks OpenAI API rate limits from response headers and provides monitoring capabilities.
"""

import time
import threading
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class RateLimitInfo:
    """Rate limit information for a specific limit type"""
    limit: Optional[int] = None
    remaining: Optional[int] = None
    reset_timestamp: Optional[float] = None  # Unix timestamp
    reset_datetime: Optional[datetime] = None
    
    def time_until_reset(self) -> Optional[float]:
        """
        Calculate seconds until reset.
        
        Returns:
            Seconds until reset, or None if not available
        """
        if self.reset_timestamp:
            remaining = self.reset_timestamp - time.time()
            return max(0, remaining)
        return None
    
    def is_exhausted(self) -> bool:
        """
        Check if limit is exhausted.
        
        Returns:
            True if remaining is 0 or None
        """
        return self.remaining is not None and self.remaining <= 0
    
    def utilization_percent(self) -> Optional[float]:
        """
        Calculate utilization percentage.
        
        Returns:
            Utilization percentage (0-100), or None if limit unknown
        """
        if self.limit is not None and self.limit > 0:
            used = self.limit - (self.remaining or 0)
            return (used / self.limit) * 100
        return None


@dataclass
class ProviderRateLimits:
    """Rate limit information for a provider"""
    requests: RateLimitInfo
    tokens: RateLimitInfo
    last_updated: datetime
    provider: str
    organization: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'provider': self.provider,
            'organization': self.organization,
            'requests': asdict(self.requests),
            'tokens': asdict(self.tokens),
            'last_updated': self.last_updated.isoformat(),
            'requests_time_until_reset': self.requests.time_until_reset(),
            'tokens_time_until_reset': self.tokens.time_until_reset(),
            'requests_utilization': self.requests.utilization_percent(),
            'tokens_utilization': self.tokens.utilization_percent(),
        }


class RateLimitMonitor:
    """
    Thread-safe rate limit monitor.
    Tracks rate limits per provider and organization.
    """
    
    def __init__(self):
        self._limits: Dict[str, ProviderRateLimits] = {}
        self._lock = threading.Lock()
        self._warning_threshold = 0.8  # Warn at 80% utilization
    
    def _parse_rate_limit_header(self, header_value: Optional[str]) -> Optional[int]:
        """
        Parse rate limit header value.
        
        Args:
            header_value: Header value string
            
        Returns:
            Integer value or None
        """
        if not header_value:
            return None
        try:
            return int(header_value.strip())
        except (ValueError, AttributeError):
            return None
    
    def _parse_reset_timestamp(self, reset_value: Optional[str]) -> Optional[float]:
        """
        Parse reset timestamp from header.
        OpenAI uses Unix timestamp format.
        
        Args:
            reset_value: Reset header value
            
        Returns:
            Unix timestamp or None
        """
        if not reset_value:
            return None
        try:
            return float(reset_value.strip())
        except (ValueError, AttributeError):
            return None
    
    def update_from_headers(
        self,
        headers: Dict[str, str],
        provider: str,
        organization: Optional[str] = None
    ) -> ProviderRateLimits:
        """
        Update rate limits from response headers.
        
        Expected headers:
        - x-ratelimit-limit-requests
        - x-ratelimit-remaining-requests
        - x-ratelimit-reset-requests
        - x-ratelimit-limit-tokens
        - x-ratelimit-remaining-tokens
        - x-ratelimit-reset-tokens
        
        Args:
            headers: Response headers dictionary
            provider: Provider name (openai, groq, etc.)
            organization: Organization ID if applicable
            
        Returns:
            Updated ProviderRateLimits object
        """
        # Create key for storage
        key = f"{provider}:{organization or 'default'}"
        
        # Parse request limits
        requests_limit = self._parse_rate_limit_header(
            headers.get('x-ratelimit-limit-requests')
        )
        requests_remaining = self._parse_rate_limit_header(
            headers.get('x-ratelimit-remaining-requests')
        )
        requests_reset = self._parse_reset_timestamp(
            headers.get('x-ratelimit-reset-requests')
        )
        
        requests_info = RateLimitInfo(
            limit=requests_limit,
            remaining=requests_remaining,
            reset_timestamp=requests_reset
        )
        if requests_reset:
            requests_info.reset_datetime = datetime.fromtimestamp(requests_reset)
        
        # Parse token limits
        tokens_limit = self._parse_rate_limit_header(
            headers.get('x-ratelimit-limit-tokens')
        )
        tokens_remaining = self._parse_rate_limit_header(
            headers.get('x-ratelimit-remaining-tokens')
        )
        tokens_reset = self._parse_reset_timestamp(
            headers.get('x-ratelimit-reset-tokens')
        )
        
        tokens_info = RateLimitInfo(
            limit=tokens_limit,
            remaining=tokens_remaining,
            reset_timestamp=tokens_reset
        )
        if tokens_reset:
            tokens_info.reset_datetime = datetime.fromtimestamp(tokens_reset)
        
        # Create or update rate limits
        rate_limits = ProviderRateLimits(
            requests=requests_info,
            tokens=tokens_info,
            last_updated=datetime.now(),
            provider=provider,
            organization=organization
        )
        
        with self._lock:
            self._limits[key] = rate_limits
        
        return rate_limits
    
    def get_rate_limits(
        self,
        provider: str,
        organization: Optional[str] = None
    ) -> Optional[ProviderRateLimits]:
        """
        Get current rate limits for provider.
        
        Args:
            provider: Provider name
            organization: Organization ID if applicable
            
        Returns:
            ProviderRateLimits if found, None otherwise
        """
        key = f"{provider}:{organization or 'default'}"
        with self._lock:
            return self._limits.get(key)
    
    def check_warnings(
        self,
        provider: str,
        organization: Optional[str] = None
    ) -> list[str]:
        """
        Check for rate limit warnings.
        
        Args:
            provider: Provider name
            organization: Organization ID if applicable
            
        Returns:
            List of warning messages
        """
        warnings = []
        rate_limits = self.get_rate_limits(provider, organization)
        
        if not rate_limits:
            return warnings
        
        # Check requests limit
        if rate_limits.requests.utilization_percent() is not None:
            utilization = rate_limits.requests.utilization_percent()
            if utilization >= (self._warning_threshold * 100):
                remaining = rate_limits.requests.remaining or 0
                time_until_reset = rate_limits.requests.time_until_reset()
                if time_until_reset:
                    warnings.append(
                        f"Requests rate limit {utilization:.1f}% utilized "
                        f"({remaining} remaining, resets in {time_until_reset:.0f}s)"
                    )
                else:
                    warnings.append(
                        f"Requests rate limit {utilization:.1f}% utilized "
                        f"({remaining} remaining)"
                    )
        
        # Check tokens limit
        if rate_limits.tokens.utilization_percent() is not None:
            utilization = rate_limits.tokens.utilization_percent()
            if utilization >= (self._warning_threshold * 100):
                remaining = rate_limits.tokens.remaining or 0
                time_until_reset = rate_limits.tokens.time_until_reset()
                if time_until_reset:
                    warnings.append(
                        f"Tokens rate limit {utilization:.1f}% utilized "
                        f"({remaining} remaining, resets in {time_until_reset:.0f}s)"
                    )
                else:
                    warnings.append(
                        f"Tokens rate limit {utilization:.1f}% utilized "
                        f"({remaining} remaining)"
                    )
        
        return warnings
    
    def get_all_rate_limits(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all rate limits as dictionary.
        
        Returns:
            Dictionary of all rate limits
        """
        with self._lock:
            return {
                key: limits.to_dict()
                for key, limits in self._limits.items()
            }
    
    def extract_rate_limit_info(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract rate limit information from headers as dictionary.
        
        Args:
            headers: Response headers
            
        Returns:
            Dictionary with rate limit information
        """
        info = {}
        
        # Requests
        if 'x-ratelimit-limit-requests' in headers:
            info['requests_limit'] = self._parse_rate_limit_header(
                headers['x-ratelimit-limit-requests']
            )
        if 'x-ratelimit-remaining-requests' in headers:
            info['requests_remaining'] = self._parse_rate_limit_header(
                headers['x-ratelimit-remaining-requests']
            )
        if 'x-ratelimit-reset-requests' in headers:
            reset_ts = self._parse_reset_timestamp(
                headers['x-ratelimit-reset-requests']
            )
            info['requests_reset_timestamp'] = reset_ts
            if reset_ts:
                info['requests_reset_datetime'] = datetime.fromtimestamp(reset_ts).isoformat()
                info['requests_time_until_reset'] = max(0, reset_ts - time.time())
        
        # Tokens
        if 'x-ratelimit-limit-tokens' in headers:
            info['tokens_limit'] = self._parse_rate_limit_header(
                headers['x-ratelimit-limit-tokens']
            )
        if 'x-ratelimit-remaining-tokens' in headers:
            info['tokens_remaining'] = self._parse_rate_limit_header(
                headers['x-ratelimit-remaining-tokens']
            )
        if 'x-ratelimit-reset-tokens' in headers:
            reset_ts = self._parse_reset_timestamp(
                headers['x-ratelimit-reset-tokens']
            )
            info['tokens_reset_timestamp'] = reset_ts
            if reset_ts:
                info['tokens_reset_datetime'] = datetime.fromtimestamp(reset_ts).isoformat()
                info['tokens_time_until_reset'] = max(0, reset_ts - time.time())
        
        return info


# Global rate limit monitor instance
_rate_limit_monitor: Optional[RateLimitMonitor] = None
_monitor_lock = threading.Lock()


def get_rate_limit_monitor() -> RateLimitMonitor:
    """
    Get or create the global rate limit monitor instance.
    
    Returns:
        RateLimitMonitor instance
    """
    global _rate_limit_monitor
    if _rate_limit_monitor is None:
        with _monitor_lock:
            if _rate_limit_monitor is None:
                _rate_limit_monitor = RateLimitMonitor()
    return _rate_limit_monitor

