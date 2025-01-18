from flask import Blueprint

# Define the Blueprint for the homepage
home_bp = Blueprint(
    'home',
    __name__,
)

# Import the routes related to the homepage
from . import home_route
from . import find_luke