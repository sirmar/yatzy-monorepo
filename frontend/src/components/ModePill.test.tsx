import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ModePill } from './ModePill';

describe('ModePill', () => {
  it('renders "Maxi Yatzy" for maxi mode', () => {
    givenMode('maxi');
    thenTextIsVisible('Maxi Yatzy');
  });

  it('renders "Yatzy" for yatzy mode', () => {
    givenMode('yatzy');
    thenTextIsVisible('Yatzy');
  });

  it('renders "Maxi Sequential" for maxi_sequential mode', () => {
    givenMode('maxi_sequential');
    thenTextIsVisible('Maxi Sequential');
  });

  it('renders "Yatzy Sequential" for yatzy_sequential mode', () => {
    givenMode('yatzy_sequential');
    thenTextIsVisible('Yatzy Sequential');
  });

  it('falls back to the raw mode string for unknown modes', () => {
    givenMode('unknown_mode');
    thenTextIsVisible('unknown_mode');
  });

  function givenMode(mode: string) {
    render(<ModePill mode={mode} />);
  }

  function thenTextIsVisible(text: string) {
    expect(screen.getByText(text)).toBeInTheDocument();
  }
});
