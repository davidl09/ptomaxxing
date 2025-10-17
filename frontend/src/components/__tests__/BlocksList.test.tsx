import { render, screen } from '@testing-library/react';
import React from 'react';

import type { Plan } from '../../api/types';
import BlocksList from '../BlocksList';

const plan: Plan = {
  score: 10,
  pto_used: 5,
  blocks: [
    {
      start: '2024-05-01',
      end: '2024-05-05',
      days_off: 5,
      pto: ['2024-05-02', '2024-05-03'],
      holidays: ['2024-05-01'],
      weekends: ['2024-05-04', '2024-05-05'],
      explain: 'Example block',
    },
  ],
};

describe('BlocksList', () => {
  it('renders block details', () => {
    render(
      <BlocksList
        plan={plan}
        onExport={() => undefined}
        onCopy={() => undefined}
        locale="en-CA"
      />,
    );
    expect(screen.getByText(/Example block/)).toBeInTheDocument();
    expect(screen.getByText(/5 days off/)).toBeInTheDocument();
  });
});
