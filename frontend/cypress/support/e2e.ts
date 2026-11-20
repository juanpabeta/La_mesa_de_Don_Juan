import './commands';

Cypress.on('uncaught:exception', (error) => {
  if (/ResizeObserver loop|Failed to fetch|Load failed/i.test(error.message)) return false;
  return true;
});
