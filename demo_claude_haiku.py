#!/usr/bin/env python3
"""Demo script showing how to use Claude Haiku for video transcription.

This demonstrates the power of the hexagonal architecture - we can swap
Ollama for Claude just by changing the adapter!

Usage:
    python demo_claude_haiku.py
"""

import os
from dotenv import load_dotenv

from video_transcriber.adapters.opencv_video import OpenCVVideoAdapter
from video_transcriber.adapters.claude_vision import ClaudeVisionAdapter
from video_transcriber.domain.video_transcriber import VideoTranscriber

# Load API key from .env
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key or api_key == "your_api_key_here":
    print("ERROR: Please set ANTHROPIC_API_KEY in your .env file")
    print("Get your API key from: https://console.anthropic.com/settings/keys")
    exit(1)

# Create adapters
video_reader = OpenCVVideoAdapter()
vision_transcriber = ClaudeVisionAdapter(
    api_key=api_key,
    model="claude-3-haiku-20240307",  # Fast and economical
    max_tokens=1024
)

# Create transcriber with dependency injection
transcriber = VideoTranscriber(
    video_reader=video_reader,
    vision_transcriber=vision_transcriber,
    similarity_threshold=0.92,
    min_frame_interval=15
)

# Process video
print("Processing video with Claude Haiku...")
print("=" * 60)

video_path = "data/cp-demo.mp4"

# Extract and transcribe frames
results = transcriber.process_video(
    video_path,
    sample_interval=30,
    prompt="Transcribe all text visible in this presentation slide. Include headings, bullet points, and any other text. Format it clearly.",
    transcribe_visuals=True
)

print(f"\nExtracted {len(results.frames)} distinct frames")
print("=" * 60)

# Display results
for i, frame in enumerate(results.frames, 1):
    minutes = int(frame.timestamp_seconds // 60)
    seconds = int(frame.timestamp_seconds % 60)

    print(f"\n{'='*60}")
    print(f"Frame {i}/{len(results.frames)} - [{minutes:02d}:{seconds:02d}] (Frame #{frame.frame_number})")
    print(f"{'='*60}")

    if frame.transcription:
        print(frame.transcription)
    else:
        print("(No transcription)")

    print()

print("\n" + "=" * 60)
print("✅ Demo complete!")
print(f"✅ Processed with Claude Haiku (Anthropic)")
print(f"✅ Total frames: {len(results.frames)}")
print("=" * 60)

# Compare with Ollama
print("\n💡 TIP: To use Ollama instead, just swap the adapter:")
print("   vision_transcriber = OllamaVisionAdapter(")
print("       ollama_url='http://polwarth:11434',")
print("       vision_model='llava'")
print("   )")
print("\n   The rest of the code stays exactly the same!")
print("   That's the power of hexagonal architecture! 🎉")
