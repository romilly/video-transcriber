"""FFmpeg-based audio extraction adapter."""

import subprocess
import tempfile
from pathlib import Path

from video_transcriber.ports.audio_extractor import AudioExtractionError


class FFmpegAudioExtractor:
    """Extract audio from video using ffmpeg.

    Converts video audio to WAV format suitable for speech recognition:
    - Configurable sample rate (default: 16kHz for Whisper)
    - Mono channel audio
    - PCM 16-bit encoding
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1
    ):
        """Initialize ffmpeg audio extractor.

        Args:
            sample_rate: Output sample rate in Hz (default: 16000)
            channels: Number of audio channels (default: 1 for mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels

    def extract_audio(self, video_path: str, output_path: str | None = None) -> str:
        """Extract audio from video using ffmpeg subprocess.

        Args:
            video_path: Path to video file
            output_path: Optional path for output audio file.
                        If None, creates temporary WAV file.

        Returns:
            Path to extracted audio file (WAV format)

        Raises:
            AudioExtractionError: If ffmpeg fails or video doesn't exist
        """
        # Create temp file if no output path specified
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".wav")
            # Close the file descriptor, ffmpeg will create the file
            import os
            os.close(fd)

        # Build ffmpeg command
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file
            "-i", video_path,  # Input video
            "-vn",  # No video output
            "-acodec", "pcm_s16le",  # PCM 16-bit little-endian
            "-ar", str(self.sample_rate),  # Sample rate
            "-ac", str(self.channels),  # Audio channels
            output_path
        ]

        try:
            # Run ffmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False  # Don't raise exception, we'll handle it
            )

            if result.returncode != 0:
                error_msg = result.stderr or "Unknown error"
                raise AudioExtractionError(
                    f"ffmpeg failed with code {result.returncode}: {error_msg}"
                )

            # Verify output file was created
            if not Path(output_path).exists():
                raise AudioExtractionError(
                    f"ffmpeg succeeded but output file not created: {output_path}"
                )

            return output_path

        except FileNotFoundError:
            raise AudioExtractionError(
                "ffmpeg not found. Please install ffmpeg: "
                "apt install ffmpeg (Ubuntu/Debian) or brew install ffmpeg (macOS)"
            )
        except Exception as e:
            if isinstance(e, AudioExtractionError):
                raise
            raise AudioExtractionError(f"Unexpected error during audio extraction: {e}")
