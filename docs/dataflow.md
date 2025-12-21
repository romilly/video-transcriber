# Video Transcriber Dataflow

This document describes the data flow through the video-transcriber application.

## Architecture Overview

The application follows a **Hexagonal Architecture (Ports & Adapters)** pattern with parallel processing pipelines for frames and audio that merge before output generation.

## Dataflow Diagram

```mermaid
flowchart TD
    subgraph Input
        VIDEO[/"Video File<br/>(MP4)"/]
    end

    subgraph Parallel Processing
        direction LR
        subgraph Frame Pipeline
            VR[OpenCVVideoAdapter]
            FS[FrameSelector]
            VR -->|"Iterator[Frame]<br/>every Nth frame"| FS
            FS -->|"perceptual hash<br/>comparison"| FR[/"FrameResult[]<br/>(distinct frames)"/]
        end

        subgraph Audio Pipeline
            AE[FFmpegAudioExtractor]
            AT[WhisperAudioTranscriber]
            AE -->|"WAV file<br/>(16kHz mono)"| AT
            AT -->|"speech-to-text"| AS[/"AudioSegment[]<br/>(timestamped text)"/]
        end
    end

    VIDEO --> VR
    VIDEO --> AE

    subgraph Merge
        TM[Timeline Merger]
        FR --> TM
        AS --> TM
        TM -->|"match audio to frames<br/>by timestamp"| TR[/"TranscriptResult<br/>(frames + audio)"/]
    end

    subgraph Output
        RG[ZipMarkdownReportGenerator]
        TR --> RG
        RG --> ZIP[/"Output ZIP<br/>• transcript.md<br/>• img/frame_*.png"/]
    end

    style VIDEO fill:#e1f5fe
    style ZIP fill:#c8e6c9
    style FR fill:#fff3e0
    style AS fill:#fff3e0
    style TR fill:#ffe0b2
```

## Data Transformations

| Stage | Input | Output |
|-------|-------|--------|
| **Frame Extraction** | Video file | `Iterator[Frame]` (number, timestamp, BGR image) |
| **Frame Selection** | Frame stream | `FrameResult[]` (distinct frames via perceptual hashing) |
| **Audio Extraction** | Video file | WAV file path (temp file) |
| **Transcription** | WAV file | `AudioSegment[]` (start_s, end_s, text) |
| **Timeline Merge** | Frames + Audio | `TranscriptResult` (frames with associated audio) |
| **Report Generation** | TranscriptResult | ZIP with markdown + images |

## Key Components

### Ports (Interfaces)

- **VideoReader** - Reads video frames from file
- **AudioExtractor** - Extracts audio track from video
- **AudioTranscriber** - Converts speech to text

### Adapters (Implementations)

- **OpenCVVideoAdapter** - Uses OpenCV (cv2) for video reading
- **FFmpegAudioExtractor** - Uses ffmpeg subprocess for audio extraction
- **WhisperAudioTranscriber** - Uses faster-whisper for transcription
- **ZipMarkdownReportGenerator** - Creates output ZIP with markdown report

### Domain Models

- **Frame** - Single video frame with image data and perceptual hash
- **AudioSegment** - Timestamped text segment (start, end, text)
- **FrameResult** - Frame with associated audio segments
- **TranscriptResult** - Complete result containing all frames and audio
