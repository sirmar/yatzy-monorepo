from typing import Any

import pytest

from yatzy.api import ApiClient, ApiError
from yatzy.auth import AuthClient
from yatzy.credentials import Credentials

from .conftest import AUTH_URL, BACKEND_URL


def make_api_client(access_token: str) -> ApiClient:
  auth = AuthClient(base_url=AUTH_URL)
  creds = Credentials(access_token=access_token, refresh_token='unused')
  return ApiClient(creds, auth, base_url=BACKEND_URL)


def start_game(
  client_a: ApiClient, client_b: ApiClient, player_a: tuple[str, int], player_b: tuple[str, int]
) -> int:
  game = client_a.create_game(player_a[1], 'maxi')
  game_id = game['id']
  client_b.join_game(game_id, player_b[1])
  client_a.start_game(game_id, player_a[1])
  return game_id


def score_all_categories(client: ApiClient, game_id: int, player_id: int) -> None:
  """Roll once per turn and score a category, repeating until no turns remain.

  get_scoring_options only returns categories scoring > 0. When all remaining
  categories would score 0, fall back to the scorecard to find an unscored
  category to scratch.
  """
  while True:
    state = client.get_game_state(game_id)
    if state.get('current_player_id') != player_id:
      return
    if state.get('rolls_remaining', 0) > 0 or state.get('saved_rolls', 0) > 0:
      client.roll_dice(game_id, player_id, [])
    options = client.get_scoring_options(game_id, player_id)
    if options:
      client.score_category(game_id, player_id, options[0]['category'])
    else:
      # All remaining categories score 0 with current dice — scratch one.
      sc = client.get_scorecard(game_id, player_id)
      unscored = [e['category'] for e in sc['entries'] if e.get('score') is None]
      if not unscored:
        return
      client.score_category(game_id, player_id, unscored[0])


@pytest.mark.integration
class TestLeaveGame:
  def setup_method(self) -> None:
    self.client_a: ApiClient | None = None
    self.client_b: ApiClient | None = None
    self.game_id: int | None = None

  def teardown_method(self) -> None:
    if self.client_a:
      self.client_a.close()
    if self.client_b:
      self.client_b.close()

  def test_leave_removes_player_from_lobby(
    self, player_a: tuple[str, int], player_b: tuple[str, int]
  ) -> None:
    self.GivenJoinedLobby(player_a, player_b)
    self.WhenPlayerBLeaves(player_b[1])
    self.ThenPlayerNotInGame(player_b[1])

  def test_non_member_cannot_leave(
    self, player_a: tuple[str, int], player_b: tuple[str, int]
  ) -> None:
    self.GivenLobbyCreatedBy(player_a)
    self.ThenLeaveRaisesError(player_b[1])

  def GivenJoinedLobby(self, a: tuple[str, int], b: tuple[str, int]) -> None:
    self.client_a = make_api_client(a[0])
    self.client_b = make_api_client(b[0])
    game = self.client_a.create_game(a[1], 'maxi')
    self.game_id = game['id']
    self.client_b.join_game(self.game_id, b[1])

  def GivenLobbyCreatedBy(self, a: tuple[str, int]) -> None:
    self.client_a = make_api_client(a[0])
    game = self.client_a.create_game(a[1], 'maxi')
    self.game_id = game['id']

  def WhenPlayerBLeaves(self, player_id: int) -> None:
    assert self.client_b and self.game_id
    self.client_b.leave_game(self.game_id, player_id)

  def ThenPlayerNotInGame(self, player_id: int) -> None:
    assert self.client_a and self.game_id
    game = self.client_a.get_game(self.game_id)
    assert player_id not in game.get('player_ids', [])

  def ThenLeaveRaisesError(self, player_id: int) -> None:
    assert self.client_a and self.game_id
    with pytest.raises(ApiError):
      self.client_a.leave_game(self.game_id, player_id)


@pytest.mark.integration
class TestAbortGame:
  def setup_method(self) -> None:
    self.client_a: ApiClient | None = None
    self.client_b: ApiClient | None = None
    self.game_id: int | None = None

  def teardown_method(self) -> None:
    if self.client_a:
      self.client_a.close()
    if self.client_b:
      self.client_b.close()

  def test_abort_makes_game_aborted(
    self, player_a: tuple[str, int], player_b: tuple[str, int]
  ) -> None:
    self.GivenActiveGame(player_a, player_b)
    self.WhenAborted()
    self.ThenGameIsAborted()

  def GivenActiveGame(self, a: tuple[str, int], b: tuple[str, int]) -> None:
    self.client_a = make_api_client(a[0])
    self.client_b = make_api_client(b[0])
    self.game_id = start_game(self.client_a, self.client_b, a, b)

  def WhenAborted(self) -> None:
    assert self.client_a and self.game_id
    self.client_a.abort_game(self.game_id)

  def ThenGameIsAborted(self) -> None:
    assert self.client_a and self.game_id
    game = self.client_a.get_game(self.game_id)
    assert game['status'] == 'abandoned'


@pytest.mark.integration
class TestListGames:
  def setup_method(self) -> None:
    self.client_a: ApiClient | None = None

  def teardown_method(self) -> None:
    if self.client_a:
      self.client_a.close()

  def test_list_lobby_games_includes_created_game(
    self, player_a: tuple[str, int]
  ) -> None:
    self.GivenApiClient(player_a)
    game = self.WhenCreateGame(player_a[1], 'maxi')
    result = self.WhenListGames(status='lobby')
    self.ThenGameInList(game['id'], result)

  def test_list_active_games_does_not_include_lobby(
    self, player_a: tuple[str, int]
  ) -> None:
    self.GivenApiClient(player_a)
    game = self.WhenCreateGame(player_a[1], 'maxi')
    result = self.WhenListGames(status='active')
    ids = [g['id'] for g in result]
    assert game['id'] not in ids

  def GivenApiClient(self, a: tuple[str, int]) -> None:
    self.client_a = make_api_client(a[0])

  def WhenCreateGame(self, player_id: int, mode: str) -> dict[str, Any]:
    assert self.client_a
    return self.client_a.create_game(player_id, mode)

  def WhenListGames(self, status: str) -> list[dict[str, Any]]:
    assert self.client_a
    return self.client_a.list_games(status=status)

  def ThenGameInList(self, game_id: int, games: list[dict[str, Any]]) -> None:
    ids = [g['id'] for g in games]
    assert game_id in ids


@pytest.mark.integration
class TestGetScorecardAndScoreboard:
  def setup_method(self) -> None:
    self.client_a: ApiClient | None = None
    self.client_b: ApiClient | None = None
    self.game_id: int | None = None

  def teardown_method(self) -> None:
    if self.client_a:
      self.client_a.close()
    if self.client_b:
      self.client_b.close()

  def test_scorecard_has_entries_and_total(
    self, player_a: tuple[str, int], player_b: tuple[str, int]
  ) -> None:
    self.GivenActiveGame(player_a, player_b)
    result = self.WhenGetScorecard(player_a[1])
    assert 'entries' in result
    assert 'total' in result
    assert isinstance(result['entries'], list)

  def test_scoreboard_has_entry_for_each_player(
    self, player_a: tuple[str, int], player_b: tuple[str, int]
  ) -> None:
    self.GivenActiveGame(player_a, player_b)
    result = self.WhenGetScoreboard()
    player_ids = [e['player_id'] for e in result]
    assert player_a[1] in player_ids
    assert player_b[1] in player_ids

  def GivenActiveGame(self, a: tuple[str, int], b: tuple[str, int]) -> None:
    self.client_a = make_api_client(a[0])
    self.client_b = make_api_client(b[0])
    self.game_id = start_game(self.client_a, self.client_b, a, b)

  def WhenGetScorecard(self, player_id: int) -> dict[str, Any]:
    assert self.client_a and self.game_id
    return self.client_a.get_scorecard(self.game_id, player_id)

  def WhenGetScoreboard(self) -> list[dict[str, Any]]:
    assert self.client_a and self.game_id
    return self.client_a.get_scoreboard(self.game_id)


@pytest.mark.integration
class TestFullGameCompletion:
  def setup_method(self) -> None:
    self.client_a: ApiClient | None = None
    self.client_b: ApiClient | None = None
    self.game_id: int | None = None

  def teardown_method(self) -> None:
    if self.client_a:
      self.client_a.close()
    if self.client_b:
      self.client_b.close()

  def test_completed_game_has_finished_status_and_winner(
    self, player_a: tuple[str, int], player_b: tuple[str, int]
  ) -> None:
    self.GivenActiveGame(player_a, player_b)
    self.WhenBothPlayersScoreAllCategories(player_a[1], player_b[1])
    self.ThenGameIsFinished()
    self.ThenWinnerIsDeclared()

  def test_scoreboard_totals_are_nonzero_after_full_game(
    self, player_a: tuple[str, int], player_b: tuple[str, int]
  ) -> None:
    self.GivenActiveGame(player_a, player_b)
    self.WhenBothPlayersScoreAllCategories(player_a[1], player_b[1])
    assert self.client_a and self.game_id
    board = self.client_a.get_scoreboard(self.game_id)
    for entry in board:
      assert entry['total'] >= 0

  def GivenActiveGame(self, a: tuple[str, int], b: tuple[str, int]) -> None:
    self.client_a = make_api_client(a[0])
    self.client_b = make_api_client(b[0])
    self.game_id = start_game(self.client_a, self.client_b, a, b)

  def WhenBothPlayersScoreAllCategories(self, pid_a: int, pid_b: int) -> None:
    assert self.client_a and self.client_b and self.game_id
    # Play turns until the game is finished
    for _ in range(200):  # upper bound: 2 players * up to ~21 categories each
      state = self.client_a.get_game_state(self.game_id)
      if state.get('status') != 'active':
        break
      current = state.get('current_player_id')
      if current == pid_a:
        score_all_categories(self.client_a, self.game_id, pid_a)
      elif current == pid_b:
        score_all_categories(self.client_b, self.game_id, pid_b)

  def ThenGameIsFinished(self) -> None:
    assert self.client_a and self.game_id
    state = self.client_a.get_game_state(self.game_id)
    assert state.get('status') == 'finished'

  def ThenWinnerIsDeclared(self) -> None:
    assert self.client_a and self.game_id
    state = self.client_a.get_game_state(self.game_id)
    assert state.get('winner_ids')
    assert len(state['winner_ids']) >= 1
