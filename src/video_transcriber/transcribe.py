"""Simple API for transcribing videos."""

from pathlib import Path

from video_transcriber.adapters.opencv_video import OpenCVVideoAdapter
from video_transcriber.adapters.ffmpeg_audio import FFmpegAudioExtractor
from video_transcriber.adapters.whisper_audio import WhisperAudioTranscriber
from video_transcriber.adapters.zip_markdown_report import ZipMarkdownReportGenerator
from video_transcriber.domain.video_transcriber import VideoTranscriber, TranscriberPorts


def transcribe_video(
    video_path: str,
    output_dir: str,
    model_size: str = "base",
    sample_interval: int = 30,
    include_timestamps: bool = False,
    audio_only: bool = False
) -> str:
    """Transcribe a video and generate a zip file with markdown and frame images.

    Args:
        video_path: Path to the input video file.
        output_dir: Directory where the output zip file will be saved.
        model_size: Whisper model size (tiny, base, small, medium, large-v3).
                   Default is "base".
        sample_interval: Check for new frames every N frames. Default is 30.
        include_timestamps: Whether to include timestamps in the markdown output.
                          Default is False.
        audio_only: If True, only transcribe audio without extracting frames.
                   Default is False.

    Returns:
        Path to the generated zip file.
    """
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_zip = output_dir / f"{video_path.stem}_transcript.zip"

    # Create adapters
    video_reader = OpenCVVideoAdapter()
    audio_extractor = FFmpegAudioExtractor()
    audio_transcriber = WhisperAudioTranscriber(model_size=model_size)

    # Create VideoTranscriber with all ports
    ports = TranscriberPorts(
        video_reader=video_reader,
        audio_extractor=audio_extractor,
        audio_transcriber=audio_transcriber
    )
    transcriber = VideoTranscriber(ports=ports)

    # Process the video
    result = transcriber.process_video(
        str(video_path),
        sample_interval=sample_interval,
        extract_frames=not audio_only
    )

    # Generate zip file
    generator = ZipMarkdownReportGenerator(include_timestamps=include_timestamps)
    zip_path = generator.generate(result, output_path=str(output_zip))

    return zip_path
