describe('Usuarios y desactivación lógica', () => {
  beforeEach(() => cy.resetTestState());

  it('crea un empleado, asigna rol y verifica su desactivación', () => {
    cy.fixture('usuarios').then((usuarios) => {
      cy.loginByApi(usuarios.administrador.correo, usuarios.administrador.contraseña);
      cy.visit('/app/usuarios');
      cy.contains('button', 'Agregar empleado').click();
      const stamp = Date.now();
      const correo = `qa-${stamp}@lamesadedonjuan.local`;
      cy.get('#user-name').type('Empleado');
      cy.get('#user-surname').type('QA');
      cy.get('#user-email').type(correo);
      cy.get('#user-password').type('Empleado123!');
      cy.contains('.role-option', 'Cocinero').find('input[type="checkbox"]').check();
      cy.contains('button', 'Crear integrante').click();
      cy.contains(correo).should('be.visible');

      cy.request('GET', `${Cypress.env('apiUrl')}/usuarios`).then(({ body: users }) => {
        const empleado = users.find((user: { correo: string }) => user.correo === correo);
        expect(empleado).to.exist;
        cy.request('DELETE', `${Cypress.env('apiUrl')}/usuarios/${empleado.id_usuario}`).its('status').should('eq', 204);
        cy.request('GET', `${Cypress.env('apiUrl')}/usuarios`).its('body').should('satisfy', (items: Array<{ correo: string; estado: boolean }>) =>
          items.some((item) => item.correo === correo && item.estado === false),
        );
      });
    });
  });

  it('bloquea el acceso de un usuario inactivo', () => {
    cy.fixture('usuarios').then((usuarios) => {
      cy.request({
        method: 'POST',
        url: `${Cypress.env('apiUrl')}/auth/login`,
        body: { correo: usuarios.inactivo.correo, contraseña: usuarios.inactivo.contraseña },
        failOnStatusCode: false,
      }).its('status').should('be.oneOf', [401, 403]);
    });
  });
});
