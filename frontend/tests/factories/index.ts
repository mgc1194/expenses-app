// tests/factories/index.ts — Re-exports all test factories.
//
// Import from '@tests/factories' in test files and Storybook stories.
// Adding a new required field to a domain type only requires updating the
// corresponding factory here — not every test or story that uses it.
 
export { makeAccount, makeAccountType, makeBank } from '@tests/factories/accounts';
export { makeUser } from '@tests/factories/auth';
export { makeHousehold, makeHouseholdDetail, makeHouseholdMember } from '@tests/factories/households';
export { makeLabel } from '@tests/factories/labels';
export { makeFileImportResult, makeTransaction } from '@tests/factories/transactions';