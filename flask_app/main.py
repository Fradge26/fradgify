import os
from flask import Flask, send_from_directory

from .api import music_bp
from .home import home_bp

app = Flask(
    __name__,
    static_folder='../static',
    template_folder='templates'
)

# Register the Blueprints
app.register_blueprint(home_bp, url_prefix='/')  # This will handle the homepage route
app.register_blueprint(music_bp, url_prefix='/music')   # This will handle the API routes


if __name__ == '__main__':
    app.run(debug=True)
