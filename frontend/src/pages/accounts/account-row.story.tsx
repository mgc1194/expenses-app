// pages/accounts/account-row.story.tsx

import { Table, TableBody } from '@mui/material';
import type { Decorator, Meta, StoryObj } from '@storybook/react';

import { AccountRow } from '@pages/accounts/account-row';
import { makeAccount } from '@serve/mocks';

// Wrap every story in a Table so TableRow / TableCell render correctly.
const tableDecorator: Decorator = Story => (
  <Table size="small">
    <TableBody>
      <Story />
    </TableBody>
  </Table>
);

const meta: Meta<typeof AccountRow> = {
  title: 'Accounts/AccountRow',
  component: AccountRow,
  decorators: [tableDecorator],
  parameters: { layout: 'padded' },
  args: {
    account: makeAccount(),
    onUpdated: () => {},
    onDeleted: () => {},
  },
};

export default meta;
type Story = StoryObj<typeof AccountRow>;

// Default idle state: name, bank, type, household chip, edit + delete icons.
export const Default: Story = {};

// A different account to show a second household chip colour in context.
export const SecondHousehold: Story = {
  args: {
    account: makeAccount({
      id: 2,
      name: "Seth's SoFi Checking",
      handler_key: 'sofi-checking',
      account_type: 'SoFi Checking',
      bank_name: 'SoFi',
      household_id: 2,
      household_name: 'Johnson Household',
    }),
  },
};

// Long account name — verifies text doesn't overflow the cell.
export const LongName: Story = {
  args: {
    account: makeAccount({
      name: "Mario & Luigi's Joint 360 Performance Savings Account",
    }),
  },
};
