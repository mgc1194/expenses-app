// pages/settings/change-password-form.tsx — Password change form for the Settings page.

import { Alert, Box, Button, Divider, Paper, TextField, Typography } from '@mui/material';
import { useState } from 'react';

import { updatePassword } from '@services/auth';

export function ChangePasswordForm() {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleChangePassword() {
    setSuccessMessage(null);
    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      await updatePassword({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_new_password: confirmNewPassword,
      });
      setCurrentPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
      setSuccessMessage('Password updated successfully.');
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : 'Something went wrong.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Paper variant="outlined" sx={{ p: 3 }}>
      <Typography variant="h6" sx={{ mb: 0.5 }}>Password</Typography>
      <Divider sx={{ mb: 3 }} />
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField
          id="currentPassword"
          label="Current password"
          type="password"
          autoComplete="current-password"
          fullWidth
          value={currentPassword}
          onChange={e => setCurrentPassword(e.target.value)}
        />
        <TextField
          id="newPassword"
          label="New password"
          type="password"
          autoComplete="new-password"
          fullWidth
          value={newPassword}
          onChange={e => setNewPassword(e.target.value)}
        />
        <TextField
          id="confirmNewPassword"
          label="Confirm new password"
          type="password"
          autoComplete="new-password"
          fullWidth
          value={confirmNewPassword}
          onChange={e => setConfirmNewPassword(e.target.value)}
        />
        {successMessage && <Alert severity="success">{successMessage}</Alert>}
        {errorMessage && <Alert severity="error">{errorMessage}</Alert>}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button variant="contained" onClick={handleChangePassword} disabled={isSubmitting}>
            {isSubmitting ? 'Updating…' : 'Update password'}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
}
