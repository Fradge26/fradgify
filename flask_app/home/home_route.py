from flask import render_template, current_app
from . import home_bp
import os
from pathlib import Path
from urllib.parse import quote
from collections import defaultdict


SERVER_SITE_HOME = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEDIA_DIR = os.path.join(SERVER_SITE_HOME, "media")
SITE_DOMAIN = "dev.fradgify.kozow.com"
CWD_DIR = os.getcwd()
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

    normalized_latest_files = defaultdict(list)
    for library, files in latest_files.items():
        for file in files:
            if library == "Music":
                normalized_latest_files[library].append(
                    {
                        "text": file.replace(os.sep, '/').split('/')[-1],
                        "href": f"/music/play/?path={quote(file[21:].replace(os.sep, '/'), safe='/')}"
                    }
                )
            else:
                normalized_latest_files[library].append(
                    {
                        "text": file.replace(os.sep, '/').split('/')[-1],
                        "href": f"{quote(file.replace(os.sep, '/'), safe='/')}"
                    }
                )
    current_app.logger.debug(f"{normalized_latest_files}")
    # Render the HTML template with the dynamic data
    return render_template('homepage.html', latest_files=normalized_latest_files)


@home_bp.route('/report')
def report():
    return render_template('report.html')


def get_latest(library, exts, num_files=10):
    directory_url = os.path.join(MEDIA_DIR, library.lower())
    folders = get_recent_folders(directory_url, exts, num_files)
    relative_paths = [os.path.relpath(folder, SERVER_SITE_HOME) for folder in folders]
    return relative_paths


def list_video_folders(directory, exts):
    video_files = []
    top_level_dir = os.path.basename(os.path.normpath(directory))
    for dirpath, dirnames, filenames in os.walk(os.path.join(SERVER_SITE_HOME, directory)):
        if os.path.basename(dirpath) == top_level_dir:
            continue
        for entry in filenames:
            if entry.lower().endswith(tuple(exts)):
                full_path = os.path.join(dirpath, entry)
                folder = str(Path(full_path).parent.as_posix())
                if folder not in video_files and "media/music/downloading" not in folder:
                    video_files.append(folder)
    return video_files


def get_recent_folders(directory, exts, num_files=10):
    out_files = []
    video_folder = list_video_folders(directory, exts)
    sorted_folders = sorted(video_folder, key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
    for file in sorted_folders[:num_files]:
        out_files.append(file)
    return out_files
