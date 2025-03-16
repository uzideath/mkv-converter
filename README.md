# Convert.py — GPU-Accelerated MKV to MP4 Converter

![GitHub license](https://img.shields.io/badge/license-MIT-green.svg)
![GitHub stars](https://img.shields.io/github/stars/uzideath/mkv-converter?style=social)
![GitHub forks](https://img.shields.io/github/forks/uzideath/mkv-converter?style=social)

A **Python 3** script that uses **NVIDIA’s NVENC** hardware acceleration to convert videos from **MKV** to **MP4**.  
It features an **interactive CLI**, a **colorful progress bar**, and an **animated spinner**.  

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration & Advanced Options](#configuration--advanced-options)
- [License](#license)
- [Author / Credits](#author--credits)

---

## Overview
`convert.py` prompts you for an **input MKV file** and an **output MP4 filename**, then utilizes **FFmpeg** with **NVIDIA’s NVENC** to quickly transcode your video.  
It displays:
1. A **colorful progress bar** showing % complete.  
2. A **rotating ASCII spinner**.  
3. **Detailed** status messages and error handling.  

> [!TIP]
> The script ensures that the provided file paths exist before continuing. If an invalid file is entered, you will be prompted again.

If you **press Ctrl+C** or type `cancel` at any prompt, the script will cleanly **stop** and print a “Process canceled” message.

---

## Features
- **Interactive CLI**: Type in your paths, or cancel at any time.  
- **GPU Accelerated**: Leverages NVIDIA NVENC to speed up encoding dramatically.  
- **Configurable Quality**: By default, uses **constant QP** with `-qp 18` and `-preset slow` for a balance of high quality and moderate file size.  
- **Colorful**: Uses ANSI escape codes to produce colored text, a spinner, and a dynamic progress bar.  
- **Keyboard Interrupt Handling**: Gracefully terminates if you press Ctrl+C during the encode.

---

## Prerequisites
> [!IMPORTANT]  
> Before using this script, ensure the following dependencies are installed.

1. **NVIDIA GPU & Drivers**  
   - Confirm with:
     ```bash
     nvidia-smi
     ```
   - You should see your NVIDIA GPU and driver info.

2. **FFmpeg with NVENC support**  
   - Confirm with:
     ```bash
     ffmpeg -encoders | grep nvenc
     ```
   - Look for `h264_nvenc` and/or `hevc_nvenc`.  
   - If you see them, your **FFmpeg build** supports NVENC.

3. **Python 3**  
   - The script uses only the **standard library** (no extra `pip install` required).  

4. **Basic Terminal** that supports ANSI colors  
   - Most modern terminals on Windows 10+, macOS, or Linux will work.

---

## Installation
> [!TIP]  
> Ensure you have administrator or root access if installing system-wide dependencies.

1. **Clone or Download** this repository:
   ```bash
   git clone https://github.com/uzideath/mkv-converter.git
   cd repo
   ```
   Or simply download the **`convert.py`** file manually.

2. **Ensure FFmpeg** is installed on your system and is in your system’s `PATH`.  
   - On Windows, add the `bin` folder of your FFmpeg install to the PATH.  
   - On Linux/Mac, you can install it via package managers or official binaries.

3. **Make the script executable** (optional on Linux/macOS):
   ```bash
   chmod +x convert.py
   ```

---

## Usage
> [!WARNING]  
> Running the script requires a valid `.mkv` file and sufficient disk space for the output `.mp4` file.

1. **Open a terminal** in the same folder as `convert.py`.
2. Run:
   ```bash
   python convert.py
   ```
   *(On Windows, you can also use `py convert.py` if Python is correctly associated.)*

3. **Follow the prompts**:
   - Enter the path of your `.mkv` file.  
   - Enter the desired `.mp4` output path.  
   - The script will confirm if the file exists or prompt again if it doesn’t.  

4. **Watch the progress bar** and **spinner**.  
   - If you press **Ctrl+C**, the script will terminate and show “Process canceled by user.”
   - If everything goes well, you’ll see “Conversion completed successfully!” at the end.

---

## Configuration & Advanced Options
> [!NOTE]  
> Users can tweak settings inside `convert.py` by modifying the `run_ffmpeg_with_progress()` function.

Inside `convert.py`, check the function **`run_ffmpeg_with_progress()`** to customize encoding settings.

For example:
- **Change video codec** (H.264 vs. H.265):
  ```python
  "-c:v", "h264_nvenc"  # Change to "hevc_nvenc" for H.265 encoding
  ```
- **Modify quality settings**:
  ```python
  "-rc", "constqp", "-qp", "18"  # Lower = higher quality, larger file size
  ```
- **Adjust speed vs. quality**:
  ```python
  "-preset", "slow"  # Change to "medium", "fast", "p7", "hq", etc.
  ```

---

## License
[MIT License](LICENSE) — feel free to modify and distribute, but **use at your own risk**.  
Check any relevant **FFmpeg** and **NVIDIA** licenses for their terms.

---

## Author / Credits
- **Your Name**  
  - GitHub: [github.com/yourusername](https://github.com/yourusername)  
- Built on top of [FFmpeg](https://ffmpeg.org/) & [NVIDIA NVENC](https://developer.nvidia.com/nvidia-video-codec-sdk)  
- Inspired by various open-source tutorials.

> [!CAUTION]  
> This script is provided “as-is” without warranty. Performance and results will vary depending on your source file, GPU, and version of FFmpeg.  

Happy encoding!
