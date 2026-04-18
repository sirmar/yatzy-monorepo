import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import type { components } from '@/api';
import { PlayerRow } from './PlayerRow';

type Player = components['schemas']['Player'];

const player = { id: 1, account_id: 'a1', name: 'Alice', is_bot: false, created_at: '' };

describe('PlayerRow', () => {
  it('shows the player name as a select button', () => {
    givenRow();
    expect(screen.getByRole('button', { name: 'Alice' })).toBeInTheDocument();
  });

  it('calls onSelect when the name button is clicked', async () => {
    const onSelect = vi.fn();
    givenRow({ onSelect });
    await userEvent.click(screen.getByRole('button', { name: 'Alice' }));
    expect(onSelect).toHaveBeenCalledWith(player);
  });

  it('shows edit input when edit button is clicked', async () => {
    givenRow();
    await userEvent.click(screen.getByRole('button', { name: /edit alice/i }));
    expect(screen.getByRole('textbox', { name: /edit name/i })).toBeInTheDocument();
  });

  it('calls onUpdate with trimmed name when saved', async () => {
    const onUpdate = vi.fn().mockResolvedValue(undefined);
    givenRow({ onUpdate });
    await userEvent.click(screen.getByRole('button', { name: /edit alice/i }));
    const input = screen.getByRole('textbox', { name: /edit name/i });
    await userEvent.clear(input);
    await userEvent.type(input, 'Alicia ');
    await userEvent.click(screen.getByRole('button', { name: /^save$/i }));
    expect(onUpdate).toHaveBeenCalledWith(player, 'Alicia');
  });

  it('saves on Enter key', async () => {
    const onUpdate = vi.fn().mockResolvedValue(undefined);
    givenRow({ onUpdate });
    await userEvent.click(screen.getByRole('button', { name: /edit alice/i }));
    const input = screen.getByRole('textbox', { name: /edit name/i });
    await userEvent.clear(input);
    await userEvent.type(input, 'Ali{Enter}');
    expect(onUpdate).toHaveBeenCalledWith(player, 'Ali');
  });

  it('cancels editing on Escape and restores original name', async () => {
    givenRow();
    await userEvent.click(screen.getByRole('button', { name: /edit alice/i }));
    const input = screen.getByRole('textbox', { name: /edit name/i });
    await userEvent.clear(input);
    await userEvent.type(input, 'Changed{Escape}');
    expect(screen.getByRole('button', { name: 'Alice' })).toBeInTheDocument();
  });

  it('cancels editing on Cancel button click', async () => {
    givenRow();
    await userEvent.click(screen.getByRole('button', { name: /edit alice/i }));
    await userEvent.click(screen.getByRole('button', { name: /^cancel$/i }));
    expect(screen.getByRole('button', { name: 'Alice' })).toBeInTheDocument();
  });

  it('does not call onUpdate when name is unchanged', async () => {
    const onUpdate = vi.fn();
    givenRow({ onUpdate });
    await userEvent.click(screen.getByRole('button', { name: /edit alice/i }));
    await userEvent.click(screen.getByRole('button', { name: /^save$/i }));
    expect(onUpdate).not.toHaveBeenCalled();
  });

  it('keeps editor open when onUpdate throws', async () => {
    const onUpdate = vi.fn().mockRejectedValue(new Error('fail'));
    givenRow({ onUpdate });
    await userEvent.click(screen.getByRole('button', { name: /edit alice/i }));
    const input = screen.getByRole('textbox', { name: /edit name/i });
    await userEvent.clear(input);
    await userEvent.type(input, 'NewName');
    await userEvent.click(screen.getByRole('button', { name: /^save$/i }));
    expect(screen.getByRole('textbox', { name: /edit name/i })).toBeInTheDocument();
  });

  it('calls onDelete when delete button is clicked', async () => {
    const onDelete = vi.fn().mockResolvedValue(undefined);
    givenRow({ onDelete });
    await userEvent.click(screen.getByRole('button', { name: /delete alice/i }));
    expect(onDelete).toHaveBeenCalledWith(player);
  });

  function givenRow(
    overrides: {
      onSelect?: (player: Player) => void;
      onUpdate?: (player: Player, newName: string) => Promise<void>;
      onDelete?: (player: Player) => Promise<void>;
    } = {}
  ) {
    render(
      <PlayerRow
        player={player}
        onSelect={overrides.onSelect ?? vi.fn()}
        onUpdate={overrides.onUpdate ?? vi.fn().mockResolvedValue(undefined)}
        onDelete={overrides.onDelete ?? vi.fn().mockResolvedValue(undefined)}
      />
    );
  }
});
