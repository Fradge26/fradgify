import sys
import os

# Path to your virtual environment
venv_path = '/srv/fradgify/venv'

# Add the site-packages directory to the path
site_packages_path = os.path.join(venv_path, 'lib', 'python3.10', 'site-packages')
sys.path.insert(0, site_packages_path)

# Add your application path to the sys.path
sys.path.insert(0, '/var/www/fradgify.kozow.com')

# Set the FLASK_APP environment variable
os.environ['FLASK_APP'] = 'fradgify_api'

# Import your Flask app
from flask_app.main import app as application
