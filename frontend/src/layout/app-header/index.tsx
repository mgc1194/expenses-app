// layout/app-header/index.tsx — Top navigation bar for authenticated pages.

import { AppBar, Avatar, Box, Divider, IconButton, Menu, MenuItem, Toolbar } from '@mui/material';
import { useState } from 'react';
import { useNavigate } from 'react-router';

import { useAuth } from '@context/auth-context';
import { logout } from '@services/auth';

/** Derives up-to-two-character initials from a user's name or email. */
function getInitials(user: { first_name?: string; last_name?: string; email: string }): string {
  if (user.first_name && user.last_name) {
    return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
  }
  if (user.first_name) {
    return user.first_name[0].toUpperCase();
  }
  return user.email[0].toUpperCase();
}

export function AppHeader() {
  const { user, setUser } = useAuth();
  const navigate = useNavigate();

  const [menuAnchor, setMenuAnchor] = useState<HTMLElement | null>(null);

  function handleAvatarClick(e: React.MouseEvent<HTMLElement>) {
    setMenuAnchor(e.currentTarget);
  }

  function handleClose() {
    setMenuAnchor(null);
  }

  async function handleLogout() {
    handleClose();
    try {
      await logout();
    } finally {
      setUser(null);
      navigate('/login');
    }
  }

  function handleSettings() {
    handleClose();
    navigate('/settings');
  }

  return (
    <AppBar
      position="static"
      color="inherit"
      elevation={0}
      sx={{ borderBottom: 1, borderColor: 'divider' }}
    >
      <Toolbar>
        <Box
          component="img"
          src="/images/serve-logo-light.svg"
          alt="SERVE"
          sx={{ height: 100, mr: 'auto' }}
        />
        {user && (
          <>
            <IconButton
              onClick={handleAvatarClick}
              size="small"
              aria-label="Open user menu"
              aria-controls={menuAnchor ? 'user-menu' : undefined}
              aria-haspopup="true"
              aria-expanded={menuAnchor ? 'true' : undefined}
            >
              <Avatar sx={{ width: 50, height: 50, fontSize: 20, bgcolor: 'primary.main' }}>
                {getInitials(user)}
              </Avatar>
            </IconButton>
            <Menu
              id="user-menu"
              anchorEl={menuAnchor}
              open={Boolean(menuAnchor)}
              onClose={handleClose}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
              transformOrigin={{ vertical: 'top', horizontal: 'right' }}
              slotProps={{ paper: { elevation: 2, sx: { mt: 0.5, minWidth: 160 } } }}
            >
              <MenuItem onClick={handleSettings}>Settings</MenuItem>
              <Divider />
              <MenuItem onClick={handleLogout}>Sign out</MenuItem>
            </Menu>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
}
