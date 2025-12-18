# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**video-transcriber** - Extracts visually distinct frames from videos and transcribes audio using Whisper.

## Core Architecture

### Current State
- **tests/** - Test structure exists with `data/` and `output/` subdirectories

### Key Components
The `VideoTranscriber` class handles:
1. **Frame extraction** - Uses perceptual hashing to detect distinct frames/slides
2. **Audio extraction** - Uses ffmpeg to extract audio from video
3. **Audio transcription** - Uses faster-whisper (local Whisper model) for speech-to-text
4. **Timeline merging** - Associates audio segments with corresponding frames based on timestamps

### Key Dependencies
- **opencv-python** - Video processing and frame extraction
- **numpy** - Image processing and perceptual hashing
- **pillow** - Image encoding
- **faster-whisper** - Local audio transcription (CPU/GPU)
- **ffmpeg** (system dependency) - Audio extraction from video

## Development Approach

**Strict Test-Driven Development (TDD)** - All development follows the Red-Green-Refactor cycle:

1. **Red**: Write a failing test for new functionality
2. **Green**: Write minimal code to make the test pass
3. **Commit**: Commit the passing test and implementation
4. **Refactor** (if needed): Improve test or code while keeping tests green
5. **Retest**: Ensure all tests still pass after refactoring
6. **Commit**: Commit the refactored code
7. **Repeat**: Go back to step 4 for further refactoring or step 1 for next feature

### TDD Workflow Commands

```bash
# Activate virtual environment first (required)
source venv/bin/activate

# TDD Cycle Commands
# 1. Write test, verify it fails
pytest tests/test_new_feature.py::test_specific_function -v

# 2. Run specific test during development
pytest tests/test_new_feature.py::test_specific_function -v

# 3. Run all tests to ensure no regressions
pytest

# 4. Commit after each passing test
git add . && git commit -m "Add feature X with passing test"

# Other useful test commands
pytest -v
pytest -k "test_name_pattern" -v
```

**Note**: The project uses `pytest.ini` to configure the Python path, so you don't need to install the package in editable mode (`pip install -e .`) before running tests. Just activate the venv and run pytest.

### TDD Guidelines

- **Write the simplest test that can fail first**
- **Write only enough code to make the test pass**
- **Refactor after each green test while keeping all tests passing**
- **Commit after every successful test cycle**
- **One test per commit** - keeps git history clean and focused
- **Test file naming**: `test_[feature_name].py`
- **Test method naming**: `test_[specific_behavior]`
- **Never skip tests due to configuration issues** - if test data files or dependencies are missing, tests should fail, not skip. Skipped tests hide problems.

## Testing Structure

- `tests/data/` - Test input data (videos, etc.)
- `tests/output/` - Test output artifacts

## Installation & Setup

```bash
# Activate virtual environment (required before running any commands)
source venv/bin/activate

# Install dependencies (only needed once or when dependencies change)
pip install -e .[test]

# Ensure ffmpeg is installed (required for audio extraction)
# Ubuntu/Debian: apt install ffmpeg
# macOS: brew install ffmpeg
```

## Running the Code

```bash
# Run the spike notebook implementation
jupyter notebook notebooks/spike.ipynb

# Process a video (when code is moved to src/)
python -m video_transcriber <video_file> [output_dir]

# Preview ignore regions for presenter windows
python -m video_transcriber <video_file> --preview
```

## Configuration Options

The `VideoTranscriber` class accepts these key parameters:
- `whisper_model` - Whisper model size: `tiny`, `base`, `small`, `medium`, `large-v3` (default: `base`)
- `similarity_threshold` - Frame similarity threshold 0-1 (default: `0.92`) - lower values = more frames captured
- `min_frame_interval` - Minimum frames between captures to avoid transitions (default: `15`)