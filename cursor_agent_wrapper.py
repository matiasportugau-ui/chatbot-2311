#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor Agent Wrapper for Multi-Provider AI Integration
Provides a unified interface for Cursor to use OpenAI, Groq, Gemini, and Grok
"""

import os
import logging
from typing import Dict, List, Optional, Any, Literal
from model_integrator import get_model_integrator, UnifiedModelIntegrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CursorAgent:
    """
    Cursor-compatible agent wrapper for multi-provider AI models
    """
    
    def __init__(
        self,
        strategy: Literal["cost", "speed", "quality", "balanced"] = "balanced",
        default_provider: Optional[str] = None
    ):
        """
        Initialize Cursor Agent
        
        Args:
            strategy: Model selection strategy (cost, speed, quality, balanced)
            default_provider: Force a specific provider (openai, groq, gemini, grok)
        """
        self.integrator = get_model_integrator()
        self.integrator.strategy = strategy
        self.default_provider = default_provider
        logger.info(f"Cursor Agent initialized with strategy: {strategy}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat completion compatible with Cursor's expected format
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Optional model ID to use (e.g., 'grok_grok-4-latest')
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            Dict with 'content', 'model', 'usage', etc.
        """
        # Extract system prompt and user messages
        system_prompt = None
        user_messages = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                system_prompt = content
            elif role == "user":
                user_messages.append(content)
            elif role == "assistant":
                # For multi-turn, we'd need to handle this differently
                # For now, just append to context
                user_messages.append(f"[Previous response]: {content}")
        
        # Combine user messages
        prompt = "\n".join(user_messages) if user_messages else ""
        
        # Select model
        model_id = model
        if not model_id and self.default_provider:
            # Try to find a model from the default provider
            available = self.integrator.list_available_models()
            for m in available:
                if m["provider"] == self.default_provider and m["enabled"]:
                    model_id = m["model_id"]
                    break
        
        # Generate response
        response = self.integrator.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            model_id=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Format response in Cursor-compatible format
        return {
            "content": response["content"],
            "model": response["model_used"],
            "provider": response["provider"],
            "usage": {
                "prompt_tokens": response["tokens_input"],
                "completion_tokens": response["tokens_output"],
                "total_tokens": response["total_tokens"],
            },
            "cost": response["cost"],
            "response_time": response["response_time"],
            "success": response["success"],
        }
    
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        Streaming chat completion (generator)
        
        Note: Full streaming support depends on provider capabilities
        """
        # For now, return non-streaming and yield chunks
        # Full streaming would require provider-specific implementations
        response = self.chat(messages, model, temperature, max_tokens, **kwargs)
        
        # Simulate streaming by yielding chunks
        content = response["content"]
        chunk_size = 10
        
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            yield {
                "delta": {"content": chunk},
                "model": response["model"],
            }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all available models"""
        return self.integrator.list_available_models()
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.integrator.get_usage_summary()
    
    def set_strategy(self, strategy: Literal["cost", "speed", "quality", "balanced"]):
        """Update model selection strategy"""
        self.integrator.strategy = strategy
        logger.info(f"Strategy updated to: {strategy}")


# Convenience function for Cursor integration
def get_cursor_agent(
    strategy: Literal["cost", "speed", "quality", "balanced"] = "balanced",
    provider: Optional[str] = None
) -> CursorAgent:
    """
    Get a Cursor agent instance
    
    Args:
        strategy: Model selection strategy
        provider: Optional provider to prefer (openai, groq, gemini, grok)
    
    Returns:
        CursorAgent instance
    """
    return CursorAgent(strategy=strategy, default_provider=provider)


# Example usage
if __name__ == "__main__":
    # Initialize agent with balanced strategy
    agent = get_cursor_agent(strategy="balanced")
    
    # Example chat
    messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a Python function to calculate factorial"}
    ]
    
    response = agent.chat(messages, temperature=0.7, max_tokens=500)
    
    print(f"Model: {response['model']}")
    print(f"Provider: {response['provider']}")
    print(f"Response: {response['content']}")
    print(f"Tokens: {response['usage']['total_tokens']}")
    print(f"Cost: ${response['cost']:.6f}")

