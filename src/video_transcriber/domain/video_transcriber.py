"""Core video transcription use case with dependency injection."""

from typing import Optional, Iterator
from pathlib import Path

from .models import FrameResult, TranscriptResult, AudioSegment
from .frame_comparison import compute_frame_hash, frames_similar
from ..ports.video_reader import VideoReader
from ..ports.vision_transcriber import VisionTranscriber


class VideoTranscriber:
    """Core use case for transcribing videos.

    Uses dependency injection to accept port implementations for reading
    video and transcribing images, enabling testing without external dependencies.
    """

    def __init__(
        self,
        video_reader: VideoReader,
        vision_transcriber: VisionTranscriber,
        similarity_threshold: float = 0.92,
        min_frame_interval: int = 15
    ):
        """Initialize the video transcriber with port implementations.

        Args:
            video_reader: Port for reading video files
            vision_transcriber: Port for transcribing images
            similarity_threshold: Frames more similar than this are considered duplicates (0-1)
            min_frame_interval: Minimum frames between captures (avoids transition frames)
        """
        self.video_reader = video_reader
        self.vision_transcriber = vision_transcriber
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

    def process_video(
        self,
        video_path: str,
        sample_interval: int = 30,
        prompt: Optional[str] = None,
        transcribe_visuals: bool = True
    ) -> TranscriptResult:
        """Process entire video: extract distinct frames and transcribe visuals.

        Args:
            video_path: Path to video file
            sample_interval: Check every N frames for changes
            prompt: Custom prompt for visual transcription
            transcribe_visuals: Whether to transcribe visuals with vision model

        Returns:
            TranscriptResult with frames
        """
        # Default prompt if not specified
        if prompt is None:
            prompt = "Transcribe all text visible in this presentation slide. Include headings, bullet points, and any other text. Format it clearly."

        # Extract and transcribe frames
        frames = []
        for frame_result in self.extract_distinct_frames(video_path, sample_interval):
            if transcribe_visuals:
                frame_result.transcription = self.vision_transcriber.transcribe_image(
                    frame_result.image,
                    prompt
                )

            frames.append(frame_result)

        # Return result (no audio segments for now - that's future work)
        return TranscriptResult(frames=frames, audio_segments=[])
