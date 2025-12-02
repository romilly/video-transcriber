"""Core video transcription use case with dependency injection."""

from typing import Optional, Iterator
from pathlib import Path
import tempfile
import os

from .models import FrameResult, TranscriptResult, AudioSegment
from .frame_comparison import compute_frame_hash, frames_similar
from ..ports.video_reader import VideoReader
from ..ports.vision_transcriber import VisionTranscriber
from ..ports.audio_extractor import AudioExtractor, AudioExtractionError
from ..ports.audio_transcriber import AudioTranscriber, AudioTranscriptionError


class VideoTranscriber:
    """Core use case for transcribing videos.

    Uses dependency injection to accept port implementations for reading
    video, transcribing images, and optionally transcribing audio.
    Enables testing without external dependencies.
    """

    def __init__(
        self,
        video_reader: VideoReader,
        vision_transcriber: VisionTranscriber,
        audio_extractor: Optional[AudioExtractor] = None,
        audio_transcriber: Optional[AudioTranscriber] = None,
        similarity_threshold: float = 0.92,
        min_frame_interval: int = 15
    ):
        """Initialize the video transcriber with port implementations.

        Args:
            video_reader: Port for reading video files
            vision_transcriber: Port for transcribing images
            audio_extractor: Optional port for extracting audio from video
            audio_transcriber: Optional port for transcribing audio to text
            similarity_threshold: Frames more similar than this are considered duplicates (0-1)
            min_frame_interval: Minimum frames between captures (avoids transition frames)
        """
        self.video_reader = video_reader
        self.vision_transcriber = vision_transcriber
        self.audio_extractor = audio_extractor
        self.audio_transcriber = audio_transcriber
        self.similarity_threshold = similarity_threshold
        self.min_frame_interval = min_frame_interval

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
        last_hash = None
        last_captured_frame = -self.min_frame_interval

        for frame in self.video_reader.read_frames(video_path, sample_interval):
            # Compute hash for this frame
            current_hash = compute_frame_hash(frame.image)

            # Check if frame is sufficiently different
            is_distinct = False
            if last_hash is None:
                is_distinct = True
            else:
                similarity = frames_similar(current_hash, last_hash)
                if similarity < self.similarity_threshold:
                    if (frame.frame_number - last_captured_frame) >= self.min_frame_interval:
                        is_distinct = True

            if is_distinct:
                yield FrameResult(
                    frame_number=frame.frame_number,
                    timestamp_seconds=frame.timestamp_seconds,
                    image=frame.image
                )

                last_hash = current_hash
                last_captured_frame = frame.frame_number

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
        except (AudioExtractionError, AudioTranscriptionError):
            pass  # Return empty list
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
        sample_interval: int,
        prompt: str,
        transcribe_visuals: bool
    ) -> list[FrameResult]:
        """Extract distinct frames and optionally transcribe them.

        Uses perceptual hashing to identify distinct frames, then optionally
        transcribes visual content using the vision model.

        Args:
            video_path: Path to video file
            sample_interval: Check every N frames for changes
            prompt: Prompt for visual transcription
            transcribe_visuals: Whether to transcribe visuals with vision model

        Returns:
            List of frame results with optional transcriptions
        """
        frames = []
        for frame_result in self.extract_distinct_frames(video_path, sample_interval):
            if transcribe_visuals:
                frame_result.transcription = self.vision_transcriber.transcribe_image(
                    frame_result.image,
                    prompt
                )
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
            start_time = frame.timestamp_seconds
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
        prompt: Optional[str] = None,
        transcribe_visuals: bool = True,
        transcribe_audio: bool = True
    ) -> TranscriptResult:
        """Process entire video: extract frames, transcribe visuals and audio.

        Args:
            video_path: Path to video file
            sample_interval: Check every N frames for changes
            prompt: Custom prompt for visual transcription
            transcribe_visuals: Whether to transcribe visuals with vision model
            transcribe_audio: Whether to transcribe audio (requires audio ports)

        Returns:
            TranscriptResult with frames and audio segments
        """
        # Default prompt if not specified
        if prompt is None:
            prompt = "Transcribe all text visible in this presentation slide. Include headings, bullet points, and any other text. Format it clearly."

        # Extract and transcribe audio (if requested and adapters available)
        audio_segments = []
        if transcribe_audio and self.audio_extractor and self.audio_transcriber:
            audio_segments = self._extract_and_transcribe_audio(video_path)

        # Extract and transcribe frames
        frames = self._extract_and_transcribe_frames(
            video_path, sample_interval, prompt, transcribe_visuals
        )

        # Merge audio with frames based on timestamps
        frames = self._merge_audio_with_frames(frames, audio_segments)

        return TranscriptResult(frames=frames, audio_segments=audio_segments)
