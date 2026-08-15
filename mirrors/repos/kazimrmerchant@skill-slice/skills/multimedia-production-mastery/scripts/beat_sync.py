#!/usr/bin/env python3
"""
beat_sync.py
Analyze an audio file for beats/onsets and cut/stitch video clips to sync with the tempo.
"""

import os
import sys
import argparse
import json
import librosa
import numpy as np
from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip
from moviepy.video.fx import Loop

def detect_beats(audio_path, use_onsets=False):
    """
    Load audio and detect beat timestamps using librosa.
    If use_onsets is True, returns onset strengths for transient-rich tracks.
    """
    print(f"Loading audio from: {audio_path}")
    y, sr = librosa.load(audio_path, sr=None)
    
    if use_onsets:
        print("Detecting onsets...")
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True)
        times = librosa.frames_to_time(onset_frames, sr=sr)
    else:
        print("Detecting beats and tempo...")
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        times = librosa.frames_to_time(beat_frames, sr=sr)
        if isinstance(tempo, np.ndarray):
            tempo_val = float(tempo[0]) if tempo.size > 0 else 0.0
        else:
            tempo_val = float(tempo)
        print(f"Detected tempo: {tempo_val:.2f} BPM")
        
    return times.tolist()

def sync_single_video(video_path, beat_times, output_path):
    """
    Slice a single video file at each beat using MoviePy 2.x.
    """
    print(f"Loading video: {video_path}")
    video = VideoFileClip(video_path)
    video_dur = video.duration
    
    # Filter beats that occur within the video duration
    valid_beats = [0.0] + [t for t in beat_times if t < video_dur] + [video_dur]
    
    print(f"Slicing video into {len(valid_beats)-1} segments based on beats...")
    clips = []
    for i in range(len(valid_beats) - 1):
        start = valid_beats[i]
        end = valid_beats[i+1]
        if end - start < 0.1: # Skip segments that are too short
            continue
        subclip = video.subclipped(start, end)
        clips.append(subclip)
        
    if not clips:
        print("Error: No valid clips generated for beat sync.")
        video.close()
        return

    print("Stitching clips together...")
    final_video = concatenate_videoclips(clips)
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    # Clean up
    video.close()
    for clip in clips:
        clip.close()
    final_video.close()
    print("Synchronization complete!")

def sync_multi_clips(clips_dir, beat_times, output_path, audio_path):
    """
    Stitch together multiple video files from a directory, cutting each to fit between beats,
    and mix with the original audio.
    """
    # Find all video files in directory
    valid_exts = ('.mp4', '.avi', '.mov', '.mkv', '.webm')
    clip_files = sorted([
        os.path.join(clips_dir, f) for f in os.listdir(clips_dir)
        if f.lower().endswith(valid_exts)
    ])
    
    if not clip_files:
        raise ValueError(f"No video clips found in directory: {clips_dir}")
        
    print(f"Found {len(clip_files)} source clips in {clips_dir}")
    
    # We will slice clips to fit between each beat interval
    clips = []
    raw_clips = []
    clip_index = 0
    
    for i in range(len(beat_times) - 1):
        start = beat_times[i]
        end = beat_times[i+1]
        duration = end - start
        
        # Load the next video file (loop back if we run out)
        video_file = clip_files[clip_index % len(clip_files)]
        clip_index += 1
        
        print(f"Mapping beat {i} ({start:.2f}s -> {end:.2f}s) to: {os.path.basename(video_file)}")
        v = VideoFileClip(video_file)
        raw_clips.append(v)
        
        # If the video file is shorter than the beat duration, loop or speed it up.
        # Otherwise, take a subclip starting from 0.0
        if v.duration < duration:
            subclip = v.with_effects([Loop(duration=duration)])
        else:
            subclip = v.subclipped(0, duration)
            
        clips.append(subclip)
        
    if not clips:
        print("Error: No valid clips generated for beat sync.")
        return

    print("Stitching clips together...")
    final_video = concatenate_videoclips(clips)
    
    # Add the original audio
    print(f"Writing stitched video with audio track: {audio_path}")
    final_video.write_videofile(output_path, codec="libx264", audio=audio_path)
    
    # Clean up
    for clip in clips:
        clip.close()
    for r_clip in raw_clips:
        r_clip.close()
    final_video.close()
    print("Multi-clip beat sync complete!")

def main():
    parser = argparse.ArgumentParser(description="Synchronize video cuts to audio beats.")
    parser.add_argument("--audio", required=True, help="Path to input audio file.")
    parser.add_argument("--video", help="Path to a single input video file.")
    parser.add_argument("--dir", help="Path to a directory of video clips to stitch.")
    parser.add_argument("--output", required=True, help="Path to save output video.")
    parser.add_argument("--onset", action="store_true", help="Use onset detection instead of beat tracking.")
    parser.add_argument("--export-beats", help="Path to export beat timestamps as JSON.")
    
    args = parser.parse_args()
    
    beat_times = detect_beats(args.audio, use_onsets=args.onset)
    print(f"Detected {len(beat_times)} beat markers.")
    
    if args.export_beats:
        with open(args.export_beats, "w") as f:
            json.dump(beat_times, f, indent=2)
        print(f"Exported timestamps to {args.export_beats}")
        
    if args.video:
        sync_single_video(args.video, beat_times, args.output)
    elif args.dir:
        sync_multi_clips(args.dir, beat_times, args.output, args.audio)
    else:
        print("Error: You must provide either --video (single file) or --dir (multiple files) to sync.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
