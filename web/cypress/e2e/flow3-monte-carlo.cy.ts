describe('Flow 3: Monte Carlo (percentiles)', () => {
  beforeEach(() => {
    cy.visit('/dashboard');
  });

  it('should redirect PG-only route for UG user', () => {
    // Monte Carlo is PG-only; default is UG mode
    cy.visit('/monte-carlo');
    // Should either redirect to dashboard or show toast
    cy.url().should('include', '/dashboard');
  });

  it('should allow Monte Carlo access after switching to PG mode', () => {
    // Toggle to PG mode via topbar
    cy.get('.pm-topbar__toggle--level').click();
    // Now navigate to Monte Carlo
    cy.get('nav a[href="/monte-carlo"]').click();
    cy.url().should('include', '/monte-carlo');
    cy.get('.mc-host').should('exist');
  });
});
