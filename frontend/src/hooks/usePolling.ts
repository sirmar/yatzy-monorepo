import { useEffect, useRef } from 'react';

interface UsePollingOptions {
  interval?: number;
  enabled?: boolean;
}

export function usePolling(
  callback: () => void,
  { interval = 2000, enabled = true }: UsePollingOptions = {}
) {
  const callbackRef = useRef(callback);

  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!enabled) return;
    const id = setInterval(() => callbackRef.current(), interval);
    return () => clearInterval(id);
  }, [enabled, interval]);
}
