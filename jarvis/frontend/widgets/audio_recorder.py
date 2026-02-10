"""
Audio Recorder Widget - Records audio from microphone
"""
import io
import wave
import threading
from typing import Optional


class AudioRecorder:
    """Records audio from the microphone"""

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = 1024
        self._is_recording = False
        self._audio_frames = []
        self._stream = None
        self._pyaudio = None
        self._record_thread: Optional[threading.Thread] = None

    @property
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self._is_recording

    def start_recording(self):
        """Start recording audio"""
        if self._is_recording:
            return

        try:
            import pyaudio

            self._pyaudio = pyaudio.PyAudio()
            self._stream = self._pyaudio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            self._is_recording = True
            self._audio_frames = []

            # Start recording in separate thread
            self._record_thread = threading.Thread(target=self._record_loop)
            self._record_thread.daemon = True
            self._record_thread.start()

            print("🎤 Recording started...")

        except Exception as e:
            print(f"Failed to start recording: {e}")
            self._cleanup()

    def _record_loop(self):
        """Recording loop running in separate thread"""
        while self._is_recording:
            try:
                data = self._stream.read(self.chunk_size, exception_on_overflow=False)
                self._audio_frames.append(data)
            except Exception as e:
                print(f"Recording error: {e}")
                break

    def stop_recording(self) -> Optional[bytes]:
        """Stop recording and return audio data as WAV bytes"""
        if not self._is_recording:
            return None

        self._is_recording = False

        # Wait for recording thread to finish
        if self._record_thread:
            self._record_thread.join(timeout=1.0)

        print("🎤 Recording stopped.")

        # Get recorded data
        audio_data = self._get_wav_data()

        # Cleanup
        self._cleanup()

        return audio_data

    def _get_wav_data(self) -> Optional[bytes]:
        """Convert recorded frames to WAV format"""
        if not self._audio_frames:
            return None

        try:
            import pyaudio

            # Create WAV in memory
            buffer = io.BytesIO()
            with wave.open(buffer, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self._pyaudio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b"".join(self._audio_frames))

            return buffer.getvalue()

        except Exception as e:
            print(f"Error creating WAV: {e}")
            return None

    def _cleanup(self):
        """Cleanup audio resources"""
        try:
            if self._stream:
                self._stream.stop_stream()
                self._stream.close()
                self._stream = None

            if self._pyaudio:
                self._pyaudio.terminate()
                self._pyaudio = None

        except Exception as e:
            print(f"Cleanup error: {e}")

        self._audio_frames = []
