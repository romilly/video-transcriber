"""Concrete adapter implementations."""

from .ollama_vision import OllamaVisionAdapter
from .opencv_video import OpenCVVideoAdapter

__all__ = ["OllamaVisionAdapter", "OpenCVVideoAdapter"]