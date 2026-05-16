import '@testing-library/jest-dom';
import { server } from '@tests/utils/msw';
import { afterAll, afterEach, beforeAll, beforeEach } from 'vitest';

beforeEach(() => {
  Object.defineProperty(document, 'cookie', {
    writable: true,
    configurable: true,
    value: 'csrftoken=test-csrf-token',
  });
});

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

export {};
