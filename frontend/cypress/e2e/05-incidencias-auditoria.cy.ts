describe('Incidencias y auditoría administrativa', () => {
  beforeEach(() => cy.resetTestState());

  it('reporta una incidencia y permite consultarla como administrador', () => {
    cy.fixture('usuarios').then((usuarios) => {
      cy.fixture('platos').then((platos) => {
        cy.loginByApi(usuarios.administrador.correo, usuarios.administrador.contraseña);
        cy.request('POST', `${Cypress.env('apiUrl')}/mesas`, { numero_mesa: 960 + Math.floor(Math.random() * 30), zona: 'Salón', capacidad: 4 }).then(({ body: table }) => {
          cy.request('POST', `${Cypress.env('apiUrl')}/menu`, { ...platos.ajiaco, nombre: `E2E ${platos.ajiaco.nombre}` }).then(({ body: dish }) => {
            cy.request('POST', `${Cypress.env('apiUrl')}/pedidos`, { id_mesa: table.id_mesa, detalles: [{ id_plato: dish.id_plato, cantidad: 1 }] }).then(({ body: order }) => {
              cy.loginByApi(usuarios.mesero.correo, usuarios.mesero.contraseña);
              cy.visit('/app/incidencias');
              cy.contains('button', 'Reportar incidencia').click();
              cy.get('#incident-order').type(String(order.id_pedido));
              cy.get('#incident-description').type('Prueba E2E: atraso en la entrega de la comanda.');
              cy.get('#incident-priority').select('ALTA');
              cy.contains('button', 'Registrar incidencia').click();
              cy.contains('Prueba E2E: atraso').should('be.visible');

              cy.loginByApi(usuarios.administrador.correo, usuarios.administrador.contraseña);
              cy.request('GET', `${Cypress.env('apiUrl')}/incidencias`).its('body').should('satisfy', (items: Array<{ descripcion: string }>) =>
                items.some((item) => item.descripcion.includes('Prueba E2E')),
              );
              cy.visit('/app/incidencias');
              cy.contains('Prueba E2E: atraso').should('be.visible');
            });
          });
        });
      });
    });
  });
});
