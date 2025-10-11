let currentTrack = 0;
let sound = null;
let progressInterval = null;
let albumTracks = [];
let isPlaying = false;
let isPaused = false;

const artistNameElement = document.getElementById('artist-name');
const albumNameElement = document.getElementById('album-name');
const albumArtElement = document.getElementById('album-art');
const trackListElement = document.getElementById('track-list');
const trackInfoElement = document.getElementById('track-info');

// Use full URL for deployment and local
const musicBaseFolder = `${window.location.origin}/media/music/complete`;
const defaultAlbumArt = "/static/album-art/default_album_art.jpg";

// Fetch album data
function fetchAlbumData(folderPath) {
    fetch(`/music/album/?path=${encodeURIComponent(folderPath)}`)
        .then(response => response.json())
        .then(data => {
            albumTracks = data.musicFiles.map(file => {
                const encodedFolderPath = encodeURIComponent(folderPath).replace(/%2F/g, '/');
                return {
                    file: `${musicBaseFolder}/${encodedFolderPath}/${file}`, // full URL
                    name: file.replace('.mp3', '')
                };
            });

            artistNameElement.textContent = data.albumInfo["artist"];
            albumNameElement.textContent = data.albumInfo["album"];
            albumArtElement.src = data.albumArt || defaultAlbumArt;

            renderTrackList();
            trackInfoElement.innerText = "Now Playing:";
        })
        .catch(error => console.error('Error fetching album data:', error));
}

// Load album from URL
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const albumPath = urlParams.get('path');

    if (albumPath) fetchAlbumData(albumPath);

    const previousTrackButton = document.querySelector('button[aria-label="Previous Track"]');
    const playPauseButton = document.querySelector('button[aria-label="Play / Pause"]');
    const nextTrackButton = document.querySelector('button[aria-label="Next Track"]');

    if (previousTrackButton) previousTrackButton.addEventListener('click', () => previousTrack(albumTracks));
    if (playPauseButton) playPauseButton.addEventListener('click', togglePlayPause);
    if (nextTrackButton) nextTrackButton.addEventListener('click', () => nextTrack(albumTracks));

    const volumeSlider = document.getElementById('volume');
    if (volumeSlider) volumeSlider.addEventListener('change', (event) => setVolume(event.target.value));

    const progressContainer = document.getElementById('progress-container');
    if (progressContainer) {
        progressContainer.addEventListener('click', (event) => {
            if (!sound) return;
            const rect = event.currentTarget.getBoundingClientRect();
            const offsetX = event.clientX - rect.left;
            const percentage = offsetX / rect.width;
            sound.seek(percentage * sound.duration());

            const castSession = cast.framework.CastContext.getInstance().getCurrentSession();
            const media = castSession.getMediaSession(); // the loaded media
            if (castSession && media) {
                const seekRequest = new chrome.cast.media.SeekRequest();
                seekRequest.currentTime = percentage * sound.duration();
                media.seek(
                    seekRequest,
                    () => console.log('Seek successful on cast device ✅'), // successCallback
                    (err) => console.error('Failed to seek on Cast ❌', err) // errorCallback
                );
            };
        });
    }

    const castButton = document.getElementById('cast-button');
    if (castButton) castButton.addEventListener('click', castAudio(currentTrack));
});

// Play a track
function playTrack(index, albumTracks, castOnly = false) {
    currentTrack = index;

    if (!castOnly && sound) {
        sound.stop(); // Stop any local playback
    }

    console.log("track URL", albumTracks[currentTrack].file);

    if (!castOnly) {
        // Local playback
        sound = new Howl({
            src: [albumTracks[currentTrack].file],
            preload: true,
            autoplay: true,
            html5: true,
            volume: document.getElementById('volume').value,
            onend: function() {
                nextTrack(albumTracks);
            }
        });
        sound.play();
        isPlaying = true;
        progressInterval = setInterval(updateProgress, 100);
    } else {
        // Cast playback
        castAudio(currentTrack);
    }

    // Update UI
    trackInfoElement.innerText = 'Now Playing: ' + albumTracks[currentTrack].name;
}


// Next/previous tracks
function nextTrack(albumTracks, castOnly = false) {
    currentTrack = (currentTrack + 1) % albumTracks.length;
    playTrack(currentTrack, albumTracks, castOnly);
}


function previousTrack(tracks) {
    currentTrack = (currentTrack - 1 + tracks.length) % tracks.length;
    playTrack(currentTrack, tracks);
}

// Pause track
function pauseTrack() {
    if (!sound) return;
    sound.pause();
    clearInterval(progressInterval);
    isPlaying = false;

    const castSession = cast.framework.CastContext.getInstance().getCurrentSession();
    const media = castSession.getMediaSession(); // the loaded media
    // Pause
    media.pause(
        null,
        () => console.log('Pause successful on cast device ✅'), // successCallback
        (err) => console.error('Failed to pause playback ❌', err) // errorCallback
    );
}

// Toggle play/pause
function togglePlayPause() {
    const playPauseText = document.getElementById('play-pause-text');

    if (!isPlaying && albumTracks.length && !isPaused) {
        playTrack(0, albumTracks);
        if (playPauseText) playPauseText.textContent = 'Pause';
        return;
    }

    if (!sound) return;

    if (isPlaying) {
        sound.pause();
        if (playPauseText) playPauseText.textContent = 'Play';
        isPaused = true;
    } else {
        sound.play();
        if (playPauseText) playPauseText.textContent = 'Pause';
        isPaused = false;
    }
    isPlaying = !isPlaying;
}

// Volume
function setVolume(value) {
    if (sound) sound.volume(value);
}

// Update progress bar
function updateProgress() {
    if (sound && sound.playing()) {
        const progress = sound.seek() / sound.duration();
        document.getElementById('progress').style.width = (progress * 100) + '%';
    }
    const castSession = cast.framework.CastContext.getInstance().getCurrentSession();
    const media = castSession.getMediaSession();
    if (castSession && media) {
        const progress = media.getEstimatedTime() / sound.duration();
        document.getElementById('progress').style.width = (progress * 100) + '%';
    }
}

// Render track list
function renderTrackList() {
    trackListElement.innerHTML = '';
    albumTracks.forEach((track, index) => {
        const listItem = document.createElement('li');
        listItem.style.display = 'flex';
        listItem.style.alignItems = 'center';
        listItem.style.justifyContent = 'space-between';

        const trackNameContainer = document.createElement('div');
        trackNameContainer.style.flex = '1';
        trackNameContainer.style.textAlign = 'center';

        const trackName = document.createElement('span');
        trackName.textContent = track.name;
        trackNameContainer.appendChild(trackName);

        const buttonContainer = document.createElement('div');
        buttonContainer.style.display = 'flex';
        buttonContainer.style.gap = '5px';

        const playButton = document.createElement('button');
        playButton.innerHTML = '<img src="/static/icons/play_arrow_37dp_007BFF_FILL0_wght400_GRAD0_opsz40.svg" alt="Play" width="24" height="24">';
        playButton.onclick = () => playTrack(index, albumTracks);
        playButton.style.padding = '2px';
        playButton.style.width = '30px';
        playButton.style.height = '30px';

        const downloadButton = document.createElement('button');
        downloadButton.innerHTML = '<img src="/static/icons/download_37dp_007BFF_FILL0_wght400_GRAD0_opsz40.svg" alt="Download" width="24" height="24">';
        downloadButton.onclick = () => downloadTrack(track);
        downloadButton.style.padding = '2px';
        downloadButton.style.width = '30px';
        downloadButton.style.height = '30px';

        buttonContainer.appendChild(playButton);
        buttonContainer.appendChild(downloadButton);

        listItem.appendChild(trackNameContainer);
        listItem.appendChild(buttonContainer);

        trackListElement.appendChild(listItem);
    });
}

// Download
function downloadTrack(track) {
    const link = document.createElement('a');
    link.href = track.file;
    link.download = track.name + '.mp3';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Cast API
window.__onGCastApiAvailable = function(isAvailable) {
    if (isAvailable) initializeCastContext();
};

function initializeCastContext() {
    if (typeof cast !== 'undefined') {
        cast.framework.CastContext.getInstance().setOptions({
            receiverApplicationId: chrome.cast.media.DEFAULT_MEDIA_RECEIVER_APP_ID,
            autoJoinPolicy: chrome.cast.AutoJoinPolicy.ORIGIN_SCOPED
        });
    } else {
        console.error("Cast API not initialized");
    }
}

function castAudio(trackIndex = currentTrack) {
    const track = albumTracks[trackIndex];

    if (!track || !track.file) {
        console.error('Track data missing!', track);
        return;
    }

    // Stop local playback
    if (sound) sound.pause();

    const audioUrl = track.file;
    const castSession = cast.framework.CastContext.getInstance().getCurrentSession();
    if (!castSession) {
        console.error('No cast session available!');
        return;
    }

    const mediaInfo = new chrome.cast.media.MediaInfo(audioUrl, 'audio/mp3');
    const request = new chrome.cast.media.LoadRequest(mediaInfo);

    castSession.loadMedia(request)
        .then(() => {
            console.log('Media loaded successfully on Cast:', track.name);
            trackInfoElement.innerText = 'Now Playing: ' + track.name;

            // Get media session for updates
            const media = castSession.getMediaSession();
            if (!media) return;

            // When track finishes, play the next one
            media.addUpdateListener(() => {
                if (media.playerState === chrome.cast.media.PlayerState.IDLE &&
                    media.idleReason === chrome.cast.media.IdleReason.FINISHED) {

                    currentTrack = (currentTrack + 1) % albumTracks.length;
                    castAudio(currentTrack); // Pass new index explicitly
                }
            });
        })
        .catch(err => console.error('Failed to load media:', err));
}





