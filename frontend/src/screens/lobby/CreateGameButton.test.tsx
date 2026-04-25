import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { CreateGameButton } from './CreateGameButton';

describe('CreateGameButton', () => {
  it('renders a "New Game" button', () => {
    givenButton({ loading: false });
    expect(screen.getByRole('button', { name: /new game/i })).toBeInTheDocument();
  });

  it('is disabled while loading', () => {
    givenButton({ loading: true });
    expect(screen.getByRole('button', { name: /new game/i })).toBeDisabled();
  });

  it('is enabled when not loading', () => {
    givenButton({ loading: false });
    expect(screen.getByRole('button', { name: /new game/i })).toBeEnabled();
  });

  it('calls onCreate when clicked', async () => {
    const onCreate = vi.fn().mockResolvedValue(undefined);
    givenButton({ loading: false, onCreate });
    await userEvent.click(screen.getByRole('button', { name: /new game/i }));
    expect(onCreate).toHaveBeenCalledOnce();
  });

  it('does not call onCreate when disabled', async () => {
    const onCreate = vi.fn().mockResolvedValue(undefined);
    givenButton({ loading: true, onCreate });
    await userEvent.click(screen.getByRole('button', { name: /new game/i }));
    expect(onCreate).not.toHaveBeenCalled();
  });

  function givenButton({
    loading,
    onCreate = vi.fn().mockResolvedValue(undefined),
  }: {
    loading: boolean;
    onCreate?: () => Promise<void>;
  }) {
    render(<CreateGameButton loading={loading} onCreate={onCreate} />);
  }
});
