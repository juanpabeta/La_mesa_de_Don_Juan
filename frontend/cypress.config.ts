import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5173',
    viewportWidth: 1440,
    viewportHeight: 900,
    defaultCommandTimeout: 10_000,
    requestTimeout: 15_000,
    responseTimeout: 15_000,
    video: false,
    retries: { runMode: 1, openMode: 0 },
    experimentalWebKitSupport: false,
    setupNodeEvents(on, config) {
      return config;
    },
  },
  env: {
    apiUrl: 'http://localhost:8000/api/v1',
  },
});
