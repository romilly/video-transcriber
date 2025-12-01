"""Integration tests for ClaudeVisionAdapter.

These tests require an Anthropic API key in the .env file.
"""

import numpy as np
import pytest
import os
from pathlib import Path
from dotenv import load_dotenv

from video_transcriber.adapters.claude_vision import ClaudeVisionAdapter

# Load environment variables from .env file
load_dotenv()

# Skip tests if API key not available
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
pytestmark = pytest.mark.skipif(
    not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your_api_key_here",
    reason="ANTHROPIC_API_KEY not set in .env file"
)


class TestClaudeVisionAdapter:
    """Integration tests for Claude vision adapter."""

    def test_transcribes_simple_image(self):
        """ClaudeVisionAdapter can transcribe a simple text image."""
        # Create a simple test image with text (white background, black text)
        image = np.ones((100, 300, 3), dtype=np.uint8) * 255

        adapter = ClaudeVisionAdapter(
            api_key=ANTHROPIC_API_KEY,
            model="claude-3-haiku-20240307"
        )

        result = adapter.transcribe_image(
            image,
            prompt="Describe this image briefly."
        )

        # Should return a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        print(f"\nClaude Haiku response: {result}")

    def test_uses_custom_model(self):
        """ClaudeVisionAdapter respects custom model parameter."""
        image = np.zeros((50, 50, 3), dtype=np.uint8)

        adapter = ClaudeVisionAdapter(
            api_key=ANTHROPIC_API_KEY,
            model="claude-3-haiku-20240307"
        )

        result = adapter.transcribe_image(image, "What do you see?")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_handles_different_image_sizes(self):
        """ClaudeVisionAdapter handles various image sizes."""
        # Medium-sized image (within Claude's 5MB limit)
        medium_image = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)

        adapter = ClaudeVisionAdapter(api_key=ANTHROPIC_API_KEY)

        result = adapter.transcribe_image(
            medium_image,
            "Describe this image."
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_raises_error_for_invalid_api_key(self):
        """ClaudeVisionAdapter raises error with invalid API key."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)

        adapter = ClaudeVisionAdapter(
            api_key="invalid_key_12345",
            model="claude-3-haiku-20240307"
        )

        with pytest.raises(Exception):  # Anthropic SDK will raise an exception
            adapter.transcribe_image(image, "Test prompt")
