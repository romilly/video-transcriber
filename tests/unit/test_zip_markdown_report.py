"""Tests for ZipMarkdownReportGenerator."""
import os
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pytest

from video_transcriber.domain.models import AudioSegment, FrameResult, TranscriptResult
from video_transcriber.adapters.zip_markdown_report import ZipMarkdownReportGenerator


class TestZipMarkdownReportGenerator:
    """Tests for ZipMarkdownReportGenerator adapter."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_transcript_result(self):
        """Create a sample TranscriptResult with frames and audio."""
        # Create sample frames with audio segments
        frame1 = FrameResult(
            frame_number=0,
            timestamp_seconds=0.0,
            image=np.zeros((100, 100, 3), dtype=np.uint8),
            audio_segments=[
                AudioSegment(0.0, 3.5, "Hello everyone, welcome to today's presentation."),
                AudioSegment(3.5, 7.0, "Today we'll be discussing video transcription."),
            ]
        )

        frame2 = FrameResult(
            frame_number=30,
            timestamp_seconds=10.0,
            image=np.ones((100, 100, 3), dtype=np.uint8) * 128,
            audio_segments=[
                AudioSegment(10.0, 15.0, "Let's start with the key concepts."),
            ]
        )

        all_audio = frame1.audio_segments + frame2.audio_segments
        return TranscriptResult(frames=[frame1, frame2], audio_segments=all_audio)

    def test_generates_zip_with_markdown_and_images(self, temp_output_dir, sample_transcript_result):
        """Test that generator creates a zip file with markdown and images."""
        # Given: A TranscriptResult
        generator = ZipMarkdownReportGenerator()
        output_path = os.path.join(temp_output_dir, "report.zip")

        # When: Generate zip report
        result_path = generator.generate(sample_transcript_result, output_path=output_path)

        # Then: Zip file exists
        assert os.path.exists(result_path)
        assert result_path == output_path

        # And: Zip contains transcript.md and images
        with zipfile.ZipFile(result_path, 'r') as zf:
            namelist = zf.namelist()
            assert "transcript.md" in namelist
            assert "img/frame_000.png" in namelist
            assert "img/frame_001.png" in namelist

    def test_markdown_contains_timeline_merged_content(self, temp_output_dir, sample_transcript_result):
        """Test that markdown contains frames with their associated audio segments."""
        # Given: A TranscriptResult with frames and audio
        generator = ZipMarkdownReportGenerator()
        output_path = os.path.join(temp_output_dir, "report.zip")

        # When: Generate zip report
        generator.generate(sample_transcript_result, output_path=output_path)

        # Then: Markdown contains timeline structure
        with zipfile.ZipFile(output_path, 'r') as zf:
            markdown_content = zf.read("transcript.md").decode('utf-8')

            # Check for frame headers with timestamps
            assert "## Frame 1" in markdown_content or "## Slide 1" in markdown_content
            assert "0:00" in markdown_content or "00:00" in markdown_content

            # Check for image links
            assert "![" in markdown_content
            assert "img/frame_000.png" in markdown_content

            # Check for audio transcription
            assert "Hello everyone" in markdown_content
            assert "Today we'll be discussing" in markdown_content

    def test_handles_empty_frames(self, temp_output_dir):
        """Test that generator handles TranscriptResult with no frames."""
        # Given: A TranscriptResult with no frames
        result = TranscriptResult(frames=[], audio_segments=[])
        generator = ZipMarkdownReportGenerator()
        output_path = os.path.join(temp_output_dir, "empty.zip")

        # When: Generate zip report
        result_path = generator.generate(result, output_path=output_path)

        # Then: Zip file exists and contains markdown (even if empty)
        assert os.path.exists(result_path)
        with zipfile.ZipFile(result_path, 'r') as zf:
            assert "transcript.md" in zf.namelist()
            markdown_content = zf.read("transcript.md").decode('utf-8')
            assert len(markdown_content) > 0  # Should have at least a title or message
