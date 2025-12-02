#!/usr/bin/env python3
"""Complete video transcription demo with Claude vision and Whisper audio.

This demonstrates the full hexagonal architecture:
- OpenCV for video reading
- Claude Haiku for visual transcription
- FFmpeg for audio extraction
- Whisper for audio transcription
- VideoTranscriber orchestrating everything

Usage:
    python demo_complete_transcription.py data/tony.mp4
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

from video_transcriber.adapters.opencv_video import OpenCVVideoAdapter
from video_transcriber.adapters.claude_vision import ClaudeVisionAdapter
from video_transcriber.adapters.ffmpeg_audio import FFmpegAudioExtractor
from video_transcriber.adapters.whisper_audio import WhisperAudioTranscriber
from video_transcriber.domain.video_transcriber import (
    VideoTranscriber,
    TranscriberPorts,
    TranscriberConfig
)


def save_transcript(result, output_path):
    """Save transcript to file with frames and audio."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("VIDEO TRANSCRIPTION RESULTS\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Total Frames Extracted: {len(result.frames)}\n")
        f.write(f"Total Audio Segments: {len(result.audio_segments)}\n")
        f.write("=" * 80 + "\n\n")

        for i, frame in enumerate(result.frames, 1):
            minutes = int(frame.timestamp_seconds // 60)
            seconds = int(frame.timestamp_seconds % 60)

            f.write(f"\n{'='*80}\n")
            f.write(f"SLIDE {i}/{len(result.frames)} - [{minutes:02d}:{seconds:02d}] (Frame #{frame.frame_number})\n")
            f.write(f"{'='*80}\n\n")

            # Visual content
            if frame.transcription:
                f.write("📊 VISUAL CONTENT:\n")
                f.write("-" * 80 + "\n")
                f.write(frame.transcription)
                f.write("\n\n")

            # Audio during this slide
            if frame.audio_segments:
                f.write("🎤 AUDIO DURING THIS SLIDE:\n")
                f.write("-" * 80 + "\n")
                for seg in frame.audio_segments:
                    seg_min = int(seg.start_seconds // 60)
                    seg_sec = int(seg.start_seconds % 60)
                    f.write(f"[{seg_min:02d}:{seg_sec:02d}] {seg.text}\n")
                f.write("\n")

        # Complete audio transcript at the end
        if result.audio_segments:
            f.write(f"\n{'='*80}\n")
            f.write("COMPLETE AUDIO TRANSCRIPT\n")
            f.write(f"{'='*80}\n\n")
            for seg in result.audio_segments:
                start_min = int(seg.start_seconds // 60)
                start_sec = int(seg.start_seconds % 60)
                end_min = int(seg.end_seconds // 60)
                end_sec = int(seg.end_seconds % 60)
                f.write(f"[{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}] {seg.text}\n")


def main():
    # Load API key
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        print("❌ ERROR: ANTHROPIC_API_KEY not set in .env file")
        print("Get your API key from: https://console.anthropic.com/settings/keys")
        sys.exit(1)

    # Get video path
    if len(sys.argv) < 2:
        print("Usage: python demo_complete_transcription.py <video_file>")
        print("Example: python demo_complete_transcription.py data/tony.mp4")
        sys.exit(1)

    video_path = sys.argv[1]
    if not Path(video_path).exists():
        print(f"❌ ERROR: Video file not found: {video_path}")
        sys.exit(1)

    print("🎬 Complete Video Transcription Demo")
    print("=" * 80)
    print(f"Video: {video_path}")
    print(f"Vision: Claude Haiku (Anthropic)")
    print(f"Audio: Whisper (base model)")
    print("=" * 80)
    print()

    # Create all adapters
    print("🔧 Initializing adapters...")
    video_reader = OpenCVVideoAdapter()
    vision_transcriber = ClaudeVisionAdapter(
        api_key=api_key,
        model="claude-3-haiku-20240307",
        max_tokens=1024
    )
    audio_extractor = FFmpegAudioExtractor(sample_rate=16000)
    audio_transcriber = WhisperAudioTranscriber(model_size="base")
    print("✅ Adapters initialized\n")

    # Create transcriber with dependency injection
    ports = TranscriberPorts(
        video_reader=video_reader,
        vision_transcriber=vision_transcriber,
        audio_extractor=audio_extractor,
        audio_transcriber=audio_transcriber
    )
    config = TranscriberConfig(
        similarity_threshold=0.92,
        min_frame_interval=15
    )
    transcriber = VideoTranscriber(ports=ports, config=config)

    # Process video
    print("🎥 Processing video...")
    print("   - Extracting distinct frames...")
    print("   - Transcribing visuals with Claude Haiku...")
    print("   - Extracting audio with ffmpeg...")
    print("   - Transcribing audio with Whisper...")
    print("   - Merging timeline...")
    print()

    result = transcriber.process_video(
        video_path,
        sample_interval=30,
        prompt="Transcribe all text visible in this image. Include headings, bullet points, and any other text. Be concise and accurate.",
        transcribe_visuals=True,
        transcribe_audio=True
    )

    print("\n✅ Processing complete!")
    print("=" * 80)
    print(f"📊 Results:")
    print(f"   - Frames extracted: {len(result.frames)}")
    print(f"   - Audio segments: {len(result.audio_segments)}")

    # Calculate approximate API usage
    # Rough estimate: each image is ~100KB PNG, plus prompt tokens
    # Haiku pricing: $0.25 per MTok input, $1.25 per MTok output
    # Very rough estimate for visibility into costs
    estimated_input_tokens = len(result.frames) * 1500  # ~1500 tokens per image
    estimated_output_tokens = sum(len(f.transcription or "") // 4 for f in result.frames)  # ~4 chars per token
    estimated_cost = (estimated_input_tokens * 0.25 / 1_000_000) + (estimated_output_tokens * 1.25 / 1_000_000)

    print(f"   - Estimated Claude API cost: ${estimated_cost:.4f}")
    print(f"     (Input: ~{estimated_input_tokens:,} tokens, Output: ~{estimated_output_tokens:,} tokens)")
    print("=" * 80)
    print()

    # Save results
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    video_name = Path(video_path).stem
    transcript_path = output_dir / f"{video_name}_transcript.txt"

    print(f"💾 Saving transcript to: {transcript_path}")
    save_transcript(result, transcript_path)

    print("\n🎉 Done!")
    print(f"📄 View results: {transcript_path}")
    print()

    # Show preview of first frame
    if result.frames:
        print("📋 Preview of first slide:")
        print("-" * 80)
        first_frame = result.frames[0]
        if first_frame.transcription:
            preview = first_frame.transcription[:300]
            if len(first_frame.transcription) > 300:
                preview += "..."
            print(preview)
        print("-" * 80)

        if first_frame.audio_segments:
            print("\n🎤 Audio during first slide:")
            print("-" * 80)
            for seg in first_frame.audio_segments[:3]:  # Show first 3
                print(f"  {seg.text}")
            if len(first_frame.audio_segments) > 3:
                print(f"  ... and {len(first_frame.audio_segments) - 3} more segments")
            print("-" * 80)


if __name__ == "__main__":
    main()
