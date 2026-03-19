# Plan: Build Yatzy Frontend from Scratch

## Status Legend
- [ ] Not started
- [~] In progress
- [x] Complete

## Steps

- [x] **1. Project Scaffold**
- [ ] **2. shadcn/ui Setup**
- [ ] **3. GitHub Actions CI**
- [ ] **4. Docker Setup (local dev)**
- [ ] **5. API Client**
- [ ] **6. Test Infrastructure**
- [ ] **7. Pure Utilities (TDD)**
- [ ] **8. Shared Hooks**
- [ ] **9. App Entry + Routing**
- [ ] **10. Player Screen**
- [ ] **11. Lobby Screen**
- [ ] **12. Game Screen**
- [ ] **13. End Screen**
- [ ] **14. Smoke Tests (Playwright)**
- [ ] **15. README**

---

## UX & Design Decisions

**Style**: Dark / game-like — dark background (`bg-gray-950` / `bg-gray-900`), bright accent colors, bold typography. Use shadcn's dark mode CSS variables as the default.

**Dice display**: Visual dot faces (like real dice). Each die is a square card with dot positions varying by face value. Kept dice are highlighted with a gold/yellow ring. Unrolled dice (value: null) show as dim placeholders.

**Game screen layout** (side-by-side, two-column):
- Left column: dice area (6 dice in 2 rows of 3), roll button, current player info
- Right column: full scorecard table, always visible and scrollable

**Scorecard**: Always-visible table of all 20 categories + bonus + total. After rolling, available categories are highlighted as clickable buttons showing their potential score. Filled categories are shown as plain text (disabled).

**Player screen**: Centered card. Create player form at top; existing players listed as selectable rows below.

**Lobby screen**: List of open game cards. Each card shows game ID, player count, and a Join button. "New Game" button at the top.

**End screen**: Large winner banner, then a full scoreboard table with all players ranked by total score.

---

## Implementation Details

### 1. Project Scaffold ✅

Run from `frontend/`:
```bash
pnpm create vite@latest . -- --template react-ts
pnpm install
```

Then install additional dependencies:
```bash
pnpm add react-router-dom openapi-fetch class-variance-authority clsx tailwind-merge lucide-react
pnpm add -D @biomejs/biome vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @playwright/test tailwindcss autoprefixer postcss
```

Key config files to create/update:
- `vite.config.ts` — add jsdom test env, `@/` alias, dev proxy `/api → http://localhost:8000`
- `tsconfig.json` — strict mode, `@/` path alias
- `biome.json` — single quotes, 2-space indent, 100 char line width, trailing commas ES5
- `tailwind.config.js` + `postcss.config.js`
- `src/test/setup.ts` — imports `@testing-library/jest-dom`
- `playwright.config.ts` — baseURL `http://localhost:5173`, webServer `pnpm dev`

### 2. shadcn/ui Setup

```bash
pnpm dlx shadcn@latest init
pnpm dlx shadcn@latest add button card input label dialog toast badge
```

Generated files go into `src/components/ui/` — **do not manually edit**.
Also creates `src/lib/utils.ts` with `cn()` helper.

### 3. GitHub Actions CI

**`.github/workflows/ci.yml`** — mirrors the backend's CI structure.

**Triggers**: `push` and `pull_request` on all branches

**Jobs**:
1. **build** — Docker Buildx, login to GHCR, build and push image tagged `ghcr.io/{repo}-frontend:dev-{git-sha}`. Cache with `type=gha,scope=dev`.
2. **lint** (depends on build) — pull image, run `pnpm biome check .`
3. **typecheck** (depends on build) — pull image, run `pnpm tsc --noEmit`
4. **test** (depends on build) — pull image, run `pnpm vitest run --coverage`, upload coverage artifact, fail if below 80%
5. **e2e** (depends on build) — pull image, spin up the full stack (frontend + backend + DB via docker compose), run Playwright tests

**Docker strategy**: Build once using a `dev` stage (includes devDependencies). CI runs lint/typecheck/test against that image. Production `Dockerfile` uses multi-stage: `dev` → `builder` (runs `pnpm build`) → `production` (Nginx).

**Permissions**: `contents: read`, `packages: write` (for GHCR push)

### 4. Docker Setup (local dev)

**`Dockerfile`** stages:
```dockerfile
FROM node:22-alpine AS dev
RUN npm install -g pnpm
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .

FROM dev AS builder
RUN pnpm build

FROM nginx:1.27-alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

**`nginx.conf`**:
- `location /api/` → proxy_pass `http://backend:8000/`
- `location /` → `try_files $uri $uri/ /index.html` (SPA routing)

**`docker-compose.yml`** (monorepo root `/Users/marcus/code/yatzy/`):
```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
  frontend:
    build: ./frontend
    ports: ["80:80"]
    depends_on: [backend]
```

### 5. API Client

Generate the typed schema (backend must be running):
```bash
pnpm dlx openapi-typescript http://localhost:8000/openapi.json -o src/api/schema.ts
```

**`src/api/client.ts`**:
```typescript
import createClient from 'openapi-fetch'
import type { paths } from './schema'
export const apiClient = createClient<paths>({ baseUrl: '/api' })
```

**`src/api/index.ts`** — re-export `apiClient` and `components` type.

### 6. Test Infrastructure

**`src/test/setup.ts`** — `import '@testing-library/jest-dom'`

**`src/test/helpers.tsx`** — `Providers` wrapper component (BrowserRouter + PlayerProvider with a preset test player) used by all component tests.

### 7. Pure Utilities (TDD)

Write tests first, then implement:

**`src/lib/scoring.test.ts`** + **`src/lib/scoring.ts`**:
- `sumDice(dice)`, `countDiceValue(dice, value)`
- `isFullHouse`, `isSmallStraight`, `isLargeStraight`, `isYatzy`
- `calculateCategoryScore(category, dice)`

**`src/lib/formatting.test.ts`** + **`src/lib/formatting.ts`**:
- `formatScore(score: number | null): string` — returns `'-'` for null

### 8. Shared Hooks

**`src/hooks/PlayerContext.tsx`**:
- Context stores `player: Player | null` with localStorage persistence (key: `yatzy_player`)
- `PlayerProvider` wraps the app; `usePlayer()` returns `{ player, setPlayer }`
- Hydrates from localStorage on initial render (no flash on reload)

**`src/hooks/usePolling.ts`**:
```typescript
usePolling(callback, { interval = 2000, enabled = true })
```
- Uses `setInterval` + `useRef` to keep callback stable
- Stops when `enabled = false` (game finished or component unmounts)

### 9. App Entry + Routing

**`src/main.tsx`**: StrictMode → BrowserRouter → PlayerProvider → App

**`src/App.tsx`**: Routes:
- `/` → `PlayerScreen`
- `/lobby` → `LobbyScreen` (redirects to `/` if no player)
- `/games/:gameId` → `GameScreen` (redirects to `/` if no player)
- `/games/:gameId/end` → `EndScreen` (redirects to `/` if no player)

### 10. Player Screen

**Files**: `src/screens/player/`
- `PlayerScreen.tsx` — fetches player list on mount, owns loading/error state
- `CreatePlayerForm.tsx` — name input + submit, calls `POST /players`
- `PlayerList.tsx` — renders selectable player cards

**Flow**: Select or create player → `setPlayer(player)` → navigate to `/lobby`

**Tests** (`PlayerScreen.test.tsx`):
```
it('shows list of existing players')
it('allows selecting an existing player and navigates to lobby')
it('creates a new player and navigates to lobby')
it('shows error when player creation fails')
```

### 11. Lobby Screen

**Files**: `src/screens/lobby/`
- `LobbyScreen.tsx` — polls lobby games every 2s; also polls active games to auto-redirect
- `GameList.tsx`, `GameCard.tsx`, `CreateGameButton.tsx`

**API calls**:
- `GET /games?status=lobby` — polled every 2s
- `GET /games?status=active` — polled every 2s; if current player is in one, navigate to it
- `POST /games { creator_id }` — create game → navigate to `/games/{id}`
- `POST /games/{id}/join { player_id }` — join → navigate to `/games/{id}`

**Tests** (`LobbyScreen.test.tsx`):
```
it('shows list of open games')
it('shows empty state when no games')
it('creates a game and navigates')
it('joins a game and navigates')
it('auto-redirects if player already in active game')
```

### 12. Game Screen

**Files**: `src/screens/game/`

**`types.ts`** — screen-specific types

**`useGameState.ts`** — central hook:
- Polls `GET /games/{id}/state` every 2s (stops when `status === 'finished'`)
- Tracks `keptDiceIndices: number[]` and `rollsThisTurn: number` in local state
- Resets both when `current_player_id` changes
- `roll()` → `POST /games/{id}/roll { player_id, kept_dice }` → updates dice, fetches scoring options
- `toggleKeep(index)` — toggles local kept state
- `scoreCategory(cat)` → `PUT /games/{id}/players/{pid}/scorecard { category }` → refreshes scorecard
- `isMyTurn` derived: `gameState.current_player_id === player.id`
- On `status === 'finished'` → navigate to `/games/{id}/end`

**Sub-components**:
- `DieComponent.tsx` — square card with dot-face layout; null = dim placeholder; kept = gold ring
- `DiceArea.tsx` — renders 6 `DieComponent` in a 2×3 grid
- `RollButton.tsx` — shows rolls remaining (3 - rollsThisTurn), disabled after 3 rolls or after scoring
- `ScoreCard.tsx` — 20 categories; filled = disabled, available = clickable button with score
- `WaitingBanner.tsx` — shown when `!isMyTurn`
- `GameScreen.tsx` — composes all sub-components from `useGameState`

**Tests**:
- `GameScreen.test.tsx`: waiting banner, roll button visibility, end-screen navigation
- `DiceArea.test.tsx`: 6 dice rendered, kept highlighting, toggle calls, disabled state
- `ScoreCard.test.tsx`: filled = disabled, scoring options = clickable, bonus display, total

### 13. End Screen

**Files**: `src/screens/end/`
- `EndScreen.tsx` — one-time fetch of `GET /games/{id}/state` and `GET /games/{id}/scoreboard`
- `WinnerBanner.tsx` — winner announcement, handles ties
- `ScoreBoard.tsx` — table of all players + final scores

**Tests** (`EndScreen.test.tsx`):
```
it('shows all players and their scores')
it('highlights the winner')
it('shows draw message for multiple winners')
it('has a link/button back to lobby')
```

### 14. Smoke Tests (Playwright)

**`e2e/happy-path.spec.ts`**:
1. App loads, player screen visible
2. Create a player, lobby appears
3. Create a game, navigate to game screen
4. Roll dice, dice values are visible
5. Select a scoring category

### 15. README

`README.md` covering:
- Prerequisites (Docker, pnpm)
- Local dev setup (`docker compose up` or `pnpm dev` + backend separately)
- Regenerating API client
- Running tests (`pnpm test`, `pnpm test:e2e`)

---

## Critical Files

| File | Why Critical |
|------|-------------|
| `src/api/client.ts` | All components depend on this |
| `src/hooks/PlayerContext.tsx` | Required by routing guards + all screens |
| `src/screens/game/useGameState.ts` | Most complex logic; polling, dice state, scoring |
| `src/lib/scoring.ts` | Pure logic, highest unit test coverage |
| `src/test/helpers.tsx` | Prerequisite for all component tests |

## Verification

1. **Unit tests**: `pnpm test` — all scoring/formatting tests pass
2. **Component tests**: `pnpm test` — all screen tests pass with mocked API
3. **Docker build**: `docker build -t yatzy-frontend .` succeeds
4. **Dev server**: `pnpm dev` starts, app loads at `http://localhost:5173`
5. **Full integration**: `docker compose up` from monorepo root — create player, play a game end-to-end
6. **Smoke tests**: `pnpm test:e2e` against running dev server
