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
    },
};
