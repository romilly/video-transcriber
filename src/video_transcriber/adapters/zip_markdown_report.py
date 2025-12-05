"""Zip Markdown Report Generator - creates zip files with markdown transcripts and images."""
import io
import os
import tempfile
import zipfile
from typing import Optional

import cv2
import numpy as np
from PIL import Image

from video_transcriber.domain.models import TranscriptResult


class ZipMarkdownReportGenerator:
    """Generates a zip file containing markdown transcript and frame images."""

    def generate(self, result: TranscriptResult, output_path: Optional[str] = None) -> str:
        """
        Generate a zip file containing markdown transcript and frame images.

        Args:
            result: The TranscriptResult containing frames and audio segments
            output_path: Optional path for the output zip file. If None, creates in temp directory.

        Returns:
            str: Path to the generated zip file
        """
        # Create temp zip if no output path provided
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".zip")
            os.close(fd)

        # Create zip file
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Save frame images
            for i, frame in enumerate(result.frames):
                image_filename = f"img/frame_{i:03d}.png"
                image_bytes = self._encode_image(frame.image)
                zf.writestr(image_filename, image_bytes)

            # Generate and save markdown
            markdown = self._generate_markdown(result)
            zf.writestr("transcript.md", markdown.encode('utf-8'))

        return output_path

    def _encode_image(self, image: np.ndarray) -> bytes:
        """
        Encode numpy image array as PNG bytes.

        Args:
            image: Numpy array representing the image (BGR or RGB format)

        Returns:
            bytes: PNG-encoded image data
        """
        # Convert BGR to RGB (OpenCV uses BGR by default)
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image

        # Convert to PIL Image and encode as PNG
        pil_image = Image.fromarray(image_rgb)
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        return buffer.getvalue()

    def _generate_markdown(self, result: TranscriptResult) -> str:
        """
        Generate markdown content from TranscriptResult.

        Creates a timeline-merged format showing slides with their associated audio.

        Args:
            result: The TranscriptResult to convert to markdown

        Returns:
            str: Markdown-formatted transcript
        """
        lines = ["# Video Transcript\n"]

        if not result.frames:
            lines.append("No frames extracted from video.\n")
            return "\n".join(lines)

        for i, frame in enumerate(result.frames):
            # Frame header with timestamp
            timestamp = self._format_timestamp(frame.timestamp_seconds)
            lines.append(f"## Slide {i + 1} ({timestamp})\n")

            # Image link
            lines.append(f"![Slide {i + 1}](img/frame_{i:03d}.png)\n")

            # Audio segments associated with this frame
            if frame.audio_segments:
                lines.append("**Audio:**\n")
                for seg in frame.audio_segments:
                    start = self._format_timestamp(seg.start_seconds)
                    end = self._format_timestamp(seg.end_seconds)
                    lines.append(f"- [{start} - {end}] {seg.text}\n")

            lines.append("")  # Blank line between slides

        return "\n".join(lines)

    def _format_timestamp(self, seconds: float) -> str:
        """
        Format seconds as MM:SS timestamp.

        Args:
            seconds: Time in seconds

        Returns:
            str: Formatted timestamp (e.g., "1:23" or "12:05")
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
