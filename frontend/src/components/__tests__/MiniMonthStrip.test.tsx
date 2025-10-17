import { render, screen } from '@testing-library/react';
import React from 'react';

import MiniMonthStrip from '../MiniMonthStrip';

describe('MiniMonthStrip', () => {
  it('labels PTO and holidays', () => {
    render(
      <MiniMonthStrip
        start="2024-05-01"
        end="2024-05-05"
        pto={['2024-05-02']}
        holidays={['2024-05-01']}
        weekends={['2024-05-04', '2024-05-05']}
      />,
    );
    expect(screen.getByLabelText('2024-05-02 PTO')).toBeInTheDocument();
    expect(screen.getByLabelText('2024-05-01 Holiday')).toBeInTheDocument();
  });
});
