const { defineConfig } = require("cypress");

module.exports = defineConfig({
  allowCypressEnv: false,
  // O Render suspende instâncias ociosas: a primeira requisição pode levar
  // mais de 30s (cold start) ou responder 502/503 enquanto o app acorda.
  retries: {
    runMode: 2,
    openMode: 0,
  },
  responseTimeout: 120000,
  pageLoadTimeout: 120000,
  e2e: {
    baseUrl:
      process.env.CYPRESS_BASE_URL || "https://valletweb.onrender.com",
    specPattern: "cypress/e2e/**/*.cy.js",
    supportFile: false,
  },
});
