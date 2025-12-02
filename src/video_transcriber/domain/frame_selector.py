"""Frame selection logic for identifying distinct frames in video."""

from typing import Iterator

from .models import FrameResult
from .frame_comparison import compute_frame_hash, frames_similar
from ..ports.video_reader import VideoReader


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
        self._reset_state()

    def _reset_state(self):
        """Initialize/reset state fields for frame extraction."""
        self.current_hash = None
        self.current_frame_number = None
        self.last_hash = None
        self.last_captured_frame_number = -self.min_frame_interval

    def _is_frame_distinct(self) -> bool:
        """Check if current frame is sufficiently different from last captured frame."""
        return self._differ_enough() and self._interval_is_enough()

    def _interval_is_enough(self):
        return  (self.current_frame_number - self.last_captured_frame_number) >= self.min_frame_interval

    def _differ_enough(self) -> bool:
        return frames_similar(self.current_hash, self.last_hash) < self.similarity_threshold

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
        self._reset_state()

        for frame in self.video_reader.read_frames(video_path, sample_interval):
            # Compute hash for this frame
            self.current_hash = compute_frame_hash(frame.image)
            self.current_frame_number = frame.frame_number

            # Check if frame is sufficiently different
            if self._is_frame_distinct():
                yield FrameResult(
                    frame_number=frame.frame_number,
                    timestamp_seconds=frame.timestamp_seconds,
                    image=frame.image
                )

                self.last_hash = self.current_hash
                self.last_captured_frame_number = self.current_frame_number
