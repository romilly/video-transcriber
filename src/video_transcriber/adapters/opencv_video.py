"""OpenCV-based video reading adapter."""

import sys
import cv2
from typing import Iterator

from video_transcriber.ports.video_reader import VideoMetadata, Frame, VideoReadError


class OpenCVVideoAdapter:
    """Video reader using OpenCV (cv2.VideoCapture).

    Reads video files and extracts frames using OpenCV.
    """

    def get_metadata(self, video_path: str) -> VideoMetadata:
        """Get video file metadata using OpenCV.

        Args:
            video_path: Path to video file

        Returns:
            VideoMetadata with video properties

        Raises:
            VideoReadError: If video cannot be opened
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise VideoReadError(f"Could not open video: {video_path}")

        try:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0.0

            return VideoMetadata(
                width=width,
                height=height,
                fps=fps,
                total_frames=total_frames,
                duration_seconds=duration
            )
        finally:
            cap.release()

    def read_frames(
        self,
        video_path: str,
        sample_interval: int = 1,
        limit: int = sys.maxsize
    ) -> Iterator[Frame]:
        """Read frames from video using OpenCV.

        Args:
            video_path: Path to video file
            sample_interval: Read every Nth frame (1 = every frame)
            limit: Maximum number of frames to yield (default: unlimited)

        Yields:
            Frame objects with frame number, timestamp, and image

        Raises:
            VideoReadError: If video cannot be opened
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise VideoReadError(f"Could not open video: {video_path}")

        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = 0
            yielded_count = 0

            while True:
                ret, image = cap.read()

                if not ret:
                    break

                frame_count += 1

                # Only yield frames at sample intervals
                if frame_count % sample_interval == 0:
                    timestamp = frame_count / fps if fps > 0 else 0.0

                    yield Frame(
                        frame_number=frame_count,
                        timestamp_seconds=timestamp,
                        image=image.copy()
                    )

                    yielded_count += 1
                    if yielded_count >= limit:
                        break
        finally:
            cap.release()
