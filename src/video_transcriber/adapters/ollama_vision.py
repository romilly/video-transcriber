"""Ollama-based vision transcription adapter."""

import base64
import cv2
import numpy as np
import requests
from typing import Optional

from video_transcriber.ports.vision_transcriber import VisionTranscriptionError


class OllamaVisionAdapter:
    """Vision transcriber using Ollama API with vision models.

    Supports any Ollama vision model (llava, bakllava, llava-llama3, etc.).
    """

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "llava",
        image_quality: int = 100,
        use_png: bool = False,
        timeout: int = 300,
    ):
        """Initialize the Ollama vision adapter.

        Args:
            ollama_url: Base URL for Ollama API
            model: Vision model name (llava, bakllava, etc.)
            image_quality: JPEG quality (1-100) when use_png=False
            use_png: Use PNG encoding (lossless but larger)
            timeout: Request timeout in seconds
        """
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self.image_quality = image_quality
        self.use_png = use_png
        self.timeout = timeout

    def _encode_image(self, image: np.ndarray) -> str:
        """Encode image to base64 for Ollama API.

        Args:
            image: Image as numpy array (BGR format)

        Returns:
            Base64-encoded image string
        """
        if self.use_png:
            # PNG: lossless but larger file size
            _, buffer = cv2.imencode('.png', image)
        else:
            # JPEG: configurable quality
            _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, self.image_quality])

        return base64.b64encode(buffer).decode('utf-8')

    def transcribe_image(self, image: np.ndarray, prompt: str) -> str:
        """Transcribe image using Ollama vision model.

        Args:
            image: Image as numpy array (BGR format)
            prompt: Instructions for the vision model

        Returns:
            Transcribed text from the image

        Raises:
            VisionTranscriptionError: If API call fails
        """
        try:
            encoded_image = self._encode_image(image)

            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [encoded_image],
                "stream": False,
            }

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            return response.json().get("response", "")

        except requests.exceptions.RequestException as e:
            raise VisionTranscriptionError(f"Ollama API request failed: {e}") from e
        except Exception as e:
            raise VisionTranscriptionError(f"Vision transcription failed: {e}") from e