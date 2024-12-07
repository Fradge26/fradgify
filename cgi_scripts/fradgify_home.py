#!/usr/bin/env python3
import os 
from pathlib import Path


def main():
    print("Content-Type: text/html")
    print() 
    print(
        """
        <html>
        <head>
        <title>Fradgify: Streaming you can trust!</title>
        <link rel="icon" type="image/x-icon" href="https://fradgify.kozow.com/media/music/fradgify/favicon.ico">
        <style>
            body {
                background-color: rgb(232, 250, 250);
            }
            h2 {
                font-size: 1.5em; /* Adjust the size as needed */
                margin-bottom: 0.2em; /* Adjust the bottom margin */
            }
        </style>
        </head>
        <img src="fradgify_full.jpg">
        <body>
        <html>
        <body>
        <h2>Where is Luke?</h2>
        <a href="https://fradgify.kozow.com/whereisluke">Find out</a><br>
        <h2>Media Libraries</h2>
        <a href="https://fradgify.kozow.com/media/movies">Movies</a><br>
        <a href="https://fradgify.kozow.com/media/tv">TV</a><br>
        <a href="https://fradgify.kozow.com/media/music">Music</a><br>
        <a href="https://fradgify.kozow.com/media/sheets">Sheet Music</a><br>
        """
    )
    get_latest()
    print('<h4><a href="https://fradgify.kozow.com/media/report" target="_blank">Site Traffic Dashboard</a></h2>')
    print("</body></html>")


def get_latest():
    for library in ["Movies", "TV", "Music", "Sheets"]:
        print(f"<h2>Latest {library}</h2>")
        directory_url = f'/var/www/fradgify.kozow.com/media/{library.lower()}'
        site_url = f"https://fradgify.kozow.com/media/{library.lower()}"
        files = get_recent_files(directory_url)
        for file in files:
            file_url = file.replace(directory_url, site_url)
            filename = os.path.basename(file)
            print(f'<a href="{file_url}">{filename}</a><br>')


def list_video_folders(directory):
    # Define a set of video file extensions
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.mpeg', '.mpg', "mp3", ".pdf"}
    video_files = []
    # Walk through the directory tree
    top_level_dir = os.path.basename(os.path.normpath(directory))
    for dirpath, dirnames, filenames in os.walk(directory):
        if os.path.basename(dirpath) == top_level_dir:
            continue
        for entry in filenames:
            # Check if the file has a video extension
            if entry.lower().endswith(tuple(video_extensions)):
                # Construct full file path and add to the list
                full_path = os.path.join(dirpath, entry)
                folder = str(Path(full_path).parent)
                if folder not in video_files:
                    video_files.append(folder)
    return video_files


def get_recent_files(directory, num_files=10):
    out_files = []
    video_folder = list_video_folders(directory)
    sorted_folders = sorted(video_folder, key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
    for file in sorted_folders[:num_files]:
        out_files.append(file)
    return out_files


if __name__ == "__main__":
    main()