# 🐴 Rider Finder

**Automatically extract horse jump clips from raw video footage.**

Rider Finder uses AI-powered object detection (YOLOv8) to scan through video files, identify every moment a horse appears on screen, and automatically cut and save individual jump clips — complete with configurable buffer time before and after each event. No manual scrubbing required.

Built for [RNS Videomedia](https://rns.schifftacular.com).

---

## How It Works

1. **Detect** — YOLOv8 scans every few frames looking for horses (COCO class 17)
2. **Group** — Detections close together are merged into a single "jump event"
3. **Extract** — `ffmpeg` cuts each event into its own clip with buffer padding

---

## Prerequisites

- **Python 3.9+**
- **ffmpeg** installed and on your PATH

### Install ffmpeg

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu / Debian:**
```bash
sudo apt install ffmpeg
```

**Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your PATH.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Schifftacular/rider-finder.git
cd rider-finder
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

**macOS / Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** On first run, Rider Finder will automatically download the YOLOv8 nano model weights (~6 MB). You'll need an internet connection the first time.

---

## Usage

### Basic usage

```bash
python extract_jump_clips.py path/to/your/video.mp4
```

Clips are saved to a `clips/` folder next to your video file by default.

### Custom output directory

```bash
python extract_jump_clips.py path/to/your/video.mp4 --output_dir path/to/output/
```

### Adjust buffer time (seconds before/after each jump)

```bash
python extract_jump_clips.py path/to/your/video.mp4 --buffer 8
```

### Adjust gap threshold (seconds of no detection to split into a new event)

```bash
python extract_jump_clips.py path/to/your/video.mp4 --gap 20
```

### All options combined

```bash
python extract_jump_clips.py path/to/your/video.mp4 \
  --output_dir ./my_clips \
  --buffer 8 \
  --gap 20
```

---

## Arguments

| Argument | Default | Description |
|---|---|---|
| `video_file` | *(required)* | Path to the input video file |
| `--output_dir` | `<video_dir>/clips/` | Directory to save extracted clips |
| `--buffer` | `5.0` | Seconds to pad before and after each detected jump event |
| `--gap` | `15.0` | Seconds of no horse detection to treat as a new separate event |

---

## Output

Clips are named sequentially: `jump_001.mp4`, `jump_002.mp4`, etc.

```
clips/
├── jump_001.mp4
├── jump_002.mp4
└── jump_003.mp4
```

---

## Tips

- **Faster processing:** The script processes every 3rd frame by default, which is a good balance of speed and accuracy. Longer gaps between horses (arena exits, ring changes) are automatically handled by the `--gap` threshold.
- **Short clips getting merged?** Increase `--gap` to split events that are being combined.
- **Missing jumps?** Decrease `--gap` to be more sensitive, or increase `--buffer` to capture more footage around each detection.
- **Supported formats:** Any video format supported by `ffmpeg` (mp4, mov, avi, mkv, mts, etc.)

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'cv2'`**
Make sure your virtual environment is activated and you've run `pip install -r requirements.txt`.

**`ffmpeg: command not found`**
Install ffmpeg (see Prerequisites above) and make sure it's on your system PATH.

**`Error: Video file not found`**
Double-check the path to your video file. Use quotes if the path contains spaces:
```bash
python extract_jump_clips.py "path/to/my video.mp4"
```

**No horses detected / zero clips**
The model may struggle with unusual camera angles or lighting. Try increasing the buffer with `--buffer 10` and ensure the video quality is sufficient for detection.

---

## License

Internal tool — © RNS Videomedia. All rights reserved.
