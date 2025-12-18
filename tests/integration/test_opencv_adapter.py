"""Integration tests for OpenCVVideoAdapter.

These tests require a test video file to be present.
"""

import numpy as np
import pytest
from pathlib import Path

from video_transcriber.adapters.opencv_video import OpenCVVideoAdapter
from video_transcriber.ports.video_reader import VideoReadError


# Path to test video file
TEST_VIDEO = Path(__file__).parent.parent / "data" / "demo.mp4"


class TestOpenCVVideoAdapter:
    """Integration tests for OpenCV video adapter."""

    def test_reads_video_metadata(self):
        """OpenCVVideoAdapter can read video file metadata."""
        adapter = OpenCVVideoAdapter()

        metadata = adapter.get_metadata(str(TEST_VIDEO))

        # Should return valid metadata
        assert metadata.width > 0
        assert metadata.height > 0
        assert metadata.fps > 0
        assert metadata.total_frames > 0
        assert metadata.duration_seconds > 0
        # Duration should be approximately total_frames / fps
        expected_duration = metadata.total_frames / metadata.fps
        assert abs(metadata.duration_seconds - expected_duration) < 0.1

    def test_reads_frames_from_video(self):
        """OpenCVVideoAdapter can read frames from video."""
        adapter = OpenCVVideoAdapter()

        frames = list(adapter.read_frames(str(TEST_VIDEO), sample_interval=30, limit=10))

        # Should yield at least some frames
        assert len(frames) > 0
        assert len(frames) <= 10  # Should respect limit

        # Check first frame properties
        first_frame = frames[0]
        assert first_frame.frame_number >= 0
        assert first_frame.timestamp_seconds >= 0
        assert isinstance(first_frame.image, np.ndarray)
        assert first_frame.image.dtype == np.uint8
        assert len(first_frame.image.shape) == 3  # Height, width, channels
        assert first_frame.image.shape[2] == 3  # BGR

    def test_respects_sample_interval(self):
        """OpenCVVideoAdapter respects the sample_interval parameter."""
        adapter = OpenCVVideoAdapter()

        # Read with different intervals to show sampling effect
        # Keep limits low for fast tests
        frames_all = list(adapter.read_frames(str(TEST_VIDEO), sample_interval=1, limit=20))
        frames_sampled = list(adapter.read_frames(str(TEST_VIDEO), sample_interval=10, limit=2))

        # Should respect the limits
        assert len(frames_all) == 20
        assert len(frames_sampled) == 2
        # Verify sampling: frames_sampled should be every 10th frame
        # So frame numbers should be 10, 20
        assert frames_sampled[0].frame_number == 10
        assert frames_sampled[1].frame_number == 20

    def test_raises_error_for_nonexistent_file(self):
        """OpenCVVideoAdapter raises error for nonexistent video file."""
        adapter = OpenCVVideoAdapter()

        with pytest.raises(VideoReadError):
            adapter.get_metadata("nonexistent_video.mp4")

        with pytest.raises(VideoReadError):
            list(adapter.read_frames("nonexistent_video.mp4"))
