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
        'no-invalid-position-declaration': [
            true,
            {
                ignoreAtRules: ['utility'],
            },
        ],
        'scss/dollar-variable-no-missing-interpolation': null,
    },
};
