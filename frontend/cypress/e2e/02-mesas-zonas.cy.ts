describe('Mesas, zonas y transferencia', () => {
  beforeEach(() => {
    cy.resetTestState();
  });

  it('filtra mesas por zona y crea una mesa desde el módulo', () => {
    cy.fixture('usuarios').then((usuarios) => {
      cy.loginByApi(usuarios.administrador.correo, usuarios.administrador.contraseña);
      cy.visit('/app/mesas');
      cy.contains('button', 'Todas').click();
      cy.get('.floor-table').should('have.length.greaterThan', 0);
      cy.contains('button', 'Terraza').click();
      cy.contains('Terraza').should('be.visible');

      cy.contains('button', 'Agregar mesa').click();
      const numero = 900 + Math.floor(Math.random() * 100);
      cy.get('input[type="number"]').first().type(String(numero));
      cy.contains('button', 'Guardar mesa').click();
      cy.request({
        method: 'GET',
        url: `${Cypress.env('apiUrl')}/mesas`,
        qs: { zona: 'Terraza' },
      }).its('body').should('be.an', 'array');
    });
  });

  it('transfiera una comanda activa a una mesa destino disponible', () => {
    cy.fixture('usuarios').then((usuarios) => {
      cy.fixture('platos').then((platos) => {
      cy.loginByApi(usuarios.mesero.correo, usuarios.mesero.contraseña);
      cy.loginByApi(usuarios.administrador.correo, usuarios.administrador.contraseña);
      cy.request('POST', `${Cypress.env('apiUrl')}/mesas`, { numero_mesa: 970 + Math.floor(Math.random() * 20), zona: 'Salón', capacidad: 4 }).then(({ body: origen }) => {
        cy.request('POST', `${Cypress.env('apiUrl')}/mesas`, { numero_mesa: 990 + Math.floor(Math.random() * 20), zona: 'Terraza', capacidad: 4 }).then(({ body: destino }) => {
          cy.request('POST', `${Cypress.env('apiUrl')}/menu`, { ...platos.ajiaco, nombre: `E2E transferencia ${platos.ajiaco.nombre}` }).then(({ body: dish }) => {
            cy.loginByApi(usuarios.mesero.correo, usuarios.mesero.contraseña);
            cy.request('POST', `${Cypress.env('apiUrl')}/pedidos`, { id_mesa: origen.id_mesa, detalles: [{ id_plato: dish.id_plato, cantidad: 1 }] }).then(({ body: order }) => {
              cy.visit('/app/mesas');
              cy.get('.floor-table').contains(String(origen.numero_mesa).padStart(2, '0')).click();
              cy.contains('button', 'Transferir').click();
              cy.get('#transfer-table').select(String(destino.id_mesa));
              cy.contains('button', 'Confirmar transferencia').click();
              cy.contains(`Mesa ${destino.numero_mesa}`).should('be.visible');
              cy.request('GET', `${Cypress.env('apiUrl')}/pedidos`).its('body').should('satisfy', (orders: Array<{ id_pedido: number; id_mesa: number }>) =>
                orders.some((item) => item.id_pedido === order.id_pedido && item.id_mesa === destino.id_mesa),
              );
            });
          });
        });
      });
      });
    });
  });
});
