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
        this.calculateSwiperHeight();
        this.initSwiper();
        this.addResizeListener();
    }

    calculateSwiperHeight() {
        let maxHeight = 0;

        this.slides.forEach((slide) => {
            const { height } = slide.getBoundingClientRect();
            maxHeight = Math.max(maxHeight, height);
        });

        // Add 60px to the max height to account for the padding-bottom
        this.swiperContainer.style.height = `${maxHeight + 60}px`;
    }

    initSwiper() {
        if (!this.swiperContainer) {
            return;
        }

        this.swiper = new Swiper(this.swiperContainer, {
            modules: [Autoplay],
            direction: 'vertical',
            slidesPerView: 1,
            speed: 1000,
            loop: true,
            autoplay: {
                delay: 5000,
                enabled: false,
            },
            breakpoints: {
                1023: {
                    autoplay: {
                        enabled: true,
                    },
                },
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
    }

    addResizeListener() {
        window.addEventListener('resize', () => {
            this.calculateSwiperHeight();
            this.initSwiper();
        });
    }

    /*     // Check if the user prefers reduced motion - only use smooth scroll if they don't
    const isReduced =
    window.matchMedia('(prefers-reduced-motion: reduce)').matches ===
    true; */
}
