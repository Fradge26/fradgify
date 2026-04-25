let currentTrack = 0;
let sound = null;
let progressInterval = null;
let albumTracks = [];
let isPlaying = false;
let isPaused = false;
let activePlayback = null;
let preferredPlayback = 'local';

const artistNameElement = document.getElementById('artist-name');
const albumNameElement = document.getElementById('album-name');
const albumArtElement = document.getElementById('album-art');
const trackListElement = document.getElementById('track-list');
const trackInfoElement = document.getElementById('track-info');
const progressElement = document.getElementById('progress');
const volumeSlider = document.getElementById('volume');

const musicBaseFolder = `${window.location.origin}/media/music/complete`;
const defaultAlbumArt = '/static/album-art/default_album_art.jpg';

function updatePlayPauseText(label) {
    const playPauseText = document.getElementById('play-pause-text');
    if (playPauseText) {
        playPauseText.textContent = label;
    }
}

function clearProgressTimer() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

function startProgressTimer() {
    clearProgressTimer();
    progressInterval = setInterval(updateProgress, 250);
}

function getCastContext() {
    if (typeof cast === 'undefined' || !cast.framework) {
        return null;
    }
    return cast.framework.CastContext.getInstance();
}

function getCastSession() {
    const context = getCastContext();
    return context ? context.getCurrentSession() : null;
}

function getCastMediaSession() {
    const session = getCastSession();
    return session ? session.getMediaSession() : null;
}

function stopLocalPlayback() {
    if (sound) {
        sound.stop();
        sound.unload();
        sound = null;
    }
}

function setPlaybackState(source, playing) {
    activePlayback = source;
    if (source) {
        preferredPlayback = source;
    }
    isPlaying = playing;
    isPaused = !playing && source !== null;
    updatePlayPauseText(playing ? 'Pause' : 'Play');

    if (playing) {
        startProgressTimer();
    } else if (source !== 'cast') {
        clearProgressTimer();
    }
}

function fetchAlbumData(folderPath) {
    fetch(`/music/album/?path=${encodeURIComponent(folderPath)}`)
        .then(response => response.json())
        .then(data => {
            albumTracks = data.musicFiles.map(file => {
                const encodedFolderPath = encodeURIComponent(folderPath).replace(/%2F/g, '/');
                return {
                    file: `${musicBaseFolder}/${encodedFolderPath}/${encodeURIComponent(file)}`,
                    name: file.replace('.mp3', '')
                };
            });

            artistNameElement.textContent = data.albumInfo.artist;
            albumNameElement.textContent = data.albumInfo.album;
            albumArtElement.src = data.albumArt || defaultAlbumArt;

            renderTrackList();
            trackInfoElement.innerText = 'Now Playing:';
        })
        .catch(error => console.error('Error fetching album data:', error));
}

function playTrack(index, tracks, castOnly = false) {
    if (!tracks.length) {
        return;
    }

    currentTrack = index;

    if (castOnly) {
        castAudio(currentTrack);
        return;
    }

    stopLocalPlayback();

    sound = new Howl({
        src: [tracks[currentTrack].file],
        preload: true,
        autoplay: true,
        html5: true,
        volume: volumeSlider ? Number(volumeSlider.value) : 1,
        onplay: function() {
            setPlaybackState('local', true);
        },
        onpause: function() {
            setPlaybackState('local', false);
        },
        onstop: function() {
            clearProgressTimer();
        },
        onend: function() {
            nextTrack(tracks, false);
        }
    });

    sound.play();
    trackInfoElement.innerText = `Now Playing: ${tracks[currentTrack].name}`;
}

function nextTrack(tracks, castOnly = activePlayback === 'cast') {
    if (!tracks.length) {
        return;
    }
    currentTrack = (currentTrack + 1) % tracks.length;
    playTrack(currentTrack, tracks, castOnly);
}

function previousTrack(tracks, castOnly = activePlayback === 'cast') {
    if (!tracks.length) {
        return;
    }
    currentTrack = (currentTrack - 1 + tracks.length) % tracks.length;
    playTrack(currentTrack, tracks, castOnly);
}

function pauseTrack() {
    if (activePlayback === 'cast') {
        const media = getCastMediaSession();
        if (!media) {
            return;
        }
        media.pause(
            null,
            () => setPlaybackState('cast', false),
            err => console.error('Failed to pause cast playback', err)
        );
        return;
    }

    if (!sound) {
        return;
    }

    sound.pause();
}

function resumeTrack() {
    if (activePlayback === 'cast') {
        const media = getCastMediaSession();
        if (!media) {
            if (albumTracks.length) {
                castAudio(currentTrack);
            }
            return;
        }
        media.play(
            null,
            () => setPlaybackState('cast', true),
            err => console.error('Failed to resume cast playback', err)
        );
        return;
    }

    if (sound) {
        sound.play();
    }
}

function togglePlayPause() {
    if (!albumTracks.length) {
        return;
    }

    if (!isPlaying && !isPaused) {
        if (preferredPlayback === 'cast' && getCastSession()) {
            castAudio(currentTrack);
        } else {
            playTrack(currentTrack, albumTracks);
        }
        return;
    }

    if (isPlaying) {
        pauseTrack();
    } else {
        resumeTrack();
    }
}

function setVolume(value) {
    if (sound) {
        sound.volume(Number(value));
    }
}

function updateProgress() {
    if (!progressElement) {
        return;
    }

    if (activePlayback === 'cast') {
        const media = getCastMediaSession();
        const duration = media && media.media ? media.media.duration : 0;
        if (media && duration) {
            const progress = media.getEstimatedTime() / duration;
            progressElement.style.width = `${Math.min(progress, 1) * 100}%`;
        }
        return;
    }

    if (sound && sound.playing() && sound.duration()) {
        const progress = sound.seek() / sound.duration();
        progressElement.style.width = `${Math.min(progress, 1) * 100}%`;
    }
}

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
        playButton.onclick = () => {
            const shouldCast = preferredPlayback === 'cast' && !!getCastSession();
            playTrack(index, albumTracks, shouldCast);
        };
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

function downloadTrack(track) {
    const link = document.createElement('a');
    link.href = track.file;
    link.download = `${track.name}.mp3`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

window.__onGCastApiAvailable = function(isAvailable) {
    if (isAvailable) {
        initializeCastContext();
    }
};

function initializeCastContext(retries = 10) {
    const context = getCastContext();
    if (!context) {
        if (retries > 0) {
            window.setTimeout(() => initializeCastContext(retries - 1), 250);
            return;
        }
        console.error('Cast API not initialized');
        return;
    }

    context.setOptions({
        receiverApplicationId: chrome.cast.media.DEFAULT_MEDIA_RECEIVER_APP_ID,
        autoJoinPolicy: chrome.cast.AutoJoinPolicy.ORIGIN_SCOPED
    });

    context.addEventListener(
        cast.framework.CastContextEventType.SESSION_STATE_CHANGED,
        event => {
            if (
                event.sessionState === cast.framework.SessionState.SESSION_STARTED ||
                event.sessionState === cast.framework.SessionState.SESSION_RESUMED
            ) {
                preferredPlayback = 'cast';
            } else if (event.sessionState === cast.framework.SessionState.SESSION_ENDED) {
                preferredPlayback = 'local';
                activePlayback = sound ? 'local' : null;
                if (!sound) {
                    clearProgressTimer();
                    updatePlayPauseText('Play');
                    isPlaying = false;
                    isPaused = false;
                }
            }
        }
    );
}

function castAudio(trackIndex = currentTrack) {
    const session = getCastSession();
    const track = albumTracks[trackIndex];

    if (!track || !track.file) {
        console.error('Track data missing', track);
        return;
    }

    if (!session) {
        console.error('No cast session available');
        return;
    }

    stopLocalPlayback();

    const mediaInfo = new chrome.cast.media.MediaInfo(track.file, 'audio/mp3');
    const request = new chrome.cast.media.LoadRequest(mediaInfo);

    session.loadMedia(request)
        .then(() => {
            currentTrack = trackIndex;
            activePlayback = 'cast';
            setPlaybackState('cast', true);
            trackInfoElement.innerText = `Now Playing: ${track.name}`;

            const media = session.getMediaSession();
            if (!media) {
                return;
            }

            media.addUpdateListener(() => {
                if (media.playerState === chrome.cast.media.PlayerState.PLAYING) {
                    setPlaybackState('cast', true);
                } else if (media.playerState === chrome.cast.media.PlayerState.PAUSED) {
                    setPlaybackState('cast', false);
                } else if (
                    media.playerState === chrome.cast.media.PlayerState.IDLE &&
                    media.idleReason === chrome.cast.media.IdleReason.FINISHED
                ) {
                    nextTrack(albumTracks, true);
                }
            });
        })
        .catch(err => console.error('Failed to load media on cast device', err));
}

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const albumPath = urlParams.get('path');

    if (albumPath) {
        fetchAlbumData(albumPath);
    }

    const previousTrackButton = document.querySelector('button[aria-label="Previous Track"]');
    const playPauseButton = document.querySelector('button[aria-label="Play / Pause"]');
    const nextTrackButton = document.querySelector('button[aria-label="Next Track"]');
    const castButton = document.getElementById('cast-button');
    const progressContainer = document.getElementById('progress-container');

    if (previousTrackButton) {
        previousTrackButton.addEventListener('click', () => previousTrack(albumTracks));
    }
    if (playPauseButton) {
        playPauseButton.addEventListener('click', togglePlayPause);
    }
    if (nextTrackButton) {
        nextTrackButton.addEventListener('click', () => nextTrack(albumTracks));
    }
    if (volumeSlider) {
        volumeSlider.addEventListener('input', event => setVolume(event.target.value));
    }
    if (castButton) {
        castButton.addEventListener('click', () => {
            const session = getCastSession();
            if (session) {
                preferredPlayback = 'cast';
                if (albumTracks.length) {
                    castAudio(currentTrack);
                }
            }
        });
    }

    if (progressContainer) {
        progressContainer.addEventListener('click', event => {
            const rect = event.currentTarget.getBoundingClientRect();
            const offsetX = event.clientX - rect.left;
            const percentage = offsetX / rect.width;

            if (activePlayback === 'cast') {
                const media = getCastMediaSession();
                if (!media || !media.media || !media.media.duration) {
                    return;
                }
                const seekRequest = new chrome.cast.media.SeekRequest();
                seekRequest.currentTime = percentage * media.media.duration;
                media.seek(
                    seekRequest,
                    () => updateProgress(),
                    err => console.error('Failed to seek on cast device', err)
                );
                return;
            }

            if (!sound || !sound.duration()) {
                return;
            }

            sound.seek(percentage * sound.duration());
            updateProgress();
        });
    }
});
