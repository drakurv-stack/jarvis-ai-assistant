"""
Speech-to-Text Service using faster-whisper
"""
import asyncio
from pathlib import Path
from typing import Optional


class STTService:
    """
    Speech-to-Text service using faster-whisper for multilingual transcription.
    Runs in a thread pool to avoid blocking the event loop.
    """

    def __init__(self, model_size: str = "base"):
        """
        Initialize the STT service.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large-v2)
        """
        self.model_size = model_size
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the faster-whisper model"""
        try:
            from faster_whisper import WhisperModel

            # Use CPU with int8 for broader compatibility
            # Change to "cuda" and "float16" for GPU
            self.model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8"
            )
            print(f"✅ Whisper model '{self.model_size}' loaded successfully")
        except Exception as e:
            print(f"⚠️ Failed to load Whisper model: {e}")
            print("   STT will use fallback mode (no transcription)")
            self.model = None

    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to the audio file
            language: Optional language code (e.g., 'en', 'es', 'fr')
                     If None, auto-detects language

        Returns:
            Transcribed text
        """
        if not self.model:
            return "[STT not available - please install faster-whisper]"

        if not Path(audio_path).exists():
            return "[Audio file not found]"

        # Run transcription in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._transcribe_sync,
            audio_path,
            language
        )
        return result

    def _transcribe_sync(self, audio_path: str, language: Optional[str]) -> str:
        """Synchronous transcription method"""
        try:
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                vad_filter=True,  # Filter out silence
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            # Combine all segments
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())

            full_text = " ".join(text_parts)

            # Log detected language
            if not language:
                print(f"🎤 Detected language: {info.language} (prob: {info.language_probability:.2f})")

            return full_text if full_text else "[No speech detected]"

        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return f"[Transcription failed: {str(e)}]"
