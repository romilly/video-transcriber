"""Fake implementations of audio ports for testing."""

from video_transcriber.ports.audio_extractor import AudioExtractionError
from video_transcriber.ports.audio_transcriber import AudioTranscriptionError
from video_transcriber.domain.models import AudioSegment


class FakeAudioExtractor:
    """Fake audio extractor for testing without actual audio extraction.

    Returns pre-configured audio file paths without performing real extraction.
    """

    def __init__(
        self,
        audio_file_path: str = "/tmp/fake_audio.wav",
        should_fail: bool = False
    ):
        """Initialize fake audio extractor.

        Args:
            audio_file_path: Path to return as extracted audio
            should_fail: If True, raises AudioExtractionError
        """
        self.audio_file_path = audio_file_path
        self.should_fail = should_fail
        self.call_count = 0
        self.last_video_path = None
        self.last_output_path = None

    def extract_audio(self, video_path: str, output_path: str | None = None) -> str:
        """Return configured audio path without actual extraction.

        Args:
            video_path: Path to video (stored but not used)
            output_path: Optional output path (if provided, returns this)

        Returns:
            output_path if provided, otherwise configured audio_file_path

        Raises:
            AudioExtractionError: If should_fail is True
        """
        self.call_count += 1
        self.last_video_path = video_path
        self.last_output_path = output_path

        if self.should_fail:
            raise AudioExtractionError("Fake extraction failure")

        return output_path or self.audio_file_path


class FakeAudioTranscriber:
    """Fake audio transcriber for testing without actual transcription.

    Returns pre-configured audio segments without performing real transcription.
    """

    def __init__(
        self,
        segments: list[AudioSegment] | None = None,
        should_fail: bool = False
    ):
        """Initialize fake audio transcriber.

        Args:
            segments: Pre-configured segments to return
            should_fail: If True, raises AudioTranscriptionError
        """
        self.segments = segments or []
        self.should_fail = should_fail
        self.call_count = 0
        self.last_audio_path = None

    @classmethod
    def build(cls, segment_duration, *texts: list[str]):
        """Build a FakeAudioTranscriber from a list of text strings.

        Args:
            texts: List of text strings for each audio segment
            segment_duration: Duration of each segment in seconds (default: 2.0)

        Returns:
            FakeAudioTranscriber with sequential audio segments
        """
        segments = []
        current_time = 0.0
        for text in texts:
            segment = AudioSegment(
                start_seconds=current_time,
                end_seconds=current_time + segment_duration,
                text=text
            )
            segments.append(segment)
            current_time += segment_duration
        return cls(segments=segments)

    def transcribe_audio(self, audio_path: str) -> list[AudioSegment]:
        """Return configured segments without actual transcription.

        Args:
            audio_path: Path to audio (stored but not used)

        Returns:
            Configured list of AudioSegment objects

        Raises:
            AudioTranscriptionError: If should_fail is True
        """
        self.call_count += 1
        self.last_audio_path = audio_path

        if self.should_fail:
            raise AudioTranscriptionError("Fake transcription failure")

        return self.segments
