#!/usr/bin/env python3
"""Create zip files with markdown transcripts and frame images from a list of videos.

Usage:
    python video-transcribe.py videos.txt
    python video-transcribe.py videos.txt --output-dir video-transcription --force
"""

import argparse
from pathlib import Path

from video_transcriber.adapters.opencv_video import OpenCVVideoAdapter
from video_transcriber.adapters.ffmpeg_audio import FFmpegAudioExtractor
from video_transcriber.adapters.whisper_audio import WhisperAudioTranscriber
from video_transcriber.adapters.zip_markdown_report import ZipMarkdownReportGenerator
from video_transcriber.domain.video_transcriber import VideoTranscriber, TranscriberPorts


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process a list of videos from a text file into transcript zip files."
    )
    parser.add_argument(
        "video_list",
        type=Path,
        help="Path to the text file containing video file paths (one per line)."
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("tests/data/generated"),
        help="Directory to save generated zip files (default: tests/data/generated)."
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Re-process videos even if the output zip file already exists."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    video_list_file = args.video_list
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    if not video_list_file.exists():
        print(f"❌ Error: Could not find {video_list_file}")
        return

    # Read non-empty lines from the text file
    with video_list_file.open("r", encoding="utf-8") as f:
        video_paths = [line.strip() for line in f if line.strip()]

    if not video_paths:
        print("⚠️ The video list file is empty.")
        return

    # Create adapters once outside the loop
    print("🔧 Setting up adapters...")
    video_reader = OpenCVVideoAdapter()
    audio_extractor = FFmpegAudioExtractor()
    audio_transcriber = WhisperAudioTranscriber(model_size="large-v3")

    # Create VideoTranscriber with all ports
    ports = TranscriberPorts(
        video_reader=video_reader,
        audio_extractor=audio_extractor,
        audio_transcriber=audio_transcriber
    )
    transcriber = VideoTranscriber(ports=ports)
    generator = ZipMarkdownReportGenerator(include_timestamps=True)

    # Loop through each video in the text file
    for index, raw_path in enumerate(video_paths, start=1):
        video_path = Path(raw_path)
        video_filename = video_path.stem
        output_zip = output_dir / f"{video_filename}.zip"

        print("=" * 50)
        print(f"🎬 [{index}/{len(video_paths)}] Video: {video_path}")

        # Skip if zip already exists (unless --force is used)
        if output_zip.exists() and not args.force:
            print(f"⏭️ Skipping: {output_zip} already exists (use --force to overwrite)")
            continue

        if not video_path.exists():
            print(f"⚠️ Skipping: Source video not found at {video_path}")
            continue

        try:
            print("🎥 Extracting frames and transcribing audio...")
            result = transcriber.process_video(str(video_path), sample_interval=30)

            print(f"✅ Extracted {len(result.frames)} distinct frames")
            print(f"✅ Transcribed {len(result.audio_segments)} audio segments")

            print("📝 Generating markdown and creating zip file...")
            zip_path = generator.generate(
                result,
                output_path=str(output_zip),
                markdown_filename=f"{video_filename}-transcript.md"
            )
            print(f"🎉 Created: {zip_path}")

        except Exception as e:
            print(f"❌ Failed to process {video_path}: {e}")


if __name__ == "__main__":
    main()

