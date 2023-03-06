# MP3 YouTube Downloader Trimmer

This is my pet project to download a MP3 file from a YouTube URL. You can also trim the MP3 file into the segment that you want.

## A Hosted Website

The app is currently being hosted on Google Firebase, you can check it out with the URL here below:

`https://mp3--downloader-trimmer.web.app/`

If the hosted app doesn't work, you can try using the local app by commanding:

`python main.py`

### How to use this app?

- Fill in a YouTube URL, click `Download` button to download the original file converted to MP3 file.
- Fill in the `initial` and `final` to trim the segment of the newest MP3 file just-downloaded.

Pretty easy, huh? Feel free to play around this app more.

## Python Script

If you want to run the Python script to use the app, you can do that too in this way:

`python youtube_downloader_trimmer.py '<Youtube URL>' <initial point> <final point>`
For example: `python youtube_downloader_trimmer.py 'https://www.youtube.com/watch?v=8OAPLk20epo' 9:51 14:04`

- `youtube_downloader_trimmer.py`: Notice that you must uncomment the last 2 lines in the file to run the `main` function
- `'<YouTube URL>'`: The URL of the YouTube video
- `<initial point>`: The starting point of the timestamp
- `<final point>`: The end point where you want to trim

## Others & Environment

- To create a Python virtual environment: `python -m venv venv`
- Python version: `3.10.0`
- Main packages: `yt-dlp` (for processing YouTube URLs), `pydub` (for trimming), `re` (for validating)
