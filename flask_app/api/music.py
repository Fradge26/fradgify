from . import music_bp
import logging
import os
from flask import jsonify, send_from_directory, request, render_template
from mutagen import File
from mutagen.id3 import ID3, APIC
from PIL import Image
import json
import hashlib
from datetime import datetime as dt
from pathlib import Path
import io


SITE_DOMAIN = "dev.fradgify.kozow.com"
SITE_HOME = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEDIA_DIR = os.path.join(SITE_HOME, "media")
MUSIC_DIR = os.path.join(MEDIA_DIR, "music", "complete")
ALBUMS_JSON_PATH = os.path.join(SITE_HOME, "static", "json", "albums.json")
ALBUM_ART_REL_DIR = os.path.join("\\", "static", "album-art")
ALBUM_ART_DIR = os.path.join(SITE_HOME, "static", "album-art")
logging.debug(f"api started: {__file__}")


@music_bp.route('/favicon.ico')
def favicon():
    return send_from_directory('static/icons', 'favicon.ico', type='image/svg+xml')


@music_bp.route('/browse')
def browse():
    return render_template('browse.html')


@music_bp.route('/play/')
def play():
    # Get the 'path' query parameter
    path = request.args.get('path', '')  # Default to an empty string if 'path' is not provided
    return render_template('play.html', path=path)


@music_bp.route('/album/', methods=['GET'])
def get_album():
    # Get the folder path from the query parameter
    logging.debug(f"api endpoint /album called")
    folder_path = request.args.get('path', default='', type=str)
    album_path = os.path.join(MUSIC_DIR, folder_path)

    try:
        # List all MP3 files in the specified directory
        music_files = list_music_files(album_path)
        f1 = next(f for f in os.listdir(album_path) if f.endswith(".mp3"))
        audio_file = File(f"{album_path}/{f1}")
        album_art = get_album_art_path(album_path, audio_file)
        artist, album, year = get_audio_file_info(audio_file)
        album_info = {"artist": artist, "album": album}
        out_dict = {'musicFiles': music_files, 'albumArt': album_art, "albumInfo": album_info}
        logging.debug(f"{out_dict=}")
        return jsonify(out_dict)

    except Exception as e:
        logging.debug(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500


@music_bp.route('/album_list', methods=['GET'])
def get_album_list():
    # Get the folder path from the query parameter
    logging.debug(f"api endpoint /album_list called")
    try:
        # album_dict = defaultdict(list)
        album_list = []
        # for folder in os.listdir(MUSIC_FOLDER):
        for root_path, dirnames, filenames in os.walk(MUSIC_DIR):
            for dirname in dirnames:
                current_dir = os.path.join(root_path, dirname)
                # logging.debug(f"{current_dir=}")
                audio_file_path = get_first_audio_file(current_dir)
                # logging.debug(f"{audio_file_path=}")
                # logging.debug(f"os.path.isdir(folder) {os.path.isdir(os.path.join(MUSIC_FOLDER, folder))} {folder}")
                if os.path.isdir(current_dir) and audio_file_path:
                    audio_file = File(audio_file_path)
                    artist, album, year = get_audio_file_info(audio_file)
                    rel_path = os.path.relpath(current_dir, MUSIC_DIR)
                    # logging.debug(f"{artist=}, {album=}, {year=}, {rel_path=}")
                    # album_dict[artist].append([album, os.path.join(MUSIC_FOLDER, dirname)])
                    album_list.append(
                        {
                            "artist": artist,
                            "album": album,
                            "year": year,
                            "path": rel_path
                        }
                    )
        final_albums_dict = {"albums": album_list}
        Path(ALBUMS_JSON_PATH).parent.mkdir(exist_ok=True, parents=True)
        with open(ALBUMS_JSON_PATH, "w") as final:
            json.dump(final_albums_dict, final)
        return jsonify({"success": f"{len(album_list)} albums written to albums.json at {dt.now()}"}, 200)

    except Exception as e:
        logging.debug(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500


def list_music_files(folder):
    filenames = os.listdir(folder.encode("utf-8"))
    out_files = [f.decode('utf-8').encode('utf-8', "surrogatepass").decode('utf-8') for f in filenames]
    out_files = [f for f in out_files if f.endswith(".mp3")]
    logging.debug(f"out_files: {out_files}")
    return sorted(out_files)


def get_album_art_path(album_path, audio):
    hash_object = hashlib.sha256(album_path.encode('utf-8'))
    short_hash = hash_object.hexdigest()[:12]
    album_art_filename = short_hash + ".jpg"
    album_art_filepath = os.path.join(ALBUM_ART_DIR, album_art_filename)
    album_art_rel_filepath = os.path.join(ALBUM_ART_REL_DIR, album_art_filename)

    if os.path.exists(album_art_filepath):
        return album_art_rel_filepath
    folder_img = next((f for f in os.listdir(album_path) if f.lower().endswith('.jpg')), None)
    if folder_img:
        with Image.open(os.path.join(album_path, folder_img)) as img:
            img_resized = img.resize((400, 400))  # Example: Resize to 800x600
            img_resized.save(album_art_filepath, "JPEG")
        return album_art_rel_filepath

    for tag in audio.values():
        if isinstance(tag, APIC):
            logging.debug("2")
            album_art_data = tag.data
            image = Image.open(io.BytesIO(album_art_data))
            image = image.convert("RGB")
            image.save(album_art_filepath, "JPEG")
            logging.debug(f"Album art extracted to: {album_art_filepath}")
            return album_art_rel_filepath
    else:
        return os.path.join(ALBUM_ART_REL_DIR, "default_album_art.jpg")


def get_audio_file_info(audio):
    if audio is not None:
        # Extract artist and album, handle various file types by inspecting the tag names
        if 'TPE2' in audio:  # For MP3 ID3 tags
            artist = audio['TPE2'][0]
        elif 'TPE1' in audio:  # For MP3 ID3 tags
            artist = audio['TPE1'][0]
        elif 'artist' in audio:
            artist = audio['artist'][0]
        else:
            artist = 'Unknown Artist'

        if 'TALB' in audio:  # For MP3 ID3 tags
            # logging.debug(f"TALB: {audio['TALB']}")
            # logging.debug(f"TALB: {audio['TALB'][0]}")
            album = audio['TALB'][0]
        elif 'album' in audio:
            album = audio['album'][0]
        else:
            album = 'Unknown Album'
        if "TDRC" in audio:
            year = audio.get("TDRC")[0].year
        elif "year" in audio:
            year = audio.get('year')[0]
        elif "date" in audio:
            year = audio.get('date')[0]
        else:
            year = ''

    else:
        artist = 'Unknown Artist'
        album = 'Unknown Album'
        year = ""
    return upper_first_word(artist), upper_first_word(album), year


def upper_first_word(word):
    return f"{word[0].upper()}{word[1:]}"


def get_first_audio_file(directory):
    audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.aac')
    audio_extensions = ['.mp3']
    #for root, dirs, files in os.walk(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            for ext in audio_extensions:
                if file.endswith(ext):
                    return file_path
    else:
        return None





