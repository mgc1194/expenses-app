// tests/factories/accounts.ts — Factories for AccountDetail, AccountType, and Bank.

import type { AccountDetail, AccountType, Bank } from '@serve/types/global';

export function makeAccountType(overrides: Partial<AccountType> = {}): AccountType {
  return {
    id: 1,
    name: '360 Performance Savings',
    handler_key: 'co-savings',
    ...overrides,
  };
}

export function makeBank(overrides: Partial<Bank> = {}): Bank {
  return {
    id: 1,
    name: 'Capital One',
    account_types: [makeAccountType()],
    ...overrides,
  };
}

export function makeAccount(overrides: Partial<AccountDetail> = {}): AccountDetail {
  return {
    id: 1,
    name: "Alice's 360 Savings",
    handler_key: 'co-savings',
    account_type_id: 1,
    account_type: '360 Performance Savings',
    bank_id: 1,
    bank_name: 'Capital One',
    household_id: 1,
    household_name: 'Smith Household',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}
