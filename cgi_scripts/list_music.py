#!/usr/bin/env python3

import os
import cgi
import cgitb

# Enable CGI error reporting
cgitb.enable()

# Set the content type to HTML
print("Content-Type: text/html\n")

# Get the query parameters
form = cgi.FieldStorage()
dir_param = form.getvalue('dir', '')

# Base music directory
base_music_dir = '/var/www/fradgify.kozow.com/media/music/complete'
site_music_dir = 'https://fradgify.kozow.com/media/music/complete'

# Construct the full path
full_path = os.path.join(base_music_dir, dir_param)

# Check if the directory exists
if not os.path.isdir(full_path):
    print(f"<h1>Error: Directory '{full_path}' not found.</h1>")
else:
    print(f"<h1>Listing files in: {full_path}</h1>")
    print("<ul>")

    # List all files in the directory
    for filename in sorted(os.listdir(full_path)):
        # Only show audio files
        if filename.lower().endswith(('.mp3', '.wav', '.flac')):  # Add other audio extensions if needed
            file_path = os.path.join(full_path, filename)  # Full path to the audio file
            source_path = file_path.replace(base_music_dir, site_music_dir)
            # Display the audio player on the left and filename on the right
            print(f'<li style="display: flex; align-items: center;">')
            print(f'<audio controls style="margin-right: 10px;">')  # Margin for spacing
            print(f'  <source src="{source_path}" type="audio/mpeg">')  # Change the type based on file extension
            print(f'  Your browser does not support the audio tag.')
            print(f'</audio>')
            print(f'<span>{filename}</span>')
            print('</li>')

    print("</ul>")
