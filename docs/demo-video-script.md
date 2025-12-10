# Video-Transcriber Demo Script

**Duration:** ~3-4 minutes
**Target Audience:** Developers, educators, content creators who work with video presentations

---

## Scene 1: Introduction (30 seconds)

**[Screen: Title card or logo]**

**Narration:**

> Ever recorded a presentation or lecture and wished you could easily extract the slides and get a transcript?
>
> Video-transcriber is a Python tool that automatically:
> - Extracts distinct slides from your video
> - Transcribes the audio using AI
> - Combines everything into a neat, portable package

---

## Scene 2: The Problem (20 seconds)

**[Screen: Show a typical presentation video playing]**

**Narration:**

> When you have a recorded presentation, you often need to:
> - Pull out the slides for reference
> - Get a text transcript for accessibility or notes
> - Match what was said to each slide
>
> Doing this by hand is slow, boring, and error-prone. Video-transcriber automates the entire process.

---

## Scene 3: How It Works - Overview (30 seconds)

**[Screen: Simple diagram showing the workflow]**

```
Video File (.mp4)
       │
       ▼
┌──────────────────┐
│ Frame Extraction │  ← Uses perceptual hashing to find distinct slides
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ Audio Extraction │  ← Extracts audio track with ffmpeg
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ Transcription    │  ← Whisper AI converts speech to text
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ Timeline Merge   │  ← Associates speech with corresponding slides
└──────────────────┘
       │
       ▼
   Output.zip
   ├── transcript.md
   └── img/
       ├── frame_000.png
       └── ...
```

**Narration:**

> The tool works in four stages:
> 1. It scans the video and uses perceptual hashing to detect when slides change
> 2. It extracts the audio track
> 3. It runs Whisper locally to transcribe what's being said
> 4. Finally, it merges everything together, matching audio to the right slides

---

## Scene 4: Demo - Running the Tool (30 seconds)

**[Screen: Terminal / code editor]**

**Narration:**

> Let me show you how simple it is to use.

**[Show terminal with code]**

```python
from video_transcriber.transcribe import transcribe_video

zip_path = transcribe_video("my-presentation.mp4", "output/")
```

**Narration:**

> That's it - just two lines of code. Import the function and call it with your video file and output directory.
>
> The tool extracts the slides, transcribes the audio, and generates a zip file with everything inside.

---

## Scene 5: Demo - The Output (45 seconds)

**[Screen: Show the generated zip contents]**

**Narration:**

> Let's look at what we get.

**[Show file explorer opening the zip]**

> The output is a zip file containing a markdown document and an images folder.

**[Show the markdown file]**

```markdown
# Video Transcript

## Slide 1 (0:00)
![Slide 1](img/frame_000.png)

**Audio:**
- [0:00 - 0:45] Welcome everyone to today's presentation.
  We're going to cover three main topics...

## Slide 2 (0:52)
![Slide 2](img/frame_001.png)

**Audio:**
- [0:52 - 1:30] First, let's look at the architecture...
```

**Narration:**

> The markdown shows each slide with its timestamp, the slide image, and the transcribed audio that was spoken while that slide was displayed.
>
> You can open this in any markdown viewer, import it into Obsidian, or convert it to PDF. The images are all included in the zip, so it's completely portable.

---

## Scene 6: Key Features (30 seconds)

**[Screen: Feature list with icons]**

**Narration:**

> A few things that make video-transcriber useful:
>
> **Smart slide detection** - It doesn't just capture every frame. It uses perceptual hashing to find when content actually changes.
>
> **Local processing** - Everything runs on your machine. Your videos never leave your computer.
>
> **Configurable** - You can adjust the similarity threshold, choose different Whisper models for speed or accuracy, and tune the frame detection.

---

## Scene 7: Configuration Options (20 seconds)

**[Screen: Code snippet showing configuration]**

```python
from video_transcriber.transcribe import transcribe_video

# Use a larger Whisper model for better accuracy
zip_path = transcribe_video(
    "my-presentation.mp4",
    "output/",
    model_size="large-v3"
)

# Check for slide changes more frequently
zip_path = transcribe_video(
    "my-presentation.mp4",
    "output/",
    sample_interval=15  # Check every 15 frames instead of 30
)
```

**Narration:**

> You can choose from different Whisper models - from tiny for speed to large for accuracy.
>
> And you can adjust how often it checks for new slides with the sample_interval parameter.

---

## Scene 8: Wrap-up (15 seconds)

**[Screen: GitHub repo / installation instructions]**

```bash
# Install
pip install -e .

# Requires ffmpeg
apt install ffmpeg  # or: brew install ffmpeg
```

**Narration:**

> Video-transcriber is open source and easy to install.
>
> Check out the repository to get started, and let us know what you build with it!

---

## Production Notes

### Visuals to Prepare
- Title card/logo
- Workflow diagram (can use the ASCII art above or create a proper graphic)
- Screen recording of running the demo code
- Screen recording of exploring the output zip file
- Feature icons or slides

### Sample Video Needed
- A short (2-3 minute) presentation video with clear slides and narration
- Ideally something that will produce 5-10 distinct slides

### Technical Setup
- Terminal with clear, readable font size
- Code editor with good syntax highlighting
- File explorer to show zip contents
- Markdown viewer to show the transcript

### Timing Summary
| Scene | Duration |
|-------|----------|
| 1. Introduction | 30s |
| 2. The Problem | 20s |
| 3. How It Works | 30s |
| 4. Demo - Running | 30s |
| 5. Demo - Output | 45s |
| 6. Key Features | 30s |
| 7. Configuration | 20s |
| 8. Wrap-up | 15s |
| **Total** | **~3.5 minutes** |
