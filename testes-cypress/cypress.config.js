const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: process.env.BASE_URL || "https://valletweb.onrender.com",
    specPattern: "cypress/e2e/**/*.cy.js",
    viewportWidth: 1366,
    viewportHeight: 800,
    pageLoadTimeout: 120000,
    defaultCommandTimeout: 20000,
    requestTimeout: 60000,
    responseTimeout: 60000,
    video: false,
    screenshotOnRunFailure: true,
    retries: { runMode: 1, openMode: 0 },
  },
});
