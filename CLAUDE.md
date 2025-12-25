# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LinuxHandController is a computer vision project that uses hand gestures to control functions on Linux. The project uses MediaPipe for hand tracking and OpenCV for video processing.

## Development Environment

This project uses `uv` for Python package management with Python 3.13.

**Setup:**
```bash
# Sync dependencies (install/update based on uv.lock)
uv sync

# Run the application
uv run main.py
```

## Key Dependencies

- **MediaPipe** (≥0.10.31): Hand landmark detection and tracking
- **OpenCV** (≥4.12.0.88): Video capture and display

## Architecture

### Single-Module Structure

The entire application currently lives in `main.py` - a straightforward video processing loop.

### Core Components

1. **Hand Landmarker Initialization** (lines 12-23)
   - Uses the `hand_landmarker.task` model file (required, ~7.6MB)
   - Configured for VIDEO running mode (not LIVE_STREAM or IMAGE)
   - Detects up to 2 hands simultaneously
   - Confidence thresholds set to 0.5 for detection, presence, and tracking

2. **Video Processing Loop** (lines 30-86)
   - Captures from camera index 2 (`cv2.VideoCapture(2)`)
   - Frames are horizontally flipped for mirror effect
   - Processes frames with timestamps in milliseconds
   - Results contain `hand_landmarks` and `handedness` (Left/Right classification)

3. **Hand Landmark Data Structure**
   - Each hand has 21 landmarks (MediaPipe standard)
   - Landmark 0 is the wrist (used for label positioning)
   - Coordinates are normalized (0-1) and must be multiplied by frame dimensions
   - Left hand rendered in green (0, 255, 0), right hand in red (0, 0, 255)

### Current Functionality

- Real-time hand tracking visualization
- FPS counter (top-left)
- Hand count display (top-left)
- Handedness labels (Left/Right) displayed above each wrist
- **Volume control**: Right hand claw + palm rotation
- **Brightness control**: Left hand claw + palm rotation
- Press 'q' to quit

### Gesture Control Details

**Claw Detection** (distance-based):
- Fingertips must be clustered together (avg distance < 0.15)
- Fingertips must be close to palm center (distance < 0.20)
- At least 3 fingers must meet proximity requirement

**Rotation Tracking**:
- Uses index-pinky MCP vector angle for stability
- Implements angle unwrapping to prevent -180°/+180° jumps
- Accumulates rotation continuously (can exceed ±180°)
- Resets when claw gesture is released

**Control Mapping**:
- Deadzone: ±30° (no change in this range)
- Full rotation range: -180° to +180°
- Exponential moving average (alpha=0.3) for smoothing
- Rate limited to ~7 updates/second (150ms intervals)

### System Requirements

- **brightnessctl** must be installed: `sudo apt install brightnessctl`
- User must be in `video` group: `sudo usermod -a -G video $USER` (then log out/in)
- PulseAudio must be running for volume control

### Coding Design Choices

- The more modular the better: opt to create separate files or turn existing code into functions and classes if easier to implement everything
- There will be more features in the future
- CUDA is available for use if machine learning is necessary

## Important Notes

- The `hand_landmarker.task` model file must be present in the project root
- Camera index is hardcoded to 2 - adjust `cv2.VideoCapture(2)` if using a different camera
- MediaPipe's VIDEO mode requires monotonically increasing timestamps
- The landmarker instance must be properly closed (`landmarker.close()`) to avoid resource leaks
