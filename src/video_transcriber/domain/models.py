"""Domain models for video transcription."""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class AudioSegment:
    """A segment of transcribed audio."""
    start_seconds: float
    end_seconds: float
    text: str


@dataclass
class FrameResult:
    """Holds a frame and its transcription."""
    frame_number: int
    timestamp_seconds: float
    image: np.ndarray
    transcription: Optional[str] = None
    audio_segments: list[AudioSegment] = field(default_factory=list)


@dataclass
class TranscriptResult:
    """Complete transcript with visual and audio components."""
    frames: list[FrameResult]
    audio_segments: list[AudioSegment]