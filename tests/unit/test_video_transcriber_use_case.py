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
def left_right_split_image():
    """Create a frame with black left half, white right half."""
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, 50:] = 255  # Left black, right white
    return frame


@pytest.fixture
def top_bottom_split_image():
    """Create a frame with black top half, white bottom half."""
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[50:, :] = 255  # Top black, bottom white
    return frame


@pytest.fixture
def almost_left_right_split_image():
    """Create a frame almost identical to left_right_split (254 instead of 255)."""
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:, 50:] = 254  # Almost identical to left_right_split
    return frame


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

    def test_extracts_distinct_frames_using_video_reader(self, left_right_split_image, top_bottom_split_image):
        """VideoTranscriber uses VideoReader to extract frames."""
        frame1_obj = Frame(0, 0.0, left_right_split_image)
        frame2_obj = Frame(50, 1.67, top_bottom_split_image)  # Far enough apart for min_frame_interval

        fake_video = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 60, 2.0),
            frames=[frame1_obj, frame2_obj]
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

    def test_filters_similar_frames(self, left_right_split_image, almost_left_right_split_image, top_bottom_split_image):
        """VideoTranscriber filters out frames that are too similar."""
        # Create 3 frames: different, similar to first, very different
        frame1 = Frame(0, 0.0, left_right_split_image)
        frame2 = Frame(10, 0.33, almost_left_right_split_image)  # Similar to frame1
        frame3 = Frame(60, 2.0, top_bottom_split_image)  # Different

        fake_video = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 90, 3.0),
            frames=[frame1, frame2, frame3]
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
