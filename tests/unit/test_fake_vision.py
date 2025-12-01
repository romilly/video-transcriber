"""Tests for FakeVisionTranscriber."""

import numpy as np
import pytest

from video_transcriber.testing.fake_vision import FakeVisionTranscriber


class TestFakeVisionTranscriber:
    """Tests for fake vision transcriber."""

    def test_returns_default_response(self):
        """FakeVisionTranscriber returns default response when no prompt mapping exists."""
        fake = FakeVisionTranscriber(default_response="Default text")
        image = np.zeros((100, 100, 3), dtype=np.uint8)

        result = fake.transcribe_image(image, "Any prompt")

        assert result == "Default text"

    def test_returns_response_for_specific_prompt(self):
        """FakeVisionTranscriber returns specific response when prompt matches."""
        fake = FakeVisionTranscriber(
            default_response="Default",
            responses_by_prompt={"OCR this": "Extracted text"}
        )
        image = np.zeros((100, 100, 3), dtype=np.uint8)

        result = fake.transcribe_image(image, "OCR this")

        assert result == "Extracted text"

    def test_tracks_call_count(self):
        """FakeVisionTranscriber tracks how many times it was called."""
        fake = FakeVisionTranscriber()
        image = np.zeros((100, 100, 3), dtype=np.uint8)

        assert fake.call_count == 0

        fake.transcribe_image(image, "First call")
        assert fake.call_count == 1

        fake.transcribe_image(image, "Second call")
        assert fake.call_count == 2

    def test_stores_last_image_and_prompt(self):
        """FakeVisionTranscriber stores the last image and prompt for inspection."""
        fake = FakeVisionTranscriber()
        image1 = np.ones((50, 50, 3), dtype=np.uint8)
        image2 = np.ones((100, 100, 3), dtype=np.uint8) * 255

        fake.transcribe_image(image1, "First prompt")
        assert np.array_equal(fake.last_image, image1)
        assert fake.last_prompt == "First prompt"

        fake.transcribe_image(image2, "Second prompt")
        assert np.array_equal(fake.last_image, image2)
        assert fake.last_prompt == "Second prompt"