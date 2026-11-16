describe("Endpoints do ValletWeb", () => {
  it("disponibiliza a página inicial", () => {
    cy.request("/").then((response) => {
      expect(response.status).to.equal(200);
      expect(response.headers["content-type"]).to.include("text/html");
      expect(response.body).to.include("Vallet");
    });
  });

  it("disponibiliza a página de login", () => {
    cy.request("/login/").then((response) => {
      expect(response.status).to.equal(200);
      expect(response.body).to.include("loginForm");
    });
  });

  it("redireciona a área do gestor para o login quando não autenticado", () => {
    cy.request({
      url: "/gestor/",
      followRedirect: false,
    }).then((response) => {
      expect(response.status).to.equal(302);
      expect(response.headers.location).to.include("/login/");
    });
  });

  it("redireciona a API de notificações para o login quando não autenticado", () => {
    cy.request({
      url: "/notificacoes/api/",
      followRedirect: false,
    }).then((response) => {
      expect(response.status).to.equal(302);
      expect(response.headers.location).to.include("/login/");
    });
  });

  it("valida os dados obrigatórios no endpoint de autenticação Firebase", () => {
    cy.request({
      method: "POST",
      url: "/auth/firebase/",
      body: {},
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.equal(400);
      expect(response.body).to.deep.equal({
        error: "E-mail e senha são obrigatórios.",
      });
    });
  });

  it("retorna 404 para uma rota inexistente", () => {
    cy.request({
      url: "/rota-inexistente/",
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.equal(404);
      expect(response.body).to.include("Not Found");
    });
  });

  it("redireciona o admin do Django para o login administrativo", () => {
    cy.request({
      url: "/admin/",
      followRedirect: false,
    }).then((response) => {
      expect(response.status).to.equal(302);
      expect(response.headers.location).to.include("/admin/login/");
    });
  });

  it("aplica cabeçalhos básicos de segurança", () => {
    cy.request("/").then((response) => {
      expect(response.headers["x-content-type-options"]).to.equal("nosniff");
      expect(response.headers["x-frame-options"]).to.equal("DENY");
      expect(response.headers["referrer-policy"]).to.equal("same-origin");
    });
  });

  it("mantém os campos obrigatórios no formulário de login", () => {
    cy.request("/login/").then((response) => {
      expect(response.body).to.include('id="email"');
      expect(response.body).to.include('id="password"');
      expect(response.body).to.include('id="loginForm"');
    });
  });
});
