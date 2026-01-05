"""Core video transcription use case with dependency injection."""

from typing import Optional, Iterator
from pathlib import Path
from dataclasses import dataclass
import tempfile
import os

from .models import FrameResult, TranscriptResult, AudioSegment
from .frame_selector import FrameSelector
from ..ports.video_reader import VideoReader
from ..ports.audio_extractor import AudioExtractor, AudioExtractionError
from ..ports.audio_transcriber import AudioTranscriber, AudioTranscriptionError


@dataclass
class TranscriberPorts:
    """Port implementations for VideoTranscriber dependency injection."""
    video_reader: VideoReader
    audio_extractor: Optional[AudioExtractor] = None
    audio_transcriber: Optional[AudioTranscriber] = None


@dataclass
class TranscriberConfig:
    """Configuration settings for VideoTranscriber."""
    similarity_threshold: float = 0.92
    min_frame_interval: int = 15


class VideoTranscriber:
    """Core use case for transcribing videos.

    Uses dependency injection to accept port implementations for reading
    video, transcribing images, and optionally transcribing audio.
    Enables testing without external dependencies.
    """

    def __init__(
        self,
        ports: TranscriberPorts,
        config: TranscriberConfig = TranscriberConfig()
    ):
        """Initialize the video transcriber with port implementations and configuration.

        Args:
            ports: Port implementations for dependency injection
            config: Configuration settings (similarity threshold, frame interval, etc.)
        """
        self.video_reader = ports.video_reader
        self.audio_extractor = ports.audio_extractor
        self.audio_transcriber = ports.audio_transcriber
        self.similarity_threshold = config.similarity_threshold
        self.min_frame_interval = config.min_frame_interval

        # Create frame selector with configured parameters
        self.frame_selector = FrameSelector(
            video_reader=ports.video_reader,
            similarity_threshold=config.similarity_threshold,
            min_frame_interval=config.min_frame_interval
        )

    def extract_distinct_frames(
        self,
        video_path: str,
        sample_interval: int = 30
    ) -> Iterator[FrameResult]:
        """Extract visually distinct frames from video.

        Uses perceptual hashing to detect when frames change significantly.

        Args:
            video_path: Path to video file
            sample_interval: Check every N frames for changes

        Yields:
            FrameResult objects for each distinct frame
        """
        return self.frame_selector.extract_distinct_frames(video_path, sample_interval)

    def _extract_and_transcribe_audio(self, video_path: str) -> list[AudioSegment]:
        """Extract and transcribe audio from video.

        Handles extraction, transcription, error handling, and cleanup of temp files.
        Returns empty list if extraction or transcription fails.

        Args:
            video_path: Path to video file

        Returns:
            List of audio segments with timestamps and text
        """
        audio_segments = []
        audio_path = None

        try:
            audio_path = self.audio_extractor.extract_audio(video_path)
            audio_segments = self.audio_transcriber.transcribe_audio(audio_path)
        except AudioExtractionError as e:
            print(f"Warning: Audio extraction failed: {e}")
        except AudioTranscriptionError as e:
            print(f"Warning: Audio transcription failed: {e}")
        finally:
            if audio_path and audio_path.startswith(tempfile.gettempdir()):
                try:
                    os.remove(audio_path)
                except (FileNotFoundError, PermissionError):
                    pass

        return audio_segments

    def _extract_and_transcribe_frames(
        self,
        video_path: str,
        sample_interval: int
    ) -> list[FrameResult]:
        """Extract distinct frames from video.

        Uses perceptual hashing to identify distinct frames.

        Args:
            video_path: Path to video file
            sample_interval: Check every N frames for changes

        Returns:
            List of frame results
        """
        frames = []
        for frame_result in self.extract_distinct_frames(video_path, sample_interval):
            frames.append(frame_result)
        return frames

    def _merge_audio_with_frames(
        self,
        frames: list[FrameResult],
        audio_segments: list[AudioSegment]
    ) -> list[FrameResult]:
        """Associate audio segments with frames based on timestamps.

        Each frame gets audio segments that start between its timestamp
        and the next frame's timestamp.

        Args:
            frames: List of frame results with timestamps
            audio_segments: List of audio segments with timestamps

        Returns:
            Updated frames list with audio_segments populated
        """
        if not audio_segments:
            return frames

        for i, frame in enumerate(frames):
            # Find time range for this frame
            # First frame captures all audio from the start of the video
            start_time = 0.0 if i == 0 else frame.timestamp_seconds
            if i + 1 < len(frames):
                end_time = frames[i + 1].timestamp_seconds
            else:
                # Last frame: include all remaining audio
                end_time = float('inf')

            # Find audio segments that start in this time range
            frame.audio_segments = [
                seg for seg in audio_segments
                if start_time <= seg.start_seconds < end_time
            ]

        return frames

    def process_video(
        self,
        video_path: str,
        sample_interval: int = 30,
        transcribe_audio: bool = True,
        extract_frames: bool = True
    ) -> TranscriptResult:
        """Process entire video: extract frames and transcribe audio.

        Args:
            video_path: Path to video file
            sample_interval: Check every N frames for changes
            transcribe_audio: Whether to transcribe audio (requires audio ports)
            extract_frames: Whether to extract frames (set False for audio-only)

        Returns:
            TranscriptResult with frames and audio segments
        """
        # Extract and transcribe audio (if requested and adapters available)
        audio_segments = []
        if transcribe_audio and self.audio_extractor and self.audio_transcriber:
            audio_segments = self._extract_and_transcribe_audio(video_path)

        # Extract frames (unless audio-only mode)
        frames = []
        if extract_frames:
            frames = self._extract_and_transcribe_frames(
                video_path, sample_interval
            )
            # Merge audio with frames based on timestamps
            frames = self._merge_audio_with_frames(frames, audio_segments)

        return TranscriptResult(frames=frames, audio_segments=audio_segments)
