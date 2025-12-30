import os
import math
import subprocess
import json
import time
import re

# Direct FFmpeg Engine - Maximum Speed, Zero Fluff

class VideoProcessor:
    def __init__(self, output_dir="processed"):
        self.output_dir = output_dir
        self.last_error = None
        self.cancelled = False
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Locate binary
        bin_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin'))
        self.ffmpeg = os.path.join(bin_path, 'ffmpeg.exe')
        self.ffprobe = os.path.join(bin_path, 'ffprobe.exe')

    def cancel(self):
        self.cancelled = True

    def _get_video_info(self, path):
        """Get duration and dimensions instantly via ffprobe."""
        try:
            cmd = [
                self.ffprobe, 
                "-v", "error", 
                "-show_entries", "format=duration", 
                "-show_entries", "stream=width,height", 
                "-of", "json", 
                path
            ]
            
            # Hide window
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo)
            data = json.loads(result.stdout)
            
            duration = float(data['format']['duration'])
            width = int(data['streams'][0]['width'])
            height = int(data['streams'][0]['height'])
            
            return duration, width, height
        except:
            return 0, 0, 0

    def _parse_time(self, time_str):
        """Convert HH:MM:SS.mm to seconds."""
        try:
            parts = time_str.split(':')
            return int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
        except:
            return 0.0

    def _monitor_ffmpeg(self, cmd, part_num, total_parts, duration, report):
        """Run FFmpeg and parse stderr for real-time progress."""
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            startupinfo=startupinfo
        )
        
        # Regex for time=00:00:00.00
        time_pattern = re.compile(r"time=(\d{2}:\d{2}:\d{2}\.\d{2})")
        
        start_real = time.time()
        last_report = 0
        
        # Colors (HTML)
        C_WHITE = "#FFFFFF"
        C_DIM = "#888888"
        C_ACCENT = "#0078D4"
        C_GREEN = "#107C10"
        
        while True:
            # Check if user cancelled
            if self.cancelled:
                process.terminate()
                return False
                
            # Read stderr line-by-line (FFmpeg writes progress to stderr)
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
                
            if not line:
                continue
                
            # Parse progress
            match = time_pattern.search(line)
            if match:
                current_pts = self._parse_time(match.group(1))
                now = time.time()
                
                # Throttle updates (max 20 per second for smooth visuals)
                if now - last_report > 0.05:
                    pct = min(int((current_pts / duration) * 100), 100)
                    
                    # Calculate ETA
                    elapsed = now - start_real
                    if current_pts > 0:
                        rate = elapsed / current_pts
                        remaining = duration - current_pts
                        eta = int(remaining * rate)
                    else:
                        eta = 0
                    
                    # Format: Part 1 | 32% | ETA: 12s left
                    # HTML Color Coding
                    msg = (
                        f"<span style='color:{C_WHITE}'>Part {part_num}</span> "
                        f"<span style='color:{C_DIM}'>|</span> "
                        f"<span style='color:{C_ACCENT}'>{pct}%</span> "
                        f"<span style='color:{C_DIM}'>|</span> "
                        f"<span style='color:{C_DIM}'>ETA: {eta}s left</span>"
                    )
                    
                    report(None, msg)
                    last_report = now
        
        return process.poll() == 0

    def segment_video(self, input_path, segment_duration=60, crop_vertical=True, speed_up=False, progress_callback=None):
        self.last_error = None
        self.cancelled = False
        output_files = []
        part_times = []
        
        def report(pct, msg):
            if progress_callback: progress_callback(pct, msg)

        # Colors (HTML)
        C_WHITE = "#FFFFFF"
        C_DIM = "#888888"
        C_GREEN = "#107C10"

        try:
            report(0, "Scanning video...")
            duration, w, h = self._get_video_info(input_path)
            
            if duration == 0:
                report(0, "Error: Could not read video file.")
                return []
            
            # Adjust effective duration if speeding up
            effective_duration = duration / 1.25 if speed_up else duration
            num_segments = math.ceil(effective_duration / segment_duration)
            
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            base_name = "".join(c for c in base_name if c.isalnum() or c in " _-").strip()[:30]
            
            report(5, f"Source: {int(duration)}s | Parts: {num_segments} {'(1.25x Speed)' if speed_up else ''}")

            start_overall = time.time()
            
            for i in range(num_segments):
                if self.cancelled:
                    report(0, "Cancelled.")
                    return output_files
                
                # Calculate time chunks based on ORIGINAL duration
                # If we speed up, we need to grab 1.25x more content to fill the same 60s slot
                chunk_len_src = segment_duration * 1.25 if speed_up else segment_duration
                start_time_src = i * chunk_len_src
                
                if start_time_src >= duration: break
                
                current_len_src = min(chunk_len_src, duration - start_time_src)
                if current_len_src < 1.0: continue

                output_filename = f"{base_name}_part{i+1}.mp4"
                output_path = os.path.join(self.output_dir, output_filename)
                
                # Smart Skip: Check if valid file exists
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1024:
                    report(None, f"Part {i+1} Exists - Skipping Render")
                    output_files.append(output_path)
                    continue
                
                part_start = time.time()
                report(None, f"Part {i+1} Starting...")
                
                # BUILD COMMAND
                cmd = [self.ffmpeg, "-y", "-ss", str(start_time_src), "-t", str(current_len_src), "-i", input_path]
                
                filter_complex = []
                
                # 1. Speed Filter (Must trigger first to affect timestamps)
                if speed_up:
                    # setpts=PTS/1.25 (Speed Visuals), atempo=1.25 (Speed Audio + Pitch Correct)
                    filter_complex.append("setpts=PTS/1.25,atempo=1.25")
                
                # 2. Crop/Scale Filter
                if crop_vertical:
                    filter_complex.append("scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=black")

                # Combine filters
                if filter_complex:
                    cmd.extend(["-filter_complex", ",".join(filter_complex)])
                
                # Encoding Settings
                cmd.extend([
                    "-c:v", "libx264", 
                    "-preset", "ultrafast", 
                    "-crf", "23",
                    "-c:a", "aac", 
                    output_path
                ])
                
                # Execute with Real-Time Monitoring
                success = self._monitor_ffmpeg(cmd, i+1, num_segments, current_part_len, report)
                
                # Record Timing
                dt = time.time() - part_start
                part_times.append(dt)
                
                if success:
                    # Completion Format: Part 1 Complete | 100% | 14.6s
                    msg = (
                        f"<span style='color:{C_WHITE}'>Part {i+1} Complete</span> "
                        f"<span style='color:{C_DIM}'>|</span> "
                        f"<span style='color:{C_GREEN}'>100%</span> "
                        f"<span style='color:{C_DIM}'>|</span> "
                        f"<span style='color:{C_WHITE}'>{dt:.1f}s</span> "
                        f"<span style='color:{C_DIM}'>|</span> "
                        f"<span style='color:{C_DIM}'>Length: {current_part_len:.1f}s</span>"
                    )
                    report(None, msg)
                else:
                    report(None, f"Part {i+1} Failed")
                
                output_files.append(output_path)
                
                # Update Overall Bar
                overall_pct = int(10 + ((i+1) / num_segments) * 90)
                report(overall_pct, None)
            
            # FINAL SUMMARY
            total_time = time.time() - start_overall
            avg_time = sum(part_times)/len(part_times) if part_times else 0
            summary = f"Done! Total: {total_time:.1f}s | Avg: {avg_time:.1f}s/part"
            report(100, summary)
            
            return output_files

        except Exception as e:
            self.last_error = str(e)
            report(0, f"Error: {e}")
            return output_files
