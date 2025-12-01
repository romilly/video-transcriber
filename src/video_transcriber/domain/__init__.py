"""Domain models for video transcription."""

from .models import AudioSegment, FrameResult, TranscriptResult
from .frame_comparison import compute_frame_hash, frames_similar

__all__ = [
    "AudioSegment",
    "FrameResult",
    "TranscriptResult",
    "compute_frame_hash",
    "frames_similar"
]