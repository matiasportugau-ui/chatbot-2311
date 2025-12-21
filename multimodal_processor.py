#!/usr/bin/env python3
"""
Multimodal Input Processor
Handles Audio (Whisper), Images (Vision), and Documents for the BMC chatbot
"""

import base64
import io
import json
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠️ Pillow not available - image processing disabled")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI not available - multimodal processing disabled")

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("⚠️ PyPDF2 not available - PDF processing disabled")


@dataclass
class MultimodalInput:
    """Unified multimodal input object"""
    input_type: str  # "text", "audio", "image", "document"
    content: str  # Processed text content
    original_data: Any  # Original binary/file data
    metadata: dict[str, Any]
    confidence: float
    processing_timestamp: str


class MultimodalProcessor:
    """Processes multimodal inputs and converts them to unified context"""
    
    def __init__(self):
        self.openai_client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                print("✅ OpenAI client initialized for multimodal processing")
            else:
                print("⚠️ OPENAI_API_KEY not set - multimodal processing limited")
        
        self.supported_image_formats = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        self.supported_audio_formats = [".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"]
        self.supported_document_formats = [".pdf", ".txt"]
    
    def process_input(self, input_data: Any, input_type: str = "auto") -> MultimodalInput:
        """
        Process any input type and return unified multimodal input
        
        Args:
            input_data: Can be text, bytes, file path, or base64 string
            input_type: "auto", "text", "audio", "image", "document"
        
        Returns:
            MultimodalInput object with processed content
        """
        from datetime import datetime
        
        # Auto-detect input type if needed
        if input_type == "auto":
            input_type = self._detect_input_type(input_data)
        
        # Process based on type
        if input_type == "text":
            return self._process_text(input_data)
        elif input_type == "audio":
            return self._process_audio(input_data)
        elif input_type == "image":
            return self._process_image(input_data)
        elif input_type == "document":
            return self._process_document(input_data)
        else:
            raise ValueError(f"Unsupported input type: {input_type}")
    
    def _detect_input_type(self, input_data: Any) -> str:
        """Auto-detect input type from data"""
        if isinstance(input_data, str):
            # Check if it's a file path
            if os.path.exists(input_data):
                ext = Path(input_data).suffix.lower()
                if ext in self.supported_audio_formats:
                    return "audio"
                elif ext in self.supported_image_formats:
                    return "image"
                elif ext in self.supported_document_formats:
                    return "document"
            return "text"
        elif isinstance(input_data, bytes):
            # Try to detect from magic bytes
            if input_data.startswith(b'\xff\xd8'):  # JPEG
                return "image"
            elif input_data.startswith(b'\x89PNG'):  # PNG
                return "image"
            elif input_data.startswith(b'%PDF'):  # PDF
                return "document"
            elif input_data.startswith(b'ID3') or input_data.startswith(b'\xff\xfb'):  # MP3
                return "audio"
            else:
                return "document"  # Default for unknown binary
        else:
            return "text"
    
    def _process_text(self, text: str) -> MultimodalInput:
        """Process text input"""
        from datetime import datetime
        
        return MultimodalInput(
            input_type="text",
            content=text,
            original_data=text,
            metadata={"length": len(text)},
            confidence=1.0,
            processing_timestamp=datetime.now().isoformat()
        )
    
    def _process_audio(self, audio_data: Any) -> MultimodalInput:
        """
        Process audio input using Whisper
        
        Args:
            audio_data: Can be file path, bytes, or file-like object
        """
        from datetime import datetime
        
        if not OPENAI_AVAILABLE or not self.openai_client:
            return MultimodalInput(
                input_type="audio",
                content="[Audio transcription not available - OpenAI not configured]",
                original_data=audio_data,
                metadata={"error": "OpenAI not configured"},
                confidence=0.0,
                processing_timestamp=datetime.now().isoformat()
            )
        
        try:
            # Handle different audio input formats
            if isinstance(audio_data, str) and os.path.exists(audio_data):
                # File path
                with open(audio_data, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="es"  # Spanish for BMC Uruguay
                    )
            elif isinstance(audio_data, bytes):
                # Bytes data
                audio_file = io.BytesIO(audio_data)
                audio_file.name = "audio.mp3"  # Required by OpenAI
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es"
                )
            else:
                raise ValueError("Unsupported audio data format")
            
            return MultimodalInput(
                input_type="audio",
                content=transcript.text,
                original_data=audio_data,
                metadata={
                    "transcription_model": "whisper-1",
                    "language": "es"
                },
                confidence=0.95,  # Whisper is highly accurate
                processing_timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            print(f"❌ Error transcribing audio: {e}")
            return MultimodalInput(
                input_type="audio",
                content=f"[Error transcribing audio: {str(e)}]",
                original_data=audio_data,
                metadata={"error": str(e)},
                confidence=0.0,
                processing_timestamp=datetime.now().isoformat()
            )
    
    def _process_image(self, image_data: Any) -> MultimodalInput:
        """
        Process image input using GPT-4o Vision
        
        Args:
            image_data: Can be file path, bytes, PIL Image, or base64 string
        """
        from datetime import datetime
        
        if not OPENAI_AVAILABLE or not self.openai_client:
            return MultimodalInput(
                input_type="image",
                content="[Image analysis not available - OpenAI not configured]",
                original_data=image_data,
                metadata={"error": "OpenAI not configured"},
                confidence=0.0,
                processing_timestamp=datetime.now().isoformat()
            )
        
        try:
            # Convert image to base64
            if isinstance(image_data, str) and os.path.exists(image_data):
                # File path
                with open(image_data, "rb") as img_file:
                    image_bytes = img_file.read()
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                    mime_type = mimetypes.guess_type(image_data)[0] or "image/jpeg"
            elif isinstance(image_data, bytes):
                # Bytes data
                base64_image = base64.b64encode(image_data).decode('utf-8')
                mime_type = "image/jpeg"
            elif PILLOW_AVAILABLE and isinstance(image_data, Image.Image):
                # PIL Image
                buffer = io.BytesIO()
                image_data.save(buffer, format="PNG")
                base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
                mime_type = "image/png"
            else:
                # Assume it's already base64
                base64_image = image_data if isinstance(image_data, str) else str(image_data)
                mime_type = "image/jpeg"
            
            # Use GPT-4o Vision to analyze the image
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analiza esta imagen y describe qué productos, especificaciones técnicas, o información relevante para una empresa de construcción (BMC Uruguay) puedes identificar. Si es una foto de un producto, describe sus características. Si es un documento técnico, extrae la información clave."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            analysis = response.choices[0].message.content
            
            return MultimodalInput(
                input_type="image",
                content=analysis,
                original_data=image_data,
                metadata={
                    "analysis_model": "gpt-4o",
                    "mime_type": mime_type
                },
                confidence=0.85,
                processing_timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            print(f"❌ Error analyzing image: {e}")
            return MultimodalInput(
                input_type="image",
                content=f"[Error analyzing image: {str(e)}]",
                original_data=image_data,
                metadata={"error": str(e)},
                confidence=0.0,
                processing_timestamp=datetime.now().isoformat()
            )
    
    def _process_document(self, doc_data: Any) -> MultimodalInput:
        """
        Process document input (PDF, TXT)
        
        Args:
            doc_data: Can be file path or bytes
        """
        from datetime import datetime
        
        try:
            content = ""
            
            if isinstance(doc_data, str) and os.path.exists(doc_data):
                # File path
                ext = Path(doc_data).suffix.lower()
                
                if ext == ".pdf":
                    if not PYPDF2_AVAILABLE:
                        content = "[PDF processing not available - PyPDF2 not installed]"
                    else:
                        with open(doc_data, "rb") as pdf_file:
                            pdf_reader = PyPDF2.PdfReader(pdf_file)
                            content = "\n".join([page.extract_text() for page in pdf_reader.pages])
                elif ext == ".txt":
                    with open(doc_data, "r", encoding="utf-8") as txt_file:
                        content = txt_file.read()
                else:
                    content = f"[Unsupported document format: {ext}]"
            
            elif isinstance(doc_data, bytes):
                # Try to decode as text first
                try:
                    content = doc_data.decode("utf-8")
                except UnicodeDecodeError:
                    # Try PDF
                    if PYPDF2_AVAILABLE:
                        try:
                            pdf_file = io.BytesIO(doc_data)
                            pdf_reader = PyPDF2.PdfReader(pdf_file)
                            content = "\n".join([page.extract_text() for page in pdf_reader.pages])
                        except Exception:
                            content = "[Could not parse document]"
                    else:
                        content = "[Document processing not available]"
            
            return MultimodalInput(
                input_type="document",
                content=content,
                original_data=doc_data,
                metadata={"length": len(content)},
                confidence=0.9,
                processing_timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            print(f"❌ Error processing document: {e}")
            return MultimodalInput(
                input_type="document",
                content=f"[Error processing document: {str(e)}]",
                original_data=doc_data,
                metadata={"error": str(e)},
                confidence=0.0,
                processing_timestamp=datetime.now().isoformat()
            )


def main():
    """Test multimodal processor"""
    processor = MultimodalProcessor()
    
    # Test text processing
    print("\n=== Testing Text Processing ===")
    text_input = processor.process_input("¿Cuál es el precio del Isodec?", "text")
    print(f"Type: {text_input.input_type}")
    print(f"Content: {text_input.content}")
    print(f"Confidence: {text_input.confidence}")
    
    print("\n✅ Multimodal processor basic test completed")


if __name__ == "__main__":
    main()
