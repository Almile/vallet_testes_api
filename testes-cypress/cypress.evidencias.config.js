const { defineConfig } = require("cypress");
const baseConfig = require("./cypress.config");

// Configuração separada para captura de evidências visuais. Não faz parte da
// suíte de regressão executada por `npm run cy:run`.
module.exports = defineConfig({
  ...baseConfig,
  e2e: {
    ...baseConfig.e2e,
    specPattern: "cypress/evidencias/**/*.cy.js",
  },
});
