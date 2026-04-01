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


@pytest.mark.integration
class TestPlayerApi:
  def setup_method(self) -> None:
    self.client: ApiClient | None = None

  def teardown_method(self) -> None:
    if self.client:
      self.client.close()

  def test_get_my_player_returns_player(self, player_a: tuple[str, int]) -> None:
    self.GivenApiClient(player_a[0])
    result = self.WhenGetMyPlayer()
    self.ThenResultHasId(player_a[1], result)

  def test_get_player_by_id(self, player_a: tuple[str, int]) -> None:
    self.GivenApiClient(player_a[0])
    result = self.WhenGetPlayer(player_a[1])
    self.ThenResultHasName('PlayerA', result)

  def GivenApiClient(self, token: str) -> None:
    self.client = make_api_client(token)

  def WhenGetMyPlayer(self) -> dict[str, Any]:
    assert self.client
    return self.client.get_my_player()

  def WhenGetPlayer(self, player_id: int) -> dict[str, Any]:
    assert self.client
    return self.client.get_player(player_id)

  def ThenResultHasId(self, expected_id: int, result: dict[str, Any]) -> None:
    assert result['id'] == expected_id

  def ThenResultHasName(self, expected_name: str, result: dict[str, Any]) -> None:
    assert result['name'] == expected_name


@pytest.mark.integration
class TestGameLifecycle:
  def setup_method(self) -> None:
    self.client_a: ApiClient | None = None
    self.client_b: ApiClient | None = None
    self.game_id: int | None = None

  def teardown_method(self) -> None:
    if self.client_a:
      self.client_a.close()
    if self.client_b:
      self.client_b.close()

  def test_create_game_returns_lobby_status(self, player_a: tuple[str, int]) -> None:
    self.GivenApiClients(player_a, player_a)
    result = self.WhenCreateGame(player_a[1], 'maxi')
    self.ThenGameHasStatus('lobby', result)

  def test_join_game_adds_player(
    self, player_a: tuple[str, int], player_b: tuple[str, int]
  ) -> None:
    self.GivenApiClients(player_a, player_b)
    self.WhenCreateGame(player_a[1], 'maxi')
    result = self.WhenJoinGame(player_b[1])
    self.ThenGameHasPlayerCount(2, result)

  def test_start_game_makes_active(
    self, player_a: tuple[str, int], player_b: tuple[str, int]
  ) -> None:
    self.GivenApiClients(player_a, player_b)
    self.WhenCreateGame(player_a[1], 'maxi')
    self.WhenJoinGame(player_b[1])
    result = self.WhenStartGame(player_a[1])
    self.ThenGameHasStatus('active', result)

  def test_delete_lobby_game(self, player_a: tuple[str, int]) -> None:
    self.GivenApiClients(player_a, player_a)
    self.WhenCreateGame(player_a[1], 'yatzy')
    self.WhenDeleteGame()
    self.ThenGameNotFound()

  def GivenApiClients(self, a: tuple[str, int], b: tuple[str, int]) -> None:
    self.client_a = make_api_client(a[0])
    self.client_b = make_api_client(b[0])
    self.player_id_a = a[1]
    self.player_id_b = b[1]

  def WhenCreateGame(self, player_id: int, mode: str) -> dict[str, Any]:
    assert self.client_a
    result = self.client_a.create_game(player_id, mode)
    self.game_id = result['id']
    return result

  def WhenJoinGame(self, player_id: int) -> dict[str, Any]:
    assert self.client_b and self.game_id
    return self.client_b.join_game(self.game_id, player_id)

  def WhenStartGame(self, player_id: int) -> dict[str, Any]:
    assert self.client_a and self.game_id
    return self.client_a.start_game(self.game_id, player_id)

  def WhenDeleteGame(self) -> None:
    assert self.client_a and self.game_id
    self.client_a.delete_game(self.game_id)

  def ThenGameHasStatus(self, status: str, result: dict[str, Any]) -> None:
    assert result['status'] == status

  def ThenGameHasPlayerCount(self, count: int, result: dict[str, Any]) -> None:
    assert len(result['player_ids']) == count

  def ThenGameNotFound(self) -> None:
    assert self.client_a and self.game_id
    with pytest.raises(ApiError) as exc:
      self.client_a.get_game(self.game_id)
    assert exc.value.status_code == 404


@pytest.mark.integration
class TestRollAndScore:
  def setup_method(self) -> None:
    self.client_a: ApiClient | None = None
    self.client_b: ApiClient | None = None
    self.game_id: int | None = None

  def teardown_method(self) -> None:
    if self.client_a:
      self.client_a.close()
    if self.client_b:
      self.client_b.close()

  def test_roll_returns_six_dice(
    self, player_a: tuple[str, int], player_b: tuple[str, int]
  ) -> None:
    self.GivenActiveGame(player_a, player_b)
    result = self.WhenRoll(player_a[1], [])
    self.ThenDiceCountIs(6, result)

  def test_roll_with_kept_dice_preserves_values(
    self, player_a: tuple[str, int], player_b: tuple[str, int]
  ) -> None:
    self.GivenActiveGame(player_a, player_b)
    first_roll = self.WhenRoll(player_a[1], [])
    kept_index = first_roll['dice'][0]['index']
    kept_value = first_roll['dice'][0]['value']
    second_roll = self.WhenRoll(player_a[1], [kept_index])
    self.ThenDieValuePreserved(kept_index, kept_value, second_roll)

  def test_score_category_advances_turn(
    self, player_a: tuple[str, int], player_b: tuple[str, int]
  ) -> None:
    self.GivenActiveGame(player_a, player_b)
    self.WhenRoll(player_a[1], [])
    options = self.WhenGetScoringOptions(player_a[1])
    self.WhenScoreFirstOption(player_a[1], options)
    state = self.WhenGetGameState()
    self.ThenCurrentPlayerIs(player_b[1], state)

  def test_get_scoring_options_returns_list(
    self, player_a: tuple[str, int], player_b: tuple[str, int]
  ) -> None:
    self.GivenActiveGame(player_a, player_b)
    self.WhenRoll(player_a[1], [])
    options = self.WhenGetScoringOptions(player_a[1])
    self.ThenOptionsNotEmpty(options)

  def GivenActiveGame(self, a: tuple[str, int], b: tuple[str, int]) -> None:
    self.client_a = make_api_client(a[0])
    self.client_b = make_api_client(b[0])
    game = self.client_a.create_game(a[1], 'maxi')
    self.game_id = game['id']
    self.client_b.join_game(self.game_id, b[1])
    self.client_a.start_game(self.game_id, a[1])

  def WhenRoll(self, player_id: int, kept_dice: list[int]) -> dict[str, Any]:
    assert self.client_a and self.game_id
    return self.client_a.roll_dice(self.game_id, player_id, kept_dice)

  def WhenGetScoringOptions(self, player_id: int) -> list[dict[str, Any]]:
    assert self.client_a and self.game_id
    return self.client_a.get_scoring_options(self.game_id, player_id)

  def WhenScoreFirstOption(self, player_id: int, options: list[dict[str, Any]]) -> None:
    assert self.client_a and self.game_id
    category = options[0]['category']
    self.client_a.score_category(self.game_id, player_id, category)

  def WhenGetGameState(self) -> dict[str, Any]:
    assert self.client_a and self.game_id
    return self.client_a.get_game_state(self.game_id)

  def ThenDiceCountIs(self, count: int, result: dict[str, Any]) -> None:
    assert len(result['dice']) == count

  def ThenDieValuePreserved(
    self, index: int, expected_value: int | None, result: dict[str, Any]
  ) -> None:
    die = next(d for d in result['dice'] if d['index'] == index)
    assert die['value'] == expected_value

  def ThenCurrentPlayerIs(self, player_id: int, state: dict[str, Any]) -> None:
    assert state['current_player_id'] == player_id

  def ThenOptionsNotEmpty(self, options: list[dict[str, Any]]) -> None:
    assert len(options) > 0
