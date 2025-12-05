"""Port interfaces for video transcription."""

from video_transcriber.domain.models import Frame
from .video_reader import VideoReader, VideoMetadata

__all__ = ["VideoReader", "VideoMetadata", "Frame"]