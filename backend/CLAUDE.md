**Goal**
A REST API for a Yatzy game. It should keep track of players, games, dice, score and so on.

**Tools**
- Language: Python 3.14
- Packages: FastAPI (with Pydantic and aiomysql) and MySQL. No ORM.
- Dev packages: Ruff for lint and code formatting. Ty for static type checking.
- Always commit and push using the `/commit` skill — never raw `git commit`/`git push`
- Always build and run using Docker
- Use `make` targets for all dev workflow — never raw `docker compose` or `uvicorn` commands. Key targets: `dev` (hot reload), `start` (prod), `build`, `rebuild`, `stop`, `logs`, `ps`, `clean`, `shell`, `db`, `check`, `release-patch/minor/major`.
- Use uv for package management
- Configure project using pyproject.toml
- Organise `app/` into domain subdirectories: `players/`, `games/`, `scoring/`. Infrastructure files (`config.py`, `database.py`, `main.py`) stay at the root. Tests stay flat under `tests/unit/` and `tests/e2e/`.

**Design rules**
- One class per file for routers and repositories. Small related models (request/response bodies, enums) may be grouped in a single file when they are closely related and each is under ~15 lines — e.g. `requests.py` for request bodies, grouping model + its sub-models in one file.
- Dependency injection
- Use type hints
- Soft deletes: never delete rows, use a `deleted_at` column instead. All queries filter `WHERE deleted_at IS NULL`.

**Testing**
- Each REST endpoint should have e2e tests
- Unit test business logic (score calculation, guard rules). Do not unit test repositories — their correctness is verified by e2e tests against a real database.
- E2e tests use a separate test database.
- Use PyTest for both unit tests and end-to-end tests
- Write tests first
- Provision database using a separate Docker container
- Unit tests follow BDD style: a test class per subject, `setup_method` for mock setup, then test methods, then shared `GivenX`, `WhenX`, `ThenX` methods in that order. Results are stored as `self` fields, not passed as parameters. The specific values being tested must appear in the test method body as arguments to Given/When/Then — not hardcoded inside the helpers. Example:
  ```python
  class TestFoo:
    def setup_method(self):
      self.dep = MagicMock()
      self.foo = Foo(self.dep)

    def test_something(self):
      self.GivenDepReturns('expected')
      self.WhenSomethingHappensWith('input')
      self.ThenResultIs('expected')

    def GivenDepReturns(self, value):
      self.dep.get.return_value = value

    def WhenSomethingHappensWith(self, value):
      self.result = self.foo.do_something(value)

    def ThenResultIs(self, value):
      assert self.result == value
  ```

**Documentation**
- Avoid comments in code
- Swagger for API documentation
- README.md with repository purpose and developer focused information.

**Interface**
- REST API with json requests and responses
- POST and PUT (don't use PATCH) requests should respond with complete resources

**Code Style**
- Two space indent
- Single quotes

**API design**
- Create, list, get, join, start, end, delete game.
- Create, edit, get, list, delete player.
- Get and update score card. One scorecard per player per game.
- See valid possible score categories given the current dice and score board. pure information for player.
- Roll dice including which to keep and which to reroll. Dice rolling is per game and player.
- Game state endpoint for polling.
- No auth management at this point. Players should be separate from user management.

**Game lifecycle**
- A player creates a game. Other players list and join games. When enough has joined, the game is started.
- Only creator can start game.

**Domain**
- Rules: Swedish Maxi Yatzy (6 dice, up to 3 rolls per turn, save unused rolls for later). Bonus is 100 points at 84 or more. Yatzy is also worth 100.
- Categories: standard Swedish Maxi Yatzy scoring categories
- 1 to 6 players per game, turn-based
