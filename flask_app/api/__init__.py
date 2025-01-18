from flask import Blueprint

# Define the Blueprint for the API
music_bp = Blueprint('music', __name__)

# Import the routes related to the API
from . import music
