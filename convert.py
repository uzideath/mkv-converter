#!/usr/bin/env python3
import os
import re
import sys
import shutil
import subprocess
import time

# ---- ANSI Escape Sequences for Terminal Colors & Styles ----
# These codes are supported on most modern terminals (Windows 10+, Linux, macOS).
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

def get_video_duration(input_file):
    """
    Use ffprobe to get the total duration (in seconds) of a video file.
    If successful, returns a float representing the total seconds.
    If unsuccessful, returns None.
    
    Why do we do this?
    - We need the total duration in order to display an accurate progress bar.
    - ffprobe is part of the FFmpeg suite, so make sure FFmpeg is installed and in your PATH.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_file
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration_str = result.stdout.strip()
        return float(duration_str) if duration_str else None
    except subprocess.CalledProcessError:
        # This can happen if ffprobe can't read the file or if FFmpeg isn't installed properly.
        return None

def seconds_from_timecode(time_str):
    """
    Given a time string in the format HH:MM:SS.xxx (e.g. '00:01:23.456'),
    convert it to total seconds as a float (e.g. 83.456).
    
    FFmpeg prints progress lines like:
      time=00:01:23.45
    We parse this to figure out how many seconds have elapsed in the encoding process.
    """
    h, m, s = time_str.split(":")
    if "." in s:
        secs, millis = s.split(".")
        millis = float("0." + millis)
    else:
        secs, millis = s, 0.0
    return int(h) * 3600 + int(m) * 60 + int(secs) + millis

def run_ffmpeg_with_progress(input_file, output_file):
    """
    Runs FFmpeg in a subprocess, parsing stderr to extract progress,
    and displays:
      1) A progress bar showing % completion.
      2) A rotating spinner for a simple animation.
      3) Colorful status text.

    NVENC SETTINGS:
    - -c:v h264_nvenc: Uses NVIDIA’s NVENC hardware encoder for H.264.
    - -rc constqp:     Constant QP (quantization parameter) rate control.
    - -qp 18:          QP = 18 typically yields high quality (the lower the QP, the higher the quality
                       and the larger the file).
                       * 0 can be “lossless” on some GPUs, but huge files.
                       * 23 is a bit more compressed but smaller size.
    - -preset slow:    Tells NVENC to spend more time optimizing compression.
                       * "medium", "fast", "hq", "ll", etc. are also possible.
                       * "slow" yields better quality but slower speeds.

    AUDIO:
    - -c:a copy:       Copies the audio track without re-encoding. If you want to convert audio (e.g., to AAC),
                       replace with "-c:a aac -b:a 192k" or similar.

    OVERWRITING OUTPUT:
    - -y:              Overwrites the output file if it already exists.

    If you prefer HEVC (H.265) for better compression, you can change:
      -c:v h264_nvenc  => -c:v hevc_nvenc
    (Your NVIDIA GPU must support it.)
    """
    total_duration = get_video_duration(input_file)
    if not total_duration or total_duration <= 0:
        print(f"{RED}Could not determine video duration for '{input_file}'.{RESET}")
        return

    # Build your FFmpeg command line
    command = [
        "ffmpeg",
        "-hide_banner",         # Minimizes FFmpeg banner output
        "-stats",               # Periodically prints progress info to stderr
        "-hwaccel", "cuda",     # Hardware acceleration via CUDA (NVENC)
        "-i", input_file,       # Input file
        "-c:v", "h264_nvenc",   # Encode H.264 with NVENC
        "-rc", "constqp",       # Constant QP mode
        "-qp", "18",            # QP value for controlling quality
        "-preset", "slow",      # "slow" = better quality, slower speed
        "-c:a", "copy",         # Copy audio (no re-encoding)
        "-y",                   # Overwrite existing output
        output_file
    ]

    print(f"{GREEN}Converting '{input_file}' to '{output_file}' using NVIDIA NVENC...{RESET}\n")

    # Start FFmpeg as a subprocess
    process = subprocess.Popen(
        command,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        universal_newlines=True
    )

    # Regex to capture lines like "time=00:01:23.45"
    time_pattern = re.compile(r"time=(\d+:\d+:\d+(?:\.\d+)?)")

    # For a nice progress bar, figure out how wide the terminal is
    try:
        terminal_width = shutil.get_terminal_size().columns
    except:
        terminal_width = 80
    bar_width = min(50, terminal_width - 20)

    # Simple ASCII spinner frames
    spinner_frames = ["|", "/", "-", "\\"]
    spinner_index = 0

    def draw_progress(current_sec):
        """
        Render a colored progress bar and a spinner in one line.
        
        current_sec: how many seconds FFmpeg has processed.
        """
        nonlocal spinner_index
        progress = min(current_sec / total_duration, 1.0)
        filled_length = int(round(bar_width * progress))
        bar = "#" * filled_length + "-" * (bar_width - filled_length)
        percent = int(round(progress * 100))

        spinner_char = spinner_frames[spinner_index]
        spinner_index = (spinner_index + 1) % len(spinner_frames)

        # Build the terminal line with color
        line = (
            f"\r{GREEN}[{bar}]{RESET} "    # The green progress bar
            f"{YELLOW}{percent}%{RESET} "  # The percentage in yellow
            f"{MAGENTA}{spinner_char}{RESET}"  # The spinner character in magenta
        )
        sys.stdout.write(line)
        sys.stdout.flush()

    try:
        # Read FFmpeg stderr line by line
        while True:
            line = process.stderr.readline()
            if not line:
                # If there's no more output and the process ended, break.
                if process.poll() is not None:
                    break
                continue

            # Look for time=HH:MM:SS.xxx
            match = time_pattern.search(line)
            if match:
                current_sec = seconds_from_timecode(match.group(1))
                draw_progress(current_sec)

        process.wait()
    except KeyboardInterrupt:
        # If user hits Ctrl+C (or another interrupt), stop gracefully
        process.terminate()
        print(f"\n{RED}Process canceled by user.{RESET}")
        sys.exit(1)

    # Ensure final progress bar is at 100%
    draw_progress(total_duration)
    print()  # new line

    # Check exit code
    if process.returncode == 0:
        print(f"{GREEN}Conversion completed successfully!{RESET}")
    else:
        print(f"{RED}Conversion failed. Please check the error messages above.{RESET}")

def main():
    """
    The main function runs interactively:
      1) Asks for the input file path (MKV). If invalid, prompts again.
      2) Asks for the output file path (MP4).
      3) If user types 'cancel' at any prompt, we exit with a message.
      4) Launches the FFmpeg conversion with a progress bar.
    """
    print(f"{BOLD}Welcome to the MKV-to-MP4 Converter (GPU-Accelerated){RESET}")
    print("Type 'cancel' at any prompt to exit.\n")

    # Prompt for the input file until we get a valid path or "cancel"
    while True:
        input_path = input(f"{BLUE}Enter the path of the input .mkv file:{RESET} ").strip()
        if input_path.lower() == "cancel":
            print(f"{RED}Process canceled.{RESET}")
            sys.exit(0)

        if os.path.isfile(input_path):
            # Valid file
            break
        else:
            print(f"{RED}File does not exist. Please try again.{RESET}")

    # Prompt for the output file
    while True:
        output_path = input(f"{BLUE}Enter the desired output .mp4 file path:{RESET} ").strip()
        if output_path.lower() == "cancel":
            print(f"{RED}Process canceled.{RESET}")
            sys.exit(0)
        # We won't do deep validation of the path; just accept it.
        break

    # Run FFmpeg with a progress bar
    run_ffmpeg_with_progress(input_path, output_path)

if __name__ == "__main__":
    main()