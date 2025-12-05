"""Frame selection logic for identifying distinct frames in video."""

from typing import Iterator

from .models import FrameResult
from ..ports.video_reader import VideoReader, Frame


class FrameSelector:
    """Selects distinct frames from video based on visual similarity."""

    def __init__(
        self,
        video_reader: VideoReader,
        similarity_threshold: float = 0.92,
        min_frame_interval: int = 15
    ):
        """
        Initialize frame selector.

        Args:
            video_reader: Port for reading video frames
            similarity_threshold: Frames more similar than this are considered duplicates (0-1)
            min_frame_interval: Minimum frames between captures (avoids transition frames)
        """
        self.video_reader = video_reader
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
        last_captured_frame = Frame.initial_frame()

        for current_frame in self.video_reader.read_frames(video_path, sample_interval):
            # Check if frame is sufficiently different
            frames_differ_enough = current_frame.similarity_to(last_captured_frame) < self.similarity_threshold
            frame_interval_is_enough = current_frame.frame_interval_to(last_captured_frame) >= self.min_frame_interval

            if frames_differ_enough and frame_interval_is_enough:
                yield FrameResult(frame=current_frame)

                last_captured_frame = current_frame
