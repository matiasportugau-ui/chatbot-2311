#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Audio Message Handler
Handles audio messages from WhatsApp and integrates with transcription service
"""

import os
import logging
import requests
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

from services.audio_transcription import (
    AudioTranscriptionService,
    TranscriptionConfig,
    TranscriptionModel,
    ResponseFormat,
    TranscriptionResult
)
from utils.audio_utils import AudioFileManager

logger = logging.getLogger(__name__)


@dataclass
class WhatsAppAudioMessage:
    """WhatsApp audio message data"""
    message_id: str
    from_number: str
    audio_id: str
    mime_type: str
    sha256: str
    file_size: Optional[int] = None
    voice: bool = False  # True for voice messages, False for audio files


class WhatsAppAudioHandler:
    """Handles audio messages from WhatsApp"""
    
    def __init__(
        self,
        transcription_service: AudioTranscriptionService,
        whatsapp_token: str,
        phone_id: str
    ):
        """
        Initialize WhatsApp audio handler
        
        Args:
            transcription_service: Audio transcription service
            whatsapp_token: WhatsApp Business API token
            phone_id: WhatsApp phone number ID
        """
        self.transcription_service = transcription_service
        self.whatsapp_token = whatsapp_token
        self.phone_id = phone_id
        self.file_manager = AudioFileManager()
        
        # WhatsApp API URLs
        self.base_url = f"https://graph.facebook.com/v18.0"
        self.media_url = f"{self.base_url}/{{media_id}}"
        
        logger.info("WhatsApp audio handler initialized")
    
    def extract_audio_message(self, message: Dict[str, Any]) -> Optional[WhatsAppAudioMessage]:
        """
        Extract audio message data from WhatsApp message
        
        Args:
            message: WhatsApp message dictionary
            
        Returns:
            WhatsAppAudioMessage if audio message, None otherwise
        """
        message_type = message.get('type')
        
        if message_type == 'audio':
            audio_data = message['audio']
            return WhatsAppAudioMessage(
                message_id=message['id'],
                from_number=message['from'],
                audio_id=audio_data['id'],
                mime_type=audio_data['mime_type'],
                sha256=audio_data.get('sha256', ''),
                file_size=audio_data.get('file_size'),
                voice=False
            )
        
        elif message_type == 'voice':
            voice_data = message['voice']
            return WhatsAppAudioMessage(
                message_id=message['id'],
                from_number=message['from'],
                audio_id=voice_data['id'],
                mime_type=voice_data['mime_type'],
                sha256=voice_data.get('sha256', ''),
                file_size=voice_data.get('file_size'),
                voice=True
            )
        
        return None
    
    def download_audio(self, audio_message: WhatsAppAudioMessage) -> Path:
        """
        Download audio file from WhatsApp
        
        Args:
            audio_message: WhatsApp audio message data
            
        Returns:
            Path to downloaded audio file
        """
        try:
            # Step 1: Get media URL
            media_info_url = self.media_url.format(media_id=audio_message.audio_id)
            headers = {'Authorization': f'Bearer {self.whatsapp_token}'}
            
            logger.info(f"Fetching media info for: {audio_message.audio_id}")
            response = requests.get(media_info_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            media_info = response.json()
            download_url = media_info['url']
            
            # Step 2: Download audio file
            logger.info(f"Downloading audio from WhatsApp")
            audio_response = requests.get(download_url, headers=headers, timeout=30)
            audio_response.raise_for_status()
            
            # Determine file format from MIME type
            mime_to_ext = {
                'audio/ogg': 'ogg',
                'audio/mpeg': 'mp3',
                'audio/mp4': 'm4a',
                'audio/amr': 'amr',
                'audio/opus': 'opus',
            }
            file_format = mime_to_ext.get(audio_message.mime_type, 'mp3')
            
            # Save audio file
            filename = f"whatsapp_{audio_message.message_id}.{file_format}"
            audio_path = self.file_manager.save_audio_from_bytes(
                audio_response.content,
                file_format,
                filename
            )
            
            logger.info(f"Audio downloaded: {audio_path}")
            return audio_path
        
        except Exception as e:
            logger.error(f"Error downloading audio from WhatsApp: {e}")
            raise
    
    def convert_audio_if_needed(self, audio_path: Path) -> Path:
        """
        Convert audio to supported format if needed
        
        Note: WhatsApp voice messages are often in OGG/Opus format which
        OpenAI API supports. If conversion is needed, this method can be
        extended to use ffmpeg or similar tools.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Path to converted file (or original if no conversion needed)
        """
        # Check if format is supported
        file_format = audio_path.suffix.lower().lstrip('.')
        
        if file_format in AudioTranscriptionService.SUPPORTED_FORMATS:
            return audio_path
        
        # If not supported, would need conversion here
        # For now, log warning and return original
        logger.warning(
            f"Audio format '{file_format}' may not be supported. "
            "Consider implementing conversion using ffmpeg."
        )
        return audio_path
    
    def transcribe_audio_message(
        self,
        audio_message: WhatsAppAudioMessage,
        config: Optional[TranscriptionConfig] = None,
        cleanup: bool = True
    ) -> TranscriptionResult:
        """
        Download and transcribe audio message from WhatsApp
        
        Args:
            audio_message: WhatsApp audio message data
            config: Transcription configuration
            cleanup: Whether to delete audio file after transcription
            
        Returns:
            TranscriptionResult with transcribed text
        """
        if config is None:
            # Default config for WhatsApp voice messages
            config = TranscriptionConfig(
                model=TranscriptionModel.GPT4O_MINI_TRANSCRIBE,
                response_format=ResponseFormat.TEXT
            )
        
        audio_path = None
        
        try:
            # Download audio
            audio_path = self.download_audio(audio_message)
            
            # Convert if needed
            audio_path = self.convert_audio_if_needed(audio_path)
            
            # Transcribe
            logger.info(f"Transcribing audio message: {audio_message.message_id}")
            result = self.transcription_service.transcribe(audio_path, config)
            
            logger.info(f"Transcription complete: {len(result.text)} characters")
            return result
        
        except Exception as e:
            logger.error(f"Error transcribing audio message: {e}")
            raise
        
        finally:
            # Cleanup if requested
            if cleanup and audio_path and audio_path.exists():
                self.file_manager.delete_file(audio_path)
    
    def process_audio_message(
        self,
        message: Dict[str, Any],
        config: Optional[TranscriptionConfig] = None
    ) -> Optional[TranscriptionResult]:
        """
        Process audio message from WhatsApp webhook
        
        Args:
            message: WhatsApp message dictionary
            config: Transcription configuration
            
        Returns:
            TranscriptionResult if audio message, None otherwise
        """
        # Extract audio message data
        audio_message = self.extract_audio_message(message)
        
        if not audio_message:
            return None
        
        logger.info(
            f"Processing {'voice' if audio_message.voice else 'audio'} message "
            f"from {audio_message.from_number}"
        )
        
        # Transcribe audio
        return self.transcribe_audio_message(audio_message, config)


class WhatsAppAudioIntegration:
    """Integration layer for WhatsApp audio messages"""
    
    def __init__(
        self,
        transcription_service: AudioTranscriptionService,
        whatsapp_token: str,
        phone_id: str,
        auto_reply: bool = True
    ):
        """
        Initialize WhatsApp audio integration
        
        Args:
            transcription_service: Audio transcription service
            whatsapp_token: WhatsApp Business API token
            phone_id: WhatsApp phone number ID
            auto_reply: Whether to automatically reply with transcription
        """
        self.audio_handler = WhatsAppAudioHandler(
            transcription_service,
            whatsapp_token,
            phone_id
        )
        self.whatsapp_token = whatsapp_token
        self.phone_id = phone_id
        self.auto_reply = auto_reply
        
        self.messages_url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    
    def send_reply(self, to_number: str, text: str):
        """
        Send reply message via WhatsApp
        
        Args:
            to_number: Recipient phone number
            text: Message text
        """
        headers = {
            'Authorization': f'Bearer {self.whatsapp_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": text}
        }
        
        try:
            response = requests.post(
                self.messages_url,
                headers=headers,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Reply sent to {to_number}")
        except Exception as e:
            logger.error(f"Error sending reply: {e}")
    
    def handle_webhook_message(
        self,
        message: Dict[str, Any],
        custom_handler: Optional[callable] = None
    ) -> Optional[str]:
        """
        Handle incoming WhatsApp message from webhook
        
        Args:
            message: WhatsApp message dictionary
            custom_handler: Optional custom function to process transcription
            
        Returns:
            Transcribed text if audio message, None otherwise
        """
        # Process audio message
        result = self.audio_handler.process_audio_message(message)
        
        if not result:
            return None
        
        transcribed_text = result.text
        from_number = message['from']
        
        logger.info(f"Transcribed audio from {from_number}: {transcribed_text[:100]}...")
        
        # Custom processing if handler provided
        if custom_handler:
            try:
                custom_handler(from_number, transcribed_text, message)
            except Exception as e:
                logger.error(f"Error in custom handler: {e}")
        
        # Auto-reply if enabled
        if self.auto_reply:
            reply_text = f"🎤 Mensaje de voz recibido:\n\n{transcribed_text}"
            self.send_reply(from_number, reply_text)
        
        return transcribed_text


def create_whatsapp_audio_integration(
    whatsapp_token: Optional[str] = None,
    phone_id: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    auto_reply: bool = True
) -> WhatsAppAudioIntegration:
    """
    Factory function to create WhatsApp audio integration
    
    Args:
        whatsapp_token: WhatsApp Business API token
        phone_id: WhatsApp phone number ID
        openai_api_key: OpenAI API key
        auto_reply: Whether to auto-reply with transcriptions
        
    Returns:
        WhatsAppAudioIntegration instance
    """
    # Get tokens from environment if not provided
    whatsapp_token = whatsapp_token or os.getenv("WHATSAPP_TOKEN")
    phone_id = phone_id or os.getenv("WHATSAPP_PHONE_ID")
    openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    
    if not whatsapp_token or not phone_id:
        raise ValueError("WhatsApp credentials required")
    
    if not openai_api_key:
        raise ValueError("OpenAI API key required")
    
    # Create transcription service
    transcription_service = AudioTranscriptionService(api_key=openai_api_key)
    
    # Create integration
    return WhatsAppAudioIntegration(
        transcription_service,
        whatsapp_token,
        phone_id,
        auto_reply
    )


if __name__ == "__main__":
    print("WhatsApp Audio Message Handler")
    print("=" * 50)
    print("This module handles audio messages from WhatsApp")
    print("and transcribes them using OpenAI's API")
