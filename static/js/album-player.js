let currentTrack = 0;
let sound = null;
let progressInterval = null;
let albumTracks = [];
let isPlaying = false; // Track if audio is currently playing
let isPaused = false; // Track if audio is currently paused

const artistNameElement = document.getElementById('artist-name');
const albumNameElement = document.getElementById('album-name');
const albumArtElement = document.getElementById('album-art');
const trackListElement = document.getElementById('track-list');
const trackInfoElement = document.getElementById('track-info');
const musicBaseFolder = "/media/music/complete";
const albumArtExtractFolder = "/static/album-art";
const defaultAlbumArt = "default_album_art.jpg";

// Function to fetch album data from the server with a dynamic folder path
function fetchAlbumData(folderPath) {
    fetch(`/music/album/?path=${encodeURIComponent(folderPath)}`)
        .then(response => response.json())
        .then(data => {
            albumTracks = data.musicFiles.map(file => {
                // Decode the filename first
                const decodedFile = decodeURIComponent(file); // Decode the URL-encoded file name
                const encodedFolderPath = encodeURIComponent(folderPath).replace(/%2F/g, '/');
                // console.log(file, decodedFile)
                return {
                    file: `${musicBaseFolder}/${encodedFolderPath}/${decodedFile}`, // Use the decoded file name
                    name: decodedFile.replace('.mp3', '') // Remove file extension for display
                };
            });

            console.log("Loading album-player with: ", folderPath)
            
            // Set the album and artist elements
            artistNameElement.textContent = data.albumInfo["artist"];
            albumNameElement.textContent = data.albumInfo["album"];

            const albumArt = data.albumArt;
            // Set the album art
            albumArtElement.src = `${albumArt}`;

            renderTrackList();
            trackInfoElement.innerText = "Now playing:"
        })
        .catch(error => console.error('Error fetching album data:', error));
}

// Example: Call fetchAlbumData based on user selection or a URL parameter
function loadAlbumBasedOnUserSelection(albumPath) {
    fetchAlbumData(albumPath);
    // Call the function to render the track list on page load or when the album is set
    console.log("THS ONE IT")
}

document.addEventListener('DOMContentLoaded', () => {
    // Get the full URL search parameters
    const urlParams = new URLSearchParams(window.location.search);

    // Get the 'path' parameter from the URL, which represents the album folder path
    const albumPath = urlParams.get('path');

    // Check if the album path exists in the URL
    if (albumPath) {
        // Call fetchAlbumData with the decoded album path
        fetchAlbumData(albumPath);
        // fetchAlbumData(decodeURIComponent(albumPath));
    } else {
        console.error('No album path specified in the URL.');
    }

    // Get references to the buttons and set up event listeners
    const previousTrackButton = document.querySelector('button[aria-label="Previous Track"]');
    const playPauseButton = document.querySelector('button[aria-label="Play / Pause"]');
    const nextTrackButton = document.querySelector('button[aria-label="Next Track"]');

    // Ensure the elements exist before attaching event listeners
    if (previousTrackButton) {
        previousTrackButton.addEventListener('click', function () {
            previousTrack(albumTracks);  // Assuming albumTracks is defined
        });
    } else {
        console.error('Previous track button not found');
    }

    if (playPauseButton) {
        playPauseButton.addEventListener('click', function () {
            togglePlayPause();  // Implement this function for play/pause functionality
        });
    } else {
        console.error('Play/Pause button not found');
    }

    if (nextTrackButton) {
        nextTrackButton.addEventListener('click', function () {
            nextTrack(albumTracks);  // Assuming nextTrack is defined
        });
    } else {
        console.error('Next track button not found');
    }

    // volume slide on change
    const volumeSlider = document.getElementById('volume');
    if (volumeSlider) {
        volumeSlider.addEventListener('change', (event) => {
            setVolume(event.target.value);
        });
    }
});

// Function to load and play a track
function playTrack(index, albumTracks) {
    currentTrack = index;

    if (sound) {
        sound.stop(); // Stop any currently playing track
    }
    console.log("track URL", albumTracks[currentTrack].file);
    // Load the current track
    sound = new Howl({
        src: [albumTracks[currentTrack].file],
        preload: true,
        autoplay: true,
        html5: true,
        volume: document.getElementById('volume').value,
        onend: function() {
            nextTrack(albumTracks); // Automatically play the next track when one finishes
        }
    });

    // Display the track info
    trackInfoElement.innerText = 'Now Playing: ' + albumTracks[currentTrack].name;

    // Start playing the track and update play state
    sound.play();
    isPlaying = true;

    // Update track progress every 100ms
    progressInterval = setInterval(updateProgress, 100);

    // Start the spinning animation
    // albumArtElement.classList.add('spin-animation');
}

// Function to play the next track
function nextTrack(albumTracks) {
    currentTrack = (currentTrack + 1) % albumTracks.length; // Loop back to the start
    playTrack(currentTrack, albumTracks); // Load and play the next track
}

// Function to play the previous track
function previousTrack(albumTracks) {
    currentTrack = (currentTrack - 1 + albumTracks.length) % albumTracks.length; // Loop back to the start
    playTrack(currentTrack, albumTracks); // Load and play the next track
}

// Function to pause the current track
function pauseTrack() {
    if (sound) {
        sound.pause(); // Pause the currently playing track
        clearInterval(progressInterval); // Clear the progress interval to stop updating the progress bar

        // Stop the spinning animation
        // albumArtElement.classList.remove('spin-animation');
        isPlaying = false; // Update the state
    }
}

// Function to set the volume
function setVolume(value) {
    if (sound) {
        sound.volume(value); // Set the volume in real-time
    }
}

// Function to update the progress bar
function updateProgress() {
    if (sound && sound.playing()) {
        const progress = sound.seek() / sound.duration(); // Get progress as a percentage
        document.getElementById('progress').style.width = (progress * 100) + '%'; // Update progress bar
    }
}

// Add event listener for seeking in the progress bar
document.getElementById('progress-container').addEventListener('click', (event) => {
    const progressBar = event.currentTarget;
    const rect = progressBar.getBoundingClientRect(); // Get bounding box
    const offsetX = event.clientX - rect.left; // Click position
    const width = rect.width; // Width of the progress bar
    const percentage = offsetX / width; // Calculate the percentage
    const newTime = percentage * sound.duration(); // Calculate new time in seconds

    if (sound) {
        sound.seek(newTime); // Seek to new time
        console.log('Seeking to:', newTime);
    }
});

// Function to toggle play/pause
function togglePlayPause() {
    const playPauseText = document.getElementById('play-pause-text');

    // If no track is currently loaded and the albumTracks array has tracks, play the first track
    if (!isPlaying && albumTracks && albumTracks.length > 0 && !isPaused) {
        playTrack(0, albumTracks); // Play the first track
        playPauseText.textContent = 'Pause'; // Update button text

        // Start the spinning animation
        // albumArtElement.classList.add('spin-animation');
        return; // Exit the function
    }

    if (sound) {
        if (isPlaying) {
            sound.pause(); // Pause the track
            playPauseText.textContent = 'Play '; // Update button text
            isPaused = true;

            // Stop the spinning animation
            // albumArtElement.classList.remove('spin-animation');
        } else {
            sound.play(); // Resume the track
            playPauseText.textContent = 'Pause'; // Update button text
            isPaused = false;

            // Start the spinning animation
            // albumArtElement.classList.add('spin-animation');
        }
        isPlaying = !isPlaying; // Toggle the state
    }
}

// Function to render the track list
function renderTrackList() {
    const trackListElement = document.getElementById('track-list');    
    trackListElement.innerHTML = ''; // Clear existing list
    console.log("GOT HERE")

    // Populate the track list
    albumTracks.forEach((track, index) => {
        
        // Set up the list item with flexbox
        const listItem = document.createElement('li');
        listItem.style.display = 'flex';      // Use flex layout
        listItem.style.alignItems = 'center'; // Center items vertically
        listItem.style.justifyContent = 'space-between';

        // Create a centered container for the track name
        const trackNameContainer = document.createElement('div');
        trackNameContainer.style.flex = '1';             // Take up available space
        trackNameContainer.style.textAlign = 'center';   // Center-align text

        // Create the track name element
        const trackName = document.createElement('span');
        trackName.textContent = track.name;
        // trackName.style.cursor = 'pointer';
        // trackName.onclick = () => playTrack(index, albumTracks); // Play the clicked track

        // Add the track name to the container
        trackNameContainer.appendChild(trackName);

        // Create a container for the buttons
        const buttonContainer = document.createElement('div');
        buttonContainer.style.display = 'flex';
        buttonContainer.style.gap = '5px'; // Space between buttons

        // Create the play button
        const playButton = document.createElement('button');
        playButton.innerHTML = '<img src="/static/icons/play_arrow_37dp_007BFF_FILL0_wght400_GRAD0_opsz40.svg" alt="Play" width="24" height="24">';
        playButton.onclick = () => playTrack(index, albumTracks); // Play the clicked track
        playButton.style.padding = '2px';
        playButton.style.width = '30px';
        playButton.style.height = '30px';

        // Create the download button
        const downloadButton = document.createElement('button');
        downloadButton.innerHTML = '<img src="/static/icons/download_37dp_007BFF_FILL0_wght400_GRAD0_opsz40.svg" alt="Download" width="24" height="24">';
        downloadButton.onclick = () => downloadTrack(track); // Function to download the track
        downloadButton.style.padding = '2px';
        downloadButton.style.width = '30px';
        downloadButton.style.height = '30px';

        // Append the buttons to the button container
        buttonContainer.appendChild(playButton);
        buttonContainer.appendChild(downloadButton);

        // Append elements to the list item
        listItem.appendChild(trackNameContainer); // Add centered track name
        listItem.appendChild(buttonContainer);    // Add buttons aligned to the right

        // Append the list item to the track list
        trackListElement.appendChild(listItem);
        console.log(listItem)
    });
    console.log("Album tracks:", albumTracks);
}

function downloadTrack(track) {
    const link = document.createElement('a');
    link.href = track.file;
    link.download = track.name + '.mp3';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Initialize Cast framework when the API is available
window.__onGCastApiAvailable = function(isAvailable) {
    if (isAvailable) {
        console.log("Cast API is available.");
        initializeCastContext();
    } else {
        console.error('Cast API is not available.');
    }
};

function initializeCastContext() {
    // Ensure that cast is defined before trying to use it
    if (typeof cast !== 'undefined') {
        console.log("Initializing Cast Context...");
        cast.framework.CastContext.getInstance().setOptions({
            receiverApplicationId: chrome.cast.media.DEFAULT_MEDIA_RECEIVER_APP_ID,
            autoJoinPolicy: chrome.cast.AutoJoinPolicy.ORIGIN_SCOPED,
        });
    } else {
        console.error("Cast API is not properly initialized.");
    }
}

// Cast audio to Chromecast
function castAudio() {
    const castSession = cast.framework.CastContext.getInstance().getCurrentSession();

    if (castSession) {
        const mediaInfo = new chrome.cast.media.MediaInfo(sound._src, 'audio/mp3');
        const request = new chrome.cast.media.LoadRequest(mediaInfo);

        castSession.loadMedia(request).then(
            () => console.log('Cast started!'),
            (errorCode) => console.error('Error starting cast:', errorCode)
        );
    } else {
        console.error('No cast session available!');
    }
}

// Bind cast button to castAudio function
document.getElementById('cast-button').addEventListener('click', castAudio);
