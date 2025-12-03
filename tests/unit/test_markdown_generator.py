"""Tests for MarkdownGenerator."""
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pytest

from video_transcriber.domain.models import TranscriptResult, FrameResult, AudioSegment
from video_transcriber.ports.video_reader import VideoMetadata, Frame
from video_transcriber.testing.fake_video import FakeVideoReader
from video_transcriber.testing.fake_vision import FakeVisionTranscriber
from video_transcriber.testing.fake_audio import FakeAudioExtractor, FakeAudioTranscriber
from video_transcriber.domain.video_transcriber import VideoTranscriber, TranscriberPorts, TranscriberConfig
from video_transcriber.generators.markdown_generator import MarkdownGenerator


@pytest.fixture
def fake_video_reader():
    """Create a FakeVideoReader with test frames."""
    return FakeVideoReader(
        metadata=VideoMetadata(width=640, height=480, fps=30.0, total_frames=90, duration_seconds=3.0),
        frames=[
            Frame(frame_number=0, timestamp_seconds=0.0, image=np.zeros((480, 640, 3), dtype=np.uint8)),
            Frame(frame_number=30, timestamp_seconds=1.0, image=np.ones((480, 640, 3), dtype=np.uint8) * 255)
        ]
    )


@pytest.fixture
def fake_audio_transcriber():
    """Create a FakeAudioTranscriber with test audio segments."""
    return FakeAudioTranscriber.build(
        2.0,
        "Hello world",
        "This is a test"
    )


class TestMarkdownGenerator:
    """Tests for MarkdownGenerator."""

    def test_creates_zipfile_in_specified_directory(self, fake_video_reader, fake_audio_transcriber):
        """MarkdownGenerator creates a zip file in the specified output directory."""
        # Arrange: Create a fake VideoTranscriber with audio segments
        video_reader = fake_video_reader
        vision_transcriber = FakeVisionTranscriber(default_response="Test slide")
        audio_extractor = FakeAudioExtractor(audio_file_path="/tmp/test_audio.wav")
        audio_transcriber = fake_audio_transcriber

        ports = TranscriberPorts(
            video_reader=video_reader,
            vision_transcriber=vision_transcriber,
            audio_extractor=audio_extractor,
            audio_transcriber=audio_transcriber
        )
        transcriber = VideoTranscriber(ports=ports)

        generator = MarkdownGenerator(video_transcriber=transcriber)

        # Act: Create zipfile
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            zip_path = generator.create_zipfile("test_video.mp4", output_dir)

            # Assert: Zip file was created in the specified directory
            assert Path(zip_path).exists()
            assert Path(zip_path).parent == output_dir
            assert Path(zip_path).suffix == ".zip"
