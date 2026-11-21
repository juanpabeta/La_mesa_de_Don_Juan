describe('Reportes, KPIs y exportación', () => {
  beforeEach(() => cy.resetTestState());

  it('muestra métricas calculadas y permite cambiar el periodo', () => {
    cy.fixture('usuarios').then((usuarios) => {
      cy.loginByApi(usuarios.administrador.correo, usuarios.administrador.contraseña);
      cy.visit('/app/reportes');
      cy.contains('Ventas totales').should('be.visible');
      cy.contains('Pedidos completados').should('be.visible');
      cy.contains('Ticket promedio').should('be.visible');
      cy.get('.period-picker select').select('30 días');
      cy.get('.period-picker select').should('have.value', '30 días');
    });
  });

  it('descarga reportes CSV y JSON', () => {
    cy.fixture('usuarios').then((usuarios) => {
      cy.loginByApi(usuarios.administrador.correo, usuarios.administrador.contraseña);
      cy.visit('/app/reportes');

      cy.contains('button', 'Exportar CSV').click();
      cy.readFile('cypress/downloads/la-mesa-de-don-juan-reporte-7-días.csv', { timeout: 10_000 }).should('contain', 'Día,Ventas COP,Pedidos');

      cy.contains('button', 'Exportar JSON').click();
      cy.readFile('cypress/downloads/la-mesa-de-don-juan-reporte-7-días.json', { timeout: 10_000 }).should((report) => {
        expect(report).to.have.property('ventas_totales_cop');
        expect(report).to.have.property('ventas_por_dia');
      });
    });
  });
});
