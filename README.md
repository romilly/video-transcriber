# video-transcriber

Extracts visually distinct frames from videos and transcribes audio using Whisper.
Creates a portable zip file containing a markdown transcript with slide images in the img sub-directory.

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
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install the package
pip install -e .
```

### Hugging Face

The first time you run the transcriber, it downloads Whisper models from Hugging Face.
This may take several minutes.

You may see this warning:

```
Warning: You are sending unauthenticated requests to the HF Hub.
```

This is harmless. Everything will still work.
To get faster downloads and higher rate limits, you can set up a free Hugging Face token _before the installation_:

1. Create an account at https://huggingface.co
2. Go to Settings → Access Tokens → Create new token (read access is sufficient)
3. Set the environment variable:

```bash
export HF_TOKEN=your_token_here
```

To make it permanent, add that line to `~/.bashrc` or `~/.profile`.

## Usage

### Quick Demo

Run the demo script to process the included test video:

```bash
source venv/bin/activate
python demo_create_zip.py
```

This processes `tests/data/demo.mp4` and creates `tests/data/generated/demo.zip`.

### Python API

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
    model_size="large-v3",     # Whisper model: tiny, base, small, medium, large-v3
    sample_interval=15,        # Check for new slides every N frames (default: 30)
    include_timestamps=True    # Include timestamps in markdown output (default: False)
)
```

## Development

```bash
pip install -e .[test]
pytest
#  pytest --cov=video_transcriber if you want coverage (currently 89%)
```