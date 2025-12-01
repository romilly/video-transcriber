"""Audio extraction port (protocol)."""

from typing import Protocol


class AudioExtractionError(Exception):
    """Raised when audio extraction from video fails."""
    pass


class AudioExtractor(Protocol):
    """Port for extracting audio from video files.

    Implementations should extract audio in a format suitable for
    speech recognition (typically WAV, 16kHz, mono).
    """

    def extract_audio(self, video_path: str, output_path: str | None = None) -> str:
        """Extract audio from video file.

        Args:
            video_path: Path to video file
            output_path: Optional path for output audio file.
                        If None, implementation should create a temporary file.

        Returns:
            Path to extracted audio file (WAV format recommended)

        Raises:
            AudioExtractionError: If extraction fails
        """
        ...
