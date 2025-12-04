"""Port for reading video files and extracting frames."""

import sys
from dataclasses import dataclass
from typing import Protocol, Iterator, Optional
import cv2
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
    image: np.ndarray | None  # BGR format (OpenCV convention), or None for initial frame
    _hash: Optional[np.ndarray] = None  # Cached perceptual hash

    @classmethod
    def initial_frame(cls) -> 'Frame':
        """Create an initial frame for bootstrapping frame comparison.

        Returns a frame with None image, a very large negative frame number,
        and the smallest possible timestamp. This eliminates the need for None checks.
        """
        return cls(
            frame_number=-999999,
            timestamp_seconds=float('-inf'),
            image=None
        )

    @staticmethod
    def _compute_hash(image: np.ndarray, hash_size: int = 16) -> np.ndarray:
        """Compute a perceptual hash for change detection.

        Uses average hash - fast and effective for slide detection.
        The hash is based on whether each pixel in a downsampled grayscale
        version of the frame is above or below the mean value.

        Args:
            image: Input frame as numpy array (BGR format)
            hash_size: Size of hash grid (default 16x16 = 256 bits)

        Returns:
            Boolean array representing the perceptual hash
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Resize to hash_size x hash_size
        resized = cv2.resize(gray, (hash_size, hash_size), interpolation=cv2.INTER_AREA)

        # Compare each pixel to mean value
        mean_val = resized.mean()

        # Return flattened boolean array
        return (resized > mean_val).flatten()

    def get_hash(self) -> np.ndarray | None:
        """Get perceptual hash for this frame, computing and caching if needed."""
        if self.image is None:
            return None
        if self._hash is None:
            self._hash = Frame._compute_hash(self.image)
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
        if my_hash is None or other_hash is None:
            return 0.0
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
