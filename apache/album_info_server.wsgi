import sys
import os

# Path to your virtual environment
venv_path = '/var/www/fradgify.kozow.com/album-player/myenv'

# Add the site-packages directory to the path
site_packages_path = os.path.join(venv_path, 'lib', 'python3.10', 'site-packages')
sys.path.insert(0, site_packages_path)

# Add your application path to the sys.path
sys.path.insert(0, '/var/www/fradgify.kozow.com/album-player')

# Set the FLASK_APP environment variable
os.environ['FLASK_APP'] = 'album_info_server'

# Import your Flask app
from album_info_server import app as application
