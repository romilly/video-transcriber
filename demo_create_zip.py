#!/usr/bin/env python3
"""Demo: Create a zip file with markdown transcript and frame images from a video.

Usage:
    python demo_create_zip.py
"""

from pathlib import Path

from video_transcriber.adapters.opencv_video import OpenCVVideoAdapter
from video_transcriber.adapters.ffmpeg_audio import FFmpegAudioExtractor
from video_transcriber.adapters.whisper_audio import WhisperAudioTranscriber
from video_transcriber.adapters.zip_markdown_report import ZipMarkdownReportGenerator
from video_transcriber.domain.video_transcriber import VideoTranscriber, TranscriberPorts


def main():
    # Setup paths
    video_filename = "demo"
    video_path = f"tests/data/{video_filename}.mp4"
    output_dir = Path("tests/data/generated")
    output_dir.mkdir(exist_ok=True)

    output_zip = output_dir / f"{video_filename}.zip"

    print(f"🎬 Processing video: {video_path}")
    print(f"📦 Output will be saved to: {output_zip}")
    print()

    # Create adapters
    print("🔧 Setting up adapters...")
    video_reader = OpenCVVideoAdapter()
    audio_extractor = FFmpegAudioExtractor()
    audio_transcriber = WhisperAudioTranscriber(model_size="base")

    # Create VideoTranscriber with all ports
    ports = TranscriberPorts(
        video_reader=video_reader,
        audio_extractor=audio_extractor,
        audio_transcriber=audio_transcriber
    )
    transcriber = VideoTranscriber(ports=ports)

    # Process the video
    print("🎥 Extracting frames and transcribing audio...")
    result = transcriber.process_video(video_path, sample_interval=30)

    print(f"✅ Extracted {len(result.frames)} distinct frames")
    print(f"✅ Transcribed {len(result.audio_segments)} audio segments")
    print()

    # Generate zip file
    print("📝 Generating markdown and creating zip file...")
    generator = ZipMarkdownReportGenerator()
    zip_path = generator.generate(result, output_path=str(output_zip), markdown_filename=f"{video_filename}-transcript.md")

    print(f"🎉 Done! Created: {zip_path}")
    print()
    print("📂 To view the transcript:")
    print(f"   1. Unzip: unzip {zip_path}")
    print(f"   2. View: cat {video_filename}-transcript.md")
    print(f"   3. Or open {video_filename}-transcript.md in your favorite markdown viewer")


if __name__ == "__main__":
    main()
