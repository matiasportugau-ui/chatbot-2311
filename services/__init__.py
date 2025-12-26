"""
Audio Transcription Services
"""

from .audio_transcription import (
    AudioTranscriptionService,
    TranscriptionConfig,
    TranscriptionModel,
    TranscriptionResult,
    ResponseFormat,
    ChunkingStrategy,
    create_audio_transcription_service
)

from .audio_config_loader import (
    AudioConfigLoader,
    AudioConfig,
    WhatsAppAudioConfig,
    load_audio_config,
    load_whatsapp_config,
    get_config_loader
)

try:
    from .whatsapp_audio_handler import (
        WhatsAppAudioHandler,
        WhatsAppAudioIntegration,
        WhatsAppAudioMessage,
        create_whatsapp_audio_integration
    )
except ImportError:
    # WhatsApp modules may not be available
    pass

__all__ = [
    # Audio Transcription
    'AudioTranscriptionService',
    'TranscriptionConfig',
    'TranscriptionModel',
    'TranscriptionResult',
    'ResponseFormat',
    'ChunkingStrategy',
    'create_audio_transcription_service',
    
    # Configuration
    'AudioConfigLoader',
    'AudioConfig',
    'WhatsAppAudioConfig',
    'load_audio_config',
    'load_whatsapp_config',
    'get_config_loader',
    
    # WhatsApp
    'WhatsAppAudioHandler',
    'WhatsAppAudioIntegration',
    'WhatsAppAudioMessage',
    'create_whatsapp_audio_integration',
]
