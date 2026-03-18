# Yatzy REST API — Implementation Plan

Each slice follows the same pattern:
1. Write e2e test (acceptance criteria)
2. Add DB migration if needed
3. Add/update Pydantic model if needed
4. Add/update repository + unit tests
5. Add/update service + unit tests
6. Add/update route
7. Verify: lint, type check, tests green

---

## Phase 0: GitHub Setup

- Step 1: Create repo — `gh repo create yatzy-backend --private --source=. --remote=origin --push`
- Step 2: Add `.github/workflows/ci.yml` — three jobs (lint, type-check, test) running on every push and PR via `uv`

---

## Phase 1: Scaffolding

No tests yet — just enough infrastructure to support the first slice.

- `pyproject.toml` (dependencies, ruff, pytest config)
- `Dockerfile` + `docker-compose.yml` (app + `db` + `db-test` containers)
- `.env.example`, `.gitignore`
- `app/config.py` — `Settings` (pydantic-settings, reads env vars)
- `app/database.py` — `Database`: aiomysql pool, `get_db()` dependency
- `app/main.py` — skeleton: lifespan, no routers yet
- `tests/e2e/conftest.py` — test DB fixture, table truncation, `AsyncClient`

### pyproject.toml highlights
```toml
[project]
dependencies = ["fastapi[standard]", "aiomysql", "pydantic-settings"]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio", "httpx", "ruff", "ty"]

[tool.ruff]
indent-width = 2
quote-style = "single"

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### Docker
- `db` — dev MySQL on port 3306
- `db-test` — test MySQL on port 3307, ephemeral
- `app` — FastAPI container

---

## Phase 2: Player Slices

### Slice 1 — POST /players
- **DB**: `players` table
- **Model**: `PlayerCreate`, `PlayerResponse`
- **Repo**: `PlayerRepository.create`, `get_by_id`
- **Service**: `PlayerService.create`
- **Route**: `POST /players` → 201 + `PlayerResponse`

### Slice 2 — GET /players
- **Repo**: `PlayerRepository.list_all`
- **Service**: `PlayerService.list`
- **Route**: `GET /players` → 200 + `list[PlayerResponse]`

### Slice 3 — GET /players/{id}
- **Route**: `GET /players/{player_id}` → 200 or 404

### Slice 4 — PUT /players/{id}
- **Model**: `PlayerUpdate`
- **Repo**: `PlayerRepository.update`
- **Service**: `PlayerService.update`
- **Route**: `PUT /players/{player_id}` → 200 + `PlayerResponse`

### Slice 5 — DELETE /players/{id}
- **Repo**: `PlayerRepository.soft_delete` — `UPDATE players SET deleted_at = NOW() WHERE id = ?`
- **Service**: `PlayerService.delete`
- **Route**: `DELETE /players/{player_id}` → 204

---

## Phase 3: Game Slices

### Slice 6 — POST /games
- **DB**: `games`, `game_players` tables
- **Model**: `GameCreate`, `GameResponse`
- **Repo**: `GameRepository.create`, `GamePlayerRepository.add_player`
- **Service**: `GameService.create` (creates game, adds creator to game_players)
- **Route**: `POST /games` → 201 + `GameResponse`

### Slice 7 — GET /games
- **Repo**: `GameRepository.list_all`
- **Service**: `GameService.list`
- **Route**: `GET /games` → 200 + `list[GameResponse]`

### Slice 8 — GET /games/{id}
- **Route**: `GET /games/{game_id}` → 200 or 404

### Slice 9 — POST /games/{id}/join
- **Repo**: `GamePlayerRepository.get_players_for_game`
- **Service**: `GameService.join` (validates: lobby status, max 6 players)
- **Route**: `POST /games/{game_id}/join` → 200 + `GameResponse`

### Slice 10 — POST /games/{id}/start
- **DB**: `turns`, `turn_dice` tables
- **Repo**: `TurnRepository.create` (creates first turn + 6 turn_dice rows)
- **Service**: `GameService.start` (validates: requesting player is creator, creates first turn)
- **Route**: `POST /games/{game_id}/start` → 200 + `GameResponse`

### Slice 11 — POST /games/{id}/end
- **Service**: `GameService.end` (validates: active status)
- **Route**: `POST /games/{game_id}/end` → 200 + `GameResponse`

### Slice 12 — DELETE /games/{id}
- **Repo**: `GameRepository.soft_delete` — `UPDATE games SET deleted_at = NOW() WHERE id = ?`
- **Service**: `GameService.delete` (validates: lobby or finished)
- **Route**: `DELETE /games/{game_id}` → 204

### Slice 13 — GET /games/{id}/state
- **Model**: `GameStateResponse`
- **Route**: `GET /games/{game_id}/state` → 200 + `GameStateResponse`

---

## Phase 4: Turn/Dice Slices

### Slice 14 — POST /games/{id}/turns/roll
- **Domain**: `DiceRoller` + unit tests
- **Model**: `RollRequest`, `RollResponse`
- **Repo**: `TurnRepository.get_current`, `TurnRepository.update_dice`; `GamePlayerRepository.get_rolls_remaining`, `decrement_rolls`
- **Service**: `TurnService.roll` (validates: player's turn, rolls_remaining > 0 on game_players)
- **Route**: `POST /games/{game_id}/turns/roll` → 200 + `RollResponse`

### Slice 15 — GET /games/{id}/turns/valid-categories
- **Domain**: `ScoringCategory` enum, `ScoringEngine` + unit tests (most test-dense)
- **Model**: `ValidCategoriesResponse`
- **Service**: `TurnService.get_valid_categories`
- **Route**: `GET /games/{game_id}/turns/valid-categories?player_id=` → 200 + `ValidCategoriesResponse`

---

## Phase 5: Scorecard Slices

### Slice 16 — GET /games/{id}/scorecards/{player_id}
- **DB**: `score_cards`, `score_entries` tables
- **Model**: `ScoreCardResponse`
- **Repo**: `ScoreCardRepository.get_by_game_and_player`, `get_entries`
- **Service**: `ScoreService.get_scorecard`
- **Route**: `GET /games/{game_id}/scorecards/{player_id}` → 200 + `ScoreCardResponse`

### Slice 17 — PUT /games/{id}/scorecards/{player_id}
- **Model**: `ScoreEntryRequest`
- **Repo**: `ScoreCardRepository.add_entry`; `TurnRepository.complete`
- **Service**: `ScoreService.record_score` (validates: player's turn, at least one roll taken, category unused; records score; completes turn; banks unused rolls to game_players capped at 3; advances turn or ends game)
- **Route**: `PUT /games/{game_id}/scorecards/{player_id}` → 200 + `ScoreCardResponse`

---

## Phase 6: Integration Test

`tests/e2e/test_game_flow.py` — 2-player game played to completion:
all categories filled → game status = finished, both scorecards fully scored, totals positive. ✅

---

## Phase 7: Winner & Scoreboard Slices

### Slice 18 — Winner info in GET /games/{id}/state
- **Model**: Add `PlayerScore` (player_id, total) and extend `GameState` with `winner_ids: list[int] | None` and `final_scores: list[PlayerScore] | None` — only populated when status = finished
- **Repo**: `GameStateRepository.get()` — when finished, query `scorecard_entries` joined via `game_players`, compute per-player totals (sum + 100 bonus if upper section >= 84), derive `winner_ids` as all players sharing the max total
- **Route**: No change — existing `GET /games/{game_id}/state` now returns the new fields
- **Tests**: Unit tests for finished state with winner/tie; e2e tests asserting `winner_ids` and `final_scores` on finished game

### Slice 19 — GET /games/{id}/scoreboard
- **Model**: Add `PlayerScorecard` (player_id + all Scorecard fields) to `scoring/scorecard.py`
- **Repo**: `ScorecardRepository.get_all(game_id)` — returns `list[PlayerScorecard]` for all players in the game; works for active and finished games
- **Route**: `GET /games/{game_id}/scoreboard` → 200 + `list[PlayerScorecard]`; returns 404 if game not found; no status restriction (usable for old finished games too)
- **Tests**: Unit tests for `get_all`; e2e tests for active game, finished game, and 404

---

## Phase 8: Docs

`README.md` — purpose, prerequisites, how to run/test/lint/type-check, Swagger at `/docs`.

---

## Full Database Schema (reference)

```sql
CREATE TABLE players (
  id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(64) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at DATETIME DEFAULT NULL
);

CREATE TABLE games (
  id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  status       ENUM('lobby','active','finished') NOT NULL DEFAULT 'lobby',
  creator_id   INT UNSIGNED NOT NULL,
  current_turn INT UNSIGNED DEFAULT NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  started_at   DATETIME DEFAULT NULL,
  ended_at     DATETIME DEFAULT NULL,
  deleted_at   DATETIME DEFAULT NULL,
  FOREIGN KEY (creator_id) REFERENCES players(id)
);

CREATE TABLE game_players (
  game_id         INT UNSIGNED NOT NULL,
  player_id       INT UNSIGNED NOT NULL,
  join_order      INT UNSIGNED NOT NULL,
  rolls_remaining TINYINT UNSIGNED NOT NULL DEFAULT 0,
  deleted_at      DATETIME DEFAULT NULL,
  PRIMARY KEY (game_id, player_id),
  FOREIGN KEY (game_id)   REFERENCES games(id),
  FOREIGN KEY (player_id) REFERENCES players(id)
);

CREATE TABLE turns (
  id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  game_id      INT UNSIGNED NOT NULL,
  player_id    INT UNSIGNED NOT NULL,
  turn_number  INT UNSIGNED NOT NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME DEFAULT NULL,
  FOREIGN KEY (game_id)   REFERENCES games(id),
  FOREIGN KEY (player_id) REFERENCES players(id)
);

CREATE TABLE turn_dice (
  turn_id   INT UNSIGNED NOT NULL,
  die_index TINYINT UNSIGNED NOT NULL,
  value     TINYINT UNSIGNED DEFAULT NULL,
  kept      BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (turn_id, die_index),
  FOREIGN KEY (turn_id) REFERENCES turns(id) ON DELETE CASCADE
);

CREATE TABLE score_cards (
  id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  game_id   INT UNSIGNED NOT NULL,
  player_id INT UNSIGNED NOT NULL,
  UNIQUE KEY uq_score_card (game_id, player_id),
  FOREIGN KEY (game_id)   REFERENCES games(id)   ON DELETE CASCADE,
  FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);

CREATE TABLE score_entries (
  score_card_id INT UNSIGNED NOT NULL,
  category      VARCHAR(32) NOT NULL,
  score         SMALLINT UNSIGNED NOT NULL,
  turn_id       INT UNSIGNED NOT NULL,
  PRIMARY KEY (score_card_id, category),
  FOREIGN KEY (score_card_id) REFERENCES score_cards(id) ON DELETE CASCADE,
  FOREIGN KEY (turn_id)       REFERENCES turns(id)
);
```

### Key schema decisions
- `deleted_at DATETIME DEFAULT NULL` on `players`, `games`, `game_players` — soft deletes, never hard delete rows. All queries filter `WHERE deleted_at IS NULL`.
- `rolls_remaining` on `game_players` — persists across all turns for a player in a game, not per turn.
- `score_entries` PK `(score_card_id, category)` — DB enforces no double-scoring.
- `games.current_turn` FK to `turns` — makes state polling cheap.

---

## Folder Structure

```
backend/
  app/
    config.py
    database.py
    main.py
    __init__.py
    players/
      __init__.py
      player.py
      player_repository.py
      player_router.py
    games/
      __init__.py
      dice.py
      game.py
      game_player_repository.py
      game_repository.py
      game_router.py
      game_state.py
      game_state_repository.py
      game_status.py
      requests.py
      roll_repository.py
      turn_repository.py
    scoring/
      __init__.py
      score_calculator.py
      score_category.py
      scorecard.py
      scorecard_repository.py
      scorecard_router.py
  tests/
    unit/
    e2e/
      conftest.py
  migrations/
  Dockerfile
  docker-compose.yml
  pyproject.toml
  README.md
```
