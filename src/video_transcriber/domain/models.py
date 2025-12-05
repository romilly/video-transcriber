"""Domain models for video transcription."""

import io
from dataclasses import dataclass, field
from typing import Optional
import cv2
import numpy as np
from PIL import Image


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

    def to_png_bytes(self) -> bytes:
        """Encode frame image as PNG bytes.

        Returns:
            bytes: PNG-encoded image data

        Raises:
            ValueError: If frame has no image (e.g., initial_frame)
        """
        if self.image is None:
            raise ValueError("Cannot encode frame with no image")

        # Convert BGR to RGB (OpenCV uses BGR by default)
        if len(self.image.shape) == 3 and self.image.shape[2] == 3:
            image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = self.image

        # Convert to PIL Image and encode as PNG
        pil_image = Image.fromarray(image_rgb)
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        return buffer.getvalue()


@dataclass
class AudioSegment:
    """A segment of transcribed audio."""
    start_seconds: float
    end_seconds: float
    text: str


@dataclass
class FrameResult:
    """Holds a frame with timestamp and audio segments."""
    frame: Frame
    audio_segments: list[AudioSegment] = field(default_factory=list)

    @property
    def frame_number(self) -> int:
        """Delegate to frame.frame_number for backward compatibility."""
        return self.frame.frame_number

    @property
    def timestamp_seconds(self) -> float:
        """Delegate to frame.timestamp_seconds for backward compatibility."""
        return self.frame.timestamp_seconds

    @property
    def image(self):
        """Delegate to frame.image for backward compatibility."""
        return self.frame.image

    def to_png_bytes(self) -> bytes:
        """Encode frame image as PNG bytes by delegating to frame."""
        return self.frame.to_png_bytes()


@dataclass
class TranscriptResult:
    """Complete transcript with visual and audio components."""
    frames: list[FrameResult]
    audio_segments: list[AudioSegment]
