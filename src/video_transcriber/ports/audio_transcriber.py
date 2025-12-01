"""Audio transcription port (protocol)."""

from typing import Protocol
from video_transcriber.domain.models import AudioSegment


class AudioTranscriptionError(Exception):
    """Raised when audio transcription fails."""
    pass


class AudioTranscriber(Protocol):
    """Port for transcribing audio to text with timestamps.

    Implementations should use speech recognition models
    (e.g., Whisper) to convert audio to text segments.
    """

    def transcribe_audio(self, audio_path: str) -> list[AudioSegment]:
        """Transcribe audio file to text with timestamps.

        Args:
            audio_path: Path to audio file (typically WAV format)

        Returns:
            List of AudioSegment objects with timestamps and transcribed text

        Raises:
            AudioTranscriptionError: If transcription fails
        """
        ...
