import Swiper from 'swiper';
// eslint-disable-next-line import/no-unresolved
import { Autoplay } from 'swiper/modules';

export default class DynamicHero {
    static selector() {
        return '[data-dynamic-hero]';
    }

    constructor(node) {
        this.node = node;
        this.swiperContainer = this.node.querySelector('.swiper');
        this.slides = this.node.querySelectorAll('.swiper-slide');
        this.nextButton = this.node.querySelector('[data-dynamic-hero-next]');
        this.prevButton = this.node.querySelector('[data-dynamic-hero-prev]');
        this.pauseButton = this.node.querySelector('[data-dynamic-hero-pause]');
        this.playButton = this.node.querySelector('[data-dynamic-hero-play]');
        this.bindEvents();
    }

    bindEvents() {
        if (!this.swiperContainer) {
            return;
        }

        // Check if the user prefers reduced motion - don't autoplay if they do
        const isReduced =
            window.matchMedia('(prefers-reduced-motion: reduce)').matches ===
            true;

        this.swiper = new Swiper(this.swiperContainer, {
            modules: [Autoplay],
            direction: 'vertical',
            slidesPerView: 1,
            speed: 1000,
            loop: true,
            autoplay: {
                delay: 5000,
                enabled: !isReduced,
            },
        });

        if (this.nextButton) {
            this.nextButton.addEventListener('click', () =>
                this.swiper.slideNext(),
            );
        }

        if (this.prevButton) {
            this.prevButton.addEventListener('click', () =>
                this.swiper.slidePrev(),
            );
        }

        if (this.pauseButton) {
            this.pauseButton.addEventListener('click', () =>
                this.swiper.autoplay.stop(),
            );
        }

        if (this.playButton) {
            this.playButton.addEventListener('click', () => {
                this.swiper.autoplay.start();
                this.swiper.slideNext();
            });
        }
    }
}
