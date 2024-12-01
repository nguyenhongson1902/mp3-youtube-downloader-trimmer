
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from youtube_downloader_trimmer import (
    download_audio, 
    get_trimmed, 
    newest_mp3_filename, 
    is_valid,
    is_valid_format
)
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        url = data.get('url')
        initial = data.get('initial')
        final = data.get('final')
        
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'})
        
        if not is_valid(url):
            return jsonify({'success': False, 'error': 'Invalid YouTube URL'})
        
        # Download the audio first
        download_audio(url)
        filename = newest_mp3_filename()
        
        # Move the downloaded file to output directory
        output_filename = os.path.join('output', os.path.basename(filename))
        os.rename(filename, output_filename)  # This line moves the file to output folder
        
        # If trimming parameters are provided, create trimmed version
        if initial and final:
            if not is_valid_format(initial, final):
                return jsonify({'success': False, 'error': 'Invalid time format'})
                
            trimmed_file = get_trimmed(output_filename, initial, final)
            trimmed_filename = os.path.join('output', filename.split(".mp3")[0] + "-TRIM.mp3")
            trimmed_file.export(trimmed_filename, format="mp3")
            
            return jsonify({
                'success': True,
                'message': 'File downloaded and trimmed successfully! Your file will start downloading shortly.',
                'filename': trimmed_filename,
                'download_ready': True
            })
        
        # Return the full version for download    
        return jsonify({
            'success': True,
            'message': 'File downloaded successfully! Your file will start downloading shortly.',
            'filename': output_filename,
            'download_ready': True
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health', methods=['GET', 'HEAD'])
def health_check():
    """Simple health check endpoint that handles both GET and HEAD requests for UptimeRobot."""
    return jsonify({'status': 'alive'}), 200

def cleanup_file(filepath):
    """Remove file after download"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Cleaned up file: {filepath}")
    except Exception as e:
        print(f"Error cleaning up file {filepath}: {e}")

@app.route('/download-file/<path:filename>')
def download_file(filename):
    try:
        response = send_file(
            filename,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name=os.path.basename(filename)
        )
        
        # Add callback to cleanup file after sending
        @response.call_on_close
        def cleanup():
            cleanup_file(filename)
            # If this was a trimmed file, clean up the original too
            if "-TRIM.mp3" in filename:
                original_file = filename.replace("-TRIM.mp3", ".mp3")
                cleanup_file(original_file)
        
        return response
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Add this line at the end for Vercel
app = app.wsgi_app