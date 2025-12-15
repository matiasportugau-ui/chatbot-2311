module.exports = {
    preset: 'ts-jest',
    testEnvironment: 'node',
    testMatch: ['**/tests/**/*.test.ts', '**/tests/**/*.test.tsx', '**/tests/**/*.test.js'],
    moduleFileExtensions: ['ts', 'tsx', 'js', 'json'],
    globals: {
        'ts-jest': {
            tsconfig: 'tsconfig.json',
        },
    },
};
