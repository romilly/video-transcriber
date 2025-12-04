"""Port for reading video files and extracting frames."""

from dataclasses import dataclass
from typing import Protocol, Iterator, Optional
import numpy as np


@dataclass
class VideoMetadata:
    """Video file metadata."""
    width: int
    height: int
    fps: float
    total_frames: int
    duration_seconds: float


@dataclass
class Frame:
    """A single video frame with metadata."""
    frame_number: int
    timestamp_seconds: float
    image: np.ndarray  # BGR format (OpenCV convention)
    _hash: Optional[np.ndarray] = None  # Cached perceptual hash

    def get_hash(self) -> np.ndarray:
        """Get perceptual hash for this frame, computing and caching if needed."""
        if self._hash is None:
            from ..domain.frame_comparison import compute_frame_hash
            self._hash = compute_frame_hash(self.image)
        return self._hash

    def similarity_to(self, other: 'Frame') -> float:
        """Compute similarity to another frame.

        Args:
            other: The frame to compare to

        Returns:
            Similarity score from 0.0 (completely different) to 1.0 (identical)
        """
        my_hash = self.get_hash()
        other_hash = other.get_hash()
        return float(np.mean(my_hash == other_hash))

    def frame_interval_to(self, other: 'Frame') -> int:
        """Calculate the number of frames between this frame and another.

        Args:
            other: The frame to compare to

        Returns:
            Absolute difference in frame numbers
        """
        return abs(self.frame_number - other.frame_number)


class VideoReader(Protocol):
    """Port for reading video files and extracting frames.

    This abstracts the video reading library (OpenCV, PyAV, etc.) to enable
    testing without actual video files and easy swapping of implementations.
    """

    def get_metadata(self, video_path: str) -> VideoMetadata:
        """Get video file metadata.

        Args:
            video_path: Path to video file

        Returns:
            Video metadata including dimensions, fps, frame count

        Raises:
            VideoReadError: If video cannot be read or doesn't exist
        """
        ...

    def read_frames(
        self,
        video_path: str,
        sample_interval: int = 1
    ) -> Iterator[Frame]:
        """Read frames from video at specified intervals.

        Args:
            video_path: Path to video file
            sample_interval: Read every Nth frame (1 = every frame)

        Yields:
            Frame objects with frame number, timestamp, and image

        Raises:
            VideoReadError: If video reading fails
        """
        ...


class VideoReadError(Exception):
    """Raised when video reading fails."""
    pass
