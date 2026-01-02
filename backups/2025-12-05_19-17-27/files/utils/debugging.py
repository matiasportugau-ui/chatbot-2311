#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debugging Utilities
Functions to format request/response data and generate debugging reports.
"""

import json
from typing import Any, Dict, Optional, List
from datetime import datetime


def format_request_response(
    request_data: Dict[str, Any],
    response_data: Optional[Dict[str, Any]] = None,
    include_headers: bool = True
) -> str:
    """
    Format request and response data for debugging.
    
    Args:
        request_data: Request data dictionary
        response_data: Optional response data dictionary
        include_headers: Whether to include headers in output
        
    Returns:
        Formatted string for debugging
    """
    lines = []
    lines.append("=" * 80)
    lines.append("REQUEST/RESPONSE DEBUG INFO")
    lines.append("=" * 80)
    lines.append("")
    
    # Request info
    lines.append("REQUEST:")
    lines.append("-" * 80)
    if 'request_id' in request_data:
        lines.append(f"Request ID: {request_data['request_id']}")
    if 'client_request_id' in request_data:
        lines.append(f"Client Request ID: {request_data.get('client_request_id', 'N/A')}")
    if 'model' in request_data:
        lines.append(f"Model: {request_data['model']}")
    if 'provider' in request_data:
        lines.append(f"Provider: {request_data['provider']}")
    if 'timestamp' in request_data:
        lines.append(f"Timestamp: {request_data['timestamp']}")
    if include_headers and 'headers' in request_data:
        lines.append("\nRequest Headers:")
        for key, value in request_data['headers'].items():
            lines.append(f"  {key}: {value}")
    lines.append("")
    
    # Response info
    if response_data:
        lines.append("RESPONSE:")
        lines.append("-" * 80)
        if 'openai_request_id' in response_data:
            lines.append(f"OpenAI Request ID: {response_data['openai_request_id']}")
        if 'status' in response_data:
            lines.append(f"Status: {response_data['status']}")
        if 'tokens_input' in response_data:
            lines.append(f"Tokens (Input): {response_data['tokens_input']}")
        if 'tokens_output' in response_data:
            lines.append(f"Tokens (Output): {response_data['tokens_output']}")
        if 'total_tokens' in response_data:
            lines.append(f"Total Tokens: {response_data['total_tokens']}")
        if 'response_time' in response_data:
            lines.append(f"Response Time: {response_data['response_time']:.3f}s")
        if 'cost' in response_data:
            lines.append(f"Cost: ${response_data['cost']:.6f}")
        if include_headers and 'response_headers' in response_data:
            lines.append("\nResponse Headers:")
            for key, value in response_data['response_headers'].items():
                lines.append(f"  {key}: {value}")
        if 'error' in response_data:
            lines.append(f"\nError: {response_data['error']}")
        lines.append("")
    
    lines.append("=" * 80)
    return "\n".join(lines)


def format_rate_limit_info(rate_limit_info: Dict[str, Any]) -> str:
    """
    Format rate limit information for debugging.
    
    Args:
        rate_limit_info: Rate limit information dictionary
        
    Returns:
        Formatted string
    """
    lines = []
    lines.append("RATE LIMIT INFORMATION")
    lines.append("-" * 80)
    
    # Requests
    if 'requests_limit' in rate_limit_info:
        lines.append("\nRequests:")
        lines.append(f"  Limit: {rate_limit_info.get('requests_limit', 'N/A')}")
        lines.append(f"  Remaining: {rate_limit_info.get('requests_remaining', 'N/A')}")
        if 'requests_reset_datetime' in rate_limit_info:
            lines.append(f"  Reset: {rate_limit_info['requests_reset_datetime']}")
        if 'requests_time_until_reset' in rate_limit_info:
            lines.append(f"  Time until reset: {rate_limit_info['requests_time_until_reset']:.0f}s")
        if 'requests_limit' in rate_limit_info and 'requests_remaining' in rate_limit_info:
            limit = rate_limit_info['requests_limit']
            remaining = rate_limit_info.get('requests_remaining', 0)
            if limit and limit > 0:
                utilization = ((limit - remaining) / limit) * 100
                lines.append(f"  Utilization: {utilization:.1f}%")
    
    # Tokens
    if 'tokens_limit' in rate_limit_info:
        lines.append("\nTokens:")
        lines.append(f"  Limit: {rate_limit_info.get('tokens_limit', 'N/A')}")
        lines.append(f"  Remaining: {rate_limit_info.get('tokens_remaining', 'N/A')}")
        if 'tokens_reset_datetime' in rate_limit_info:
            lines.append(f"  Reset: {rate_limit_info['tokens_reset_datetime']}")
        if 'tokens_time_until_reset' in rate_limit_info:
            lines.append(f"  Time until reset: {rate_limit_info['tokens_time_until_reset']:.0f}s")
        if 'tokens_limit' in rate_limit_info and 'tokens_remaining' in rate_limit_info:
            limit = rate_limit_info['tokens_limit']
            remaining = rate_limit_info.get('tokens_remaining', 0)
            if limit and limit > 0:
                utilization = ((limit - remaining) / limit) * 100
                lines.append(f"  Utilization: {utilization:.1f}%")
    
    lines.append("-" * 80)
    return "\n".join(lines)


def generate_debugging_report(
    request_id: str,
    request_metadata: Optional[Dict[str, Any]] = None,
    request_data: Optional[Dict[str, Any]] = None,
    response_data: Optional[Dict[str, Any]] = None,
    rate_limit_info: Optional[Dict[str, Any]] = None,
    error_info: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate a comprehensive debugging report for a request.
    
    Args:
        request_id: Request ID
        request_metadata: Request metadata
        request_data: Request data
        response_data: Response data
        rate_limit_info: Rate limit information
        error_info: Error information if any
        
    Returns:
        Formatted debugging report
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"DEBUGGING REPORT - Request ID: {request_id}")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append("=" * 80)
    lines.append("")
    
    # Request metadata
    if request_metadata:
        lines.append("REQUEST METADATA:")
        lines.append("-" * 80)
        for key, value in request_metadata.items():
            lines.append(f"  {key}: {value}")
        lines.append("")
    
    # Request data
    if request_data:
        lines.append("REQUEST DATA:")
        lines.append("-" * 80)
        lines.append(format_request_response(request_data, response_data))
        lines.append("")
    
    # Rate limit info
    if rate_limit_info:
        lines.append(format_rate_limit_info(rate_limit_info))
        lines.append("")
    
    # Error info
    if error_info:
        lines.append("ERROR INFORMATION:")
        lines.append("-" * 80)
        for key, value in error_info.items():
            lines.append(f"  {key}: {value}")
        lines.append("")
    
    lines.append("=" * 80)
    return "\n".join(lines)


def extract_openai_headers(headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Extract OpenAI-specific headers from response headers.
    
    Args:
        headers: Response headers dictionary
        
    Returns:
        Dictionary with extracted OpenAI headers
    """
    openai_headers = {}
    
    # API meta information
    if 'openai-organization' in headers:
        openai_headers['organization'] = headers['openai-organization']
    if 'openai-processing-ms' in headers:
        try:
            openai_headers['processing_ms'] = int(headers['openai-processing-ms'])
        except (ValueError, TypeError):
            pass
    if 'openai-version' in headers:
        openai_headers['version'] = headers['openai-version']
    if 'x-request-id' in headers:
        openai_headers['request_id'] = headers['x-request-id']
    
    # Rate limiting
    rate_limit_keys = [
        'x-ratelimit-limit-requests',
        'x-ratelimit-limit-tokens',
        'x-ratelimit-remaining-requests',
        'x-ratelimit-remaining-tokens',
        'x-ratelimit-reset-requests',
        'x-ratelimit-reset-tokens'
    ]
    
    for key in rate_limit_keys:
        if key in headers:
            openai_headers[key] = headers[key]
    
    return openai_headers


def format_error_with_context(
    error: Exception,
    request_id: Optional[str] = None,
    client_request_id: Optional[str] = None,
    openai_request_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Format error with full context for debugging.
    
    Args:
        error: Exception object
        request_id: Server-generated request ID
        client_request_id: Client-provided request ID
        openai_request_id: OpenAI's request ID
        context: Additional context dictionary
        
    Returns:
        Formatted error string
    """
    lines = []
    lines.append("ERROR DETAILS")
    lines.append("-" * 80)
    lines.append(f"Error Type: {type(error).__name__}")
    lines.append(f"Error Message: {str(error)}")
    
    if request_id:
        lines.append(f"Request ID: {request_id}")
    if client_request_id:
        lines.append(f"Client Request ID: {client_request_id}")
    if openai_request_id:
        lines.append(f"OpenAI Request ID: {openai_request_id}")
    
    if context:
        lines.append("\nAdditional Context:")
        for key, value in context.items():
            lines.append(f"  {key}: {value}")
    
    # Include traceback if available
    import traceback
    if hasattr(error, '__traceback__'):
        lines.append("\nTraceback:")
        lines.append("".join(traceback.format_tb(error.__traceback__)))
    
    lines.append("-" * 80)
    return "\n".join(lines)

