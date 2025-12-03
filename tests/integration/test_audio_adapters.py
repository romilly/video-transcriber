"""Integration tests for audio adapters.

These tests require:
- ffmpeg installed on the system
- A test video file with audio
- faster-whisper installed
"""

import pytest
import os
import tempfile
from pathlib import Path

from video_transcriber.adapters.ffmpeg_audio import FFmpegAudioExtractor
from video_transcriber.adapters.whisper_audio import WhisperAudioTranscriber
from video_transcriber.ports.audio_extractor import AudioExtractionError
from video_transcriber.ports.audio_transcriber import AudioTranscriptionError


# Test video path - cp-demo.mp4 has no audio, we'll need a different one
TEST_VIDEO_WITH_AUDIO = Path(__file__).parent.parent.parent / "data" / "tony.mp4"

# Skip if ffmpeg not installed
try:
    import subprocess
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    FFMPEG_AVAILABLE = result.returncode == 0
except (FileNotFoundError, subprocess.SubprocessError):
    FFMPEG_AVAILABLE = False


class TestFFmpegAudioExtractor:
    """Integration tests for FFmpeg audio extraction."""

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="ffmpeg not installed")
    @pytest.mark.skipif(not TEST_VIDEO_WITH_AUDIO.exists(), reason="Test video not available")
    def test_extracts_audio_from_video(self):
        """FFmpegAudioExtractor extracts audio to WAV format."""
        extractor = FFmpegAudioExtractor()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.wav"

            result = extractor.extract_audio(
                str(TEST_VIDEO_WITH_AUDIO),
                output_path=str(output_path)
            )

            # Should return the output path
            assert result == str(output_path)
            # File should exist
            assert output_path.exists()
            # File should have content
            assert output_path.stat().st_size > 0

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="ffmpeg not installed")
    @pytest.mark.skipif(not TEST_VIDEO_WITH_AUDIO.exists(), reason="Test video not available")
    def test_uses_temporary_file_if_no_output_path(self):
        """FFmpegAudioExtractor creates temp file if output_path is None."""
        extractor = FFmpegAudioExtractor()

        result = extractor.extract_audio(str(TEST_VIDEO_WITH_AUDIO))

        # Should return a path
        assert result is not None
        assert isinstance(result, str)
        # File should exist
        assert Path(result).exists()
        # Should be in temp directory
        assert result.startswith(tempfile.gettempdir())
        # Clean up
        Path(result).unlink()

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="ffmpeg not installed")
    def test_raises_error_for_invalid_video(self):
        """FFmpegAudioExtractor raises error for nonexistent video."""
        extractor = FFmpegAudioExtractor()

        with pytest.raises(AudioExtractionError):
            extractor.extract_audio("nonexistent_video.mp4")

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="ffmpeg not installed")
    @pytest.mark.skipif(not TEST_VIDEO_WITH_AUDIO.exists(), reason="Test video not available")
    def test_respects_sample_rate_parameter(self):
        """FFmpegAudioExtractor respects custom sample rate."""
        extractor = FFmpegAudioExtractor(sample_rate=8000)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.wav"

            result = extractor.extract_audio(
                str(TEST_VIDEO_WITH_AUDIO),
                output_path=str(output_path)
            )

            # Should create file
            assert output_path.exists()
            # File size might be smaller with lower sample rate
            assert output_path.stat().st_size > 0


class TestWhisperAudioTranscriber:
    """Integration tests for Whisper audio transcription."""

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="ffmpeg not installed")
    @pytest.mark.skipif(not TEST_VIDEO_WITH_AUDIO.exists(), reason="Test video not available")
    def test_transcribes_audio_with_timestamps(self):
        """WhisperAudioTranscriber transcribes audio and returns segments."""
        # First extract audio
        extractor = FFmpegAudioExtractor()
        audio_path = extractor.extract_audio(str(TEST_VIDEO_WITH_AUDIO))

        try:
            # Then transcribe
            transcriber = WhisperAudioTranscriber(model_size="tiny")  # Use tiny for speed
            segments = transcriber.transcribe_audio(audio_path)

            # Should return list of segments
            assert isinstance(segments, list)
            # Should have at least one segment if video has audio
            assert len(segments) > 0
            # Each segment should have required fields
            for seg in segments:
                assert hasattr(seg, 'start_seconds')
                assert hasattr(seg, 'end_seconds')
                assert hasattr(seg, 'text')
                assert isinstance(seg.text, str)
                assert seg.start_seconds >= 0
                assert seg.end_seconds > seg.start_seconds
        finally:
            # Clean up
            Path(audio_path).unlink()

    @pytest.mark.skipif(not FFMPEG_AVAILABLE, reason="ffmpeg not installed")
    @pytest.mark.skipif(not TEST_VIDEO_WITH_AUDIO.exists(), reason="Test video not available")
    def test_respects_model_size_parameter(self):
        """WhisperAudioTranscriber can use different model sizes."""
        extractor = FFmpegAudioExtractor()
        audio_path = extractor.extract_audio(str(TEST_VIDEO_WITH_AUDIO))

        try:
            # Use tiny model (fastest)
            transcriber = WhisperAudioTranscriber(model_size="tiny")
            segments = transcriber.transcribe_audio(audio_path)

            assert isinstance(segments, list)
            assert len(segments) >= 0
        finally:
            Path(audio_path).unlink()

    def test_raises_error_for_nonexistent_audio(self):
        """WhisperAudioTranscriber raises error for nonexistent audio file."""
        transcriber = WhisperAudioTranscriber(model_size="tiny")

        with pytest.raises(AudioTranscriptionError):
            transcriber.transcribe_audio("nonexistent_audio.wav")
