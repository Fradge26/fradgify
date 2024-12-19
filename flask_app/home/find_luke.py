from . import home_bp
import os
import re
import gzip
import json
from urllib.parse import unquote
from urllib.request import urlopen
import requests
from flask import Flask, render_template


@home_bp.route('/whereisluke')
def where_is_luke():
    luke_is_safe = False
    # Paths to the Apache access log and rotated logs
    log_dir_path = '/var/log/apache2/'
    current_log = log_dir_path + 'access.log'
    rotated_log_pattern = re.compile(r'access\.log\.\d+\.gz')
    # Regex pattern to match IP, time, and requested filename from an Apache log line
    log_pattern = r'^(\S+) - - \[(.*?)\] "GET (/[^ ]+)'

    buzzcocks_lines = []
    if os.path.exists(current_log):
        try:
            # Check the current log file
            read_log_file(current_log, buzzcocks_lines)

            if not buzzcocks_lines:
                current_log = log_dir_path + 'access.log.1'
                read_log_file(current_log, buzzcocks_lines)

            # Check the older rotated logs (access.log.*.gz)
            if not buzzcocks_lines:
                for filename in sorted(os.listdir(log_dir_path)):
                    print(filename)
                    if rotated_log_pattern.match(filename):
                        print(f"reading {filename}")
                        read_log_file(os.path.join(log_dir_path, filename), buzzcocks_lines)
                        if buzzcocks_lines:
                            break

            # Get the most recent line
            if buzzcocks_lines:
                most_recent_line = buzzcocks_lines[-1]  # The last one is the most recent

                # Extract IP, time, and filename using regex
                match = re.match(log_pattern, most_recent_line)
                print(match)

                if match:
                    print("match found")
                    ip_address = match.group(1)
                    time = match.group(2)
                    raw_filename = os.path.basename(match.group(3))

                    # Decode URL-encoded characters in the file path (e.g., %20 becomes a space)
                    decoded_filename = unquote(raw_filename)

                    # Get IP geolocation (latitude and longitude)
                    lat, lng, city, country = get_ip_location(ip_address)
                    luke_is_safe = True
        except Exception as e:
            print(e)
            return render_template("luke_is_lost.html")

    if luke_is_safe:
        return render_template('luke_is_safe.html',
                               decoded_filename=decoded_filename,
                               time=time,
                               ip_address=ip_address,
                               lat=lat, lng=lng,
                               city=city, country=country)
    else:
        return render_template("luke_is_lost.html")


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
        print(f"Error reading log file {log_file_path}: {e}")


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
        print(f"Error fetching IP location: {e}")
    return None, None
