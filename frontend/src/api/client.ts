import createClient from 'openapi-fetch';
import type { paths } from './schema';

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? '/api';

async function fetchWithErrorNormalization(input: Request): Promise<Response> {
  const response = await fetch(input);
  if (!response.ok) {
    const text = await response.text();
    let body: unknown;
    try {
      body = JSON.parse(text);
    } catch {
      body = { detail: `${response.status} ${response.statusText}` };
    }
    return new Response(JSON.stringify(body), {
      status: response.status,
      headers: { 'content-type': 'application/json' },
    });
  }
  return response;
}

export const apiClient = createClient<paths>({
  baseUrl,
  fetch: fetchWithErrorNormalization,
});
