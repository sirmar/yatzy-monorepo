**Goal**
A REST API for a Yatzy game. It should keep track of players, games, dice, score and so on.

**Tools**
- Language: Python 3.14
- Packages: FastAPI (with Pydantic and aiomysql) and MySQL. No ORM.
- Dev packages: Ruff for lint and code formatting. Ty for static type checking.
- Always build and run using Docker
- Use uv for package management
- Configure project using pyproject.toml
- Use a flat app/ python application folder structure

**Design rules**
- One class per file
- Dependency injection
- Use type hints
- Soft deletes: never delete rows, use a `deleted_at` column instead. All queries filter `WHERE deleted_at IS NULL`.

**Testing**
- Each class should be unit tested using mocks for dependencies
- Each REST endpoint should have e2e tests
- E2e tests use a separate test database.
- Use PyTest for both unit tests and end-to-end tests
- Write tests first
- Provision database using a separate Docker container
- Unit tests follow BDD style: a test class per subject, `setup_method` for mock setup, then test methods, then shared `GivenX`, `WhenX`, `ThenX` methods in that order. Results are stored as `self` fields, not passed as parameters. Example:
  ```python
  class TestFoo:
    def setup_method(self):
      self.dep = MagicMock()

    def test_something(self):
      self.GivenAFoo()
      self.WhenSomethingHappens()
      self.ThenTheResultIsCorrect()

    def GivenAFoo(self):
      self.foo = Foo(self.dep)

    def WhenSomethingHappens(self):
      self.result = self.foo.do_something()

    def ThenTheResultIsCorrect(self):
      assert self.result.field == 'expected'
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
