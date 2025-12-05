"""Port for reading video files and extracting frames."""

import sys
from dataclasses import dataclass
from typing import Protocol, Iterator

from video_transcriber.domain.models import Frame


@dataclass
class VideoMetadata:
    """Video file metadata."""
    width: int
    height: int
    fps: float
    total_frames: int
    duration_seconds: float


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
        sample_interval: int = 1,
        limit: int = sys.maxsize
    ) -> Iterator[Frame]:
        """Read frames from video at specified intervals.

        Args:
            video_path: Path to video file
            sample_interval: Read every Nth frame (1 = every frame)
            limit: Maximum number of frames to yield (default: unlimited)

        Yields:
            Frame objects with frame number, timestamp, and image

        Raises:
            VideoReadError: If video reading fails
        """
        ...


class VideoReadError(Exception):
    """Raised when video reading fails."""
    pass
