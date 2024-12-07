#!/usr/bin/env python3
import os
import cgi

# Set the URL path to the directory containing the files
directory_url = '/var/www/fradgify.kozow.com/media/movies'

# Function to get the most recently added files
def get_recent_files(directory, num_files=5):
    files = []
    for file in sorted(os.listdir(directory), key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)[:num_files]:
        files.append(file)
    return files

# Function to generate the HTML page
def generate_html(files, directory_url):
    print("Content-type: text/html\n")
    print("<html>")
    print("<head>")
    print("<title>Recent Files</title>")
    print("</head>")
    print("<body>")
    print("<h2>Most Recently Added Files:</h2>")

    for file in files:
        file_url = f"{directory_url}/{file}"
        print(f'<a href="{file_url}">{file}</a><br>')

    print("</body>")
    print("</html>")

# Main CGI script
def main():
    try:
        # Get the most recently added files
        recent_files = get_recent_files(directory_url)

        # Generate and print the HTML page
        generate_html(recent_files, directory_url)

    except Exception as e:
        # Print an error message if something goes wrong
        print(f"Content-type: text/plain\n\nError: {e}")

if __name__ == "__main__":
    main()
