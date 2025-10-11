from flask import Response, render_template
from . import home_bp
import os
import re
from pathlib import Path
from urllib.parse import quote_from_bytes
from collections import defaultdict


SERVER_SITE_HOME = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEDIA_DIR = os.path.join(SERVER_SITE_HOME, "media")
SITE_DOMAIN = "dev.fradgify.kozow.com"
CWD_DIR = os.getcwd()
VIDEO_EXT = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.mpeg', '.mpg'}
AUDIO_EXT = {".mp3"}
SHEET_EXT = {".pdf"}


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
            filename = file.replace(os.sep, '/').split('/')[-1]
            if library == "Music":
                href_path = quote_apache(file[21:])
                normalized_latest_files[library].append({
                    "text": filename,
                    "href": f"/music/play/?path={href_path}"
                })
            else:
                href_path = quote_apache(file)
                normalized_latest_files[library].append({
                    "text": filename,
                    "href": href_path
                })

    # Render template to a string
    html_content = render_template('homepage.html', latest_files=normalized_latest_files)

    # Return a Response safely encoding surrogates
    return Response(html_content.encode('utf-8', 'surrogateescape'), mimetype='text/html')


@home_bp.route('/report')
def report():
    return render_template('report.html')


def quote_apache(path: str) -> str:
    """
    Quote a filesystem path so that it matches Apache autoindex hrefs.
    Handles surrogate pairs and arbitrary byte sequences.
    """
    # Step 1: Convert to the raw filesystem bytes representation
    # This ensures we get the same byte values Apache uses
    path_bytes = os.fsencode(path.replace(os.sep, '/'))
    path_quoted = quote_from_bytes(path_bytes, safe=b'/')

    # Step 2: Percent-encode all non-ASCII bytes, leaving '/' safe
    return path_quoted


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
