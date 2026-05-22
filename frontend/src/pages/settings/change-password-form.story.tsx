// pages/settings/change-password-form.story.tsx

import { Box } from '@mui/material';
import type { Meta, StoryObj } from '@storybook/react';

import { ChangePasswordForm } from '@pages/settings/change-password-form';

const meta: Meta<typeof ChangePasswordForm> = {
  title: 'Pages/Settings/ChangePasswordForm',
  component: ChangePasswordForm,
  parameters: { layout: 'centered' },
  decorators: [
    Story => (
      <Box sx={{ width: 480, p: 3 }}>
        <Story />
      </Box>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof ChangePasswordForm>;

// Default idle state — all fields empty, no feedback shown.
export const Default: Story = {};
