# video-transcriber

Extracts visually distinct frames from videos and transcribes audio using Whisper.
Creates a portable zip file containing a markdown transcript with slide images in the img sub-directory.

---
## Features

- **Smart slide detection** - Uses perceptual hashing to capture only distinct frames, not every frame
- **Audio transcription** - Uses Whisper AI locally to transcribe speech to text
- **Timeline merging** - Associates transcribed audio with the corresponding slides
- **Portable output** - Generates a zip file with markdown and images that works anywhere

---
## Requirements

- Python 3.10+
- ffmpeg (for audio extraction)

```bash
# Ubuntu/Debian
apt install ffmpeg

# macOS
brew install ffmpeg

# Windows (using winget)
winget install ffmpeg
```

---
## Installation

### Create a Python Virtual Environment

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install video-transcriber
```

### Create a Conda Python Virtual Environment

```sh
CONDA_ENV_NAME="video-transcription"
PYTHON_VERSION="3.13"
CONDA_ENV="$CONDA_ENV_NAME-${PYTHON_VERSION//[-.]/}"
CONDA_CHANNEL="conda-forge"
echo $CONDA_ENV

# create conda environment
conda create -y \
  python=$PYTHON_VERSION \
  -n $CONDA_ENV \
  -c $CONDA_CHANNEL

# configure conda-pypi integration
conda config --set solver rattler
conda config --append channels conda-pypi
```

Install required packages
```sh
conda install -y \
  -n $CONDA_ENV \
  -c $CONDA_CHANNEL \
  ffmpeg \
  opencv \
  numpy \
  pillow \
  faster-whisper
```

Install required packages for running test scripts:
```sh
conda install -y \
  -n $CONDA_ENV \
  -c $CONDA_CHANNEL \
  pytest \
  pytest-cov \
  notebook \
  build
```

Clone git repository:
```sh
git clone https://github.com/romilly/video-transcriber.git
cd video-transcriber
```

Activate conda environment:
```sh
conda activate video-transcription-313
```

Build and install package into conda environment:
```sh
conda pypi install -e .
```

### Hugging Face

The first time you run the transcriber, it downloads Whisper models from Hugging Face.
This may take several minutes.

You may see this warning:

```
Warning: You are sending unauthenticated requests to the HF Hub.
```

This is harmless. Everything will still work.

---
## Usage

### Shell Script

Use the supplied `video-transcribe.sh` and `video-transcribe.sh` files to download all `*.mp4` video files saved locally.
The text file should contain the full path to the local video file.

```sh
conda activate video-transcription-313
video-transcribe.sh ./video.txt
```

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
    include_timestamps=True,   # Include timestamps in markdown output (default: False)
    audio_only=False           # Transcribe audio only, skip frame extraction (default: False)
)
```

### Audio-Only Mode

For videos where you only need the audio transcript (podcasts, interviews, etc.):

```python
zip_path = transcribe_video(
    "podcast.mp4",
    "output/",
    audio_only=True,
    include_timestamps=True
)
```

This skips frame extraction entirely, producing a zip with just the text transcript.

---
## Development

```bash
git clone https://github.com/romilly/video-transcriber.git
cd video-transcriber
python -m venv venv
source venv/bin/activate
pip install -e .[test]
pytest
```

### Quick Demo

Run the demo script to process the included test video:

```bash
python demo_create_zip.py
```

This processes `tests/data/demo.mp4` and creates `tests/data/generated/demo.zip`.