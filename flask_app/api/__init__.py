from flask import Blueprint

# Define the Blueprint for the API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import the routes related to the API
from . import routes
