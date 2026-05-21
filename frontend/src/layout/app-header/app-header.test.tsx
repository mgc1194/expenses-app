// layout/app-header/app-header.test.tsx

import { act, fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useAuth } from '@context/auth-context';
import { AppHeader } from '@layout/app-header';
import { logout } from '@services/auth';

vi.mock('@context/auth-context', () => ({ useAuth: vi.fn() }));
vi.mock('@services/auth', () => ({ logout: vi.fn() }));

const mockNavigate = vi.fn();
vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router');
  return { ...actual, useNavigate: () => mockNavigate };
});

const mockUseAuth = vi.mocked(useAuth);
const mockLogout = vi.mocked(logout);

const mockUser = {
  id: 1,
  email: 'test@example.com',
  username: 'testuser',
  first_name: 'Test',
  last_name: 'User',
  households: [],
};

function setup(userOverrides = {}) {
  const setUser = vi.fn();
  mockUseAuth.mockReturnValue({
    user: { ...mockUser, ...userOverrides },
    isLoading: false,
    sessionError: false,
    setUser,
  });
  render(<MemoryRouter><AppHeader /></MemoryRouter>);
  return { setUser };
}

beforeEach(() => {
  vi.clearAllMocks();
  mockNavigate.mockReset();
});

// ── Rendering ─────────────────────────────────────────────────────────────────

describe('AppHeader rendering', () => {
  it('renders the logo', () => {
    setup();
    expect(screen.getByAltText('SERVE')).toBeDefined();
  });

  it('renders the avatar button when a user is logged in', () => {
    setup();
    expect(screen.getByRole('button', { name: /open user menu/i })).toBeDefined();
  });

  it('does not render the avatar button when there is no user', () => {
    mockUseAuth.mockReturnValue({ user: null, isLoading: false, sessionError: false, setUser: vi.fn() });
    render(<MemoryRouter><AppHeader /></MemoryRouter>);
    expect(screen.queryByRole('button', { name: /open user menu/i })).toBeNull();
  });
});

// ── Initials ──────────────────────────────────────────────────────────────────

describe('AppHeader initials', () => {
  it('shows first and last initial when both names are present', () => {
    setup({ first_name: 'Test', last_name: 'User' });
    expect(screen.getByText('TU')).toBeDefined();
  });

  it('shows only the first initial when last name is absent', () => {
    setup({ first_name: 'Test', last_name: '' });
    expect(screen.getByText('T')).toBeDefined();
  });

  it('falls back to the first character of the email when no name is present', () => {
    setup({ first_name: '', last_name: '' });
    expect(screen.getByText('T')).toBeDefined(); // 't' from 'test@example.com' uppercased
  });
});

// ── Dropdown ──────────────────────────────────────────────────────────────────

describe('AppHeader dropdown', () => {
  it('opens the menu when the avatar button is clicked', () => {
    setup();
    expect(screen.queryByRole('menuitem', { name: /settings/i })).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: /open user menu/i }));
    expect(screen.getByRole('menuitem', { name: /settings/i })).toBeDefined();
    expect(screen.getByRole('menuitem', { name: /sign out/i })).toBeDefined();
  });

  it('closes the menu when clicking outside (onClose)', () => {
    setup();
    fireEvent.click(screen.getByRole('button', { name: /open user menu/i }));
    expect(screen.getByRole('menuitem', { name: /settings/i })).toBeDefined();
    // Simulate MUI Menu onClose (e.g. backdrop click / Escape)
    fireEvent.keyDown(screen.getByRole('menu'), { key: 'Escape' });
    expect(screen.queryByRole('menuitem', { name: /settings/i })).toBeNull();
  });

  it('navigates to /settings and closes the menu when Settings is clicked', () => {
    setup();
    fireEvent.click(screen.getByRole('button', { name: /open user menu/i }));
    fireEvent.click(screen.getByRole('menuitem', { name: /settings/i }));
    expect(mockNavigate).toHaveBeenCalledWith('/settings');
    expect(screen.queryByRole('menuitem', { name: /settings/i })).toBeNull();
  });
});

// ── Logout ────────────────────────────────────────────────────────────────────

describe('AppHeader logout', () => {
  it('calls logout, clears the user, and navigates to /login on sign out', async () => {
    const { setUser } = setup();
    mockLogout.mockResolvedValueOnce(undefined);

    fireEvent.click(screen.getByRole('button', { name: /open user menu/i }));
    await act(async () => {
      fireEvent.click(screen.getByRole('menuitem', { name: /sign out/i }));
    });

    expect(mockLogout).toHaveBeenCalledOnce();
    expect(setUser).toHaveBeenCalledWith(null);
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

});
