"""Claude/Anthropic-based vision transcription adapter."""

import base64
import cv2
import numpy as np
from anthropic import Anthropic


class ClaudeVisionAdapter:
    """Vision transcriber using Claude (Anthropic) API.

    Implements the VisionTranscriber protocol using Claude's vision models
    (Haiku, Sonnet, or Opus).
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        max_tokens: int = 1024,
    ):
        """Initialize the Claude vision adapter.

        Args:
            api_key: Anthropic API key
            model: Claude model to use (haiku, sonnet, or opus)
                   - claude-3-haiku-20240307 (fast, cheap)
                   - claude-3-5-sonnet-20241022 (balanced)
                   - claude-3-opus-20240229 (powerful, expensive)
            max_tokens: Maximum tokens in response
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def _encode_image(self, image: np.ndarray) -> tuple[str, str]:
        """Encode image to base64 for Claude API.

        Args:
            image: OpenCV image (BGR format)

        Returns:
            Tuple of (base64_data, media_type)
        """
        # Encode as PNG for lossless compression
        success, buffer = cv2.imencode('.png', image)
        if not success:
            raise ValueError("Failed to encode image")

        # Convert to base64
        base64_data = base64.standard_b64encode(buffer).decode('utf-8')

        return base64_data, "image/png"

    def transcribe_image(self, image: np.ndarray, prompt: str) -> str:
        """Transcribe/describe an image using Claude's vision capabilities.

        Args:
            image: Image as numpy array (OpenCV BGR format)
            prompt: Text prompt describing what to extract from the image

        Returns:
            Transcription text from Claude
        """
        # Encode image
        base64_data, media_type = self._encode_image(image)

        # Create message with vision
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        # Extract text from response
        if message.content and len(message.content) > 0:
            return message.content[0].text

        return ""
