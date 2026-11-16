/**
 * Testes de navegação do ValletWeb (Cypress).
 * NAV-01 a NAV-03 não precisam de conta. NAV-04 a NAV-06 usam a conta de gestor
 * definida em cypress.env.json; sem ela, ficam "pending" (Bloqueado).
 */
describe("ValletWeb — navegação", () => {
  before(() => {
    // Acorda o servidor (cold start do Render) antes dos testes.
    cy.request({ url: "/", timeout: 120000, failOnStatusCode: false });
  });

  it("NAV-01: da página inicial leva ao login pelo cabeçalho", () => {
    cy.visit("/");
    cy.title().should("include", "Vallet");
    cy.get("header").contains("a", "Login").click();
    cy.location("pathname").should("eq", "/login/");
    cy.title().should("eq", "Login - Vallet");
    cy.get("#email").should("be.visible");
    cy.get("#password").should("be.visible");
    cy.contains("button", "Entrar").should("be.visible");
  });

  it("NAV-02: área do gestor sem login redireciona para o login", () => {
    cy.visit("/gestor/");
    cy.location("pathname").should("eq", "/login/");
    cy.get("#loginForm").should("exist");
  });

  it("NAV-03: login com senha errada não entra e permanece no login", () => {
    cy.intercept("POST", "/auth/firebase/").as("firebaseLogin");
    cy.visit("/login/");
    cy.get("#email").type("usuario.inexistente@vallet.com");
    cy.get("#password").type("senhaErrada123");
    cy.contains("button", "Entrar").click();
    cy.wait("@firebaseLogin").its("response.statusCode").should("be.oneOf", [400, 401]);
    cy.location("pathname").should("eq", "/login/");
  });

  context("com gestor autenticado", () => {
    beforeEach(function () {
      if (!Cypress.env("ADMIN_EMAIL") || !Cypress.env("ADMIN_SENHA")) {
        this.skip(); // sem credenciais -> Bloqueado
      }
    });

    it("NAV-04: login válido abre o painel do gestor", () => {
      cy.loginGestor();
      cy.visit("/gestor/");
      cy.location("pathname").should("eq", "/gestor/");
      cy.get("body").should("not.contain", "Not Found");
    });

    it("NAV-05: do painel navega para Reservas e Notificações", () => {
      cy.loginGestor();
      cy.visit("/gestor/");

      cy.irPara("/reservas/");
      cy.location("pathname").should("eq", "/reservas/");

      cy.irPara("/notificacoes/");
      cy.location("pathname").should("eq", "/notificacoes/");
      cy.get("body").should("not.contain", "Server Error");
    });

    it("NAV-06: logout encerra a sessão e bloqueia o painel", () => {
      cy.loginGestor();
      cy.visit("/gestor/");
      cy.visit("/logout/");
      cy.location("pathname").should("eq", "/login/");
      cy.visit("/gestor/");
      cy.location("pathname").should("eq", "/login/");
    });
  });
});
