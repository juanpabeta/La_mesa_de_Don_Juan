describe('Autenticación, cookie HttpOnly y RBAC', () => {
  beforeEach(() => {
    cy.resetTestState();
  });

  it('rechaza credenciales inválidas sin crear una sesión', () => {
    cy.visit('/login');
    cy.get('#email').type('nadie@lamesadedonjuan.local');
    cy.get('#password').type('Incorrecta123!');
    cy.contains('button', 'Entrar a La mesa de Don Juan').click();
    cy.contains('[role="alert"]', 'Credenciales inválidas');
    cy.getCookie('access_token').should('be.null');
  });

  it('inicia sesión por API, establece cookie HttpOnly y redirige al resumen', () => {
    cy.fixture('usuarios').then((usuarios) => {
      cy.loginByApi(usuarios.administrador.correo, usuarios.administrador.contraseña);
      cy.visit('/app/resumen');
      cy.url().should('include', '/app/resumen');
      cy.contains('Resumen').should('be.visible');
      cy.getCookie('access_token').should((cookie) => {
        expect(cookie).not.to.be.null;
        expect(cookie?.httpOnly).to.be.true;
      });
      cy.document().then((document) => {
        expect(document.cookie).not.to.include('access_token');
      });
    });
  });

  it('bloquea rutas y navegación según el rol', () => {
    cy.fixture('usuarios').then((usuarios) => {
      cy.loginByApi(usuarios.mesero.correo, usuarios.mesero.contraseña);
      cy.visit('/app/usuarios');
      cy.url().should('include', '/app/resumen');
      cy.get('nav').should('not.contain', 'Usuarios');

      cy.visit('/app/cocina');
      cy.url().should('include', '/app/resumen');
    });
  });

  it('cierra sesión y elimina el acceso protegido', () => {
    cy.fixture('usuarios').then((usuarios) => {
      cy.loginByApi(usuarios.administrador.correo, usuarios.administrador.contraseña);
      cy.visit('/app/resumen');
      cy.get('.profile-row').click();
      cy.url().should('include', '/login');
      cy.getCookie('access_token').should('be.null');
      cy.visit('/app/reportes');
      cy.url().should('include', '/login');
    });
  });
});
