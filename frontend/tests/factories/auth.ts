// tests/factories/auth.ts — Factory for User.

import { makeHousehold } from '@test/factories/households';

import type { User } from '@serve/types/global';


export function makeUser(overrides: Partial<User> = {}): User {
  return {
    id: 1,
    username: 'alice@example.com',
    email: 'alice@example.com',
    first_name: 'Alice',
    last_name: 'Smith',
    households: [makeHousehold()],
    ...overrides,
  };
}
