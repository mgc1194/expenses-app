// src/mocks/households.ts — Mocks for Household, HouseholdDetail, and HouseholdMember.

import type { Household, HouseholdDetail, HouseholdMember } from '@serve/types/global';

export function makeHouseholdMember(overrides: Partial<HouseholdMember> = {}): HouseholdMember {
  return {
    id: 1,
    email: 'alice@example.com',
    first_name: 'Alice',
    last_name: 'Smith',
    ...overrides,
  };
}

export function makeHousehold(overrides: Partial<Household> = {}): Household {
  return {
    id: 1,
    name: 'Smith Household',
    ...overrides,
  };
}

export function makeHouseholdDetail(overrides: Partial<HouseholdDetail> = {}): HouseholdDetail {
  return {
    id: 1,
    name: 'Smith Household',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    members: [makeHouseholdMember()],
    ...overrides,
  };
}
