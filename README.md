# video-transcriber

Extracts visually distinct frames from videos and transcribes audio using Whisper. Creates a portable zip file containing a markdown transcript with embedded slide images.

## Features

- **Smart slide detection** - Uses perceptual hashing to capture only distinct frames, not every frame
- **Audio transcription** - Uses Whisper AI locally to transcribe speech to text
- **Timeline merging** - Associates transcribed audio with the corresponding slides
- **Portable output** - Generates a zip file with markdown and images that works anywhere

## Requirements

- Python 3.10+
- ffmpeg (for audio extraction)

```bash
# Ubuntu/Debian
apt install ffmpeg

# macOS
brew install ffmpeg
```

## Installation

```bash
pip install -e .
```

## Usage

```python
from video_transcriber.transcribe import transcribe_video

zip_path = transcribe_video("my-presentation.mp4", "output/")
```

The output zip file contains:
```
output/my-presentation_transcript.zip
├── transcript.md
└── img/
    ├── frame_000.png
    ├── frame_001.png
    └── ...
```

### Options

```python
zip_path = transcribe_video(
    "my-presentation.mp4",
    "output/",
    model_size="large-v3",  # Whisper model: tiny, base, small, medium, large-v3
    sample_interval=15      # Check for new slides every N frames (default: 30)
)
```

## Development

```bash
pip install -e .[test]
pytest
```