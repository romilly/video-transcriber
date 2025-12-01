"""Port for vision-based transcription of images."""

from typing import Protocol
import numpy as np


class VisionTranscriber(Protocol):
    """Port for transcribing visual content from images.

    This abstracts the vision model (Ollama, OpenAI, Claude, etc.) to enable
    testing without external dependencies and easy swapping of providers.
    """

    def transcribe_image(self, image: np.ndarray, prompt: str) -> str:
        """Transcribe text/content from an image.

        Args:
            image: Image as numpy array (OpenCV format: BGR, uint8)
            prompt: Instructions for the vision model on what to extract

        Returns:
            Transcribed text content from the image

        Raises:
            VisionTranscriptionError: If transcription fails
        """
        ...


class VisionTranscriptionError(Exception):
    """Raised when vision transcription fails."""
    pass