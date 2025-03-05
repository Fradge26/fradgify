from flask import Flask, send_from_directory
from home import home_bp
from api import music_bp
import os
import logging


app = Flask(
    __name__,
    static_folder='../static',
    template_folder='templates'
)

app.config['LOG_LEVEL'] = logging.DEBUG

# Configure the logging
logging.basicConfig(level=app.config['LOG_LEVEL'],
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Optional: Add a FileHandler to save logs to a file
file_handler = logging.FileHandler('/var/log/flask_app2.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
app.logger.addHandler(file_handler)

# Define a relative path to the media directory
MEDIA_FOLDER = os.path.join(os.path.dirname(__file__), '../media')

# Register the Blueprints
app.register_blueprint(home_bp, url_prefix='/')  # This will handle the homepage route
app.register_blueprint(music_bp, url_prefix='/music')   # This will handle the API routes


if __name__ == '__main__':
    app.run(debug=True)
