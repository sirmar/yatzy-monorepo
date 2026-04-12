**Docker**
- Nginx proxies `/api/` → backend:8000 and `/auth/` → auth:8001 (avoids CORS).

**Design rules**
- One component per file; extract sub-components when a component grows beyond ~100 lines
- No global state management — use React context for shared state
- All API calls go through the generated typed client — never raw fetch

**Testing**
- Unit test pure logic with Vitest; component tests with React Testing Library + jsdom

