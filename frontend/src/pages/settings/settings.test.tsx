// pages/settings/settings.test.tsx

import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { describe, expect, it, vi } from 'vitest';

import { SettingsPage } from '@pages/settings';

vi.mock('@context/auth-context', () => ({
  useAuth: () => ({
    user: { id: 1, email: 'test@example.com', first_name: 'Test', last_name: 'User', username: 'test', households: [] },
    setUser: vi.fn(),
  }),
}));
vi.mock('@layout/app-header', () => ({ AppHeader: () => <header /> }));

const mockNavigate = vi.fn();
vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router');
  return { ...actual, useNavigate: () => mockNavigate };
});

function renderPage() {
  return render(<MemoryRouter><SettingsPage /></MemoryRouter>);
}

// ── Rendering ─────────────────────────────────────────────────────────────────

describe('SettingsPage rendering', () => {
  it('renders the page heading', () => {
    renderPage();
    expect(screen.getByRole('heading', { name: /^settings$/i })).toBeDefined();
  });

  it('renders the subheading', () => {
    renderPage();
    expect(screen.getByText(/manage your profile and subscription/i)).toBeDefined();
  });

  it('renders the Profile section', () => {
    renderPage();
    expect(screen.getByRole('heading', { name: /^profile$/i })).toBeDefined();
  });

  it('renders the Password section', () => {
    renderPage();
    expect(screen.getByRole('heading', { name: /^password$/i })).toBeDefined();
  });

  it('renders the Subscription section', () => {
    renderPage();
    expect(screen.getByRole('heading', { name: /^subscription$/i })).toBeDefined();
  });

  it('renders the back to dashboard button', () => {
    renderPage();
    expect(screen.getByRole('button', { name: /dashboard/i })).toBeDefined();
  });
});

// ── Navigation ────────────────────────────────────────────────────────────────

describe('SettingsPage navigation', () => {
  it('navigates to / when the back button is clicked', () => {
    renderPage();
    fireEvent.click(screen.getByRole('button', { name: /dashboard/i }));
    expect(mockNavigate).toHaveBeenCalledWith('/');
  });
});
