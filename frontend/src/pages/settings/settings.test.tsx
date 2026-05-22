// pages/settings/settings.test.tsx

import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useAuth } from '@context/auth-context';
import { SettingsPage } from '@pages/settings';
import { updateProfile } from '@services/auth';
import { makeUser } from '@tests/factories';

vi.mock('@context/auth-context', () => ({ useAuth: vi.fn() }));
vi.mock('@layout/app-header', () => ({ AppHeader: () => <header /> }));
// Stub out ChangePasswordForm so password-section tests stay in their own file.
vi.mock('@pages/settings/change-password-form', () => ({
  ChangePasswordForm: () => <div data-testid="change-password-form" />,
}));
vi.mock('@services/auth', async () => {
  const actual = await vi.importActual('@services/auth');
  return { ...actual, updateProfile: vi.fn() };
});

const mockNavigate = vi.fn();
vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router');
  return { ...actual, useNavigate: () => mockNavigate };
});

const mockUseAuth = vi.mocked(useAuth);
const mockUpdateProfile = vi.mocked(updateProfile);

const mockUser = makeUser({
  first_name: 'Test',
  last_name: 'User',
  username: 'testuser',
  email: 'test@example.com',
});

function setup() {
  const setUser = vi.fn();
  mockUseAuth.mockReturnValue({ user: mockUser, isLoading: false, sessionError: false, setUser });
  render(<MemoryRouter><SettingsPage /></MemoryRouter>);
  return { setUser };
}

beforeEach(() => {
  vi.clearAllMocks();
  mockNavigate.mockReset();
});

// ── Rendering ─────────────────────────────────────────────────────────────────

describe('SettingsPage rendering', () => {
  it('renders the page heading', () => {
    setup();
    expect(screen.getByRole('heading', { name: /^settings$/i })).toBeDefined();
  });

  it('renders the Profile section', () => {
    setup();
    expect(screen.getByRole('heading', { name: /^profile$/i })).toBeDefined();
  });

  it('renders the ChangePasswordForm', () => {
    setup();
    expect(screen.getByTestId('change-password-form')).toBeDefined();
  });

  it('renders the Subscription section', () => {
    setup();
    expect(screen.getByRole('heading', { name: /^subscription$/i })).toBeDefined();
  });

  it('renders the back to dashboard button', () => {
    setup();
    expect(screen.getByRole('button', { name: /dashboard/i })).toBeDefined();
  });
});

// ── Profile form pre-population ───────────────────────────────────────────────

describe('SettingsPage profile form pre-population', () => {
  it('pre-populates first name', () => {
    setup();
    expect((screen.getByLabelText(/first name/i) as HTMLInputElement).value).toBe('Test');
  });

  it('pre-populates last name', () => {
    setup();
    expect((screen.getByLabelText(/last name/i) as HTMLInputElement).value).toBe('User');
  });

  it('pre-populates username', () => {
    setup();
    expect((screen.getByLabelText(/username/i) as HTMLInputElement).value).toBe('testuser');
  });

  it('pre-populates email', () => {
    setup();
    expect((screen.getByLabelText(/email address/i) as HTMLInputElement).value).toBe('test@example.com');
  });
});

// ── Profile save — success ────────────────────────────────────────────────────

describe('SettingsPage profile save — success', () => {
  it('calls updateProfile with current field values', async () => {
    mockUpdateProfile.mockResolvedValueOnce({ ...mockUser, first_name: 'Jane' });
    setup();
    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Jane' } });
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: /^save$/i })); });
    expect(mockUpdateProfile).toHaveBeenCalledWith(expect.objectContaining({ first_name: 'Jane' }));
  });

  it('updates the auth context with the returned user', async () => {
    const updated = { ...mockUser, email: 'new@example.com' };
    mockUpdateProfile.mockResolvedValueOnce(updated);
    const { setUser } = setup();
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: /^save$/i })); });
    expect(setUser).toHaveBeenCalledWith(updated);
  });

  it('syncs form fields from the API response', async () => {
    const updated = { ...mockUser, email: 'normalized@example.com' };
    mockUpdateProfile.mockResolvedValueOnce(updated);
    setup();
    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'NORMALIZED@EXAMPLE.COM' } });
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: /^save$/i })); });
    await waitFor(() => {
      expect((screen.getByLabelText(/email address/i) as HTMLInputElement).value).toBe('normalized@example.com');
    });
  });

  it('shows a success message after saving', async () => {
    mockUpdateProfile.mockResolvedValueOnce(mockUser);
    setup();
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: /^save$/i })); });
    await waitFor(() => expect(screen.getByText(/profile updated successfully/i)).toBeDefined());
  });

  it('does not navigate away after saving', async () => {
    mockUpdateProfile.mockResolvedValueOnce(mockUser);
    setup();
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: /^save$/i })); });
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});

// ── Profile save — error ──────────────────────────────────────────────────────

describe('SettingsPage profile save — error', () => {
  it('shows an error message on rejection', async () => {
    mockUpdateProfile.mockRejectedValueOnce(new Error('Email already exists.'));
    setup();
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: /^save$/i })); });
    await waitFor(() => expect(screen.getByText(/email already exists/i)).toBeDefined());
  });

  it('does not update the auth context on error', async () => {
    mockUpdateProfile.mockRejectedValueOnce(new Error('Something went wrong.'));
    const { setUser } = setup();
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: /^save$/i })); });
    expect(setUser).not.toHaveBeenCalled();
  });
});

// ── Navigation ────────────────────────────────────────────────────────────────

describe('SettingsPage navigation', () => {
  it('navigates to / when the back button is clicked', () => {
    setup();
    fireEvent.click(screen.getByRole('button', { name: /dashboard/i }));
    expect(mockNavigate).toHaveBeenCalledWith('/');
  });
});
