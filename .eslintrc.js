module.exports = {
    // See https://github.com/torchbox/eslint-config-torchbox for rules.
    extends: 'torchbox/typescript',
    settings: {
        // Manually set the version to disable automated detection of the "react" dependency.
        // This is actually because we don't have react in this project
        react: { version: '18.2.0' },
    },
    rules: {
        // tailwindcss@4 uses package.json exports which eslint-import-resolver-node doesn't support.
        'import/no-unresolved': ['error', { ignore: ['^tailwindcss'] }],
    },
};
