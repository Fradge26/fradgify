from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent.parent
FLASK_APP_DIR = APP_ROOT / "flask_app"
STATIC_DIR = APP_ROOT / "static"
MEDIA_DIR = APP_ROOT / "media"
MUSIC_DIR = MEDIA_DIR / "music" / "complete"
ALBUMS_JSON_PATH = STATIC_DIR / "json" / "albums.json"
ALBUM_ART_DIR = STATIC_DIR / "album-art"
ALBUM_ART_DIR_URL = "/static/album-art"
MUSIC_DIR_REL = Path("media") / "music" / "complete"
