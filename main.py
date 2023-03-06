from flask import Flask, render_template, request, send_file
from youtube_downloader_trimmer import download_audio, get_trimmed, newest_mp3_filename


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    download_audio(url)
    return 'Download complete!'


@app.route('/trim', methods=['POST'])
def trim():
    initial = request.form['initial']
    final = request.form['final']
    filename = newest_mp3_filename()
    trimmed_file = get_trimmed(filename, initial, final)
    trimmed_filename = "".join([filename.split(".mp3")[0], "- TRIM.mp3"])
    trimmed_file.export(trimmed_filename, format="mp3")
    return send_file(trimmed_filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)