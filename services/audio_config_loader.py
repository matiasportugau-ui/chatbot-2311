#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Configuration Loader
Loads and validates audio processing configuration
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Audio processing configuration"""
    enabled: bool = True
    default_model: str = "gpt-4o-mini-transcribe"
    temperature: float = 0.0
    language: Optional[str] = None
    enable_prompts: bool = True
    default_prompt: Optional[str] = None
    enable_streaming: bool = False
    cleanup_after_hours: int = 24
    max_concurrent_transcriptions: int = 5
    request_timeout_seconds: int = 30


@dataclass
class WhatsAppAudioConfig:
    """WhatsApp audio configuration"""
    enabled: bool = True
    auto_transcribe: bool = True
    auto_reply: bool = True
    reply_prefix: str = "🎤 Mensaje de voz recibido:"
    model_preference: str = "gpt-4o-mini-transcribe"
    cleanup_after_transcription: bool = True


class AudioConfigLoader:
    """Loads audio processing configuration"""
    
    DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config" / "audio_config.json"
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config loader
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config = None
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file
        
        Returns:
            Configuration dictionary
        """
        if self._config is not None:
            return self._config
        
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            
            logger.info(f"Loaded audio configuration from {self.config_path}")
            return self._config
        
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "audio_transcription": {
                "enabled": True,
                "default_model": "gpt-4o-mini-transcribe",
                "whatsapp": {
                    "enabled": True,
                    "auto_transcribe": True,
                    "auto_reply": True,
                    "model_preference": "gpt-4o-mini-transcribe"
                },
                "processing": {
                    "temperature": 0.0,
                    "language": None,
                    "enable_prompts": True
                }
            }
        }
    
    def get_audio_config(self) -> AudioConfig:
        """
        Get audio processing configuration
        
        Returns:
            AudioConfig instance
        """
        config = self.load()
        audio_config = config.get("audio_transcription", {})
        processing = audio_config.get("processing", {})
        storage = audio_config.get("storage", {})
        performance = audio_config.get("performance", {})
        
        return AudioConfig(
            enabled=audio_config.get("enabled", True),
            default_model=audio_config.get("default_model", "gpt-4o-mini-transcribe"),
            temperature=processing.get("temperature", 0.0),
            language=processing.get("language"),
            enable_prompts=processing.get("enable_prompts", True),
            default_prompt=processing.get("default_prompt"),
            enable_streaming=processing.get("enable_streaming", False),
            cleanup_after_hours=storage.get("cleanup_after_hours", 24),
            max_concurrent_transcriptions=performance.get("max_concurrent_transcriptions", 5),
            request_timeout_seconds=performance.get("request_timeout_seconds", 30)
        )
    
    def get_whatsapp_config(self) -> WhatsAppAudioConfig:
        """
        Get WhatsApp audio configuration
        
        Returns:
            WhatsAppAudioConfig instance
        """
        config = self.load()
        whatsapp = config.get("audio_transcription", {}).get("whatsapp", {})
        
        return WhatsAppAudioConfig(
            enabled=whatsapp.get("enabled", True),
            auto_transcribe=whatsapp.get("auto_transcribe", True),
            auto_reply=whatsapp.get("auto_reply", True),
            reply_prefix=whatsapp.get("reply_prefix", "🎤 Mensaje de voz recibido:"),
            model_preference=whatsapp.get("model_preference", "gpt-4o-mini-transcribe"),
            cleanup_after_transcription=whatsapp.get("cleanup_after_transcription", True)
        )
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information dictionary or None
        """
        config = self.load()
        models = config.get("audio_transcription", {}).get("models", {})
        return models.get(model_name)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled
        
        Args:
            feature: Feature name (e.g., "diarization", "translation")
            
        Returns:
            True if enabled
        """
        config = self.load()
        return config.get(feature, {}).get("enabled", False)


# Global config loader instance
_config_loader = None


def get_config_loader() -> AudioConfigLoader:
    """Get global config loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = AudioConfigLoader()
    return _config_loader


def load_audio_config() -> AudioConfig:
    """Load audio configuration"""
    return get_config_loader().get_audio_config()


def load_whatsapp_config() -> WhatsAppAudioConfig:
    """Load WhatsApp audio configuration"""
    return get_config_loader().get_whatsapp_config()


if __name__ == "__main__":
    print("Audio Configuration Loader")
    print("=" * 50)
    
    loader = AudioConfigLoader()
    
    # Load and display config
    audio_config = loader.get_audio_config()
    print(f"\n✅ Audio Config:")
    print(f"   Enabled: {audio_config.enabled}")
    print(f"   Default Model: {audio_config.default_model}")
    print(f"   Temperature: {audio_config.temperature}")
    
    whatsapp_config = loader.get_whatsapp_config()
    print(f"\n✅ WhatsApp Config:")
    print(f"   Enabled: {whatsapp_config.enabled}")
    print(f"   Auto Transcribe: {whatsapp_config.auto_transcribe}")
    print(f"   Model: {whatsapp_config.model_preference}")
