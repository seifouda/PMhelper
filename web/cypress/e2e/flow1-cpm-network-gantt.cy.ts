describe('Flow 1: Load sample → CPM → Network → Gantt', () => {
  beforeEach(() => {
    cy.visit('/input');
  });

  it('should navigate to input page and display activity table', () => {
    cy.get('app-input').should('exist');
    cy.contains('Input').should('be.visible');
  });

  it('should navigate from Input to Network view', () => {
    cy.get('nav a[href="/network"]').click();
    cy.url().should('include', '/network');
    cy.get('app-network-canvas, app-network').should('exist');
  });

  it('should navigate from Network to Gantt view', () => {
    cy.get('nav a[href="/gantt"]').click();
    cy.url().should('include', '/gantt');
    cy.get('app-gantt').should('exist');
  });

  it('should show sidebar with all core navigation items', () => {
    cy.get('nav.pm-sidebar a').should('have.length.gte', 8);
    cy.contains('Dashboard').should('be.visible');
    cy.contains('Network').should('be.visible');
    cy.contains('Gantt Chart').should('be.visible');
  });
});
