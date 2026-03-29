import { useEffect, useRef } from 'react';
import { useAuth } from './AuthContext';

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function useEventSource(url: string | null, onEvent: () => void) {
  const { accessToken } = useAuth();
  const onEventRef = useRef(onEvent);

  useEffect(() => {
    onEventRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    if (!url || !accessToken) return;
    const resolvedUrl = url;
    let cancelled = false;
    const controller = new AbortController();

    async function connect() {
      while (!cancelled) {
        try {
          const response = await fetch(resolvedUrl, {
            headers: { Authorization: `Bearer ${accessToken}` },
            signal: controller.signal,
          });
          if (!response.body || !response.ok) {
            await delay(3000);
            continue;
          }
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let buffer = '';
          while (!cancelled) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() ?? '';
            for (const line of lines) {
              if (line.startsWith('data:')) onEventRef.current();
            }
          }
          reader.cancel();
        } catch {
          if (!controller.signal.aborted && !cancelled) await delay(3000);
        }
      }
    }

    connect();
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [url, accessToken]);
}
