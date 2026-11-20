declare global {
  namespace Cypress {
    interface Chainable {
      loginByApi(email: string, password: string): Chainable<Cypress.Response<unknown>>;
      resetTestState(): Chainable<void>;
    }
  }
}

Cypress.Commands.add('loginByApi', (email: string, password: string) => {
  return cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/auth/login`,
    body: { correo: email, contraseña: password },
  }).then((response) => {
    expect(response.status).to.eq(200);
    const setCookie = response.headers['set-cookie'];
    expect(setCookie).to.exist;
    const cookieHeader = Array.isArray(setCookie) ? setCookie.join(';') : String(setCookie);
    expect(cookieHeader).to.include('HttpOnly');
    return response;
  });
});

Cypress.Commands.add('resetTestState', () => {
  cy.clearCookies();
  cy.clearLocalStorage();
  cy.visit('/login');
  cy.get('body').should('exist');
});

export {};
