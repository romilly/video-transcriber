"""Tests for VideoTranscriber with audio transcription support."""

import numpy as np
import pytest

from video_transcriber.domain.video_transcriber import (
    VideoTranscriber,
    TranscriberPorts,
    TranscriberConfig
)
from video_transcriber.domain.models import AudioSegment, FrameResult
from video_transcriber.ports.video_reader import VideoMetadata, Frame
from tests.helpers.fake_video import FakeVideoReader
from tests.helpers.fake_audio import FakeAudioExtractor, FakeAudioTranscriber
from video_transcriber.ports.audio_extractor import AudioExtractionError
from video_transcriber.ports.audio_transcriber import AudioTranscriptionError


class TestVideoTranscriberWithAudio:
    """Tests for VideoTranscriber with audio transcription capabilities."""

    def test_initializes_with_audio_ports(self):
        """VideoTranscriber can be initialized with audio ports."""
        fake_video = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 900, 30.0),
            frames=[]
        )
        fake_audio_extractor = FakeAudioExtractor()
        fake_audio_transcriber = FakeAudioTranscriber()

        ports = TranscriberPorts(
            video_reader=fake_video,
            audio_extractor=fake_audio_extractor,
            audio_transcriber=fake_audio_transcriber
        )
        transcriber = VideoTranscriber(ports=ports)

        assert transcriber.audio_extractor is fake_audio_extractor
        assert transcriber.audio_transcriber is fake_audio_transcriber

    def test_initializes_without_audio_ports(self):
        """VideoTranscriber works without audio ports (backward compatible)."""
        fake_video = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 900, 30.0),
            frames=[]
        )

        ports = TranscriberPorts(
            video_reader=fake_video
            # No audio ports!
        )
        transcriber = VideoTranscriber(ports=ports)

        assert transcriber.audio_extractor is None
        assert transcriber.audio_transcriber is None

    def test_process_video_extracts_and_transcribes_audio(self):
        """VideoTranscriber uses audio ports to extract and transcribe audio."""
        # Setup frames
        frame1 = Frame(0, 0.0, np.zeros((100, 100, 3), dtype=np.uint8))
        frame2 = Frame(30, 1.0, np.ones((100, 100, 3), dtype=np.uint8) * 128)

        fake_video = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 60, 2.0),
            frames=[frame1, frame2]
        )

        # Setup audio
        audio_segments = [
            AudioSegment(0.0, 0.5, "Hello world"),
            AudioSegment(0.5, 1.5, "This is a test")
        ]
        fake_audio_extractor = FakeAudioExtractor(audio_file_path="/tmp/test_audio.wav")
        fake_audio_transcriber = FakeAudioTranscriber(segments=audio_segments)

        ports = TranscriberPorts(
            video_reader=fake_video,
            audio_extractor=fake_audio_extractor,
            audio_transcriber=fake_audio_transcriber
        )
        transcriber = VideoTranscriber(ports=ports)

        result = transcriber.process_video("dummy.mp4", sample_interval=1)

        # Should have extracted audio
        assert fake_audio_extractor.call_count == 1
        assert fake_audio_extractor.last_video_path == "dummy.mp4"

        # Should have transcribed audio
        assert fake_audio_transcriber.call_count == 1
        assert fake_audio_transcriber.last_audio_path == "/tmp/test_audio.wav"

        # Should return audio segments in result
        assert len(result.audio_segments) == 2
        assert result.audio_segments[0].text == "Hello world"
        assert result.audio_segments[1].text == "This is a test"

    def test_can_skip_audio_transcription_with_flag(self):
        """VideoTranscriber can skip audio even when audio ports available."""
        frame1 = Frame(0, 0.0, np.zeros((100, 100, 3), dtype=np.uint8))

        fake_video = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 30, 1.0),
            frames=[frame1]
        )
        fake_audio_extractor = FakeAudioExtractor()
        fake_audio_transcriber = FakeAudioTranscriber(
            segments=[AudioSegment(0.0, 1.0, "This should not appear")]
        )

        ports = TranscriberPorts(
            video_reader=fake_video,
            audio_extractor=fake_audio_extractor,
            audio_transcriber=fake_audio_transcriber
        )
        transcriber = VideoTranscriber(ports=ports)

        result = transcriber.process_video(
            "dummy.mp4",
            sample_interval=1,
            transcribe_audio=False  # Explicitly disable audio
        )

        # Should not have called audio ports
        assert fake_audio_extractor.call_count == 0
        assert fake_audio_transcriber.call_count == 0
        # No audio segments
        assert len(result.audio_segments) == 0

    def test_merges_audio_segments_with_frames_by_timestamp(self):
        """VideoTranscriber associates audio segments with frames based on timestamps."""
        # Create 3 visually distinct frames at different timestamps
        frame1_img = np.zeros((100, 100, 3), dtype=np.uint8)
        frame1_img[:, 50:] = 255  # Left/right split

        frame2_img = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2_img[50:, :] = 255  # Top/bottom split

        frame3_img = np.ones((100, 100, 3), dtype=np.uint8) * 128  # Uniform gray

        frame1 = Frame(0, 0.0, frame1_img)
        frame2 = Frame(300, 10.0, frame2_img)
        frame3 = Frame(600, 20.0, frame3_img)

        fake_video = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 900, 30.0),
            frames=[frame1, frame2, frame3]
        )

        # Create audio segments at various timestamps
        audio_segments = [
            AudioSegment(2.0, 5.0, "Audio during frame 1"),
            AudioSegment(7.0, 9.0, "Audio during frame 1-2 transition"),
            AudioSegment(12.0, 15.0, "Audio during frame 2"),
            AudioSegment(22.0, 25.0, "Audio during frame 3")
        ]
        fake_audio_extractor = FakeAudioExtractor()
        fake_audio_transcriber = FakeAudioTranscriber(segments=audio_segments)

        ports = TranscriberPorts(
            video_reader=fake_video,
            audio_extractor=fake_audio_extractor,
            audio_transcriber=fake_audio_transcriber
        )
        config = TranscriberConfig(
            similarity_threshold=0.51,  # Frames have 50% similarity, need >0.5 threshold
            min_frame_interval=1  # Allow consecutive frames
        )
        transcriber = VideoTranscriber(ports=ports, config=config)

        result = transcriber.process_video("dummy.mp4", sample_interval=1)

        # Frame 1 (0s-10s) should get audio segments that start between 0 and 10
        frame1_audio = result.frames[0].audio_segments
        assert len(frame1_audio) == 2
        assert frame1_audio[0].text == "Audio during frame 1"
        assert frame1_audio[1].text == "Audio during frame 1-2 transition"

        # Frame 2 (10s-20s) should get audio segment that starts at 12s
        frame2_audio = result.frames[1].audio_segments
        assert len(frame2_audio) == 1
        assert frame2_audio[0].text == "Audio during frame 2"

        # Frame 3 (20s-end) should get audio segment that starts at 22s
        frame3_audio = result.frames[2].audio_segments
        assert len(frame3_audio) == 1
        assert frame3_audio[0].text == "Audio during frame 3"

    def test_handles_audio_extraction_failure_gracefully(self):
        """VideoTranscriber continues if audio extraction fails."""
        frame1 = Frame(0, 0.0, np.zeros((100, 100, 3), dtype=np.uint8))

        fake_video = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 30, 1.0),
            frames=[frame1]
        )
        fake_audio_extractor = FakeAudioExtractor(should_fail=True)
        fake_audio_transcriber = FakeAudioTranscriber()

        ports = TranscriberPorts(
            video_reader=fake_video,
            audio_extractor=fake_audio_extractor,
            audio_transcriber=fake_audio_transcriber
        )
        transcriber = VideoTranscriber(ports=ports)

        # Should not raise exception
        result = transcriber.process_video("dummy.mp4", sample_interval=1)

        # Should still have frames
        assert len(result.frames) == 1
        # But no audio segments
        assert len(result.audio_segments) == 0

    def test_handles_audio_transcription_failure_gracefully(self):
        """VideoTranscriber continues if audio transcription fails."""
        frame1 = Frame(0, 0.0, np.zeros((100, 100, 3), dtype=np.uint8))

        fake_video = FakeVideoReader(
            metadata=VideoMetadata(640, 480, 30.0, 30, 1.0),
            frames=[frame1]
        )
        fake_audio_extractor = FakeAudioExtractor()
        fake_audio_transcriber = FakeAudioTranscriber(should_fail=True)

        ports = TranscriberPorts(
            video_reader=fake_video,
            audio_extractor=fake_audio_extractor,
            audio_transcriber=fake_audio_transcriber
        )
        transcriber = VideoTranscriber(ports=ports)

        # Should not raise exception
        result = transcriber.process_video("dummy.mp4", sample_interval=1)

        # Should still have frames
        assert len(result.frames) == 1
        # But no audio segments
        assert len(result.audio_segments) == 0
