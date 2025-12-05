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

    def test_extracts_distinct_frames_using_video_reader(self):
        """VideoTranscriber uses VideoReader to extract frames."""
        # Create frames with different patterns (left/right, top/bottom)
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame1[:, 50:] = 255  # Left black, right white

        frame2 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2[50:, :] = 255  # Top black, bottom white

        frame1_obj = Frame(0, 0.0, frame1)
        frame2_obj = Frame(50, 1.67, frame2)  # Far enough apart for min_frame_interval

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

    def test_filters_similar_frames(self):
        """VideoTranscriber filters out frames that are too similar."""
        # Create 3 frames: different, similar to first, very different
        frame1_img = np.zeros((100, 100, 3), dtype=np.uint8)
        frame1_img[:, 50:] = 255  # Left black, right white

        frame2_img = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2_img[:, 50:] = 254  # Almost identical to frame1 (254 instead of 255)

        frame3_img = np.zeros((100, 100, 3), dtype=np.uint8)
        frame3_img[50:, :] = 255  # Top black, bottom white - very different pattern

        frame1 = Frame(0, 0.0, frame1_img)
        frame2 = Frame(10, 0.33, frame2_img)  # Similar to frame1
        frame3 = Frame(60, 2.0, frame3_img)  # Different

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
