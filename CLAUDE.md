# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**video-transcriber** - Extracts visually distinct frames from videos and transcribes both visual content (slides/presentations) and audio using local LLMs and Whisper.

## Core Architecture

### Current State
- **notebooks/spike.ipynb** - Contains the working `VideoTranscriber` class implementation (spike/prototype code)
- **src/video_transcriber/** - Package structure exists but is mostly empty; code needs to be moved from notebook
- **tests/** - Test structure exists with `data/` and `output/` subdirectories

### Key Components
The `VideoTranscriber` class (currently in notebook) handles:
1. **Frame extraction** - Uses perceptual hashing to detect distinct frames/slides, with configurable ignore regions for presenter windows
2. **Visual transcription** - Uses Ollama API with vision models (LLaVA) to transcribe slide content
3. **Audio extraction** - Uses ffmpeg to extract audio from video
4. **Audio transcription** - Uses faster-whisper (local Whisper model) for speech-to-text
5. **Timeline merging** - Associates audio segments with corresponding frames based on timestamps

### Key Dependencies
- **opencv-python** - Video processing and frame extraction
- **numpy** - Image processing and perceptual hashing
- **requests** - Ollama API communication
- **pillow** - Image encoding
- **faster-whisper** - Local audio transcription (CPU/GPU)
- **ffmpeg** (system dependency) - Audio extraction from video

### External Services
- **Ollama** - Must be running locally at `http://localhost:11434` with a vision model (e.g., `llava`) installed

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

# Install package in editable mode (required for development)
pip install -e .

# Install with test dependencies
pip install -e .[test]

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

### TDD Guidelines

- **Write the simplest test that can fail first**
- **Write only enough code to make the test pass**
- **Refactor after each green test while keeping all tests passing**
- **Commit after every successful test cycle**
- **One test per commit** - keeps git history clean and focused
- **Test file naming**: `test_[feature_name].py`
- **Test method naming**: `test_[specific_behavior]`

## Testing Structure

- `tests/data/` - Test input data (videos, etc.)
- `tests/output/` - Test output artifacts

## Installation & Setup

```bash
# Activate virtual environment (required before running any commands)
source venv/bin/activate

# Install package in editable mode
pip install -e .

# Install with all dependencies (including dev/test dependencies)
pip install -e .[test]

# Install Ollama and pull a vision model (required for visual transcription)
# See: https://ollama.ai
ollama pull llava

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
- `ollama_url` - Ollama API endpoint (default: `http://localhost:11434`)
- `vision_model` - Vision model name (default: `llava`)
- `whisper_model` - Whisper model size: `tiny`, `base`, `small`, `medium`, `large-v3` (default: `base`)
- `similarity_threshold` - Frame similarity threshold 0-1 (default: `0.92`) - lower values = more frames captured
- `min_frame_interval` - Minimum frames between captures to avoid transitions (default: `15`)

Ignore regions format: `[(x, y, width, height), ...]` as fractions 0-1 of frame dimensions