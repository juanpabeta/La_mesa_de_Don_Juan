describe('Catálogo, 86 list y modificadores', () => {
  beforeEach(() => cy.resetTestState());

  it('crea y edita un plato desde el catálogo', () => {
    cy.fixture('usuarios').then((usuarios) => {
      cy.fixture('platos').then((platos) => {
        cy.loginByApi(usuarios.administrador.correo, usuarios.administrador.contraseña);
        cy.visit('/app/menu');
        cy.contains('button', 'Nuevo producto').click();
        cy.get('#dish-name').type(`E2E ${platos.ajiaco.nombre}`);
        cy.get('#dish-category').clear().type(platos.ajiaco.categoria);
        cy.get('#dish-price').type(String(platos.ajiaco.precio));
        cy.get('#dish-time').clear().type(String(platos.ajiaco.tiempo_estimado_min));
        cy.contains('button', 'Guardar producto').click();
        cy.contains(`E2E ${platos.ajiaco.nombre}`).should('be.visible');
      });
    });
  });

  it('marca un plato agotado y verifica bloqueo en vivo del pedido', () => {
    cy.fixture('usuarios').then((usuarios) => {
      cy.fixture('platos').then((platos) => {
        cy.loginByApi(usuarios.administrador.correo, usuarios.administrador.contraseña);
        cy.request('POST', `${Cypress.env('apiUrl')}/menu`, {
          nombre: `E2E 86 ${platos.bandeja.nombre}`,
          categoria: platos.bandeja.categoria,
          precio: platos.bandeja.precio,
          tiempo_estimado_min: platos.bandeja.tiempo_estimado_min,
        }).then(({ body: dish }) => {
          cy.request('PATCH', `${Cypress.env('apiUrl')}/menu/${dish.id_plato}/agotado`, { agotado: true });
          cy.visit('/app/menu');
          cy.contains(`E2E 86 ${platos.bandeja.nombre}`).parents('.menu-item-card').within(() => {
            cy.contains('Agotado').should('be.visible');
          });

          cy.loginByApi(usuarios.mesero.correo, usuarios.mesero.contraseña);
          cy.visit('/app/pedidos');
          cy.contains('button', 'Nueva comanda').click();
          cy.contains(`E2E 86 ${platos.bandeja.nombre}`).should('not.exist');
        });
      });
    });
  });
});
