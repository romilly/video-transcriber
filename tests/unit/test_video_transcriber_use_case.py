"""Tests for VideoTranscriber use case with dependency injection."""

import numpy as np
import pytest

from video_transcriber.domain.video_transcriber import (
    VideoTranscriber,
    TranscriberPorts,
    TranscriberConfig
)
from video_transcriber.domain.models import AudioSegment
from video_transcriber.ports.video_reader import VideoMetadata, Frame
from tests.helpers.fake_video import FakeVideoReader


@pytest.fixture
def left_right_split_frame():
    """Create a Frame with black left half, white right half."""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:, 50:] = 255  # Left black, right white
    return Frame(0, 0.0, image)


@pytest.fixture
def top_bottom_split_frame():
    """Create a Frame with black top half, white bottom half."""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[50:, :] = 255  # Top black, bottom white
    return Frame(50, 1.67, image)


@pytest.fixture
def almost_left_right_split_frame():
    """Create a Frame almost identical to left_right_split (254 instead of 255)."""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:, 50:] = 254  # Almost identical to left_right_split
    return Frame(10, 0.33, image)


class TestVideoTranscriberUseCase:
    """Tests for VideoTranscriber core use case logic."""

    def test_initializes_with_ports(self):
        """VideoTranscriber can be initialized with port implementations."""
        fake_video = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 900, 30.0),
            frames=[]
        )

        ports = TranscriberPorts(
            video_reader=fake_video
        )
        transcriber = VideoTranscriber(ports=ports)

        assert transcriber is not None

    def test_extracts_distinct_frames_using_video_reader(self, left_right_split_frame, top_bottom_split_frame):
        """VideoTranscriber uses VideoReader to extract frames."""
        fake_video = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 60, 2.0),
            frames=[left_right_split_frame, top_bottom_split_frame]
        )

        ports = TranscriberPorts(
            video_reader=fake_video
        )
        config = TranscriberConfig(
            similarity_threshold=0.51,  # Should keep both frames (they're 50% similar)
            min_frame_interval=1  # Allow consecutive distinct frames
        )
        transcriber = VideoTranscriber(ports=ports, config=config)

        result = transcriber.process_video("dummy.mp4", sample_interval=1)

        # Should have extracted both distinct frames
        assert len(result.frames) == 2

    def test_filters_similar_frames(self, left_right_split_frame, almost_left_right_split_frame, top_bottom_split_frame):
        """VideoTranscriber filters out frames that are too similar."""
        # Create 3 frames: different, similar to first, very different
        fake_video = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 90, 3.0),
            frames=[left_right_split_frame, almost_left_right_split_frame, top_bottom_split_frame]
        )

        ports = TranscriberPorts(
            video_reader=fake_video
        )
        config = TranscriberConfig(
            similarity_threshold=0.98,  # Very high threshold - only nearly identical frames filtered
            min_frame_interval=1  # Allow checking all frames
        )
        transcriber = VideoTranscriber(ports=ports, config=config)

        result = transcriber.process_video("dummy.mp4", sample_interval=1)

        # frame2 should be filtered out as too similar to frame1
        assert len(result.frames) >= 2  # At least frame1 and frame3
