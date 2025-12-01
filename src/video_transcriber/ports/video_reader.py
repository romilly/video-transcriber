"""Port for reading video files and extracting frames."""

from dataclasses import dataclass
from typing import Protocol, Iterator
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
