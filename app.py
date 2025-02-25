import os
import time
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, jsonify, send_file
from football_utils.video_processing import process_video
import base64

app = Flask(__name__)
app.secret_key = "some_secret_key"  # Needed for session usage

# Define folders for uploads and outputs
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
OUTPUT_FOLDER = os.path.join(os.getcwd(), 'outputs')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Check if the video file is in the request
        if 'video' not in request.files:
            return redirect(request.url)
        file = request.files['video']
        if file.filename == "":
            return redirect(request.url)

        # Save uploaded video to the uploads folder
        video_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(video_path)

        # Process video and get both the output path and LLM classification result
        output_video, classification_str = process_video(video_path, OUTPUT_FOLDER)
        session['classification'] = classification_str

        # Save output video filename in session and redirect to results page
        session['processed_video_filename'] = os.path.basename(output_video)
        return redirect(url_for('results'))
    return render_template("index.html")

@app.route("/results")
def results():
    # Get processed video filename and classification from session
    processed_video_filename = session.get('processed_video_filename', None)
    classification_str = session.get('classification', "No classification")
    return render_template("results.html", 
                           processed_video_filename=processed_video_filename, 
                           classification=classification_str)

# Endpoint for video preview (streaming)
@app.route("/videos/<filename>")
def serve_video(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

# Endpoint for video download
@app.route("/downloads/<filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

# Flask Endpoint to Handle Screenshot Upload
@app.route("/upload_screenshot", methods=["POST"])
def upload_screenshot():
    data = request.get_json()
    image_data = data.get("imageData")
    if image_data:
        # Remove data URL header and decode the image data
        header, encoded = image_data.split(",", 1)
        screenshot_bytes = base64.b64decode(encoded)
        screenshot_path = os.path.join(OUTPUT_FOLDER, f"screenshot_{int(time.time())}.png")
        with open(screenshot_path, "wb") as f:
            f.write(screenshot_bytes)
        return jsonify({"message": "Screenshot uploaded and saved on server.", "path": screenshot_path}), 200
    return jsonify({"error": "No image data received"}), 400

if __name__ == "__main__":
    app.run(debug=True)
