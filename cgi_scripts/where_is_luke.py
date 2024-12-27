#!/usr/bin/env python3

import os
import re
import gzip
import json
from urllib.parse import unquote
from urllib.request import urlopen
import requests

# Paths to the Apache access log and rotated logs
log_dir_path = '/var/log/apache2/'
current_log = log_dir_path + 'access.log'
rotated_log_pattern = re.compile(r'access\.log\.\d+\.gz')

# Regex pattern to match IP, time, and requested filename from an Apache log line
log_pattern = r'^(\S+) - - \[(.*?)\] "GET (/[^ ]+)'

# Function to get IP location using ipinfo.io
def get_ip_location(ip):
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/geo')
        if response.status_code == 200:
            data = response.json()
            loc = data.get('loc', None)  # loc is a string like "lat,lng"
            if loc:
                lat, lng = map(float, loc.split(','))
                return lat, lng, data["city"], data["country"]
    except Exception as e:
        print(f"<p>Error fetching IP location: {e}</p>")
    return None, None, None, None

# Function to read and filter log lines from both current and older logs
def read_log_file(log_file_path, buzzcocks_lines):
    try:
        if log_file_path.endswith('.gz'):
            with gzip.open(log_file_path, 'rt') as log_file:
                buzzcocks_lines.extend([line for line in log_file if 'Buzzcocks' in line and 'Googlebot' not in line])
        else:
            with open(log_file_path, 'r') as log_file:
                buzzcocks_lines.extend([line for line in log_file if 'Buzzcocks' in line and 'Googlebot' not in line])
    except Exception as e:
        print(f"<p>Error reading log file {log_file_path}: {e}</p>")

# CGI Header
print("Content-Type: text/html")  # HTML is following
print()  # Blank line required

print("<html>")
print("<head><title>Where is Luke???</title>")
print("""
        <link rel="icon" type="image/x-icon" href="https://fradgify.kozow.com/media/music/fradgify/favicon.ico">
        <style>
            body {
                background-color: rgb(232, 250, 250);
            }
        </style>
"""
)

# Include Leaflet CSS and JS
print('''
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
''')

print("</head>")
print("<body>")
print('<img src="https://fradgify.kozow.com/fradgify_full.jpg" alt="Description of the image" style="max-width: 100%; height: auto;">')
print("<h1>Where is Luke???</h1>")

if os.path.exists(current_log):
    try:
        buzzcocks_lines = []
        # Check the current log file
        if os.path.exists(current_log):
            read_log_file(current_log, buzzcocks_lines)
        
        if not buzzcocks_lines:
            current_log = log_dir_path + 'access.log.1'
            read_log_file(current_log, buzzcocks_lines)

        # Check the older rotated logs (access.log.*.gz)
        if not buzzcocks_lines:
            # Find all the rotated logs and sort them numerically by their suffix (e.g., .1.gz, .2.gz, etc.)
            # rotated_logs = sorted([f for f in os.listdir(log_dir_path) if rotated_log_pattern.match(f)],
            #                   key=lambda x: int(rotated_log_pattern.match(x).group(1)))
            # print(sorted(os.listdir(log_dir_path)))
            for filename in sorted(os.listdir(log_dir_path)):
                if rotated_log_pattern.match(filename):
                    # print(filename)
                    read_log_file(os.path.join(log_dir_path, filename), buzzcocks_lines)
                    if buzzcocks_lines:
                        break

        # Get the most recent line
        if buzzcocks_lines:
            most_recent_line = buzzcocks_lines[-1]  # The last one is the most recent
            
            # Extract IP, time, and filename using regex
            match = re.match(log_pattern, most_recent_line)
            
            if match:
                ip_address = match.group(1)
                time = match.group(2)
                raw_filename = os.path.basename(match.group(3))

                # Decode URL-encoded characters in the file path (e.g., %20 becomes a space)
                decoded_filename = unquote(raw_filename)
                
                # Get IP geolocation (latitude and longitude)
                lat, lng, city, country = get_ip_location(ip_address)
                print("<p><strong>Last seen watching:</strong> {}</p>".format(decoded_filename))
                print("<p><strong>On:</strong> {}</p>".format(time))
                print("<p><strong>From IP Address:</strong> {}</p>".format(ip_address))

                if lat and lng:
                    # Generate the Leaflet map if location is available
                    print(f"<p><strong>Located at: </strong>{lat}, {lng} (lat, long)</p>")
                    print(f"<p><strong>In: </strong>{city}, {country}</p>")
                    print('''
                        <div id="map" style="height: 600px;"></div>
                        <script>
                            var map = L.map('map').setView([{lat}, {lng}], 5);
                            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                                maxZoom: 19,
                            }}).addTo(map);

                            var marker = L.marker([{lat}, {lng}]).addTo(map);
                            marker.bindPopup("<b>IP Location</b><br>Lat: {lat}<br>Lng: {lng}").openPopup();
                        </script>
                    '''.format(lat=lat, lng=lng))
                else:
                    print("<p>Could not find geolocation for the IP address.</p>")
            else:
                print("<p>Unable to parse the log entry.</p>")
        else:
            print("<p>No entries found for 'Buzzcocks' (excluding Googlebot) in the access log.</p>")
    except Exception as e:
        print(f"<p>Error reading log file: {e}</p>")
else:
    print(f"<p>Log file does not exist: {current_log}</p>")

print("</body>")
print("</html>")
