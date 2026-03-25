describe('Flow 4: UG → PG guard → redirect + toast', () => {
  it('should redirect UG user from /rcps to /dashboard', () => {
    cy.visit('/rcps');
    cy.url().should('include', '/dashboard');
  });

  it('should redirect UG user from /wbs to /dashboard', () => {
    cy.visit('/wbs');
    cy.url().should('include', '/dashboard');
  });

  it('should redirect UG user from /swot to /dashboard', () => {
    cy.visit('/swot');
    cy.url().should('include', '/dashboard');
  });

  it('should redirect UG user from /pestel to /dashboard', () => {
    cy.visit('/pestel');
    cy.url().should('include', '/dashboard');
  });

  it('should allow PG user to access /rcps after level switch', () => {
    cy.visit('/dashboard');
    cy.get('.pm-topbar__toggle--level').click();
    cy.get('nav a[href="/rcps"]').click();
    cy.url().should('include', '/rcps');
  });
});
