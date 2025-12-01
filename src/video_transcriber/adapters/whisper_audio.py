"""Whisper-based audio transcription adapter."""

from pathlib import Path

from video_transcriber.ports.audio_transcriber import AudioTranscriptionError
from video_transcriber.domain.models import AudioSegment


class WhisperAudioTranscriber:
    """Transcribe audio using faster-whisper.

    Supports all Whisper model sizes:
    - tiny: Fastest, least accurate
    - base: Good balance (default)
    - small: Better accuracy
    - medium: High accuracy
    - large-v3: Best accuracy, slowest
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "auto",
        compute_type: str = "auto",
        beam_size: int = 5
    ):
        """Initialize Whisper transcriber.

        Args:
            model_size: Whisper model size (tiny/base/small/medium/large-v3)
            device: Device to use (auto/cpu/cuda)
            compute_type: Compute type (auto/int8/float16/float32)
            beam_size: Beam size for decoding (higher = more accurate but slower)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.beam_size = beam_size
        self._model = None

    def _load_model(self):
        """Lazy-load Whisper model (downloads on first use)."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel

                self._model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
            except ImportError:
                raise AudioTranscriptionError(
                    "faster-whisper not installed. "
                    "Install with: pip install faster-whisper"
                )
            except Exception as e:
                raise AudioTranscriptionError(
                    f"Failed to load Whisper model '{self.model_size}': {e}"
                )

        return self._model

    def transcribe_audio(self, audio_path: str) -> list[AudioSegment]:
        """Transcribe audio using Whisper.

        Args:
            audio_path: Path to audio file (WAV format recommended)

        Returns:
            List of AudioSegment objects with timestamps and transcribed text

        Raises:
            AudioTranscriptionError: If transcription fails
        """
        # Verify file exists
        if not Path(audio_path).exists():
            raise AudioTranscriptionError(
                f"Audio file not found: {audio_path}"
            )

        try:
            # Load model (lazy)
            model = self._load_model()

            # Transcribe audio
            segments_iter, info = model.transcribe(
                audio_path,
                beam_size=self.beam_size,
                word_timestamps=False  # Segment-level timestamps only
            )

            # Convert to AudioSegment objects
            results = []
            for segment in segments_iter:
                results.append(AudioSegment(
                    start_seconds=segment.start,
                    end_seconds=segment.end,
                    text=segment.text.strip()
                ))

            return results

        except AudioTranscriptionError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            raise AudioTranscriptionError(
                f"Whisper transcription failed: {e}"
            )
