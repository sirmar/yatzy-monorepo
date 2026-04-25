import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ModeBadge } from './ModeBadge';

describe('ModeBadge', () => {
  it('renders "Maxi Yatzy" for maxi mode', () => {
    givenMode('maxi');
    thenTextIsVisible('Maxi Yatzy');
  });

  it('renders "Yatzy" for yatzy mode', () => {
    givenMode('yatzy');
    thenTextIsVisible('Yatzy');
  });

  it('renders "Maxi Yatzy Sequential" for maxi_sequential mode', () => {
    givenMode('maxi_sequential');
    thenTextIsVisible('Maxi Yatzy Sequential');
  });

  it('renders "Yatzy Sequential" for yatzy_sequential mode', () => {
    givenMode('yatzy_sequential');
    thenTextIsVisible('Yatzy Sequential');
  });

  function givenMode(mode: 'maxi' | 'yatzy' | 'maxi_sequential' | 'yatzy_sequential') {
    render(<ModeBadge mode={mode} />);
  }

  function thenTextIsVisible(text: string) {
    expect(screen.getByText(text)).toBeInTheDocument();
  }
});
