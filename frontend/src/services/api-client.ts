// services/api-client.ts — Shared fetch wrapper and error class for all service modules.
//
// CSRF: Django Ninja enforces CSRF on cookie-authenticated endpoints.
// We read the csrftoken cookie and send it as X-CSRFToken on all
// mutating requests (POST, PUT, PATCH, DELETE).

import { API_V1 } from '@serve/config';

let cachedCsrfToken: string | null = null;

async function getCsrfToken(): Promise<string> {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  if (match) return match[1];
  if (cachedCsrfToken) return cachedCsrfToken;
  const res = await fetch(`${import.meta.env.VITE_API_BASE ?? ''}/api/v1/csrf/`, {
    credentials: 'include',
  });
  const data = await res.json();
  cachedCsrfToken = data.csrfToken;
  return cachedCsrfToken!;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }

  get isUnauthorized(): boolean {
    return this.status === 401 || this.status === 403;
  }

  get isServerError(): boolean {
    return this.status >= 500;
  }
}

const MUTATING_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const method = (options.method ?? 'GET').toUpperCase();
  const csrfToken = MUTATING_METHODS.has(method) ? await getCsrfToken() : '';

  const response = await fetch(`${API_V1}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(MUTATING_METHODS.has(method) ? { 'X-CSRFToken': csrfToken } : {}),
      ...options.headers,
    },
    credentials: 'include',
  });

  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({ detail: 'An unexpected error occurred.' }));
    throw new ApiError(response.status, body.detail ?? 'An unexpected error occurred.');
  }

  if (response.status === 204) return undefined as T;

  return response.json() as Promise<T>;
}
