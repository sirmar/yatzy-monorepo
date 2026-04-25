import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { PlayerList } from './PlayerList';

const player1 = {
  id: 1,
  account_id: 'a1',
  name: 'Alice',
  is_bot: false,
  has_picture: false,
  created_at: '',
};
const player2 = {
  id: 2,
  account_id: 'a2',
  name: 'Bob',
  is_bot: false,
  has_picture: false,
  created_at: '',
};

describe('PlayerList', () => {
  it('shows empty message when no players', () => {
    givenPlayerList([]);
    expect(screen.getByText(/no players yet/i)).toBeInTheDocument();
  });

  it('renders a row for each player', () => {
    givenPlayerList([player1, player2]);
    expect(screen.getByRole('button', { name: 'Alice' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Bob' })).toBeInTheDocument();
  });

  function givenPlayerList(players: (typeof player1)[]) {
    render(
      <PlayerList players={players} onSelect={vi.fn()} onUpdate={vi.fn()} onDelete={vi.fn()} />
    );
  }
});
