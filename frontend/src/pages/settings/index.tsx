// pages/settings/index.tsx — User settings page shell.
//
// Hosts profile, password, and subscription management sections.
// Section content is populated in follow-up issues; this file
// establishes the layout, route entry point, and empty placeholders.

import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { Box, Button, Container, Divider, Paper, Typography } from '@mui/material';
import { useNavigate } from 'react-router';

import { AppHeader } from '@layout/app-header';

export function SettingsPage() {
  const navigate = useNavigate();

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
          {/* Profile — populated in Issue 2 */}
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 0.5 }}>
              Profile
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {/* TODO: name, username, and email editing (Issue 2) */}
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
