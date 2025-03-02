# YouTube Video Downloader

This is a simple YouTube video downloader application built using PyQt6. The application allows users to input a YouTube URL, select the desired video format, and download either the full video or a specified section of it. It features a user-friendly interface with a loading spinner during the download process.

## Features

- Input a YouTube video URL.
- Select video format (MP4 or WEBM).
- Download full videos or specify start and end times for partial downloads.
- User-friendly interface with a loading spinner.

## Requirements

To run this application, you need to have the following installed:

- Python 3.x
- PyQt6
- PyQt6-WebEngine
- yt-dlp
- ffmpeg (for video processing)

## Installation

1. Clone the repository or download the source code.

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment (optional but recommended).

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required Python packages.

   ```bash
   pip install -r requirements.txt
   ```

4. Install `ffmpeg`:

   - **For Ubuntu/Debian:**
     ```bash
     sudo apt install ffmpeg
     ```

   - **For macOS (using Homebrew):**
     ```bash
     brew install ffmpeg
     ```

   - **For Windows:**
     Download the binaries from the [FFmpeg website](https://ffmpeg.org/download.html) and follow the installation instructions.

## Usage

Run the application using the following command: