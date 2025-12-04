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
        self._reset_state()

    def _reset_state(self):
        """Initialize/reset state fields for frame extraction."""
        self.current_frame: Frame = Frame.initial_frame()
        self.last_captured_frame: Frame = Frame.initial_frame()

    def _is_frame_distinct(self) -> bool:
        """Check if current frame is sufficiently different from last captured frame."""
        return self._frames_differ_enough() and self._frame_interval_is_enough()

    def _frame_interval_is_enough(self):
        """Check if enough frames have passed since the last capture."""
        return self.current_frame.frame_interval_to(self.last_captured_frame) >= self.min_frame_interval

    def _frames_differ_enough(self) -> bool:
        """Check if similarity is below threshold (frames are distinct)."""
        return self.current_frame.similarity_to(self.last_captured_frame) < self.similarity_threshold

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
            self.current_frame = frame

            # Check if frame is sufficiently different
            if self._is_frame_distinct():
                yield FrameResult(
                    frame_number=frame.frame_number,
                    timestamp_seconds=frame.timestamp_seconds,
                    image=frame.image
                )

                self.last_captured_frame = self.current_frame
