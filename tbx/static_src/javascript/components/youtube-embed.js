import Cookies from 'js-cookie';

/**
 * YouTubeConsentManager handles the consent for loading YouTube videos on a webpage.
 */
class YouTubeConsentManager {
    static selector() {
        return '[data-youtube-embed]';
    }

    /**
     * Create a new YouTubeConsentManager.
     */
    constructor(node) {
        this.youtubeEmbedNode = node;
        this.consentButton = this.youtubeEmbedNode.querySelector(
            '[data-youtube-consent-button]',
        );
        this.dontAskAgainCheckbox = this.youtubeEmbedNode.querySelector(
            '[data-youtube-save-prefs]',
        );
        this.embedContainer = this.youtubeEmbedNode.querySelector(
            '[data-youtube-embed-container]',
        );
        this.bindEvents();
    }

    bindEvents() {
        this.consentButton.addEventListener('click', () => {
            this.handleconsentClick();
        });

        // Check if consent has been given previously
        this.checkConsent();
    }

    loadYouTubeEmbed() {
        // Hide the video placeholder and show the YouTube embed container
        this.youtubeEmbedNode.classList.add('loaded');
        this.embedContainer.setAttribute('tabindex', '1');
        this.embedContainer.focus();
    }

    handleconsentClick() {
        if (this.dontAskAgainCheckbox.checked) {
            this.handleDontAskAgainClick();
        }
        this.loadYouTubeEmbed();
    }

    handleDontAskAgainClick() {
        // Set a cookie to remember the user's choice not to ask again
        Cookies.set('youtube_consent', 'true', {
            expires: 7,
            secure: true,
            sameSite: 'Lax',
        });

        this.loadYouTubeEmbed();
    }

    checkConsent() {
        // Check if the user has previously given consent
        const hasConsent = Cookies.get('youtube_consent');
        if (hasConsent) {
            this.loadYouTubeEmbed();
        }
    }
}

export default YouTubeConsentManager;
