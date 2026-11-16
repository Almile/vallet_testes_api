<reference types="cypress" />

describe("Evidências Visuais", () => {
  it("captura a página inicial", () => {
    cy.visit("/");
    cy.contains("Mobilidade inteligente").should("be.visible");
    cy.screenshot("01-home", { capture: "fullPage" });
  });

  it("captura a página de login", () => {
    cy.visit("/login/");
    cy.get("#loginForm").should("be.visible");
    cy.screenshot("02-login", { capture: "fullPage" });
  });

  it("captura a página 404", () => {
    cy.visit("/rota-inexistente/", { failOnStatusCode: false });
    cy.contains("Not Found").should("be.visible");
    cy.screenshot("03-404", { capture: "fullPage" });
  });

  it("captura o login em viewport mobile", () => {
    cy.viewport(390, 844);
    cy.visit("/login/");
    cy.get("#loginForm").should("be.visible");
    cy.document().then((doc) => {
      expect(doc.documentElement.scrollWidth).to.be.at.most(
        doc.documentElement.clientWidth + 1,
      );
    });
    cy.screenshot("04-login-mobile", { capture: "fullPage" });
  });
});
