"""
Text-to-Speech Service using edge-tts
"""
import asyncio
import tempfile
import os
from pathlib import Path
from typing import Optional


class TTSService:
    """
    Text-to-Speech service using edge-tts for natural voices.
    Microsoft Edge TTS provides high-quality, free voices.
    """

    # Popular voice options
    VOICES = {
        # English
        "en-male": "en-US-GuyNeural",
        "en-female": "en-US-JennyNeural",
        "en-uk-male": "en-GB-RyanNeural",
        "en-uk-female": "en-GB-SoniaNeural",

        # Other languages
        "es-male": "es-ES-AlvaroNeural",
        "es-female": "es-ES-ElviraNeural",
        "fr-male": "fr-FR-HenriNeural",
        "fr-female": "fr-FR-DeniseNeural",
        "de-male": "de-DE-ConradNeural",
        "de-female": "de-DE-KatjaNeural",
        "zh-male": "zh-CN-YunxiNeural",
        "zh-female": "zh-CN-XiaoxiaoNeural",
        "ja-male": "ja-JP-KeitaNeural",
        "ja-female": "ja-JP-NanamiNeural",
    }

    def __init__(self, voice: str = "en-male", rate: str = "+0%", pitch: str = "+0Hz"):
        """
        Initialize TTS service.

        Args:
            voice: Voice preset key or full voice name
            rate: Speech rate adjustment (e.g., "+10%", "-20%")
            pitch: Pitch adjustment (e.g., "+5Hz", "-10Hz")
        """
        self.voice = self.VOICES.get(voice, voice)
        self.rate = rate
        self.pitch = pitch
        self._edge_tts_available = self._check_edge_tts()

    def _check_edge_tts(self) -> bool:
        """Check if edge-tts is available"""
        try:
            import edge_tts
            return True
        except ImportError:
            print("⚠️ edge-tts not installed. TTS will be disabled.")
            return False

    async def synthesize(self, text: str, voice: Optional[str] = None) -> Optional[bytes]:
        """
        Synthesize text to speech audio.

        Args:
            text: Text to convert to speech
            voice: Optional voice override

        Returns:
            Audio data as bytes (MP3 format), or None if failed
        """
        if not self._edge_tts_available:
            return None

        if not text or not text.strip():
            return None

        # Clean up text for better TTS
        text = self._preprocess_text(text)

        voice_to_use = self.VOICES.get(voice, voice) if voice else self.voice

        try:
            import edge_tts

            # Create communicate object
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice_to_use,
                rate=self.rate,
                pitch=self.pitch
            )

            # Collect audio data
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            return audio_data if audio_data else None

        except Exception as e:
            print(f"❌ TTS synthesis error: {e}")
            return None

    async def synthesize_to_file(self, text: str, output_path: str, voice: Optional[str] = None) -> bool:
        """
        Synthesize text to speech and save to file.

        Args:
            text: Text to convert
            output_path: Path to save the audio file
            voice: Optional voice override

        Returns:
            True if successful, False otherwise
        """
        audio_data = await self.synthesize(text, voice)
        if audio_data:
            with open(output_path, "wb") as f:
                f.write(audio_data)
            return True
        return False

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better TTS output"""
        # Remove markdown formatting
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)  # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)  # Code
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Links

        # Limit length to avoid timeout
        if len(text) > 2000:
            text = text[:2000] + "..."

        return text.strip()

    @classmethod
    async def list_voices(cls) -> list:
        """List all available voices"""
        try:
            import edge_tts
            voices = await edge_tts.list_voices()
            return voices
        except:
            return []
