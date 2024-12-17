from flask import render_template
from . import home_bp
import os
from pathlib import Path


SERVER_SITE_HOME = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE_DOMAIN = "dev.fradgify.kozow.com"
CWD_DIR = os.getcwd()
MEDIA_DIR = os.path.join(CWD_DIR, "..", "media")
VIDEO_EXT = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.mpeg', '.mpg'}
AUDIO_EXT = {".mp3", ".flac"}
SHEET_EXT = ".pdf"


@home_bp.route('/')
def homepage():
    # Generate the latest files for Movies, TV, Music, Sheets
    libraries = {
        "Movies": VIDEO_EXT,
        "TV": VIDEO_EXT,
        "Music": AUDIO_EXT,
        "Sheets": SHEET_EXT
    }
    latest_files = {}
    for library, exts in libraries.items():
        latest_files[library] = get_latest(library, exts)

    # Render the HTML template with the dynamic data
    return render_template('homepage.html', latest_files=latest_files)


def get_latest(library, exts, num_files=10):
    directory_url = os.path.join(MEDIA_DIR, library.lower())
    site_url = f"https://{SITE_DOMAIN}/media/{library.lower()}"
    files = get_recent_files(directory_url, exts, num_files)
    print(MEDIA_DIR, library, files)
    return [os.path.join(site_url, os.path.basename(file)) for file in files]


def list_video_folders(directory, exts):
    video_files = []
    top_level_dir = os.path.basename(os.path.normpath(directory))
    print("SERVER_SITE_HOME", SERVER_SITE_HOME)
    print("top_level_dir", top_level_dir)
    for dirpath, dirnames, filenames in os.walk(os.path.join(SERVER_SITE_HOME, directory)):
        if os.path.basename(dirpath) == top_level_dir:
            continue
        for entry in filenames:
            if entry.lower().endswith(tuple(exts)):
                full_path = os.path.join(dirpath, entry)
                folder = str(Path(full_path).parent)
                if folder not in video_files:
                    video_files.append(folder)
    return video_files


def get_recent_files(directory, exts, num_files=10):
    out_files = []
    print("directory", directory)
    video_folder = list_video_folders(directory, exts)
    sorted_folders = sorted(video_folder, key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
    for file in sorted_folders[:num_files]:
        out_files.append(file)
    return out_files
