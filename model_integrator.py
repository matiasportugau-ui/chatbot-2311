#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified API Model Integrator
Supports OpenAI, Groq, Google Gemini, and xAI (Grok) with cost optimization
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import time

# Import new utilities
try:
    from utils.request_tracking import get_request_tracker, set_request_context, get_request_context
    from utils.structured_logger import get_structured_logger
    from utils.rate_limit_monitor import get_rate_limit_monitor
    from utils.debugging import extract_openai_headers, format_error_with_context
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    # Fallback if utils not available
    def get_request_tracker():
        return None
    def set_request_context(*args, **kwargs):
        pass
    def get_request_context():
        return None
    def get_structured_logger(*args, **kwargs):
        return logging.getLogger(__name__)
    def get_rate_limit_monitor():
        return None
    def extract_openai_headers(*args):
        return {}
    def format_error_with_context(*args, **kwargs):
        return str(args[0]) if args else ""

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize structured logger if available
if UTILS_AVAILABLE:
    structured_logger = get_structured_logger(__name__)
else:
    structured_logger = logger

# Provider availability checks
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed")

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("Groq package not installed")

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
    GEMINI_USE_OLD_SDK = False
except ImportError:
    # Fallback to old SDK if new one not available
    try:
        import google.generativeai as genai_old
        GEMINI_AVAILABLE = True
        GEMINI_USE_OLD_SDK = True
    except ImportError:
        GEMINI_AVAILABLE = False
        GEMINI_USE_OLD_SDK = False
        logger.warning("Google Gemini package not installed. Install with: pip install google-genai")

# Grok (xAI) uses OpenAI-compatible API, so we can use OpenAI client
GROK_AVAILABLE = OPENAI_AVAILABLE  # Uses same OpenAI library


class ModelProvider(str, Enum):
    """Supported AI model providers"""
    OPENAI = "openai"
    GROQ = "groq"
    GEMINI = "gemini"
    GROK = "grok"


@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    provider: ModelProvider
    model_name: str
    api_key: str
    base_url: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    cost_per_1k_tokens_input: float = 0.0
    cost_per_1k_tokens_output: float = 0.0
    speed_rating: int = 5  # 1-10, higher is faster
    quality_rating: int = 5  # 1-10, higher is better quality
    enabled: bool = True
    organization_id: Optional[str] = None  # OpenAI organization ID
    project_id: Optional[str] = None  # OpenAI project ID


@dataclass
class UsageStats:
    """Usage statistics for cost tracking"""
    provider: str
    model: str
    tokens_input: int = 0
    tokens_output: int = 0
    requests: int = 0
    total_cost: float = 0.0
    errors: int = 0
    avg_response_time: float = 0.0
    last_used: Optional[datetime] = None


class UnifiedModelIntegrator:
    """
    Unified integrator for multiple AI providers with cost optimization
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.models: Dict[str, ModelConfig] = {}
        self.clients: Dict[str, Any] = {}
        self.usage_stats: Dict[str, UsageStats] = {}
        self.default_provider: Optional[ModelProvider] = None
        self.strategy: Literal["cost", "speed", "quality", "balanced"] = "balanced"
        self.openai_org_id: Optional[str] = None
        self.openai_project_id: Optional[str] = None
        
        # Load configuration
        self._load_config(config_file)
        self._initialize_clients()
        self._load_usage_stats()
    
    def _load_config(self, config_file: Optional[str] = None):
        """Load model configurations from environment or config file"""
        # Default model configurations with cost optimization
        default_configs = {
            "openai": {
                "gpt-4o": {
                    "cost_input": 2.50,  # per 1M tokens
                    "cost_output": 10.00,
                    "speed": 8,
                    "quality": 10,
                },
                "gpt-4o-mini": {
                    "cost_input": 0.15,
                    "cost_output": 0.60,
                    "speed": 9,
                    "quality": 8,
                },
                "gpt-4-turbo": {
                    "cost_input": 10.00,
                    "cost_output": 30.00,
                    "speed": 7,
                    "quality": 10,
                },
                "gpt-3.5-turbo": {
                    "cost_input": 0.50,
                    "cost_output": 1.50,
                    "speed": 9,
                    "quality": 7,
                },
            },
            "groq": {
                "llama-3.1-70b-versatile": {
                    "cost_input": 0.00,  # Free tier available
                    "cost_output": 0.00,
                    "speed": 10,
                    "quality": 9,
                },
                "llama-3.1-8b-instant": {
                    "cost_input": 0.00,
                    "cost_output": 0.00,
                    "speed": 10,
                    "quality": 7,
                },
                "mixtral-8x7b-32768": {
                    "cost_input": 0.00,
                    "cost_output": 0.00,
                    "speed": 10,
                    "quality": 8,
                },
            },
            "gemini": {
                "gemini-2.5-flash": {
                    "cost_input": 0.10,  # per 1M tokens (estimated, very low cost)
                    "cost_output": 0.40,
                    "speed": 10,
                    "quality": 9,
                },
                "gemini-1.5-flash": {
                    "cost_input": 0.075,
                    "cost_output": 0.30,
                    "speed": 9,
                    "quality": 8,
                },
                "gemini-1.5-pro": {
                    "cost_input": 1.25,
                    "cost_output": 5.00,
                    "speed": 8,
                    "quality": 10,
                },
                "gemini-3-pro": {
                    "cost_input": 2.50,  # per 1M tokens (estimated for preview)
                    "cost_output": 10.00,
                    "speed": 7,
                    "quality": 10,
                },
                "gemini-pro": {
                    "cost_input": 0.50,
                    "cost_output": 2.00,
                    "speed": 8,
                    "quality": 9,
                },
            },
            "grok": {
                "grok-beta": {
                    "cost_input": 0.50,  # per 1M tokens (estimated)
                    "cost_output": 1.50,
                    "speed": 8,
                    "quality": 9,
                },
                "grok-2-1212": {
                    "cost_input": 0.50,
                    "cost_output": 1.50,
                    "speed": 8,
                    "quality": 9,
                },
                "grok-2-vision-1212": {
                    "cost_input": 0.75,
                    "cost_output": 2.00,
                    "speed": 7,
                    "quality": 9,
                },
                "grok-4-latest": {
                    "cost_input": 0.60,
                    "cost_output": 1.80,
                    "speed": 8,
                    "quality": 10,
                },
            },
        }
        
        # Load from environment variables
        self._load_from_env(default_configs)
        
        # Load from config file if provided
        if config_file and os.path.exists(config_file):
            self._load_from_file(config_file)
    
    def _load_from_env(self, default_configs: Dict):
        """Load configurations from environment variables"""
        # Get OpenAI organization and project IDs (optional)
        openai_org_id = os.getenv("OPENAI_ORGANIZATION_ID")
        openai_project_id = os.getenv("OPENAI_PROJECT_ID")
        
        # OpenAI
        if OPENAI_AVAILABLE:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                models = os.getenv("OPENAI_MODELS", "gpt-4o-mini,gpt-4o").split(",")
                for model in models:
                    model = model.strip()
                    if model in default_configs["openai"]:
                        config = default_configs["openai"][model]
                        self.models[f"openai_{model}"] = ModelConfig(
                            provider=ModelProvider.OPENAI,
                            model_name=model,
                            api_key=openai_key,
                            cost_per_1k_tokens_input=config["cost_input"] / 1000,
                            cost_per_1k_tokens_output=config["cost_output"] / 1000,
                            speed_rating=config["speed"],
                            quality_rating=config["quality"],
                            enabled=True,
                            organization_id=openai_org_id,
                            project_id=openai_project_id,
                        )
                        if not self.default_provider:
                            self.default_provider = ModelProvider.OPENAI
        
        # Groq
        if GROQ_AVAILABLE:
            groq_key = os.getenv("GROQ_API_KEY")
            if groq_key:
                models = os.getenv("GROQ_MODELS", "llama-3.1-70b-versatile,llama-3.1-8b-instant").split(",")
                for model in models:
                    model = model.strip()
                    if model in default_configs["groq"]:
                        config = default_configs["groq"][model]
                        self.models[f"groq_{model}"] = ModelConfig(
                            provider=ModelProvider.GROQ,
                            model_name=model,
                            api_key=groq_key,
                            cost_per_1k_tokens_input=config["cost_input"] / 1000,
                            cost_per_1k_tokens_output=config["cost_output"] / 1000,
                            speed_rating=config["speed"],
                            quality_rating=config["quality"],
                            enabled=True,
                        )
                        if not self.default_provider:
                            self.default_provider = ModelProvider.GROQ
        
        # Gemini
        if GEMINI_AVAILABLE:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                models = os.getenv("GEMINI_MODELS", "gemini-2.5-flash,gemini-1.5-pro,gemini-3-pro").split(",")
                for model in models:
                    model = model.strip()
                    if model in default_configs["gemini"]:
                        config = default_configs["gemini"][model]
                        self.models[f"gemini_{model}"] = ModelConfig(
                            provider=ModelProvider.GEMINI,
                            model_name=model,
                            api_key=gemini_key,
                            cost_per_1k_tokens_input=config["cost_input"] / 1000,
                            cost_per_1k_tokens_output=config["cost_output"] / 1000,
                            speed_rating=config["speed"],
                            quality_rating=config["quality"],
                            enabled=True,
                        )
                        if not self.default_provider:
                            self.default_provider = ModelProvider.GEMINI
        
        # Grok (xAI) - uses OpenAI-compatible API
        if GROK_AVAILABLE:
            grok_key = os.getenv("GROK_API_KEY")
            if grok_key:
                models = os.getenv("GROK_MODELS", "grok-beta,grok-2-1212,grok-4-latest").split(",")
                for model in models:
                    model = model.strip()
                    if model in default_configs["grok"]:
                        config = default_configs["grok"][model]
                        self.models[f"grok_{model}"] = ModelConfig(
                            provider=ModelProvider.GROK,
                            model_name=model,
                            api_key=grok_key,
                            base_url="https://api.x.ai/v1",  # xAI API endpoint
                            cost_per_1k_tokens_input=config["cost_input"] / 1000,
                            cost_per_1k_tokens_output=config["cost_output"] / 1000,
                            speed_rating=config["speed"],
                            quality_rating=config["quality"],
                            enabled=True,
                        )
                        if not self.default_provider:
                            self.default_provider = ModelProvider.GROK
        
        # Set strategy from environment
        self.strategy = os.getenv("MODEL_STRATEGY", "balanced").lower()
        if self.strategy not in ["cost", "speed", "quality", "balanced"]:
            self.strategy = "balanced"
    
    def _load_from_file(self, config_file: str):
        """Load configurations from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                # Merge file config with existing configs
                # Implementation depends on file format
                logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    def _initialize_clients(self):
        """Initialize API clients for each provider"""
        # Group models by provider
        providers = {}
        for model_id, config in self.models.items():
            if config.enabled:
                provider = config.provider.value
                if provider not in providers:
                    providers[provider] = []
                providers[provider].append((model_id, config))
        
        # Initialize OpenAI client
        if ModelProvider.OPENAI.value in providers:
            try:
                openai_configs = providers[ModelProvider.OPENAI.value]
                if openai_configs:
                    api_key = openai_configs[0][1].api_key
                    org_id = openai_configs[0][1].organization_id
                    project_id = openai_configs[0][1].project_id
                    
                    # Build default headers for OpenAI client
                    default_headers = {}
                    if org_id:
                        default_headers["OpenAI-Organization"] = org_id
                    if project_id:
                        default_headers["OpenAI-Project"] = project_id
                    
                    # OpenAI client doesn't support default_headers directly,
                    # so we'll add them per-request instead
                    self.clients[ModelProvider.OPENAI.value] = OpenAI(api_key=api_key)
                    # Store org/project IDs for later use
                    self.openai_org_id = org_id
                    self.openai_project_id = project_id
                    structured_logger.info("✅ OpenAI client initialized", 
                                          organization_id=org_id, 
                                          project_id=project_id)
            except Exception as e:
                structured_logger.error(f"Error initializing OpenAI: {e}")
        
        # Initialize Groq client
        if ModelProvider.GROQ.value in providers:
            try:
                groq_configs = providers[ModelProvider.GROQ.value]
                if groq_configs:
                    api_key = groq_configs[0][1].api_key
                    self.clients[ModelProvider.GROQ.value] = Groq(api_key=api_key)
                    structured_logger.info("✅ Groq client initialized")
            except Exception as e:
                structured_logger.error(f"Error initializing Groq: {e}")
        
        # Initialize Gemini client
        if ModelProvider.GEMINI.value in providers:
            try:
                gemini_configs = providers[ModelProvider.GEMINI.value]
                if gemini_configs:
                    api_key = gemini_configs[0][1].api_key
                    # Use new google-genai SDK if available
                    if GEMINI_AVAILABLE and not GEMINI_USE_OLD_SDK:
                        from google import genai
                        self.clients[ModelProvider.GEMINI.value] = genai.Client(api_key=api_key)
                        self.gemini_use_new_sdk = True
                        structured_logger.info("✅ Gemini client initialized (new SDK - google-genai)")
                    else:
                        # Fallback to old SDK
                        import google.generativeai as genai_old
                        genai_old.configure(api_key=api_key)
                        self.clients[ModelProvider.GEMINI.value] = genai_old
                        self.gemini_use_new_sdk = False
                        structured_logger.info("✅ Gemini client initialized (old SDK - google-generativeai)")
            except Exception as e:
                structured_logger.error(f"Error initializing Gemini: {e}")
        
        # Initialize Grok (xAI) client - uses OpenAI client with custom base_url
        if ModelProvider.GROK.value in providers:
            try:
                grok_configs = providers[ModelProvider.GROK.value]
                if grok_configs:
                    api_key = grok_configs[0][1].api_key
                    base_url = grok_configs[0][1].base_url or "https://api.x.ai/v1"
                    self.clients[ModelProvider.GROK.value] = OpenAI(
                        api_key=api_key,
                        base_url=base_url
                    )
                    structured_logger.info("✅ Grok (xAI) client initialized")
            except Exception as e:
                structured_logger.error(f"Error initializing Grok: {e}")
    
    def _select_best_model(self, task_type: str = "general") -> Optional[str]:
        """
        Select the best model based on strategy and task type
        """
        enabled_models = {
            model_id: config
            for model_id, config in self.models.items()
            if config.enabled
        }
        
        if not enabled_models:
            return None
        
        # Score models based on strategy
        scored_models = []
        for model_id, config in enabled_models.items():
            score = 0.0
            
            if self.strategy == "cost":
                # Prefer lowest cost (invert cost, higher is better)
                cost_score = 1.0 / (1.0 + config.cost_per_1k_tokens_input + config.cost_per_1k_tokens_output)
                score = cost_score * 0.7 + config.quality_rating * 0.3
            elif self.strategy == "speed":
                score = config.speed_rating * 0.7 + config.quality_rating * 0.3
            elif self.strategy == "quality":
                score = config.quality_rating * 0.7 + config.speed_rating * 0.3
            else:  # balanced
                cost_score = 1.0 / (1.0 + config.cost_per_1k_tokens_input + config.cost_per_1k_tokens_output)
                score = (cost_score * 0.3 + 
                        config.speed_rating * 0.3 + 
                        config.quality_rating * 0.4)
            
            scored_models.append((model_id, score, config))
        
        # Sort by score (highest first)
        scored_models.sort(key=lambda x: x[1], reverse=True)
        
        # Return best model
        if scored_models:
            return scored_models[0][0]
        
        return None
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        client_request_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using the selected model
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model_id: Optional model ID (auto-selected if not provided)
            temperature: Optional temperature
            max_tokens: Optional max tokens
            client_request_id: Optional client-provided request ID (X-Client-Request-Id)
            **kwargs: Additional parameters
            
        Returns:
            Dict with 'content', 'model_used', 'tokens_input', 'tokens_output', 'cost', 'response_time', 'request_id', etc.
        """
        # Initialize request tracking
        request_tracker = get_request_tracker() if UTILS_AVAILABLE else None
        request_metadata = None
        
        if request_tracker:
            request_metadata = request_tracker.create_request_metadata(
                client_request_id=client_request_id
            )
            # Set request context for logging
            set_request_context(
                request_metadata.request_id,
                request_metadata.client_request_id
            )
        
        # Select model if not specified
        if not model_id:
            model_id = self._select_best_model()
        
        if not model_id or model_id not in self.models:
            error_msg = f"Model {model_id} not available"
            if request_metadata:
                request_tracker.update_request(
                    request_metadata.request_id,
                    status="failed",
                    error=error_msg
                )
            raise ValueError(error_msg)
        
        config = self.models[model_id]
        provider = config.provider.value
        
        # Update request metadata with model info
        if request_metadata and request_tracker:
            request_metadata.model = config.model_name
            request_metadata.provider = provider
        
        # Use provided parameters or fall back to config defaults
        temp = temperature if temperature is not None else config.temperature
        max_tok = max_tokens if max_tokens is not None else config.max_tokens
        
        start_time = time.time()
        
        # Log request
        if UTILS_AVAILABLE:
            structured_logger.log_openai_request(
                model=config.model_name,
                provider=provider,
                prompt_length=len(prompt),
                system_prompt_length=len(system_prompt) if system_prompt else None,
                request_id=request_metadata.request_id if request_metadata else None,
                client_request_id=request_metadata.client_request_id if request_metadata else None,
            )
        
        try:
            # Pass client_request_id to generation methods
            if provider == "openai":
                response = self._generate_openai(
                    prompt, system_prompt, config.model_name, temp, max_tok,
                    client_request_id=request_metadata.client_request_id if request_metadata else None,
                    organization_id=config.organization_id,
                    project_id=config.project_id,
                    **kwargs
                )
            elif provider == "groq":
                response = self._generate_groq(
                    prompt, system_prompt, config.model_name, temp, max_tok, **kwargs
                )
            elif provider == "gemini":
                response = self._generate_gemini(
                    prompt, system_prompt, config.model_name, temp, max_tok, **kwargs
                )
            elif provider == "grok":
                response = self._generate_grok(
                    prompt, system_prompt, config.model_name, temp, max_tok,
                    client_request_id=request_metadata.client_request_id if request_metadata else None,
                    **kwargs
                )
            else:
                raise ValueError(f"Unknown provider: {provider}")
            
            response_time = time.time() - start_time
            
            # Calculate cost
            tokens_input = response.get("tokens_input", 0)
            tokens_output = response.get("tokens_output", 0)
            cost = (
                (tokens_input / 1000) * config.cost_per_1k_tokens_input +
                (tokens_output / 1000) * config.cost_per_1k_tokens_output
            )
            
            # Extract response headers and rate limit info
            response_headers = response.get("response_headers", {})
            openai_request_id = response_headers.get("x-request-id")
            rate_limit_info = None
            
            # Update rate limit monitor
            if UTILS_AVAILABLE and response_headers:
                rate_limit_monitor = get_rate_limit_monitor()
                if rate_limit_monitor:
                    rate_limit_monitor.update_from_headers(
                        response_headers,
                        provider,
                        config.organization_id
                    )
                    rate_limit_info = rate_limit_monitor.extract_rate_limit_info(response_headers)
            
            # Update usage stats
            self._update_usage_stats(model_id, tokens_input, tokens_output, cost, response_time)
            
            # Update request tracking
            if request_metadata and request_tracker:
                request_tracker.update_request(
                    request_metadata.request_id,
                    status="completed",
                    response_time=response_time
                )
            
            # Log response
            if UTILS_AVAILABLE:
                structured_logger.log_openai_response(
                    model=config.model_name,
                    provider=provider,
                    tokens_input=tokens_input,
                    tokens_output=tokens_output,
                    response_time=response_time,
                    cost=cost,
                    request_id=request_metadata.request_id if request_metadata else None,
                    client_request_id=request_metadata.client_request_id if request_metadata else None,
                    openai_request_id=openai_request_id,
                    rate_limit_info=rate_limit_info,
                )
            
            result = {
                "content": response["content"],
                "model_used": model_id,
                "provider": provider,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "total_tokens": tokens_input + tokens_output,
                "cost": cost,
                "response_time": response_time,
                "success": True,
            }
            
            # Add request tracking info
            if request_metadata:
                result["request_id"] = request_metadata.request_id
                if request_metadata.client_request_id:
                    result["client_request_id"] = request_metadata.client_request_id
            if openai_request_id:
                result["openai_request_id"] = openai_request_id
            if rate_limit_info:
                result["rate_limit_info"] = rate_limit_info
            
            return result
        
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = str(e)
            
            # Get response headers if available (from error response)
            response_headers = {}
            openai_request_id = None
            if hasattr(e, 'response') and hasattr(e.response, 'headers'):
                response_headers = dict(e.response.headers)
                openai_request_id = response_headers.get("x-request-id")
            
            # Log error
            if UTILS_AVAILABLE:
                structured_logger.log_openai_error(
                    model=config.model_name,
                    provider=provider,
                    error=error_msg,
                    request_id=request_metadata.request_id if request_metadata else None,
                    client_request_id=request_metadata.client_request_id if request_metadata else None,
                    openai_request_id=openai_request_id,
                    response_headers=response_headers if response_headers else None,
                )
            
            # Update request tracking
            if request_metadata and request_tracker:
                request_tracker.update_request(
                    request_metadata.request_id,
                    status="failed",
                    response_time=response_time,
                    error=error_msg
                )
            
            # Try fallback model
            if model_id != self._select_best_model():
                structured_logger.info("Trying fallback model...")
                return self.generate(prompt, system_prompt, None, temp, max_tok, 
                                   client_request_id=client_request_id, **kwargs)
            
            result = {
                "content": f"Error: {error_msg}",
                "model_used": model_id,
                "provider": provider,
                "tokens_input": 0,
                "tokens_output": 0,
                "total_tokens": 0,
                "cost": 0.0,
                "response_time": response_time,
                "success": False,
                "error": error_msg,
            }
            
            # Add request tracking info
            if request_metadata:
                result["request_id"] = request_metadata.request_id
                if request_metadata.client_request_id:
                    result["client_request_id"] = request_metadata.client_request_id
            if openai_request_id:
                result["openai_request_id"] = openai_request_id
            
            return result
    
    def _generate_openai(
        self, prompt: str, system_prompt: Optional[str], model: str, 
        temperature: float, max_tokens: int,
        client_request_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate using OpenAI with request tracking and header capture"""
        client = self.clients["openai"]
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Prepare extra headers
        extra_headers = {}
        if client_request_id:
            extra_headers["X-Client-Request-Id"] = client_request_id
        if organization_id:
            extra_headers["OpenAI-Organization"] = organization_id
        if project_id:
            extra_headers["OpenAI-Project"] = project_id
        
        # Use httpx client to capture response headers
        response_headers = {}
        try:
            import httpx
            
            # Create a custom httpx client with event hooks to capture headers
            original_client = client._client if hasattr(client, '_client') else None
            
            # Make the request with extra headers
            # OpenAI SDK supports extra_headers parameter in some versions
            # For compatibility, we'll try to use it, otherwise we'll need to patch the client
            try:
                # Try using extra_headers if available (OpenAI SDK >= 1.0.0)
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_headers=extra_headers,
                    **kwargs
                )
            except TypeError:
                # Fallback: make request without extra_headers (older SDK versions)
                # We'll need to set headers via client configuration
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            
            # Try to extract headers from response
            # OpenAI SDK response object doesn't directly expose headers
            # We need to access the underlying httpx response
            if hasattr(response, '_response') and hasattr(response._response, 'headers'):
                response_headers = dict(response._response.headers)
            elif hasattr(response, 'headers'):
                response_headers = dict(response.headers)
            else:
                # If we can't get headers directly, try to access via the client
                # This is a limitation - we may not always be able to capture headers
                pass
                
        except ImportError:
            # httpx not available, make request without header capture
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        except Exception as e:
            # If anything fails, just make the request normally
            structured_logger.warning(f"Could not capture response headers: {e}")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        
        return {
            "content": response.choices[0].message.content,
            "tokens_input": response.usage.prompt_tokens,
            "tokens_output": response.usage.completion_tokens,
            "response_headers": response_headers,
        }
    
    def _generate_groq(
        self, prompt: str, system_prompt: Optional[str], model: str,
        temperature: float, max_tokens: int, **kwargs
    ) -> Dict[str, Any]:
        """Generate using Groq"""
        client = self.clients["groq"]
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return {
            "content": response.choices[0].message.content,
            "tokens_input": response.usage.prompt_tokens,
            "tokens_output": response.usage.completion_tokens,
        }
    
    def _generate_gemini(
        self, prompt: str, system_prompt: Optional[str], model: str,
        temperature: float, max_tokens: int, **kwargs
    ) -> Dict[str, Any]:
        """Generate using Google Gemini (supports both new and old SDK)"""
        genai_client = self.clients["gemini"]
        use_new_sdk = getattr(self, 'gemini_use_new_sdk', False)
        
        if use_new_sdk:
            # New google-genai SDK
            from google.genai import types
            
            try:
                # Prepare contents - can be string or Content objects
                # For simple text, pass as string
                contents = prompt
                
                # Prepare config with system instruction
                config = types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
                
                # Add system instruction if provided
                if system_prompt:
                    config.system_instruction = system_prompt
                
                # Update with any additional kwargs
                for key, value in kwargs.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                
                # Generate content
                response = genai_client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )
                
                # Extract response text
                # Response has .text attribute directly
                content_text = response.text if hasattr(response, 'text') and response.text else ""
                
                # Try to get token counts from response
                # New SDK stores usage in usage_metadata field
                tokens_input = 0
                tokens_output = 0
                
                # Check for usage metadata
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    usage = response.usage_metadata
                    # usage_metadata is a UsageMetadata object with:
                    # - prompt_token_count: input tokens
                    # - response_token_count: output tokens
                    # - total_token_count: total tokens
                    if hasattr(usage, 'prompt_token_count'):
                        tokens_input = usage.prompt_token_count or 0
                    if hasattr(usage, 'response_token_count'):
                        tokens_output = usage.response_token_count or 0
                    elif hasattr(usage, 'total_token_count') and tokens_input > 0:
                        # Fallback: calculate output from total
                        tokens_output = (usage.total_token_count or 0) - tokens_input
                
                # Fallback: estimate tokens if not available
                if tokens_input == 0:
                    tokens_input = len(prompt) // 4
                    if system_prompt:
                        tokens_input += len(system_prompt) // 4
                if tokens_output == 0:
                    tokens_output = len(content_text) // 4 if content_text else 0
                
                return {
                    "content": content_text,
                    "tokens_input": tokens_input,
                    "tokens_output": tokens_output,
                }
            except Exception as e:
                logger.error(f"Error with new Gemini SDK: {e}")
                # Fallback to old SDK if new one fails
                logger.info("Falling back to old SDK...")
                # Try to re-initialize with old SDK
                try:
                    import google.generativeai as genai_old
                    api_key = self.models[f"gemini_{model}"].api_key
                    genai_old.configure(api_key=api_key)
                    genai_client = genai_old
                    use_new_sdk = False
                except Exception as fallback_error:
                    logger.error(f"Fallback to old SDK also failed: {fallback_error}")
                    raise e
        
        # Old SDK implementation (fallback or if new SDK not available)
        if not use_new_sdk:
            # Old google-generativeai SDK (fallback)
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Create model instance
            model_instance = genai_client.GenerativeModel(model)
            
            # Generate content
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            generation_config.update(kwargs)
            
            response = model_instance.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Estimate tokens (Gemini doesn't always return token counts)
            # Rough estimate: 1 token ≈ 4 characters
            estimated_input_tokens = len(full_prompt) // 4
            estimated_output_tokens = len(response.text) // 4 if response.text else 0
            
            return {
                "content": response.text if response.text else "",
                "tokens_input": estimated_input_tokens,
                "tokens_output": estimated_output_tokens,
            }
    
    def _generate_grok(
        self, prompt: str, system_prompt: Optional[str], model: str,
        temperature: float, max_tokens: int,
        client_request_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate using Grok (xAI) - OpenAI-compatible API with request tracking"""
        client = self.clients["grok"]
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Prepare extra headers
        extra_headers = {}
        if client_request_id:
            extra_headers["X-Client-Request-Id"] = client_request_id
        
        response_headers = {}
        try:
            # Try with extra_headers
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_headers=extra_headers,
                    **kwargs
                )
            except TypeError:
                # Fallback without extra_headers
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            
            # Try to extract headers
            if hasattr(response, '_response') and hasattr(response._response, 'headers'):
                response_headers = dict(response._response.headers)
            elif hasattr(response, 'headers'):
                response_headers = dict(response.headers)
        except Exception as e:
            structured_logger.warning(f"Could not capture Grok response headers: {e}")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        
        return {
            "content": response.choices[0].message.content,
            "tokens_input": response.usage.prompt_tokens,
            "tokens_output": response.usage.completion_tokens,
            "response_headers": response_headers,
        }
    
    def _update_usage_stats(
        self, model_id: str, tokens_input: int, tokens_output: int,
        cost: float, response_time: float
    ):
        """Update usage statistics"""
        if model_id not in self.usage_stats:
            config = self.models[model_id]
            self.usage_stats[model_id] = UsageStats(
                provider=config.provider.value,
                model=config.model_name,
            )
        
        stats = self.usage_stats[model_id]
        stats.tokens_input += tokens_input
        stats.tokens_output += tokens_output
        stats.requests += 1
        stats.total_cost += cost
        stats.last_used = datetime.now()
        
        # Update average response time
        if stats.requests > 0:
            stats.avg_response_time = (
                (stats.avg_response_time * (stats.requests - 1) + response_time) / stats.requests
            )
    
    def _load_usage_stats(self):
        """Load usage statistics from file"""
        stats_file = "model_usage_stats.json"
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    data = json.load(f)
                    for model_id, stats_data in data.items():
                        self.usage_stats[model_id] = UsageStats(**stats_data)
            except Exception as e:
                logger.error(f"Error loading usage stats: {e}")
    
    def save_usage_stats(self):
        """Save usage statistics to file"""
        stats_file = "model_usage_stats.json"
        try:
            data = {
                model_id: asdict(stats)
                for model_id, stats in self.usage_stats.items()
            }
            with open(stats_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving usage stats: {e}")
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get summary of usage statistics"""
        total_cost = sum(stats.total_cost for stats in self.usage_stats.values())
        total_requests = sum(stats.requests for stats in self.usage_stats.values())
        total_tokens = sum(
            stats.tokens_input + stats.tokens_output 
            for stats in self.usage_stats.values()
        )
        
        return {
            "total_cost": total_cost,
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "by_model": {
                model_id: asdict(stats)
                for model_id, stats in self.usage_stats.items()
            },
        }
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models with their configurations"""
        return [
            {
                "model_id": model_id,
                "provider": config.provider.value,
                "model_name": config.model_name,
                "enabled": config.enabled,
                "cost_input_per_1k": config.cost_per_1k_tokens_input,
                "cost_output_per_1k": config.cost_per_1k_tokens_output,
                "speed_rating": config.speed_rating,
                "quality_rating": config.quality_rating,
            }
            for model_id, config in self.models.items()
        ]


# Global instance
_integrator_instance: Optional[UnifiedModelIntegrator] = None


def get_model_integrator(config_file: Optional[str] = None) -> UnifiedModelIntegrator:
    """Get or create the global model integrator instance"""
    global _integrator_instance
    if _integrator_instance is None:
        _integrator_instance = UnifiedModelIntegrator(config_file)
    return _integrator_instance

