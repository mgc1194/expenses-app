import '@testing-library/jest-dom';
import { afterAll, afterEach, beforeAll } from 'vitest';

import { server } from '@tests/utils/msw';


Object.defineProperty(document, 'cookie', {
  writable: true,
  configurable: true,
  value: 'csrftoken=test-csrf-token',
});

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

export {};
