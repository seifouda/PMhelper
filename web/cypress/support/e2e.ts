// Global Cypress support file
Cypress.on('uncaught:exception', () => {
  // Prevent Cypress from failing on unhandled Angular errors during tests
  return false;
});
