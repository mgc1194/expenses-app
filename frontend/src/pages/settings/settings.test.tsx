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
  mockUseAuth.mockReturnValue({
    user: mockUser,
    isLoading: false,
    sessionError: false,
    setUser,
  });
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

  it('renders the subheading', () => {
    setup();
    expect(screen.getByText(/manage your profile and subscription/i)).toBeDefined();
  });

  it('renders the Profile section heading', () => {
    setup();
    expect(screen.getByRole('heading', { name: /^profile$/i })).toBeDefined();
  });

  it('renders the Password section heading', () => {
    setup();
    expect(screen.getByRole('heading', { name: /^password$/i })).toBeDefined();
  });

  it('renders the Subscription section heading', () => {
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
  it('pre-populates first name from the auth context', () => {
    setup();
    const input = screen.getByLabelText(/first name/i) as HTMLInputElement;
    expect(input.value).toBe('Test');
  });

  it('pre-populates last name from the auth context', () => {
    setup();
    const input = screen.getByLabelText(/last name/i) as HTMLInputElement;
    expect(input.value).toBe('User');
  });

  it('pre-populates username from the auth context', () => {
    setup();
    const input = screen.getByLabelText(/username/i) as HTMLInputElement;
    expect(input.value).toBe('testuser');
  });

  it('pre-populates email from the auth context', () => {
    setup();
    const input = screen.getByLabelText(/email address/i) as HTMLInputElement;
    expect(input.value).toBe('test@example.com');
  });
});

// ── Profile form save — success ────────────────────────────────────────────────

describe('SettingsPage profile save — success', () => {
  it('calls updateProfile with the current field values', async () => {
    const updatedUser = { ...mockUser, first_name: 'Jane' };
    mockUpdateProfile.mockResolvedValueOnce(updatedUser);
    setup();

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Jane' } });

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /^save$/i }));
    });

    expect(mockUpdateProfile).toHaveBeenCalledWith(
      expect.objectContaining({ first_name: 'Jane' }),
    );
  });

  it('updates the auth context with the returned user on success', async () => {
    const updatedUser = { ...mockUser, email: 'new@example.com' };
    mockUpdateProfile.mockResolvedValueOnce(updatedUser);
    const { setUser } = setup();

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /^save$/i }));
    });

    expect(setUser).toHaveBeenCalledWith(updatedUser);
  });

  it('shows a success message after saving', async () => {
    mockUpdateProfile.mockResolvedValueOnce(mockUser);
    setup();

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /^save$/i }));
    });

    await waitFor(() =>
      expect(screen.getByText(/profile updated successfully/i)).toBeDefined()
    );
  });

  it('does not navigate away after saving', async () => {
    mockUpdateProfile.mockResolvedValueOnce(mockUser);
    setup();

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /^save$/i }));
    });

    expect(mockNavigate).not.toHaveBeenCalled();
  });
});

// ── Profile form save — error ─────────────────────────────────────────────────

describe('SettingsPage profile save — error', () => {
  it('shows an error message when updateProfile rejects', async () => {
    mockUpdateProfile.mockRejectedValueOnce(new Error('Email already exists.'));
    setup();

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /^save$/i }));
    });

    await waitFor(() =>
      expect(screen.getByText(/email already exists/i)).toBeDefined()
    );
  });

  it('does not update the auth context on error', async () => {
    mockUpdateProfile.mockRejectedValueOnce(new Error('Something went wrong.'));
    const { setUser } = setup();

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /^save$/i }));
    });

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
