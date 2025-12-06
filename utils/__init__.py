#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilities package for OpenAI API best practices implementation.
"""

from utils.request_tracking import (
    get_request_tracker,
    RequestTracker,
    RequestMetadata,
    set_request_context,
    get_request_context,
    clear_request_context,
)

from utils.structured_logger import (
    get_structured_logger,
    StructuredLogger,
)

from utils.rate_limit_monitor import (
    get_rate_limit_monitor,
    RateLimitMonitor,
    RateLimitInfo,
    ProviderRateLimits,
)

from utils.debugging import (
    format_request_response,
    format_rate_limit_info,
    generate_debugging_report,
    extract_openai_headers,
    format_error_with_context,
)

__all__ = [
    # Request tracking
    'get_request_tracker',
    'RequestTracker',
    'RequestMetadata',
    'set_request_context',
    'get_request_context',
    'clear_request_context',
    # Structured logging
    'get_structured_logger',
    'StructuredLogger',
    # Rate limit monitoring
    'get_rate_limit_monitor',
    'RateLimitMonitor',
    'RateLimitInfo',
    'ProviderRateLimits',
    # Debugging
    'format_request_response',
    'format_rate_limit_info',
    'generate_debugging_report',
    'extract_openai_headers',
    'format_error_with_context',
]

