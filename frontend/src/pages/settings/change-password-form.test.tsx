// pages/settings/change-password-form.test.tsx

import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ChangePasswordForm } from '@pages/settings/change-password-form';
import { updatePassword } from '@services/auth';

vi.mock('@services/auth', async () => {
  const actual = await vi.importActual('@services/auth');
  return { ...actual, updatePassword: vi.fn() };
});

const mockUpdatePassword = vi.mocked(updatePassword);

function setup() {
  render(<ChangePasswordForm />);
}

beforeEach(() => vi.clearAllMocks());

// ── Rendering ─────────────────────────────────────────────────────────────────

describe('ChangePasswordForm rendering', () => {
  it('renders as a form element', () => {
    setup();
    expect(document.querySelector('form')).toBeDefined();
  });

  it('renders the submit button as type=submit', () => {
    setup();
    expect((screen.getByRole('button', { name: /update password/i }) as HTMLButtonElement).type).toBe('submit');
  });


  it('renders current password field as type=password', () => {
    setup();
    expect((screen.getByLabelText(/current password/i) as HTMLInputElement).type).toBe('password');
  });

  it('renders new password field as type=password', () => {
    setup();
    expect((screen.getByLabelText(/^new password$/i) as HTMLInputElement).type).toBe('password');
  });

  it('renders confirm new password field as type=password', () => {
    setup();
    expect((screen.getByLabelText(/confirm new password/i) as HTMLInputElement).type).toBe('password');
  });

  it('all fields start empty', () => {
    setup();
    expect((screen.getByLabelText(/current password/i) as HTMLInputElement).value).toBe('');
    expect((screen.getByLabelText(/^new password$/i) as HTMLInputElement).value).toBe('');
    expect((screen.getByLabelText(/confirm new password/i) as HTMLInputElement).value).toBe('');
  });
});

// ── Success ───────────────────────────────────────────────────────────────────

describe('ChangePasswordForm — success', () => {
  it('calls updatePassword with the entered values', async () => {
    mockUpdatePassword.mockResolvedValueOnce(undefined);
    setup();
    fireEvent.change(screen.getByLabelText(/current password/i), { target: { value: 'OldPass1!' } });
    fireEvent.change(screen.getByLabelText(/^new password$/i), { target: { value: 'NewPass1!' } });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), { target: { value: 'NewPass1!' } });
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: /update password/i })); });
    expect(mockUpdatePassword).toHaveBeenCalledWith({
      current_password: 'OldPass1!',
      new_password: 'NewPass1!',
      confirm_new_password: 'NewPass1!',
    });
  });

  it('clears all fields on success', async () => {
    mockUpdatePassword.mockResolvedValueOnce(undefined);
    setup();
    fireEvent.change(screen.getByLabelText(/current password/i), { target: { value: 'OldPass1!' } });
    fireEvent.change(screen.getByLabelText(/^new password$/i), { target: { value: 'NewPass1!' } });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), { target: { value: 'NewPass1!' } });
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: /update password/i })); });
    await waitFor(() => {
      expect((screen.getByLabelText(/current password/i) as HTMLInputElement).value).toBe('');
      expect((screen.getByLabelText(/^new password$/i) as HTMLInputElement).value).toBe('');
      expect((screen.getByLabelText(/confirm new password/i) as HTMLInputElement).value).toBe('');
    });
  });

  it('shows a success message on success', async () => {
    mockUpdatePassword.mockResolvedValueOnce(undefined);
    setup();
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: /update password/i })); });
    await waitFor(() => expect(screen.getByText(/password updated successfully/i)).toBeDefined());
  });
});

// ── Error ─────────────────────────────────────────────────────────────────────

describe('ChangePasswordForm — error', () => {
  it('shows the API error message on rejection', async () => {
    mockUpdatePassword.mockRejectedValueOnce(new Error('Current password is incorrect.'));
    setup();
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: /update password/i })); });
    await waitFor(() => expect(screen.getByText(/current password is incorrect/i)).toBeDefined());
  });

  it('does not clear the fields on error', async () => {
    mockUpdatePassword.mockRejectedValueOnce(new Error('Current password is incorrect.'));
    setup();
    fireEvent.change(screen.getByLabelText(/current password/i), { target: { value: 'WrongPass1!' } });
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: /update password/i })); });
    await waitFor(() => {
      expect((screen.getByLabelText(/current password/i) as HTMLInputElement).value).toBe('WrongPass1!');
    });
  });
});
