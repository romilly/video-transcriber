"""Fake implementation of VideoReader for testing."""

import sys
from typing import Iterator, Optional

from video_transcriber.ports.video_reader import VideoMetadata, Frame


class FakeVideoReader:
    """Fake video reader that returns predefined frames.

    This allows testing without actual video files.
    """

    def __init__(
        self,
        metadata: VideoMetadata,
        frames: list[Frame]
    ):
        """Initialize the fake video reader.

        Args:
            metadata: Video metadata to return
            frames: List of frames to yield when read_frames is called
        """
        self.metadata = metadata
        self.frames = frames
        self.call_count = 0
        self.last_video_path: Optional[str] = None

    def get_metadata(self, video_path: str) -> VideoMetadata:
        """Return the configured video metadata.

        Args:
            video_path: Path to video (stored but not used)

        Returns:
            Configured VideoMetadata
        """
        self.call_count += 1
        self.last_video_path = video_path
        return self.metadata

    def read_frames(
        self,
        video_path: str,
        sample_interval: int = 1,
        limit: int = sys.maxsize
    ) -> Iterator[Frame]:
        """Yield configured frames, respecting sample_interval and limit.

        Args:
            video_path: Path to video (stored but not used)
            sample_interval: Return every Nth frame from configured frames
            limit: Maximum number of frames to yield (default: unlimited)

        Yields:
            Frame objects from the configured list
        """
        self.call_count += 1
        self.last_video_path = video_path

        yielded_count = 0
        for i, frame in enumerate(self.frames):
            if i % sample_interval == 0:
                yield frame
                yielded_count += 1
                if yielded_count >= limit:
                    break