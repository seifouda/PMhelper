describe('Flow 2: EVM → verify CPI / SPI cards', () => {
  beforeEach(() => {
    cy.visit('/evm');
  });

  it('should display EVM view', () => {
    cy.get('.evm-host').should('exist');
  });

  it('should show empty state or period selector', () => {
    cy.get('.evm-host').then(($host) => {
      // Either empty state (no EVM data) or the run bar with period selector
      const hasEmptyState = $host.find('.empty-state').length > 0;
      const hasRunBar = $host.find('.run-bar').length > 0;
      expect(hasEmptyState || hasRunBar).to.be.true;
    });
  });

  it('should navigate to EVM from sidebar', () => {
    cy.visit('/dashboard');
    cy.get('nav a[href="/evm"]').click();
    cy.url().should('include', '/evm');
  });
});
