import { useState } from 'react';

export function useFormSubmit() {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  async function submit(
    action: () => Promise<void>,
    onError?: (err: Error) => void
  ): Promise<void> {
    setError('');
    setSubmitting(true);
    try {
      await action();
    } catch (err) {
      const e = err instanceof Error ? err : new Error('Something went wrong');
      if (onError) {
        onError(e);
      } else {
        setError(e.message);
      }
    } finally {
      setSubmitting(false);
    }
  }

  return { submitting, error, setError, submit };
}
