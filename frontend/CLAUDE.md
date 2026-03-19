**Goal**
A web frontend for the Yatzy REST API. Allows players to create and join games, roll dice, fill in scorecards and see results.

**Tools**
- Language: TypeScript
- Framework: React
- Build tool: Vite
- Component library: shadcn/ui (built on Radix UI + Tailwind CSS)
- Routing: React Router
- API client: generated from the backend's OpenAPI schema (backend runs at http://localhost:8000, Swagger at /docs)
- Package manager: pnpm
- Linting and formatting: Biome
- Build: multi-stage Dockerfile (Node to build, Nginx to serve static files)

**Docker**
- Multi-stage Dockerfile: Node stage builds the Vite app, Nginx stage serves the static output
- All local development commands run via Docker
- Nginx proxies /api requests to the backend (http://backend:8000) to avoid CORS
- Use docker compose for local development with frontend and backend running together

**Folder structure**
- `src/api/` — generated API client and schema
- `src/components/` — shared UI components
- `src/screens/` — one directory per game screen (lobby, game, end screen), each containing its page component and co-located sub-components, hooks and types
- `src/hooks/` — shared hooks (e.g. polling, player context)
- `src/lib/` — pure utility functions (scoring helpers, formatting)

**Design rules**
- One component per file
- Keep components small and focused — extract sub-components when a component grows beyond ~100 lines
- Co-locate component-specific types, hooks and helpers in the same directory as the component
- No global state management library — use React context for shared state (current player, active game)
- All API calls go through a typed generated client — never write raw fetch calls
- Game state polling: implement as a custom hook using `setInterval`, configurable interval (default 2s), stop polling when the game ends or the component unmounts

**Testing**
- Unit test pure logic (score calculation helpers, formatting) with Vitest
- Component tests with React Testing Library + jsdom: render components, interact with them and assert what is visible. Mock API calls. This is the primary way to verify component behaviour.
- Smoke tests with Playwright for the real browser: a minimal suite that verifies the app loads and the happy path works in the target environment. Not a substitute for component tests.
- Write tests first
- Component tests follow BDD style using `describe`/`it`/`beforeEach` with `givenX`, `whenX`, `thenX` helper functions scoped inside the `describe` block. Example:
  ```typescript
  describe('ScoreCard', () => {
    it('shows filled categories as disabled', () => {
      givenScoreCard({ ones: 3 })
      thenCategoryIsDisabled('ones')
    })

    function givenScoreCard(scores, props = {}) {
      render(<ScoreCard scores={scores} {...props} />)
    }

    function thenCategoryIsDisabled(name: string) {
      expect(screen.getByRole('button', { name })).toBeDisabled()
    }
  })
  ```

**Documentation**
- Avoid comments in code
- README.md with repository purpose and developer focused information

**Code style**
- Enforced by Biome

**API**
- Backend repo: ../backend
- Base URL: http://localhost:8000
- Regenerate the API client from the OpenAPI schema whenever the backend changes: pnpm dlx openapi-typescript http://localhost:8000/openapi.json -o src/api/schema.ts

**Game screens**
- Player creation / selection
- Lobby: list open games, create game, join game
- Game: dice rolling, scorecard, scoring options, game state polling
- End screen: final scores and winner
