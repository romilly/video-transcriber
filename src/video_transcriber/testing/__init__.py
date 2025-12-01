"""Test doubles (fakes, mocks) for video transcription."""

from .fake_vision import FakeVisionTranscriber
from .fake_video import FakeVideoReader

__all__ = ["FakeVisionTranscriber", "FakeVideoReader"]