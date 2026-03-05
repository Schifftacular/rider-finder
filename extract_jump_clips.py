import cv2
import subprocess
import sys
import argparse
from pathlib import Path
from ultralytics import YOLO

def extract_jump_clips(video_path, output_dir, buffer_seconds=5, gap_threshold=15):
    """
    Extracts clips of horse jumps from a video file.
    
    Args:
        video_path (str): Path to the input video file.
        output_dir (str): Directory to save the extracted clips.
        buffer_seconds (int): Seconds to add before and after the detection event.
        gap_threshold (int): Seconds of no detection to consider a new event.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        print(f"Error: Video file not found at {video_path}")
        return

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Detect Horses
    print("Loading YOLOv8 model...")
    model = YOLO("yolov8n.pt")  # Load pre-trained model

    print(f"Processing video: {video_path}")
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    print(f"Video Info: {total_frames} frames, {fps:.2f} FPS, {duration:.2f} seconds")

    horse_detections = [] # List of timestamps (seconds) where a horse was detected
    
    frame_idx = 0
    # Process every x frame 
    process_interval = 3 

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_idx % process_interval == 0:
            # Run inference
            results = model(frame, verbose=False, classes=[17]) # Class 17 is horse in COCO
            
            # Check if any horse is detected
            if len(results[0].boxes) > 0:
                timestamp = frame_idx / fps
                horse_detections.append(timestamp)
                
            if frame_idx % (100 * process_interval) == 0:
                print(f"Processed {frame_idx}/{total_frames} frames (found {len(horse_detections)} detections)...")

        frame_idx += 1

    cap.release()
    print("Detection complete.")

    if not horse_detections:
        print("No horses detected in the video.")
        return

    # 2. Group Detections into Events
    events = []
    if not horse_detections:
        return

    current_event_start = horse_detections[0]
    current_event_end = horse_detections[0]

    for t in horse_detections[1:]:
        if t - current_event_end > gap_threshold:
            # Gap detected, close current event
            events.append((current_event_start, current_event_end))
            current_event_start = t
            current_event_end = t
        else:
            # Continue current event
            current_event_end = t
    
    # Append the last event
    events.append((current_event_start, current_event_end))

    print(f"Found {len(events)} jump events.")

    # 3. Extract Clips using ffmpeg
    for i, (start, end) in enumerate(events):
        clip_start = max(0, start - buffer_seconds)
        clip_end = min(duration, end + buffer_seconds)
        
        output_filename = output_dir / f"jump_{i+1:03d}.mp4"
        
        print(f"Extracting Clip {i+1}: {clip_start:.2f}s to {clip_end:.2f}s -> {output_filename.name}")
        
        # ffmpeg command
        # -ss before -i for fast seeking
        cmd = [
            "ffmpeg",
            "-y", # Overwrite output files
            "-ss", str(clip_start),
            "-i", str(video_path),
            "-to", str(clip_end - clip_start), #Duration of clip
            "-c", "copy", # Copy stream (fast, no re-encode)
            "-avoid_negative_ts", "1",
            str(output_filename)
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Error extracting clip {i+1}: {e}")

    print(f"Done! {len(events)} clips saved to {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract jump clips from video.")
    parser.add_argument("video_file", help="Path to the video file")
    parser.add_argument("--output_dir", help="Output directory", default=None)
    parser.add_argument("--buffer", type=float, default=5.0, help="Buffer seconds before/after jump")
    parser.add_argument("--gap", type=float, default=15.0, help="Gap threshold seconds")
    
    args = parser.parse_args()
    
    video_path = Path(args.video_file)
    if args.output_dir:
        output_path = Path(args.output_dir)
    else:
        output_path = video_path.parent / "clips"
        
    extract_jump_clips(video_path, output_path, buffer_seconds=args.buffer, gap_threshold=args.gap)
