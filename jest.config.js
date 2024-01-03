// See https://jestjs.io/docs/en/configuration.
module.exports = {
    testEnvironment: 'jsdom',
    testPathIgnorePatterns: ['/node_modules/', '/static_compiled/', '/venv/'],
    collectCoverageFrom: ['**/tbx/static_src/javascript/**/*.{js,ts,tsx}'],
    moduleFileExtensions: ['js', 'ts', 'tsx', 'json', 'node'],
    transform: {
        '^.+\\.(js|ts|tsx)$': 'ts-jest',
    },
};
