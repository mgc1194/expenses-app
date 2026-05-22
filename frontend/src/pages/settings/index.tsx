// pages/settings/index.tsx — User settings page.

import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { Alert, Box, Button, Container, Divider, Paper, TextField, Typography } from '@mui/material';
import { useState } from 'react';
import { useNavigate } from 'react-router';

import { useAuth } from '@context/auth-context';
import { AppHeader } from '@layout/app-header';
import { updateProfile } from '@services/auth';

export function SettingsPage() {
  const navigate = useNavigate();
  const { user, setUser } = useAuth();

  const [firstName, setFirstName] = useState(user?.first_name ?? '');
  const [lastName, setLastName] = useState(user?.last_name ?? '');
  const [username, setUsername] = useState(user?.username ?? '');
  const [email, setEmail] = useState(user?.email ?? '');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSaveProfile() {
    setSuccessMessage(null);
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      const updated = await updateProfile({
        first_name: firstName,
        last_name: lastName,
        username,
        email,
      });
      setUser(updated);
      setFirstName(updated.first_name);
      setLastName(updated.last_name);
      setUsername(updated.username);
      setEmail(updated.email);
      setSuccessMessage('Profile updated successfully.');
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : 'Something went wrong.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppHeader />

      <Container maxWidth="sm" sx={{ py: 6 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/')}
          size="small"
          sx={{ mb: 3, color: 'text.secondary' }}
        >
          Dashboard
        </Button>

        <Typography variant="h3" sx={{ mb: 0.5 }}>
          Settings
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 5 }}>
          Manage your profile and subscription.
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>

          {/* Profile */}
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 0.5 }}>
              Profile
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                <TextField
                  id="firstName"
                  label="First name"
                  autoComplete="given-name"
                  fullWidth
                  value={firstName}
                  onChange={e => setFirstName(e.target.value)}
                />
                <TextField
                  id="lastName"
                  label="Last name"
                  autoComplete="family-name"
                  fullWidth
                  value={lastName}
                  onChange={e => setLastName(e.target.value)}
                />
              </Box>

              <TextField
                id="username"
                label="Username"
                autoComplete="username"
                fullWidth
                value={username}
                onChange={e => setUsername(e.target.value)}
              />

              <TextField
                id="email"
                label="Email address"
                type="email"
                autoComplete="email"
                fullWidth
                value={email}
                onChange={e => setEmail(e.target.value)}
              />

              {successMessage && (
                <Alert severity="success">{successMessage}</Alert>
              )}
              {errorMessage && (
                <Alert severity="error">{errorMessage}</Alert>
              )}

              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  onClick={handleSaveProfile}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Saving…' : 'Save'}
                </Button>
              </Box>
            </Box>
          </Paper>

          {/* Password — populated in Issue 3 */}
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 0.5 }}>
              Password
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {/* TODO: change password form (Issue 3) */}
          </Paper>

          {/* Subscription — populated in Issue 4 */}
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 0.5 }}>
              Subscription
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {/* TODO: subscription plan display (Issue 4) */}
          </Paper>

        </Box>
      </Container>
    </Box>
  );
}
