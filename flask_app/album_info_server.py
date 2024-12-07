from flask import Flask, jsonify, send_from_directory, request
import os
import logging
from mutagen import File
from mutagen.id3 import ID3, APIC
from collections import defaultdict
import json
import hashlib
from datetime import datetime as dt
from urllib.parse import quote

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

MUSIC_FOLDER = "/var/www/fradgify.kozow.com/media/music/complete"
ALBUMS_JSON_PATH = "/var/www/fradgify.kozow.com/album-player/browse/albums.json"
TEMP_ALBUM_ART_FOLDER = "/var/www/fradgify.kozow.com/album-player/album-art-extract"
logging.debug(f"api started: {__file__}")

@app.route('/album', methods=['GET'])
def get_album():
    # Get the folder path from the query parameter
    logging.debug(f"api endpoint /album called")
    folder_path = request.args.get('path', default='', type=str)
    album_path = os.path.join(MUSIC_FOLDER, folder_path)

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

def list_music_files(folder):
    filenames = os.listdir(folder.encode("utf-8"))
    out_files = [f.decode('utf-8').encode('utf-8', "surrogatepass").decode('utf-8') for f in filenames]
    out_files = [f for f in out_files if f.endswith(".mp3")]
    logging.debug(f"out_files: {out_files}")
    return sorted(out_files)

def get_album_art_path(album_path, audio):
    logging.debug("0")
    album_art = next((f for f in os.listdir(album_path) if f.lower().endswith('.jpg')), None)
    logging.debug("1")
    if album_art:
        return album_art
    # Look for the album art (APIC) frame
    for tag in audio.values():
        if isinstance(tag, APIC):
            logging.debug("2")
            album_art_data = tag.data
            album_art_mime = tag.mime.split('/')[-1]  # Get the image file extension
            hash_object = hashlib.sha256(album_art_data)
            short_hash = hash_object.hexdigest()[:12]
            logging.debug(short_hash)
            album_art_filename = f'{short_hash}.{album_art_mime}'
            album_art_filepath = os.path.join(TEMP_ALBUM_ART_FOLDER, album_art_filename)
            
            # Save the album art as an image file
            with open(album_art_filepath, 'wb') as img_file:
                img_file.write(album_art_data)
            
            logging.debug(f"Album art extracted to: {album_art_filepath}")
            return album_art_filename
    else:
        return None


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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running"}), 200

@app.route('/album_list', methods=['GET'])
def get_album_list():
    # Get the folder path from the query parameter
    logging.debug(f"api endpoint /album_list called")
    try:
        # album_dict = defaultdict(list)
        album_list = []
        # for folder in os.listdir(MUSIC_FOLDER):
        for root_path, dirnames, filenames in os.walk(MUSIC_FOLDER):
            for dirname in dirnames:
                current_dir = os.path.join(root_path, dirname)
                # logging.debug(f"{current_dir=}")
                audio_file_path = get_first_audio_file(current_dir)
                # logging.debug(f"{audio_file_path=}")
                # logging.debug(f"os.path.isdir(folder) {os.path.isdir(os.path.join(MUSIC_FOLDER, folder))} {folder}")
                if os.path.isdir(current_dir) and audio_file_path:
                    audio_file = File(audio_file_path)
                    artist, album, year = get_audio_file_info(audio_file)
                    rel_path = os.path.relpath(current_dir, MUSIC_FOLDER)
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
        with open(ALBUMS_JSON_PATH, "w") as final:
            json.dump(final_albums_dict, final)
        return jsonify({"success": f"{len(album_list)} albums written to albums.json at {dt.now()}"}, 200)

    except Exception as e:
        logging.debug(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500

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


if __name__ == '__main__':
    app.run(debug=True, port=3000)  # Change port if needed
