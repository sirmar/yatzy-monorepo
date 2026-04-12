**Structure**
- `app/` domain dirs: `players/`, `games/`, `scoring/`. Infrastructure (`config.py`, `database.py`, `main.py`) at root. Tests under `tests/unit/` and `tests/e2e/`.

**Design rules**
- Soft deletes: never delete rows, use `deleted_at`. All queries filter `WHERE deleted_at IS NULL`.
- Auth via `../auth/` service (JWT validation). Players are separate from auth users.

**Interface**
- POST and PUT (not PATCH) respond with complete resources.

**Testing**
- Each REST endpoint must have e2e tests; unit test business logic only — not repositories
