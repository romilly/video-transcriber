"""Zip Markdown Report Generator - creates zip files with markdown transcripts and images."""
import zipfile

from video_transcriber.domain.models import TranscriptResult


class ZipMarkdownReportGenerator:
    """Generates a zip file containing markdown transcript and frame images."""

    def __init__(self, include_timestamps: bool = False):
        """
        Initialize the report generator.

        Args:
            include_timestamps: Whether to include timestamps in the markdown output.
                              Defaults to False (timestamps excluded).
        """
        self.include_timestamps = include_timestamps

    def generate(self, result: TranscriptResult, output_path: str) -> str:
        """
        Generate a zip file containing markdown transcript and frame images.

        Args:
            result: The TranscriptResult containing frames and audio segments
            output_path: Path for the output zip file

        Returns:
            str: Path to the generated zip file
        """
        # Create zip file
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Save frame images
            for i, frame in enumerate(result.frames):
                image_filename = f"img/frame_{i:03d}.png"
                image_bytes = frame.to_png_bytes()
                zf.writestr(image_filename, image_bytes)

            # Generate and save markdown
            markdown = self._generate_markdown(result)
            zf.writestr("transcript.md", markdown.encode('utf-8'))

        return output_path

    def _generate_markdown(self, result: TranscriptResult) -> str:
        """
        Generate markdown content from TranscriptResult.

        Creates a timeline-merged format showing slides with their associated audio.
        For audio-only results (no frames), outputs just the audio transcript.

        Args:
            result: The TranscriptResult to convert to markdown

        Returns:
            str: Markdown-formatted transcript
        """
        lines = ["# Video Transcript\n"]

        if not result.frames:
            # Audio-only mode: output audio segments without frame references
            if result.audio_segments:
                return self._generate_audio_only_markdown(result.audio_segments)
            lines.append("No frames extracted from video.\n")
            return "\n".join(lines)

        for i, frame in enumerate(result.frames):
            # Frame header with optional timestamp
            if self.include_timestamps:
                timestamp = self._format_timestamp(frame.timestamp_seconds)
                lines.append(f"## Slide {i + 1} ({timestamp})\n")
            else:
                lines.append(f"## Slide {i + 1}\n")

            # Image link
            lines.append(f"![Slide {i + 1}](img/frame_{i:03d}.png)\n")

            # Audio segments associated with this frame
            if frame.audio_segments:
                lines.append("**Audio:**\n")
                for seg in frame.audio_segments:
                    if self.include_timestamps:
                        start = self._format_timestamp(seg.start_seconds)
                        end = self._format_timestamp(seg.end_seconds)
                        lines.append(f"- [{start} - {end}] {seg.text}\n")
                    else:
                        lines.append(f"- {seg.text}\n")

            lines.append("")  # Blank line between slides

        return "\n".join(lines)

    def _generate_audio_only_markdown(self, audio_segments: list) -> str:
        """
        Generate markdown for audio-only transcripts (no frames).

        Args:
            audio_segments: List of AudioSegment objects

        Returns:
            str: Markdown-formatted audio transcript
        """
        lines = ["# Audio Transcript\n"]

        for seg in audio_segments:
            if self.include_timestamps:
                start = self._format_timestamp(seg.start_seconds)
                end = self._format_timestamp(seg.end_seconds)
                lines.append(f"[{start} - {end}] {seg.text}\n")
            else:
                lines.append(f"{seg.text}\n")

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
