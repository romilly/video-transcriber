# Audio Transcription Feature Plan
**Date:** December 1, 2025

## Overview

Add audio extraction and transcription capabilities to the hexagonal architecture, following the same ports and adapters pattern used for vision transcription.

## Current State

✅ **Completed Components:**
- Domain models (`AudioSegment` already exists in `models.py`)
- Vision transcription ports and adapters (Ollama, Claude)
- Video reading ports and adapters (OpenCV)
- Frame comparison and distinct frame extraction
- Core VideoTranscriber use case (without audio support)

🔲 **Missing Components:**
- Audio extraction port and adapters
- Audio transcription port and adapters
- Integration of audio into VideoTranscriber use case
- Timeline merging logic in use case
- Tests for audio functionality

## Architecture Design

### Ports (Protocols)

#### 1. AudioExtractor Protocol
```python
# src/video_transcriber/ports/audio_extractor.py

from typing import Protocol

class AudioExtractor(Protocol):
    """Port for extracting audio from video files."""

    def extract_audio(self, video_path: str, output_path: str | None = None) -> str:
        """Extract audio from video file.

        Args:
            video_path: Path to video file
            output_path: Optional path for output audio file
                        If None, creates temporary file

        Returns:
            Path to extracted audio file (WAV format)

        Raises:
            AudioExtractionError: If extraction fails
        """
        ...
```

#### 2. AudioTranscriber Protocol
```python
# src/video_transcriber/ports/audio_transcriber.py

from typing import Protocol
from video_transcriber.domain.models import AudioSegment

class AudioTranscriber(Protocol):
    """Port for transcribing audio to text."""

    def transcribe_audio(self, audio_path: str) -> list[AudioSegment]:
        """Transcribe audio file to text with timestamps.

        Args:
            audio_path: Path to audio file (WAV format)

        Returns:
            List of AudioSegment with timestamps and text

        Raises:
            AudioTranscriptionError: If transcription fails
        """
        ...
```

### Adapters (Implementations)

#### 1. FFmpegAudioExtractor
```python
# src/video_transcriber/adapters/ffmpeg_audio.py

import subprocess
import tempfile
from pathlib import Path

class AudioExtractionError(Exception):
    """Raised when audio extraction fails."""
    pass

class FFmpegAudioExtractor:
    """Extract audio from video using ffmpeg.

    Converts video audio to WAV format suitable for Whisper:
    - 16kHz sample rate
    - Mono channel
    - PCM 16-bit encoding
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1
    ):
        """Initialize ffmpeg audio extractor.

        Args:
            sample_rate: Output sample rate in Hz (default: 16000)
            channels: Number of audio channels (default: 1 for mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels

    def extract_audio(self, video_path: str, output_path: str | None = None) -> str:
        """Extract audio using ffmpeg subprocess."""
        # Implementation details...
```

#### 2. WhisperAudioTranscriber
```python
# src/video_transcriber/adapters/whisper_audio.py

from faster_whisper import WhisperModel
from video_transcriber.domain.models import AudioSegment

class AudioTranscriptionError(Exception):
    """Raised when audio transcription fails."""
    pass

class WhisperAudioTranscriber:
    """Transcribe audio using faster-whisper.

    Supports all Whisper model sizes:
    - tiny, base, small, medium, large-v3
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "auto",
        compute_type: str = "auto",
        beam_size: int = 5
    ):
        """Initialize Whisper transcriber.

        Args:
            model_size: Whisper model size (tiny/base/small/medium/large-v3)
            device: Device to use (auto/cpu/cuda)
            compute_type: Compute type (auto/int8/float16/float32)
            beam_size: Beam size for decoding
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.beam_size = beam_size
        self._model = None

    def _load_model(self):
        """Lazy-load Whisper model."""
        if self._model is None:
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
        return self._model

    def transcribe_audio(self, audio_path: str) -> list[AudioSegment]:
        """Transcribe audio using Whisper."""
        # Implementation details...
```

### Test Doubles (Fakes)

#### 1. FakeAudioExtractor
```python
# src/video_transcriber/testing/fake_audio.py

class FakeAudioExtractor:
    """Fake audio extractor for testing.

    Returns a pre-configured audio file path without actual extraction.
    """

    def __init__(
        self,
        audio_file_path: str = "/tmp/fake_audio.wav",
        should_fail: bool = False
    ):
        """Initialize fake audio extractor.

        Args:
            audio_file_path: Path to return as extracted audio
            should_fail: If True, raises AudioExtractionError
        """
        self.audio_file_path = audio_file_path
        self.should_fail = should_fail
        self.call_count = 0
        self.last_video_path = None
        self.last_output_path = None

    def extract_audio(self, video_path: str, output_path: str | None = None) -> str:
        """Return configured audio path."""
        self.call_count += 1
        self.last_video_path = video_path
        self.last_output_path = output_path

        if self.should_fail:
            raise AudioExtractionError("Fake extraction failure")

        return output_path or self.audio_file_path
```

#### 2. FakeAudioTranscriber
```python
# src/video_transcriber/testing/fake_audio.py (continued)

from video_transcriber.domain.models import AudioSegment

class FakeAudioTranscriber:
    """Fake audio transcriber for testing.

    Returns pre-configured audio segments without actual transcription.
    """

    def __init__(
        self,
        segments: list[AudioSegment] | None = None,
        should_fail: bool = False
    ):
        """Initialize fake audio transcriber.

        Args:
            segments: Pre-configured segments to return
            should_fail: If True, raises AudioTranscriptionError
        """
        self.segments = segments or []
        self.should_fail = should_fail
        self.call_count = 0
        self.last_audio_path = None

    def transcribe_audio(self, audio_path: str) -> list[AudioSegment]:
        """Return configured segments."""
        self.call_count += 1
        self.last_audio_path = audio_path

        if self.should_fail:
            raise AudioTranscriptionError("Fake transcription failure")

        return self.segments
```

### Domain Logic Updates

#### Update VideoTranscriber Use Case
```python
# src/video_transcriber/domain/video_transcriber.py (updated)

class VideoTranscriber:
    """Core use case for transcribing videos.

    Now supports audio extraction and transcription via dependency injection.
    """

    def __init__(
        self,
        video_reader: VideoReader,
        vision_transcriber: VisionTranscriber,
        audio_extractor: AudioExtractor | None = None,
        audio_transcriber: AudioTranscriber | None = None,
        similarity_threshold: float = 0.92,
        min_frame_interval: int = 15
    ):
        """Initialize with all ports.

        Args:
            video_reader: Port for reading video
            vision_transcriber: Port for transcribing images
            audio_extractor: Optional port for extracting audio (None = no audio)
            audio_transcriber: Optional port for transcribing audio (None = no audio)
            similarity_threshold: Frame similarity threshold
            min_frame_interval: Minimum frames between captures
        """
        self.video_reader = video_reader
        self.vision_transcriber = vision_transcriber
        self.audio_extractor = audio_extractor
        self.audio_transcriber = audio_transcriber
        self.similarity_threshold = similarity_threshold
        self.min_frame_interval = min_frame_interval

    def process_video(
        self,
        video_path: str,
        sample_interval: int = 30,
        prompt: str | None = None,
        transcribe_visuals: bool = True,
        transcribe_audio: bool = True
    ) -> TranscriptResult:
        """Process video with optional audio transcription.

        Args:
            video_path: Path to video file
            sample_interval: Frame sampling interval
            prompt: Custom prompt for visual transcription
            transcribe_visuals: Whether to transcribe visuals
            transcribe_audio: Whether to transcribe audio

        Returns:
            TranscriptResult with frames and audio segments
        """
        # Extract and transcribe audio (if requested and adapters available)
        audio_segments = []
        if transcribe_audio and self.audio_extractor and self.audio_transcriber:
            audio_path = self.audio_extractor.extract_audio(video_path)
            audio_segments = self.audio_transcriber.transcribe_audio(audio_path)
            # Clean up temporary audio file if needed

        # Extract and transcribe frames (existing logic)
        frames = []
        for frame_result in self.extract_distinct_frames(video_path, sample_interval):
            if transcribe_visuals:
                frame_result.transcription = self.vision_transcriber.transcribe_image(
                    frame_result.image, prompt
                )
            frames.append(frame_result)

        # Merge audio with frames based on timestamps
        frames = self._merge_audio_with_frames(frames, audio_segments)

        return TranscriptResult(frames=frames, audio_segments=audio_segments)

    def _merge_audio_with_frames(
        self,
        frames: list[FrameResult],
        audio_segments: list[AudioSegment]
    ) -> list[FrameResult]:
        """Associate audio segments with frames based on timestamps.

        Each frame gets audio segments that start between its timestamp
        and the next frame's timestamp.
        """
        if not audio_segments:
            return frames

        for i, frame in enumerate(frames):
            start_time = frame.timestamp_seconds
            end_time = frames[i + 1].timestamp_seconds if i + 1 < len(frames) else float('inf')

            frame.audio_segments = [
                seg for seg in audio_segments
                if start_time <= seg.start_seconds < end_time
            ]

        return frames
```

## Implementation Plan

### Phase 1: Ports and Error Classes (0.5 hours)

**Tasks:**
1. Create `AudioExtractionError` and `AudioTranscriptionError` exceptions
2. Define `AudioExtractor` protocol in `src/video_transcriber/ports/audio_extractor.py`
3. Define `AudioTranscriber` protocol in `src/video_transcriber/ports/audio_transcriber.py`
4. Update `__init__.py` files for imports

**Tests:**
- No tests needed for protocols (they're just interfaces)
- Will test via concrete implementations

### Phase 2: Test Doubles (1 hour)

**Tasks:**
1. Write failing test for `FakeAudioExtractor`
2. Implement `FakeAudioExtractor` in `src/video_transcriber/testing/fake_audio.py`
3. Write failing test for `FakeAudioTranscriber`
4. Implement `FakeAudioTranscriber` in same file
5. Verify tests pass

**Tests:** `tests/unit/test_fake_audio.py`
- `test_fake_extractor_returns_configured_path`
- `test_fake_extractor_tracks_calls`
- `test_fake_extractor_can_fail`
- `test_fake_transcriber_returns_configured_segments`
- `test_fake_transcriber_tracks_calls`
- `test_fake_transcriber_can_fail`

**Estimated:** 6 unit tests

### Phase 3: Real Adapters (2 hours)

**Tasks:**
1. Write failing test for `FFmpegAudioExtractor`
2. Implement `FFmpegAudioExtractor` in `src/video_transcriber/adapters/ffmpeg_audio.py`
3. Verify integration test passes with real video
4. Write failing test for `WhisperAudioTranscriber`
5. Implement `WhisperAudioTranscriber` in `src/video_transcriber/adapters/whisper_audio.py`
6. Verify integration test passes with real audio

**Tests:** `tests/integration/test_audio_adapters.py`
- `test_ffmpeg_extracts_audio_from_video`
- `test_ffmpeg_respects_custom_output_path`
- `test_ffmpeg_raises_error_for_invalid_video`
- `test_whisper_transcribes_audio_with_timestamps`
- `test_whisper_detects_language`
- `test_whisper_respects_model_size`

**Estimated:** 6 integration tests

### Phase 4: Update VideoTranscriber Use Case (2 hours)

**Tasks:**
1. Write failing test for VideoTranscriber with audio ports
2. Update VideoTranscriber constructor to accept audio ports (optional)
3. Update `process_video` to handle audio transcription
4. Implement `_merge_audio_with_frames` timeline logic
5. Verify all tests pass (existing + new)

**Tests:** `tests/unit/test_video_transcriber_with_audio.py`
- `test_initializes_with_audio_ports`
- `test_process_video_extracts_and_transcribes_audio`
- `test_process_video_without_audio_ports_still_works`
- `test_can_skip_audio_transcription_with_flag`
- `test_merges_audio_segments_with_frames_by_timestamp`
- `test_handles_audio_extraction_failure_gracefully`
- `test_handles_audio_transcription_failure_gracefully`

**Estimated:** 7 unit tests (using fakes)

### Phase 5: End-to-End Test (1 hour)

**Tasks:**
1. Create e2e test using all real adapters
2. Test complete workflow: video → frames + audio → merged result
3. Verify with test video that has audio
4. Update demo scripts to show audio capabilities

**Tests:** `tests/e2e/test_complete_transcription.py`
- `test_complete_video_transcription_with_audio`
- `test_complete_video_transcription_without_audio`

**Estimated:** 2 e2e tests

### Phase 6: Documentation and Examples (0.5 hours)

**Tasks:**
1. Update CLAUDE.md with audio capabilities
2. Create `demo_with_audio.py` showing complete workflow
3. Update progress report

## Test Summary

**Total Estimated Tests:** 21 new tests

### By Type:
- Unit tests (with fakes): 13 tests
- Integration tests (with real adapters): 6 tests
- End-to-end tests (complete workflow): 2 tests

### By Component:
- FakeAudioExtractor: 3 tests
- FakeAudioTranscriber: 3 tests
- FFmpegAudioExtractor: 3 tests
- WhisperAudioTranscriber: 3 tests
- VideoTranscriber with audio: 7 tests
- Complete workflow: 2 tests

## Dependencies

### Already Installed:
- ✅ `faster-whisper` - Already in requirements.txt
- ✅ `subprocess` - Python standard library
- ✅ `tempfile` - Python standard library

### System Dependencies:
- ⚠️ **ffmpeg** - Must be installed on system
  - Ubuntu/Debian: `apt install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Already used in notebook, likely installed

## Backward Compatibility

✅ **Fully backward compatible:**
- Audio ports are **optional** parameters in VideoTranscriber
- Existing code using VideoTranscriber without audio will continue to work
- `transcribe_audio=False` flag allows explicit opt-out
- Tests without audio ports remain unchanged

## Timeline Merging Algorithm

```python
def _merge_audio_with_frames(frames, audio_segments):
    """
    Timeline merging strategy:

    Frame timeline:
    |---- Frame 1 ----|---- Frame 2 ----|---- Frame 3 ----|
    0s               10s               20s               30s

    Audio timeline:
    [Seg A: 0-5s]  [Seg B: 7-12s]  [Seg C: 15-22s]  [Seg D: 25-28s]

    Merged result:
    - Frame 1 gets: Seg A, Seg B (both start before Frame 2)
    - Frame 2 gets: Seg C (starts between Frame 2 and 3)
    - Frame 3 gets: Seg D (starts after Frame 3)

    Rule: Frame N gets all segments where:
        Frame[N].timestamp <= segment.start < Frame[N+1].timestamp

    Last frame gets all remaining segments (end_time = infinity)
    """
    pass
```

## Risk Assessment

### Low Risk:
- ✅ Protocols follow established pattern
- ✅ Adapters mirror notebook implementation
- ✅ Test doubles enable fast unit testing

### Medium Risk:
- ⚠️ ffmpeg system dependency might not be installed
  - Mitigation: Skip integration tests if ffmpeg not found
  - Provide clear installation instructions

- ⚠️ Whisper models are large (can take time to download)
  - Mitigation: Use "tiny" or "base" model for tests
  - Document model sizes and download times

- ⚠️ Audio transcription is slow (CPU-bound)
  - Mitigation: Use fakes for unit tests
  - Keep integration tests minimal
  - Consider pytest markers to skip slow tests

### Migration Strategy:
1. Phase 1-2: Build foundation (ports + fakes) - no risk
2. Phase 3: Add real adapters - test in isolation
3. Phase 4: Update use case - maintain backward compatibility
4. Phase 5: End-to-end validation
5. Phase 6: Documentation and examples

## Success Criteria

✅ **Definition of Done:**
- [ ] All 21 tests passing
- [ ] No breaking changes to existing tests (34 tests still pass)
- [ ] Audio ports are optional (backward compatible)
- [ ] FFmpegAudioExtractor works with test video
- [ ] WhisperAudioTranscriber produces accurate segments
- [ ] Timeline merging correctly associates audio with frames
- [ ] Demo script shows complete audio workflow
- [ ] Documentation updated

## Estimated Total Effort

- Phase 1: Ports and errors - **0.5 hours**
- Phase 2: Test doubles - **1.0 hours**
- Phase 3: Real adapters - **2.0 hours**
- Phase 4: Use case updates - **2.0 hours**
- Phase 5: E2E tests - **1.0 hours**
- Phase 6: Documentation - **0.5 hours**

**Total: 7.0 hours**

## Next Steps

1. Review this plan with user
2. Confirm test video has audio (or identify one that does)
3. Verify ffmpeg is installed on system
4. Begin Phase 1: Define ports and error classes
5. Follow strict TDD: Red → Green → Refactor → Commit

---

**Plan created:** December 1, 2025
**Status:** Ready for implementation
**Estimated completion:** 7 hours of focused work
