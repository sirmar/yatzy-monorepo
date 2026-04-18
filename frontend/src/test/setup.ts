import '@testing-library/jest-dom';
import { afterEach, vi } from 'vitest';

function makeStorage(): Storage {
  let store: Record<string, string> = {};
  return {
    getItem: (key) => store[key] ?? null,
    setItem: (key, value) => {
      store[key] = String(value);
    },
    removeItem: (key) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
    get length() {
      return Object.keys(store).length;
    },
    key: (i) => Object.keys(store)[i] ?? null,
  };
}

vi.stubGlobal('localStorage', makeStorage());
vi.stubGlobal('sessionStorage', makeStorage());

afterEach(() => {
  localStorage.clear();
  sessionStorage.clear();
});
