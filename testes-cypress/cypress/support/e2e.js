// Comandos compartilhados pelos testes de navegação.

/** Login pela tela (usa cy.session para reaproveitar o cookie entre testes). */
Cypress.Commands.add("loginGestor", () => {
  const email = Cypress.env("ADMIN_EMAIL");
  const senha = Cypress.env("ADMIN_SENHA");

  cy.session(
    ["gestor", email],
    () => {
      cy.intercept("POST", "/auth/firebase/").as("firebaseLogin");
      cy.visit("/login/");
      cy.get("#email").type(email);
      cy.get("#password").type(senha, { log: false });
      cy.contains("button", "Entrar").click();
      cy.wait("@firebaseLogin").its("response.statusCode").should("eq", 200);
      cy.location("pathname").should("eq", "/gestor/");
    },
    {
      validate() {
        // Sessão ainda válida? Se não estiver, /gestor/ redireciona ao login.
        cy.request({ url: "/gestor/", followRedirect: false }).its("status").should("eq", 200);
      },
    }
  );
});

/**
 * Navega para uma rota clicando no link do menu quando ele existe na página;
 * se a página não tiver esse link, abre a rota diretamente.
 */
Cypress.Commands.add("irPara", (caminho) => {
  cy.get("body").then(($body) => {
    const link = $body.find(`a[href="${caminho}"]:visible`).first();
    if (link.length) {
      cy.wrap(link).click();
    } else {
      cy.visit(caminho);
    }
  });
});
