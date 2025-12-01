"""Tests for fake audio components (test doubles)."""

import pytest

from video_transcriber.testing.fake_audio import FakeAudioExtractor, FakeAudioTranscriber
from video_transcriber.ports.audio_extractor import AudioExtractionError
from video_transcriber.ports.audio_transcriber import AudioTranscriptionError
from video_transcriber.domain.models import AudioSegment


class TestFakeAudioExtractor:
    """Tests for FakeAudioExtractor test double."""

    def test_returns_configured_audio_path(self):
        """FakeAudioExtractor returns configured audio file path."""
        fake = FakeAudioExtractor(audio_file_path="/tmp/test_audio.wav")

        result = fake.extract_audio("dummy_video.mp4")

        assert result == "/tmp/test_audio.wav"

    def test_respects_output_path_parameter(self):
        """FakeAudioExtractor returns output_path if provided."""
        fake = FakeAudioExtractor(audio_file_path="/tmp/default.wav")

        result = fake.extract_audio("dummy_video.mp4", output_path="/tmp/custom.wav")

        assert result == "/tmp/custom.wav"

    def test_tracks_call_count(self):
        """FakeAudioExtractor tracks how many times it was called."""
        fake = FakeAudioExtractor()

        assert fake.call_count == 0

        fake.extract_audio("video1.mp4")
        assert fake.call_count == 1

        fake.extract_audio("video2.mp4")
        assert fake.call_count == 2

    def test_tracks_last_video_path(self):
        """FakeAudioExtractor tracks the last video path."""
        fake = FakeAudioExtractor()

        fake.extract_audio("video1.mp4")
        assert fake.last_video_path == "video1.mp4"

        fake.extract_audio("video2.mp4")
        assert fake.last_video_path == "video2.mp4"

    def test_tracks_last_output_path(self):
        """FakeAudioExtractor tracks the last output path."""
        fake = FakeAudioExtractor()

        fake.extract_audio("video1.mp4", output_path="/tmp/out1.wav")
        assert fake.last_output_path == "/tmp/out1.wav"

        fake.extract_audio("video2.mp4", output_path="/tmp/out2.wav")
        assert fake.last_output_path == "/tmp/out2.wav"

    def test_can_simulate_failure(self):
        """FakeAudioExtractor can simulate extraction failure."""
        fake = FakeAudioExtractor(should_fail=True)

        with pytest.raises(AudioExtractionError):
            fake.extract_audio("dummy_video.mp4")


class TestFakeAudioTranscriber:
    """Tests for FakeAudioTranscriber test double."""

    def test_returns_configured_segments(self):
        """FakeAudioTranscriber returns pre-configured segments."""
        segments = [
            AudioSegment(0.0, 5.0, "Hello world"),
            AudioSegment(5.0, 10.0, "This is a test")
        ]
        fake = FakeAudioTranscriber(segments=segments)

        result = fake.transcribe_audio("/tmp/audio.wav")

        assert len(result) == 2
        assert result[0].text == "Hello world"
        assert result[1].text == "This is a test"

    def test_returns_empty_list_by_default(self):
        """FakeAudioTranscriber returns empty list if no segments configured."""
        fake = FakeAudioTranscriber()

        result = fake.transcribe_audio("/tmp/audio.wav")

        assert result == []

    def test_tracks_call_count(self):
        """FakeAudioTranscriber tracks how many times it was called."""
        fake = FakeAudioTranscriber()

        assert fake.call_count == 0

        fake.transcribe_audio("/tmp/audio1.wav")
        assert fake.call_count == 1

        fake.transcribe_audio("/tmp/audio2.wav")
        assert fake.call_count == 2

    def test_tracks_last_audio_path(self):
        """FakeAudioTranscriber tracks the last audio path."""
        fake = FakeAudioTranscriber()

        fake.transcribe_audio("/tmp/audio1.wav")
        assert fake.last_audio_path == "/tmp/audio1.wav"

        fake.transcribe_audio("/tmp/audio2.wav")
        assert fake.last_audio_path == "/tmp/audio2.wav"

    def test_can_simulate_failure(self):
        """FakeAudioTranscriber can simulate transcription failure."""
        fake = FakeAudioTranscriber(should_fail=True)

        with pytest.raises(AudioTranscriptionError):
            fake.transcribe_audio("/tmp/audio.wav")
