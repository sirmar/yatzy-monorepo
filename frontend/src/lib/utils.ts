import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function ignoreAbort(e: unknown) {
  if ((e as { name?: string })?.name !== 'AbortError') throw e;
}

export function validateNewPassword(password: string, confirm: string): string | null {
  return validatePassword(password) ?? validatePasswordsMatch(password, confirm);
}

export function validatePassword(password: string): string | null {
  if (password.length < 8) return 'Password must be at least 8 characters';
  return null;
}

export function validatePasswordsMatch(password: string, confirm: string): string | null {
  if (password !== confirm) return 'Passwords do not match';
  return null;
}
