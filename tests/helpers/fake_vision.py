"""Fake implementation of VisionTranscriber for testing."""

import numpy as np
from typing import Dict, Optional


class FakeVisionTranscriber:
    """Fake vision transcriber that returns predefined responses.

    This allows testing without a real vision model (Ollama, etc.) running.
    Responses can be configured by prompt or a default can be set.
    """

    def __init__(
        self,
        default_response: str = "Fake transcription",
        responses_by_prompt: Optional[Dict[str, str]] = None
    ):
        """Initialize the fake transcriber.

        Args:
            default_response: Default response for any prompt not in responses_by_prompt
            responses_by_prompt: Map of prompt text to specific responses
        """
        self.default_response = default_response
        self.responses_by_prompt = responses_by_prompt or {}
        self.call_count = 0
        self.last_image: Optional[np.ndarray] = None
        self.last_prompt: Optional[str] = None

    def transcribe_image(self, image: np.ndarray, prompt: str) -> str:
        """Return a predefined transcription based on the prompt.

        Args:
            image: Image to transcribe (stored but not used)
            prompt: Prompt text (used to lookup response)

        Returns:
            Predefined response matching the prompt, or default response
        """
        self.call_count += 1
        self.last_image = image
        self.last_prompt = prompt

        # Return specific response if prompt matches, otherwise default
        return self.responses_by_prompt.get(prompt, self.default_response)