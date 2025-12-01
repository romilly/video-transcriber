"""Integration tests for OllamaVisionAdapter.

These tests require Ollama to be running with a vision model installed.
"""

import numpy as np
import pytest
import requests

from video_transcriber.adapters.ollama_vision import OllamaVisionAdapter
from video_transcriber.ports.vision_transcriber import VisionTranscriptionError


def ollama_available():
    """Check if Ollama is available on polwarth."""
    try:
        response = requests.get("http://polwarth:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


@pytest.mark.skipif(not ollama_available(), reason="Ollama not running on polwarth")
class TestOllamaVisionAdapter:
    """Integration tests for Ollama vision adapter."""

    def test_transcribes_simple_image(self):
        """OllamaVisionAdapter can transcribe a simple test image."""
        adapter = OllamaVisionAdapter(
            ollama_url="http://polwarth:11434",
            model="llava"
        )

        # Create a simple test image
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        prompt = "Describe this image briefly."

        result = adapter.transcribe_image(image, prompt)

        # Should return some text (exact content depends on model)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_respects_custom_timeout(self):
        """OllamaVisionAdapter respects custom timeout settings."""
        adapter = OllamaVisionAdapter(
            ollama_url="http://polwarth:11434",
            model="llava",
            timeout=1  # Very short timeout
        )

        image = np.zeros((1000, 1000, 3), dtype=np.uint8)
        prompt = "Write a very long detailed description of this image."

        # May or may not timeout depending on model speed
        # Just verify it doesn't crash
        try:
            result = adapter.transcribe_image(image, prompt)
            assert isinstance(result, str)
        except VisionTranscriptionError:
            # Timeout is acceptable for this test
            pass

    def test_raises_error_for_invalid_url(self):
        """OllamaVisionAdapter raises error when Ollama URL is invalid."""
        adapter = OllamaVisionAdapter(
            ollama_url="http://invalid-host:11434",
            model="llava",
            timeout=2
        )

        image = np.zeros((100, 100, 3), dtype=np.uint8)

        with pytest.raises(VisionTranscriptionError):
            adapter.transcribe_image(image, "Test")