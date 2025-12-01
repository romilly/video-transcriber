# Video Transcriber Hexagonal Architecture Refactoring Plan

## Overview

Refactor the video-transcriber from a monolithic Jupyter notebook prototype into a testable, modular application using hexagonal (ports and adapters) architecture.

**Primary Goal:** Enable testing with mocks/fakes (no Ollama/ffmpeg dependencies required)
**Approach:** Pragmatic TDD (tests alongside refactoring)
**Scope:** Incremental - prioritize VisionTranscriber and VideoReader ports

## Current State

- All code in `notebooks/spike.ipynb` (~450 lines)
- Empty `src/video_transcriber/` (only `__init__.py`)
- No tests yet
- Tight coupling to: OpenCV, Ollama HTTP API, ffmpeg, faster-whisper
- Good domain objects: `AudioSegment`, `FrameResult`, `TranscriptResult`

## Target Architecture

```
Domain Layer (Core Business Logic)
    ↓ depends on ↓
Port Layer (Python Protocols - Abstract Interfaces)
    ↑ implemented by ↑
Adapter Layer (Concrete Implementations + Fakes)
```

## Project Structure

```
src/video_transcriber/
├── domain/
│   ├── models.py                    # AudioSegment, FrameResult, TranscriptResult
│   └── video_transcriber.py        # Core use case orchestrator
├── ports/
│   ├── vision_transcriber.py       # VisionTranscriber protocol
│   └── video_reader.py              # VideoReader protocol
├── adapters/
│   ├── ollama_vision.py             # OllamaVisionAdapter
│   └── opencv_video.py              # OpenCVVideoAdapter
└── testing/
    ├── fake_vision.py               # FakeVisionTranscriber
    └── fake_video.py                # FakeVideoReader

tests/
├── conftest.py                      # Shared fixtures
├── unit/
│   ├── test_domain_models.py
│   └── test_video_transcriber_use_case.py  # Core logic with mocks
├── integration/
│   ├── test_ollama_adapter.py      # Test real Ollama (skip if unavailable)
│   └── test_opencv_adapter.py
└── acceptance/
    └── test_end_to_end.py          # Full pipeline with fakes
```

## Priority Ports

### 1. VisionTranscriber Port (CRITICAL)

**Purpose:** Abstract Ollama API for testing without running Ollama server

**Interface:**
```python
class VisionTranscriber(Protocol):
    def transcribe_image(self, image: np.ndarray, prompt: str) -> str:
        """Transcribe text/content from an image."""
        ...
```

**Implementations:**
- `OllamaVisionAdapter` - Real HTTP API calls with image encoding
- `FakeVisionTranscriber` - Returns predefined responses for testing

### 2. VideoReader Port (CRITICAL)

**Purpose:** Abstract OpenCV for testable frame extraction

**Interface:**
```python
class VideoReader(Protocol):
    def get_metadata(self, video_path: str) -> VideoMetadata:
        """Get video file metadata."""
        ...

    def read_frames(self, video_path: str, sample_interval: int) -> Iterator[Frame]:
        """Read frames from video at specified intervals."""
        ...
```

**Implementations:**
- `OpenCVVideoAdapter` - Real cv2.VideoCapture implementation
- `FakeVideoReader` - Returns synthetic frames without file I/O

### Future Ports (Not Implementing Yet)

Keep as direct implementations for now:
- AudioExtractor (ffmpeg)
- SpeechTranscriber (Whisper)
- OutputWriter (file output)

## Implementation Steps

### Phase 1: Foundation & VisionTranscriber Port

**Step 1:** Extract dataclasses to `domain/models.py`
- Test: Verify dataclass creation, defaults

**Step 2:** Define VisionTranscriber protocol in `ports/vision_transcriber.py`
- Test: Type checking verification

**Step 3:** Create FakeVisionTranscriber in `testing/fake_vision.py`
- Test: Verify fake returns expected results

**Step 4:** Create OllamaVisionAdapter in `adapters/ollama_vision.py`
- Extract Ollama logic and `_encode_image` from notebook
- Test: Integration test with real Ollama (pytest.mark.skipif)

### Phase 2: VideoReader Port

**Step 5:** Define VideoReader protocol with VideoMetadata and Frame classes
- Test: Protocol structure verification

**Step 6:** Create FakeVideoReader with configurable frame sequence
- Test: Verify fake yields expected frames

**Step 7:** Create OpenCVVideoAdapter
- Extract OpenCV logic from notebook
- Test: Integration test with real video file

**Step 8:** Extract frame comparison logic to domain
- Move `_compute_frame_hash`, `_frames_similar` to separate module
- Test: Unit tests for hash computation and similarity

### Phase 3: Core Use Case Refactoring

**Step 9:** Create VideoTranscriber use case with dependency injection
- Constructor accepts ports as parameters
- Test: Initialization

**Step 10:** Implement `extract_distinct_frames` using VideoReader port
- Test: With FakeVideoReader - verify frame filtering logic

**Step 11:** Implement visual transcription using VisionTranscriber port
- Test: With FakeVisionTranscriber - verify frames get transcribed

**Step 12:** Keep audio extraction as direct implementation (for now)
- Copy methods directly into use case
- Test: Integration test with real audio (mark as slow)

**Step 13:** Implement audio-frame merging logic
- Test: Unit test with mock data

**Step 14:** Implement `process_video` orchestration
- Test: Full workflow with all fake adapters

### Phase 4: Integration & Acceptance Testing

**Step 15:** Create pytest fixtures in `tests/conftest.py`

**Step 16:** Write acceptance test with fakes
- Full pipeline without external dependencies

**Step 17:** Write acceptance test with real adapters
- Marked as integration test

**Step 18:** Create factory functions for easy instantiation

### Phase 5: Migration & Cleanup

**Step 19:** Update notebook to use new library

**Step 20:** Update pyproject.toml dependencies

**Step 21:** Create example scripts

**Step 22:** Add documentation and docstrings

## Testing Strategy

### Unit Tests (Fast, No External Dependencies)
- Use fake adapters for all external dependencies
- Test business logic in isolation
- Example: Test frame similarity filtering with FakeVideoReader

### Integration Tests (Real Dependencies)
- Test adapters with real systems
- Use `@pytest.mark.integration`
- Skip if dependencies unavailable: `@pytest.mark.skipif(not ollama_available())`

### Acceptance Tests (Full Pipeline)
- One version with fakes (fast)
- One version with real adapters (slow, CI only)

## Key Architectural Decisions

**Why Protocols over ABC?**
- More Pythonic (duck typing)
- No inheritance required
- Better for testing
- Follows PEP 544

**Why Separate testing/ Directory?**
- Test doubles are part of public API
- Users can use fakes in their tests
- Clear distinction from production adapters

**Why Keep Some Direct Implementations?**
- Pragmatic approach - don't over-engineer
- Audio/whisper less critical initially
- Can port later without breaking changes

## Critical Files (Priority Order)

1. `src/video_transcriber/domain/models.py` - Extract dataclasses from notebook
2. `src/video_transcriber/ports/vision_transcriber.py` - Define VisionTranscriber Protocol
3. `src/video_transcriber/testing/fake_vision.py` - Implement FakeVisionTranscriber
4. `src/video_transcriber/adapters/ollama_vision.py` - Extract Ollama logic
5. `src/video_transcriber/ports/video_reader.py` - Define VideoReader Protocol
6. `src/video_transcriber/testing/fake_video.py` - Implement FakeVideoReader
7. `src/video_transcriber/adapters/opencv_video.py` - Extract OpenCV logic
8. `src/video_transcriber/domain/video_transcriber.py` - Main orchestrator
9. `tests/conftest.py` - Shared fixtures
10. `tests/unit/test_video_transcriber_use_case.py` - Core logic tests

## Estimated Effort

Total: ~9.5 hours for complete implementation
