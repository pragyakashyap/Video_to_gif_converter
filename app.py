import os
from flask import Flask, request, jsonify, send_from_directory
import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
import time

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def extract_audio(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def transcribe_audio_segment(audio_segment):
    recognizer = sr.Recognizer()
    audio_segment.export("temp.wav", format="wav")

    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    
    os.remove("temp.wav")
    return text

def create_gifs_with_captions(video_path, output_dir, fragment_duration=5):
    video = mp.VideoFileClip(video_path)
    duration = int(video.duration)
    gifs = []

    for start in range(0, duration, fragment_duration):
        end = min(start + fragment_duration, duration)
        clip = video.subclip(start, end)
        
        # Extract and transcribe audio for the current segment
        audio_segment = clip.audio
        audio_path = os.path.join(output_dir, f"audio_{start}_{end}.wav")
        audio_segment.write_audiofile(audio_path)
        text = transcribe_audio_segment(AudioSegment.from_file(audio_path))
        
        # Create a text clip with the transcribed text
        txt_clip = mp.TextClip(text, fontsize=50, color='red', bg_color='white').set_position(('center', 'bottom')).set_duration(clip.duration)
        
        # Combine the video clip and text clip
        video_with_text = mp.CompositeVideoClip([clip, txt_clip], size=clip.size)

        # Write GIF
        gif_path = os.path.join(output_dir, f"fragment_{start}_{end}.gif")
        video_with_text.write_gif(gif_path, fps=10)
        gifs.append(gif_path)
    
    return gifs

def process_video(video_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    gifs = create_gifs_with_captions(video_path, output_dir)
    return gifs

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return "No file part", 400
    file = request.files['video']
    if file.filename == '':
        return "No selected file", 400
    if file:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(video_path)

    # Simulate progress with sleep
    total_size = os.path.getsize(video_path)
    chunk_size = 1024 * 1024  # 1 MB
    bytes_uploaded = 0

    while bytes_uploaded < total_size:
        time.sleep(1)  # Simulate processing time
        bytes_uploaded += chunk_size
        progress = min(100, int(bytes_uploaded / total_size * 100))

        # Update progress in console (for debugging)
        print(f"Progress: {progress}%")
    
    # Process the video and generate GIFs
    gifs = process_video(video_path, app.config['OUTPUT_FOLDER'])
    gif_urls = [f"/output/{os.path.basename(gif)}" for gif in gifs]

    return jsonify({'gifs': gif_urls})

@app.route('/output/<filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/')
def index():
    return '''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Video Processor</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          h1 { font-size: 24px; }
          h2 { font-size: 20px; }
          .progress { width: 100%; background-color: #f3f3f3; margin-top: 10px; }
          .progress-bar { width: 0; height: 30px; background-color: #4caf50; text-align: center; line-height: 30px; color: white; }
          .loader { border: 8px solid #f3f3f3; border-top: 8px solid #3498db; border-radius: 50%; width: 60px; height: 60px; animation: spin 2s linear infinite; margin: 20px auto; }
        </style>
      </head>
      <body>
        <h1>Video Processor</h1>
        <form id="uploadForm" method="post" enctype="multipart/form-data" action="/upload">
          <input type="file" name="video" accept="video/*" required>
          <button type="submit">Upload</button>
        </form>
        <div class="progress" id="progress">
          <div class="progress-bar" id="progress-bar">0%</div>
        </div>
        <div id="results"></div>
        <script>
          document.getElementById('uploadForm').addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(this);
            const progressBar = document.getElementById('progress-bar');
            const resultsDiv = document.getElementById('results');
            
            // Show loading indicator
            resultsDiv.innerHTML = '<div class="loader"></div>';
            progressBar.style.width = '0%';
            progressBar.innerHTML = '0%';
            
            fetch('/upload', {
              method: 'POST',
              body: formData,
            })
            .then(response => response.json())
            .then(data => {
              // Clear loading indicator
              resultsDiv.innerHTML = '';
              
              // Show new GIFs
              const gifContainer = document.createElement('div');
              gifContainer.className = 'gif-container';
              data.gifs.forEach(gif => {
                const img = document.createElement('img');
                img.src = gif;
                img.alt = 'gif';
                img.style.maxWidth = '300px'; // Limit width for clarity
                img.style.border = '1px solid #ccc'; // Add border for clarity
                gifContainer.appendChild(img);
              });
              resultsDiv.appendChild(gifContainer);
            })
            .catch(error => {
              console.error('Error:', error);
              resultsDiv.innerHTML = '<p>Error uploading file. Please try again later.</p>';
            });

            // Simulate progress on the progress bar
            let progress = 0;
            const interval = setInterval(function() {
              progress += 10; // Simulate 10% progress increments
              progressBar.style.width = progress + '%';
              progressBar.innerHTML = progress + '%';
              if (progress >= 100) {
                clearInterval(interval);
                progressBar.innerHTML = 'Upload Complete';
              }
            }, 1000); // Update progress every second
          });
        </script>
      </body>
    </html>
    '''

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)