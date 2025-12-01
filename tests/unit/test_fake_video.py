"""Tests for FakeVideoReader."""

import numpy as np
import pytest

from video_transcriber.testing.fake_video import FakeVideoReader
from video_transcriber.ports.video_reader import VideoMetadata, Frame


class TestFakeVideoReader:
    """Tests for fake video reader."""

    def test_returns_configured_metadata(self):
        """FakeVideoReader returns configured video metadata."""
        metadata = VideoMetadata(
            width=1920,
            height=1080,
            fps=30.0,
            total_frames=900,
            duration_seconds=30.0
        )
        fake = FakeVideoReader(metadata=metadata, frames=[])

        result = fake.get_metadata("dummy.mp4")

        assert result == metadata

    def test_yields_configured_frames(self):
        """FakeVideoReader yields the configured frames."""
        frame1 = Frame(
            frame_number=1,
            timestamp_seconds=0.0,
            image=np.zeros((100, 100, 3), dtype=np.uint8)
        )
        frame2 = Frame(
            frame_number=30,
            timestamp_seconds=1.0,
            image=np.ones((100, 100, 3), dtype=np.uint8) * 255
        )

        fake = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 60, 2.0),
            frames=[frame1, frame2]
        )

        frames = list(fake.read_frames("dummy.mp4"))

        assert len(frames) == 2
        assert frames[0].frame_number == 1
        assert frames[1].frame_number == 30

    def test_respects_sample_interval(self):
        """FakeVideoReader respects sample_interval parameter."""
        frames_list = [
            Frame(i, i / 30.0, np.zeros((10, 10, 3), dtype=np.uint8))
            for i in range(0, 100, 10)  # Frames 0, 10, 20, ..., 90
        ]

        fake = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 100, 3.33),
            frames=frames_list
        )

        # Sample every 3rd frame (from our pre-sampled list)
        result = list(fake.read_frames("dummy.mp4", sample_interval=3))

        # Should get frames at indices 0, 3, 6, 9 from our list
        # which are frame numbers 0, 30, 60, 90
        assert len(result) == 4
        assert result[0].frame_number == 0
        assert result[1].frame_number == 30
        assert result[2].frame_number == 60
        assert result[3].frame_number == 90

    def test_tracks_call_count_and_last_path(self):
        """FakeVideoReader tracks how many times it was called."""
        fake = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 60, 2.0),
            frames=[]
        )

        assert fake.call_count == 0
        assert fake.last_video_path is None

        fake.get_metadata("video1.mp4")
        assert fake.call_count == 1
        assert fake.last_video_path == "video1.mp4"

        list(fake.read_frames("video2.mp4"))
        assert fake.call_count == 2
        assert fake.last_video_path == "video2.mp4"
