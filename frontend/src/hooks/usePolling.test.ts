import { renderHook } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { usePolling } from './usePolling';

describe('usePolling', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('calls the callback on each interval tick', () => {
    const callback = vi.fn();
    renderHook(() => usePolling(callback));
    vi.advanceTimersByTime(4000);
    expect(callback).toHaveBeenCalledTimes(2);
  });

  it('uses a custom interval', () => {
    const callback = vi.fn();
    renderHook(() => usePolling(callback, { interval: 1000 }));
    vi.advanceTimersByTime(3000);
    expect(callback).toHaveBeenCalledTimes(3);
  });

  it('does not call callback when disabled', () => {
    const callback = vi.fn();
    renderHook(() => usePolling(callback, { enabled: false }));
    vi.advanceTimersByTime(6000);
    expect(callback).not.toHaveBeenCalled();
  });

  it('stops calling after unmount', () => {
    const callback = vi.fn();
    const { unmount } = renderHook(() => usePolling(callback, { interval: 1000 }));
    vi.advanceTimersByTime(1000);
    unmount();
    vi.advanceTimersByTime(3000);
    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('always calls the latest callback reference', () => {
    const first = vi.fn();
    const second = vi.fn();
    const { rerender } = renderHook(({ cb }) => usePolling(cb, { interval: 1000 }), {
      initialProps: { cb: first },
    });
    vi.advanceTimersByTime(1000);
    rerender({ cb: second });
    vi.advanceTimersByTime(1000);
    expect(first).toHaveBeenCalledTimes(1);
    expect(second).toHaveBeenCalledTimes(1);
  });
});
