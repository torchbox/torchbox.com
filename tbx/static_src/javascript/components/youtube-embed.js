import Cookies from 'js-cookie';

/**
 * YouTubeConsentManager handles the consent for loading YouTube videos on a webpage.
 */
class YouTubeConsentManager {
    static selector() {
        return '.grid__embed.streamfield__embed.youtube-video-container';
    }

    /**
     * Create a new YouTubeConsentManager.
     */
    constructor(node) {
        this.consentButtonClass = 'consent-button';
        this.dontAskAgainButtonClass = 'dont-ask-again-button';
        this.videoPlaceholderClass = 'youtube-video-placeholder';
        this.youtubeEmbedClass = 'youtube-embed';

        this.youtubeEmbedContainer = node;
        this.consentButton = this.youtubeEmbedContainer.querySelector(
            `.${this.consentButtonClass}`,
        );
        this.dontAskAgainButton = this.youtubeEmbedContainer.querySelector(
            `.${this.dontAskAgainButtonClass}`,
        );
        this.videoPlaceholder = this.youtubeEmbedContainer.querySelector(
            `.${this.videoPlaceholderClass}`,
        );
        this.youtubeEmbed = this.youtubeEmbedContainer.querySelector(
            `.${this.youtubeEmbedClass}`,
        );

        // Bind event handlers
        this.consentButton.addEventListener(
            'click',
            this.handleconsentClick.bind(this),
        );
        this.dontAskAgainButton.addEventListener(
            'click',
            this.handleDontAskAgainClick.bind(this),
        );

        // Check if consent has been given previously
        this.checkConsent();
    }

    loadYouTubeEmbed() {
        // Hide the video placeholder
        this.videoPlaceholder.style.display = 'none';
        // Show the YouTube embed container
        this.youtubeEmbed.style.display = 'block';
    }

    handleconsentClick() {
        this.loadYouTubeEmbed();
    }

    handleDontAskAgainClick() {
        // Set a cookie to remember the user's choice not to ask again
        Cookies.set('youtube_consent', 'true', {
            expires: 7,
            secure: true,
            sameSite: 'Lax',
        });
        this.dontAskAgainButton.style.display = 'none';
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
