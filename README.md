# Video_to_gif_converter

This Flask application allows users to upload a video file, converts the video into GIFs, and adds captions based on the audio transcription. The application processes the video, generates GIFs with text overlays.

## Features

- Upload video files (MP4 format).
- Extract audio from the video and transcribe it to text.
- Generate GIFs from the video fragments with text captions.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.10.5 (Ensure you have the correct version of Python installed)
- Flask
- moviepy
- speechrecognition
- pydub

## Installation
1. Clone this repository:

```bash
git clone (https://github.com/pragyakashyap/Video_to_gif_converter.git)
cd video-to-gif
```

2. Install the required packages:
```bash
pip install moviepy speechrecognition pydub flask
```
## Usage
1. Start the Flask application:
```bash
python app.py
```
2. Open your web browser and go to http://localhost:5000.

3. Upload a video file and wait for the processing to complete.

4. Find the generated GIFs with large captions.

![Video Processor](https://github.com/pragyakashyap/Video_to_gif_converter/assets/47416981/dd86e9fe-2607-4235-ab89-cff0cebaa39c)



