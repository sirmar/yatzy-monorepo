import createClient from 'openapi-fetch';
import type { paths } from './schema';

const baseUrl = import.meta.env.VITE_AUTH_BASE_URL ?? '/auth';

export const authHttpClient = createClient<paths>({ baseUrl, fetch: (req) => fetch(req) });
