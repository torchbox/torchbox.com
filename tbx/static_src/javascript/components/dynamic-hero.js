import Swiper from 'swiper';
// eslint-disable-next-line import/no-unresolved
import { Autoplay } from 'swiper/modules';

export default class DynamicHero {
    static selector() {
        return '[data-dynamic-hero]';
    }

    constructor(node) {
        this.node = node;
        this.initSwiper();
    }

    initSwiper() {
        if (!this.node) {
            return;
        }

        this.swiper = new Swiper(this.node, {
            modules: [Autoplay],
            direction: 'vertical',
            slidesPerView: 1,
            speed: 1000,
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
            },
        });
    }
}
