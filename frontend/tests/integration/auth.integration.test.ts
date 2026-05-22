// tests/integration/auth.integration.test.ts — Auth service integration tests.

import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';

import { ApiError } from '@services/api-client';
import { getMe, login, logout, register, updatePassword, updateProfile } from '@services/auth';

import { mockUser, server } from '../utils/msw';


describe('login', () => {
  it('returns the user on success', async () => {
    const user = await login({ email: 'test@example.com', password: 'secret' });
    expect(user).toMatchObject({ email: mockUser.email });
  });

  it('throws ApiError with status 401 on invalid credentials', async () => {
    server.use(http.post('/api/v1/auth/login', () =>
      HttpResponse.json({ detail: 'Invalid credentials' }, { status: 401 })));
    await expect(login({ email: 'a@b.com', password: 'wrong' }))
      .rejects.toMatchObject({ status: 401 });
  });
});


describe('register', () => {
  it('returns the created user on success', async () => {
    const user = await register({ email: 'new@example.com', password: 'Pw1!', confirm_password: 'Pw1!' });
    expect(user).toMatchObject({ email: mockUser.email });
  });

  it('throws ApiError with status 400 on duplicate email', async () => {
    server.use(http.post('/api/v1/auth/register', () =>
      HttpResponse.json({ detail: 'Email already exists' }, { status: 400 })));
    await expect(register({ email: 'dupe@example.com', password: 'Pw1!', confirm_password: 'Pw1!' }))
      .rejects.toMatchObject({ status: 400 });
  });
});


describe('logout', () => {
  it('resolves on 204', async () => {
    await expect(logout()).resolves.toBeUndefined();
  });
});


describe('getMe', () => {
  it('returns the current user on success', async () => {
    const user = await getMe();
    expect(user).toMatchObject({ email: mockUser.email });
  });

  it('throws ApiError with status 401 when unauthenticated', async () => {
    server.use(http.get('/api/v1/auth/me', () => new HttpResponse(null, { status: 401 })));
    await expect(getMe()).rejects.toBeInstanceOf(ApiError);
  });
});


describe('updateProfile', () => {
  it('returns the updated user on success', async () => {
    const user = await updateProfile({ first_name: 'Jane' });
    expect(user).toMatchObject({ first_name: 'Jane' });
  });

  it('throws ApiError with status 400 on duplicate email', async () => {
    server.use(http.patch('/api/v1/auth/me', () =>
      HttpResponse.json({ detail: 'An account with this email already exists.' }, { status: 400 })));
    await expect(updateProfile({ email: 'taken@example.com' })).rejects.toMatchObject({ status: 400 });
  });
});


describe('updatePassword', () => {
  it('resolves on success', async () => {
    await expect(updatePassword({
      current_password: 'Old1!',
      new_password: 'New1!',
      confirm_new_password: 'New1!',
    })).resolves.toBeUndefined();
  });

  it('throws ApiError with status 400 on wrong current password', async () => {
    server.use(http.post('/api/v1/auth/me/password', () =>
      HttpResponse.json({ detail: 'Current password is incorrect.' }, { status: 400 })));
    await expect(updatePassword({
      current_password: 'wrong',
      new_password: 'New1!',
      confirm_new_password: 'New1!',
    })).rejects.toMatchObject({ status: 400, message: 'Current password is incorrect.' });
  });

  it('throws ApiError with status 400 on mismatched passwords', async () => {
    server.use(http.post('/api/v1/auth/me/password', () =>
      HttpResponse.json({ detail: 'New passwords do not match.' }, { status: 400 })));
    await expect(updatePassword({
      current_password: 'Old1!',
      new_password: 'New1!',
      confirm_new_password: 'Different1!',
    })).rejects.toMatchObject({ status: 400 });
  });

  it('throws ApiError with status 401 when unauthenticated', async () => {
    server.use(http.post('/api/v1/auth/me/password', () => new HttpResponse(null, { status: 401 })));
    await expect(updatePassword({
      current_password: 'Old1!',
      new_password: 'New1!',
      confirm_new_password: 'New1!',
    })).rejects.toMatchObject({ status: 401 });
  });
});
