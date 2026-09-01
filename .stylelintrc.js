module.exports = {
    // See https://github.com/torchbox/stylelint-config-torchbox for rules.
    extends: 'stylelint-config-torchbox',
    rules: {
        'unit-no-unknown': [
            true,
            {
                ignoreUnits: ['dvh'],
            },
        ],
        'property-no-unknown': [
            true,
            {
                ignoreProperties: ['container-type'],
            },
        ],
        'scss/at-rule-no-unknown': [
            true,
            {
                ignoreAtRules: [
                    'container',
                    'config',
                    'source',
                    'utility',
                    'theme',
                ],
            },
        ],
        'no-invalid-position-declaration': true,
        'scss/dollar-variable-no-missing-interpolation': null,
    },
    overrides: [
        {
            // Tailwind v4 CSS-first syntax (@utility/@theme/@config/@variant).
            // A newer stylelint's plain-CSS rules don't recognise these
            // at-rules as scoping contexts, so they false-positive on valid
            // v4 syntax. Null exactly these two rules for this directory —
            // every other rule (including scss/at-rule-no-unknown, which
            // already doesn't flag these at-rules as unknown) stays live.
            files: ['tbx/static_src/css/**/*.css'],
            rules: {
                'nesting-selector-no-missing-scoping-root': null,
                'no-invalid-position-declaration': null,
            },
        },
    ],
};
