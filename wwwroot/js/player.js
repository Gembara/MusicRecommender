const spotifyPlayer = {
    currentTrack: null,
    playerContainer: null,
    currentIframe: null,

    init() {
        this.playerContainer = document.getElementById('spotifyPlayer');
        this.loadPlayerState();
        window.addEventListener('beforeunload', () => this.savePlayerState());

        // Відновлюємо стан після навігації
        if (window.performance && window.performance.navigation.type === window.performance.navigation.TYPE_BACK_FORWARD) {
            this.restorePlayerState();
        }
    },

    createPlayerContent(trackId, title, artist, imageUrl) {
        return `
            <div class="player-content">
                <div class="player-info">
                    <img src="${imageUrl}" alt="${title}" class="player-image">
                    <div class="player-text">
                        <div class="player-title">${title}</div>
                        <div class="player-artist">${artist}</div>
                    </div>
                </div>
                <div class="player-iframe-container"></div>
            </div>`;
    },

    createIframe(trackId) {
        const iframe = document.createElement('iframe');
        iframe.className = 'spotify-player-iframe';
        iframe.src = `https://open.spotify.com/embed/track/${trackId}?utm_source=generator`;
        iframe.frameBorder = '0';
        iframe.allowFullscreen = true;
        iframe.allow = 'autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture';
        return iframe;
    },

    playTrack(trackId, title, artist, imageUrl) {
        if (this.currentTrack === trackId && this.currentIframe) {
            this.playerContainer.style.display = 'block';
            return;
        }

        this.currentTrack = trackId;
        this.playerContainer.style.display = 'block';

        // Оновлюємо контент плеєра
        this.playerContainer.innerHTML = this.createPlayerContent(trackId, title, artist, imageUrl);

        // Створюємо новий iframe
        const iframeContainer = this.playerContainer.querySelector('.player-iframe-container');
        if (this.currentIframe) {
            this.currentIframe.remove();
        }
        this.currentIframe = this.createIframe(trackId);
        iframeContainer.appendChild(this.currentIframe);

        this.savePlayerState();
    },

    savePlayerState() {
        if (this.currentTrack) {
            const playerState = {
                trackId: this.currentTrack,
                title: this.playerContainer.querySelector('.player-title')?.textContent,
                artist: this.playerContainer.querySelector('.player-artist')?.textContent,
                imageUrl: this.playerContainer.querySelector('.player-image')?.src,
                timestamp: Date.now(),
                scrollPosition: window.scrollY
            };
            sessionStorage.setItem('spotifyPlayerState', JSON.stringify(playerState));
        }
    },

    loadPlayerState() {
        const savedState = sessionStorage.getItem('spotifyPlayerState');
        if (savedState) {
            const state = JSON.parse(savedState);
            if (state && Date.now() - state.timestamp < 30 * 60 * 1000) {
                this.playTrack(state.trackId, state.title, state.artist, state.imageUrl);
                if (state.scrollPosition) {
                    window.scrollTo(0, state.scrollPosition);
                }
            } else {
                sessionStorage.removeItem('spotifyPlayerState');
            }
        }
    },

    restorePlayerState() {
        const savedState = sessionStorage.getItem('spotifyPlayerState');
        if (savedState) {
            const state = JSON.parse(savedState);
            if (state && Date.now() - state.timestamp < 30 * 60 * 1000) {
                this.playTrack(state.trackId, state.title, state.artist, state.imageUrl);
            }
        }
    }
};

// Ініціалізуємо плеєр після завантаження сторінки
document.addEventListener('DOMContentLoaded', () => spotifyPlayer.init());

// Зберігаємо стан перед навігацією
window.addEventListener('pagehide', () => {
    if (spotifyPlayer.currentTrack) {
        spotifyPlayer.savePlayerState();
    }
}); 