// pages/transactions/transactions-table/transaction-actions-cell.story.tsx

import { Table, TableBody } from '@mui/material';
import type { Decorator, Meta, StoryObj } from '@storybook/react';

import { TransactionActionsCell } from '@pages/transactions/transactions-table/transaction-actions-cell';
import { makeTransaction } from '@serve/mocks';

const tableDecorator: Decorator = Story => (
  <Table size="small">
    <TableBody>
      <tr>
        <Story />
      </tr>
    </TableBody>
  </Table>
);

const meta: Meta<typeof TransactionActionsCell> = {
  title: 'Transactions/TransactionsTable/TransactionActionsCell',
  component: TransactionActionsCell,
  decorators: [tableDecorator],
  parameters: { layout: 'padded' },
  args: {
    transaction: makeTransaction(),
    onStartEditing: () => {},
    onUpdated: () => {},
    onDeleted: () => {},
    onError: () => {},
  },
};

export default meta;
type Story = StoryObj<typeof TransactionActionsCell>;

// Default — transaction included in summary
export const Included: Story = {};

// Transaction excluded from summary — eye-slash icon shown
export const Excluded: Story = {
  args: {
    transaction: makeTransaction({ exclude_from_summary: true }),
  },
};
