import yt_dlp # client to many multimedia portals
import os
import glob
import sys
import re
from pydub import AudioSegment # only audio operations

def get_cookie_path():
    """Get cookie path based on environment"""
    if os.environ.get('RENDER'):
        # Use /tmp directory instead of /etc/secrets for Render
        source = '/etc/secrets/youtube.com_cookies.txt'
        dest = '/tmp/youtube.com_cookies.txt'
        if os.path.exists(source):
            with open(source, 'rb') as src, open(dest, 'wb') as dst:
                dst.write(src.read())
        return dest
    elif os.environ.get('VERCEL'):
        return '/tmp/youtube.com_cookies.txt'
    return 'youtube.com_cookies.txt'  # local development

def get_temp_dir():
    """Get appropriate temporary directory based on environment"""
    if os.environ.get('VERCEL') or os.environ.get('RENDER'):
        temp_dir = '/tmp/downloads'
    else:
        temp_dir = './downloads'
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    return temp_dir

# downloads yt_url to the same directory from which the script runs
def download_audio(yt_url):
    temp_dir = get_temp_dir()
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        'cookiefile': get_cookie_path(),
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s')
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])

def newest_mp3_filename():
    # lists all mp3s in temporary directory
    temp_dir = get_temp_dir()
    list_of_mp3s = glob.glob(os.path.join(temp_dir, '*.mp3'))
    # returns mp3 with highest timestamp value
    return max(list_of_mp3s, key=os.path.getctime) # returns the URL in the list, which has the highest creation time

def get_video_time_in_ms(video_timestamp):
    vt_split = video_timestamp.split(":")
    if (len(vt_split) == 3): # if in HH:MM:SS format
        hours = int(vt_split[0]) * 60 * 60 * 1000
        minutes = int(vt_split[1]) * 60 * 1000
        seconds = int(vt_split[2]) * 1000
    else: # MM:SS format
        hours = 0
        minutes = int(vt_split[0]) * 60 * 1000
        seconds = int(vt_split[1]) * 1000
    # time point in miliseconds
    return hours + minutes + seconds

def get_trimmed(mp3_filename, initial, final = ""):
    if (not mp3_filename):
        # raise an error to immediately halt program execution
        raise Exception("No MP3 found in local directory.")
    # reads mp3 as a PyDub object
    sound = AudioSegment.from_mp3(mp3_filename)
    t0 = get_video_time_in_ms(initial)
    print("Beginning trimming process for file ", mp3_filename, ".\n")
    print("Starting from ", initial, "...")
    if (len(final) > 0):
        print("...up to ", final, ".\n")
        t1 = get_video_time_in_ms(final)
        return sound[t0:t1] # t0 up to t1
    return sound[t0:] # t0 up to the end

def is_valid(url):
    """
    This function is only used to check if a URL is valid
    """
    # Define the regex pattern to match a valid URL
    pattern = r'^https?://(?:www\.)?[a-zA-Z0-9\.\-]+(?:\.[a-zA-Z]{2,}){1,2}(?:/[^\s]*)?$'

    # Check if the URL matches the pattern
    if re.match(pattern, url):
        return True
    else:
        return False
    
def is_valid_format(initial, final):
    """
    Check if the initial and final are in the right format hours:minutes:seconds OR minutes:seconds
    """
    if (":" not in initial) or (":" not in final):
        return False
    
    initial_splits = initial.split(":")
    final_splits = final.split(":")

    if (len(initial_splits) not in [2, 3]) or (len(final_splits) not in [2, 3]):
        return False
    
    if len(initial_splits) == 2 and len(final_splits) == 3:
        return False
    
    if len(initial_splits) == 3 and len(final_splits) == 2:
        return False
    
    return True

def is_valid_filename(filename):
    # Define the regex pattern to match a valid filename
    pattern = r'^[a-zA-Z0-9\-\._]+$'

    # Check if the filename matches the pattern
    if re.match(pattern, filename):
        return True
    else:
        return False


def main():
    """
    Tutorial: python youtube_downloader_trimmer.py 'https://www.youtube.com/watch?v=8OAPLk20epo' 9:51 14:04
    If you want to save the trimmed file with a different name, you can add a fourth argument with the name you want.
    """
    if (not len(sys.argv) > 1):
        print("Please insert a multimedia-platform URL supported by yt-dlp as your first argument.")
        return
    yt_url = str(sys.argv[1])
    # If yt_url is not valid, then print the error and return
    if not is_valid(yt_url):
        print("This URL is not valid.")
        return
    download_audio(yt_url)

    if (not len(sys.argv) > 2): # exit if no instants as args
        return
    initial = str(sys.argv[2])
    final = ""
    if sys.argv[3]:
        final = str(sys.argv[3])

    if not is_valid_format(initial, final):
        print("Initial and/or final are not in the right format.")
        return

    filename = newest_mp3_filename()
    trimmed_file = get_trimmed(filename, initial, final)
    trimmed_filename = "".join([filename.split(".mp3")[0], "- TRIM.mp3"]) # default name of trimmed file
    
    if len(sys.argv) == 5 and is_valid_filename(str(sys.argv[4])):
        trimmed_filename = str(sys.argv[4]) + ".mp3"
    print("Process concluded successfully. Saving trimmed file as ", trimmed_filename)
    # saves file with newer filename
    trimmed_file.export("./output/" + trimmed_filename, format="mp3")


if __name__ == "__main__":
    main()

