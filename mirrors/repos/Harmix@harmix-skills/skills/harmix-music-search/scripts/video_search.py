#!/usr/bin/env python3
"""
Harmix Video Music Search

Search for music that matches video content using the Harmix API.
Extracts frames from video, uploads them, and returns music recommendations.

Requirements:
    - ffmpeg (must be installed and in PATH)
    - requests (pip install requests)

Usage:
    python video_search.py <video_path> [--limit N] [--output-dir DIR]

Example:
    python video_search.py my_video.mp4 --limit 10
"""

import argparse
import subprocess
import requests
import os
import sys
import tempfile
import shutil

API_KEY = "v8mWxAGAFTEFcU9NYGGhDWWbzYXS5e"
API_BASE_URL = "https://api.harmix.ai"


class APILimitReachedError(Exception):
    """Raised when the API limit is reached (403 with code 4005)."""
    pass


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", video_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")
    return float(result.stdout.strip())


def extract_frames(video_path: str, output_dir: str) -> list[str]:
    """
    Extract 5 JPEG frames from video at equal intervals.
    
    Frames are extracted at 0%, 25%, 50%, 75%, and ~100% of duration.
    Each frame is resized to 226x226 pixels.
    """
    os.makedirs(output_dir, exist_ok=True)
    duration = get_video_duration(video_path)
    
    timestamps = [
        0,
        duration * 0.25,
        duration * 0.5,
        duration * 0.75,
        max(0, duration - 0.1)
    ]
    
    frame_paths = []
    for i, ts in enumerate(timestamps):
        output_path = os.path.join(output_dir, f"frame{i+1}.jpeg")
        result = subprocess.run([
            "ffmpeg", "-y", "-ss", str(ts), "-i", video_path,
            "-vframes", "1", "-vf", "scale=226:226", output_path
        ], capture_output=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed for frame {i+1}: {result.stderr.decode()}")
        
        frame_paths.append(output_path)
    
    return frame_paths


def check_api_limit_error(response: requests.Response):
    """Check if response indicates API limit reached (403 with code 4005)."""
    if response.status_code == 403:
        try:
            data = response.json()
            if data.get("detail", {}).get("code") == 4005:
                raise APILimitReachedError(
                    "API limit reached. To continue:\n"
                    "  1. Request your own API key at support@harmix.ai\n"
                    "  2. Or use the web platform at https://web.harmix.ai/"
                )
        except (ValueError, KeyError):
            pass
        response.raise_for_status()


def upload_frames(frame_paths: list[str]) -> str:
    """Upload JPEG frames to Harmix API and return upload_id."""
    files = [("source", (os.path.basename(path), open(path, "rb"), "image/jpeg")) 
             for path in frame_paths]
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/upload",
            headers={"api_key": API_KEY},
            data={"type": "manual-video"},
            files=files
        )
        check_api_limit_error(response)
        response.raise_for_status()
    finally:
        for _, (_, f, _) in files:
            f.close()
    
    result = response.json()
    if result.get("status") != "success" or "upload_id" not in result:
        raise RuntimeError(f"Upload failed: {result}")
    
    return result["upload_id"]


def search_by_video(upload_id: str, limit: int = 5) -> dict:
    """Search for music matching the uploaded video frames."""
    response = requests.post(
        f"{API_BASE_URL}/search",
        headers={"api_key": API_KEY, "Content-Type": "application/json"},
        params={"limit": limit},
        json={"video_reference": {"upload_id": upload_id}}
    )
    check_api_limit_error(response)
    response.raise_for_status()
    return response.json()


def format_track_output(track: dict, index: int) -> str:
    """Format a single track for display."""
    metadata = track.get("metadata", {})
    title = metadata.get("track_title", "Unknown Title")
    artists = ", ".join(metadata.get("artists", ["Unknown Artist"]))
    url = metadata.get("extra_parameters", {}).get("url", "")
    
    output = f"  {index}. \"{title}\" by {artists}"
    if url:
        output += f"\n     {url}"
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Search for music matching video content using Harmix API"
    )
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--limit", type=int, default=5, help="Number of tracks to return (default: 5)")
    parser.add_argument("--output-dir", help="Directory to save extracted frames (uses temp dir if not specified)")
    parser.add_argument("--keep-frames", action="store_true", help="Keep extracted frames after processing")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"Error: Video file not found: {args.video}", file=sys.stderr)
        sys.exit(1)
    
    use_temp_dir = args.output_dir is None
    output_dir = args.output_dir or tempfile.mkdtemp(prefix="harmix_frames_")
    
    try:
        print(f"Extracting frames from: {args.video}")
        frames = extract_frames(args.video, output_dir)
        print(f"Extracted {len(frames)} JPEG frames to: {output_dir}")
        
        print("Uploading frames to Harmix...")
        upload_id = upload_frames(frames)
        print(f"Upload successful. ID: {upload_id}")
        
        print(f"Searching for matching music (limit: {args.limit})...")
        results = search_by_video(upload_id, args.limit)
        
        print(f"\nFound {results.get('tracks_number', 0)} tracks:\n")
        for i, track in enumerate(results.get("tracks", []), 1):
            print(format_track_output(track, i))
            print()
        
    except APILimitReachedError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if use_temp_dir and not args.keep_frames:
            shutil.rmtree(output_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
