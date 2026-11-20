describe('Ciclo de pedido completo y sincronización KDS', () => {
  beforeEach(() => cy.resetTestState());

  it('Mesero crea; Cocina prepara y despacha; Mesero entrega', () => {
    cy.fixture('usuarios').then((usuarios) => {
      cy.fixture('platos').then((platos) => {
        cy.loginByApi(usuarios.administrador.correo, usuarios.administrador.contraseña);
        cy.request('POST', `${Cypress.env('apiUrl')}/mesas`, { numero_mesa: 950 + Math.floor(Math.random() * 40), zona: 'Salón', capacidad: 4 }).then(({ body: table }) => {
          cy.request('POST', `${Cypress.env('apiUrl')}/menu`, { ...platos.sancocho, nombre: `E2E ${platos.sancocho.nombre}` }).then(({ body: dish }) => {
            cy.loginByApi(usuarios.mesero.correo, usuarios.mesero.contraseña);
            cy.request('POST', `${Cypress.env('apiUrl')}/pedidos`, {
              id_mesa: table.id_mesa,
              detalles: [{ id_plato: dish.id_plato, cantidad: 1, observaciones: 'sin cebolla' }],
            }).then(({ body: order }) => {
              cy.visit('/app/pedidos');
              cy.contains(`#${order.id_pedido}`).should('be.visible');

              cy.loginByApi(usuarios.cocina.correo, usuarios.cocina.contraseña);
              cy.visit('/app/cocina');
              cy.contains(`#${order.id_pedido}`).parents('.kds-ticket').within(() => {
                cy.contains('Comenzar preparación').click();
              });
              cy.contains(`#${order.id_pedido}`).parents('.kds-ticket').within(() => {
                cy.contains('Marcar pedido listo').click();
              });

              cy.loginByApi(usuarios.mesero.correo, usuarios.mesero.contraseña);
              cy.visit('/app/pedidos');
              cy.request('PATCH', `${Cypress.env('apiUrl')}/pedidos/${order.id_pedido}/estado`, { estado: 'ENTREGADO' });
              cy.visit('/app/pedidos');
              cy.contains('Entregado').should('be.visible');
            });
          });
        });
      });
    });
  });
});
