#!/usr/bin/env python3
"""
speed_ramp.py
Apply a non-linear speed ramp to a video clip (e.g. fast -> slow motion -> fast).
"""

import argparse
import sys
import numpy as np
from moviepy import VideoFileClip

def build_ramp_function(duration, start_speed, mid_speed, end_speed, ramp_start_pct, ramp_end_pct):
    """
    Construct a time-mapping function t_src = f(t_out) that integrates a speed curve.
    
    The speed curve v(t) is:
    - Constant start_speed from 0 to ramp_start_time
    - Linear transition from start_speed to mid_speed between ramp_start_time and mid_time
    - Linear transition from mid_speed to end_speed between mid_time and ramp_end_time
    - Constant end_speed from ramp_end_time to end of output.
    """
    ramp_start_t = duration * ramp_start_pct
    ramp_end_t = duration * ramp_end_pct
    mid_t = (ramp_start_t + ramp_end_t) / 2.0
    
    # We will compute the integral numerically at high resolution to create a lookup table
    # This is extremely robust and avoids solving complex analytical integrals.
    num_steps = 10000
    t_out_grid = np.linspace(0, duration, num_steps)
    v_grid = np.zeros_like(t_out_grid)
    
    for i, t in enumerate(t_out_grid):
        if t <= ramp_start_t:
            v_grid[i] = start_speed
        elif t <= mid_t:
            # Interpolate start_speed -> mid_speed
            frac = (t - ramp_start_t) / (mid_t - ramp_start_t)
            v_grid[i] = start_speed + frac * (mid_speed - start_speed)
        elif t <= ramp_end_t:
            # Interpolate mid_speed -> end_speed
            frac = (t - mid_t) / (ramp_end_t - mid_t)
            v_grid[i] = mid_speed + frac * (end_speed - mid_speed)
        else:
            v_grid[i] = end_speed
            
    # Integrate speed to get source time
    dt = duration / (num_steps - 1)
    t_src_grid = np.zeros_like(t_out_grid)
    current_src_time = 0.0
    for i in range(1, num_steps):
        # Trapezoidal rule integration
        v_avg = (v_grid[i-1] + v_grid[i]) / 2.0
        current_src_time += v_avg * dt
        t_src_grid[i] = current_src_time
        
    # Create the lookup function
    def time_map(t):
        # Map output time t to source time t_src using linear interpolation
        # Clip t to [0, duration]
        t = np.clip(t, 0, duration)
        return np.interp(t, t_out_grid, t_src_grid)
        
    # Calculate what the final source duration needs to be
    required_src_duration = t_src_grid[-1]
    return time_map, required_src_duration

def apply_speed_ramp(video_path, output_path, start_speed, mid_speed, end_speed, ramp_start_pct, ramp_end_pct):
    print(f"Loading video: {video_path}")
    clip = VideoFileClip(video_path)
    src_duration = clip.duration
    
    # We estimate the output duration by integrating typical speed profile
    # Let's solve: How long does the output clip need to be so that we exhaust the source?
    # We can iterate or scale our time map. 
    # An easier approach for users is to specify the output duration or scale the time map
    # so that the maximum source time matches the source clip duration.
    
    # Let's generate a temporary ramp function for a nominal 10-second output
    nominal_out_duration = src_duration / ((start_speed + mid_speed + end_speed) / 3.0)
    
    time_map, nominal_src_used = build_ramp_function(
        nominal_out_duration, start_speed, mid_speed, end_speed, ramp_start_pct, ramp_end_pct
    )
    
    # Scale output duration to match the actual source duration
    scale_factor = src_duration / nominal_src_used
    actual_out_duration = nominal_out_duration * scale_factor
    
    print(f"Original video duration: {src_duration:.2f}s")
    print(f"Target speed ramp output duration: {actual_out_duration:.2f}s")
    
    # Rebuild the scaled ramp function
    final_time_map, final_src_used = build_ramp_function(
        actual_out_duration, start_speed, mid_speed, end_speed, ramp_start_pct, ramp_end_pct
    )
    
    # Adjust final lookup to map [0, actual_out_duration] -> [0, src_duration]
    # fl_time maps output time -> source time
    def fl_time_map(t):
        src_t = final_time_map(t)
        # Prevent float overflow past source duration
        return min(src_t, src_duration - 0.01)
        
    print("Applying speed ramp transformation...")
    # time_transform applies time remapping in MoviePy 2.x
    ramped_clip = clip.time_transform(fl_time_map)
    # Set the duration of the output clip explicitly using with_duration
    ramped_clip = ramped_clip.with_duration(actual_out_duration)
    
    print("Writing speed-ramped video file...")
    ramped_clip.write_videofile(output_path, codec="libx264", audio=False) # Speed ramp strips audio due to complexity
    
    clip.close()
    ramped_clip.close()
    print("Speed ramping complete!")

def main():
    parser = argparse.ArgumentParser(description="Apply non-linear speed ramping to a video clip.")
    parser.add_argument("--video", required=True, help="Path to input video file.")
    parser.add_argument("--output", required=True, help="Path to output video file.")
    parser.add_argument("--start-speed", type=float, default=2.0, help="Initial speed multiplier.")
    parser.add_argument("--mid-speed", type=float, default=0.2, help="Slow-motion speed multiplier.")
    parser.add_argument("--end-speed", type=float, default=2.0, help="Ending speed multiplier.")
    parser.add_argument("--ramp-start", type=float, default=0.2, help="Percentage of clip length where deceleration begins (0.0 to 1.0).")
    parser.add_argument("--ramp-end", type=float, default=0.8, help="Percentage of clip length where acceleration ends (0.0 to 1.0).")
    
    args = parser.parse_args()
    
    if not (0.0 <= args.ramp_start < args.ramp_end <= 1.0):
        print("Error: --ramp-start must be less than --ramp-end, and both must be between 0.0 and 1.0", file=sys.stderr)
        sys.exit(1)
        
    apply_speed_ramp(
        args.video, args.output,
        args.start_speed, args.mid_speed, args.end_speed,
        args.ramp_start, args.ramp_end
    )

if __name__ == "__main__":
    main()
