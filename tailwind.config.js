const plugin = require('tailwindcss/plugin');

module.exports = {
    content: ['./tbx/**/*.{py,html}', './tbx/static_src/**/*.{js,ts,tsx,vue}'],
    theme: {
        // Properties directly inside of theme will overwrite all tailwinds default properties for that attribute
        container: {
            center: true,
            padding: {
                DEFAULT: '1.25rem',
                sm: '2.5rem',
            },
        },
        colors: {
            primary: '#444',
            white: '#FFF',
            black: '#000',
            offBlack: '#141414',
            red: '#F00',
            inherit: 'inherit',
            current: 'currentColor',
            transparent: 'transparent',
            background: 'var(--color--background)',
            heading: 'var(--color--heading)',
            themePrimary: 'var(--color--theme-primary)',
        },
        screens: {
            sm: '410px',
            md: '599px',
            lg: '1023px',
            xlg: '1280px',
            xxlg: '1800px',
        },
        // Properties inside of extend will keep tailwinds existing properties for the attribute and add to them
        // https://tailwindcss.com/docs/theme
        extend: {
            // Any changes here will also need to be made in _variables.scss
            spacing: {
                spacerMini: '15px',
                spacerMiniPlus: '20px',
                spacerSmall: '30px',
                spacerSmallPlus: '40px',
                spacerMedium: '60px',
                spacerMediumPlus: '100px',
                spacerLarge: '120px',
                spacer: '160px',
                spacerHalf: '80px',
                spacerXLarge: '240px',
                spacerMassive: '360px',
            },
        },
    },
    // This tells tailwind which plugins specifically to use
    corePlugins: [
        'accessibility',
        'alignContent',
        'alignItems',
        'alignSelf',
        'container',
        'margin',
        'padding',
        'appearance',
        'backgroundColor',
        'borderRadius',
        'boxShadow',
        'display',
        'flex',
        'flexBasis',
        'flexDirection',
        'flexGrow',
        'flexShrink',
        'flexWrap',
        'fontSize',
        'fontStyle',
        'fontWeight',
        'gap',
        'gridAutoColumns',
        'gridAutoFlow',
        'gridAutoRows',
        'gridColumn',
        'gridColumnEnd',
        'gridColumnStart',
        'gridRow',
        'gridRowEnd',
        'gridRowStart',
        'gridTemplateColumns',
        'gridTemplateRows',
        'inset',
        'justifyContent',
        'justifyItems',
        'justifySelf',
        'margin',
        'opacity',
        'order',
        'overflow',
        'padding',
        'position',
        'preflight',
        'space',
        'textAlign',
        'textColor',
        'textDecoration',
        'textDecorationColor',
        'visibility',
        'zIndex',
    ],
    plugins: [
        /**
         * forced-colors media query for Windows High-Contrast mode support
         * See:
         * - https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors
         * - https://github.com/tailwindlabs/tailwindcss/blob/v3.0.23/src/corePlugins.js#L168-L171
         */
        plugin(({ addVariant }) => {
            addVariant('forced-colors', '@media (forced-colors: active)');
        }),
    ],
};
