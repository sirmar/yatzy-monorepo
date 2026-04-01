from unittest.mock import MagicMock, patch

import httpx
import pytest
import respx

from yatzy.api import ApiClient, ApiError
from yatzy.auth import AuthClient, AuthError
from yatzy.credentials import Credentials


def make_client(access_token: str = 'token', refresh_token: str = 'refresh') -> tuple[ApiClient, MagicMock]:
  creds = Credentials(access_token=access_token, refresh_token=refresh_token)
  auth = MagicMock(spec=AuthClient)
  client = ApiClient(creds, auth, base_url='http://test')
  return client, auth


class TestGetMyPlayer:
  def setup_method(self) -> None:
    self.client, self.auth = make_client()

  @respx.mock
  def test_returns_player_on_success(self) -> None:
    self.GivenPlayerEndpointReturns({'id': 1, 'name': 'Alice'})
    result = self.WhenGetMyPlayer()
    self.ThenResultIs({'id': 1, 'name': 'Alice'}, result)

  @respx.mock
  def test_raises_api_error_on_404(self) -> None:
    self.GivenPlayerEndpointReturns404()
    self.ThenRaisesApiError(404, self.WhenGetMyPlayerRaising)

  @respx.mock
  def test_refreshes_token_on_401(self) -> None:
    self.GivenFirstCallReturns401ThenSuccess({'id': 1, 'name': 'Alice'})
    self.GivenAuthRefreshReturns('new_token', 'new_refresh')
    result = self.WhenGetMyPlayer()
    self.ThenResultIs({'id': 1, 'name': 'Alice'}, result)
    self.ThenTokenWasRefreshed()

  @respx.mock
  def test_raises_api_error_when_refresh_fails(self) -> None:
    self.GivenAllCallsReturn401()
    self.GivenAuthRefreshFails()
    self.ThenRaisesApiError(401, self.WhenGetMyPlayerRaising)

  def GivenPlayerEndpointReturns(self, data: dict) -> None:
    respx.get('http://test/players/me').mock(return_value=httpx.Response(200, json=data))

  def GivenPlayerEndpointReturns404(self) -> None:
    respx.get('http://test/players/me').mock(return_value=httpx.Response(404, json={'detail': 'Not found'}))

  def GivenFirstCallReturns401ThenSuccess(self, data: dict) -> None:
    respx.get('http://test/players/me').mock(
      side_effect=[
        httpx.Response(401, json={'detail': 'Unauthorized'}),
        httpx.Response(200, json=data),
      ]
    )

  def GivenAllCallsReturn401(self) -> None:
    respx.get('http://test/players/me').mock(return_value=httpx.Response(401, json={'detail': 'Unauthorized'}))

  def GivenAuthRefreshReturns(self, access_token: str, refresh_token: str) -> None:
    self.auth.refresh.return_value = Credentials(access_token=access_token, refresh_token=refresh_token)

  def GivenAuthRefreshFails(self) -> None:
    self.auth.refresh.side_effect = AuthError('Session expired')

  def WhenGetMyPlayer(self) -> dict:
    return self.client.get_my_player()

  def WhenGetMyPlayerRaising(self) -> None:
    self.client.get_my_player()

  def ThenResultIs(self, expected: dict, result: dict) -> None:
    assert result == expected

  def ThenRaisesApiError(self, status_code: int, fn: object) -> None:
    with pytest.raises(ApiError) as exc:
      fn()  # type: ignore[operator]
    assert exc.value.status_code == status_code

  def ThenTokenWasRefreshed(self) -> None:
    self.auth.refresh.assert_called_once()


class TestRollDice:
  def setup_method(self) -> None:
    self.client, self.auth = make_client()

  @respx.mock
  def test_sends_correct_request(self) -> None:
    dice = [{'index': i, 'value': i + 1, 'kept': False} for i in range(6)]
    self.GivenRollEndpointReturns(1, {'dice': dice})
    result = self.WhenRollDice(game_id=1, player_id=5, kept_dice=[0, 2, 4])
    self.ThenResultContainsDice(result)
    self.ThenRequestBodyContains([0, 2, 4])

  def GivenRollEndpointReturns(self, game_id: int, data: dict) -> None:
    self._route = respx.post(f'http://test/games/{game_id}/roll').mock(return_value=httpx.Response(200, json=data))

  def WhenRollDice(self, game_id: int, player_id: int, kept_dice: list[int]) -> dict:
    return self.client.roll_dice(game_id, player_id, kept_dice)

  def ThenResultContainsDice(self, result: dict) -> None:
    assert 'dice' in result

  def ThenRequestBodyContains(self, kept_dice: list[int]) -> None:
    import json
    body = json.loads(self._route.calls[0].request.content)
    assert body['kept_dice'] == kept_dice


class TestScoreCategory:
  def setup_method(self) -> None:
    self.client, self.auth = make_client()

  @respx.mock
  def test_sends_category_in_body(self) -> None:
    scorecard = {'entries': [], 'bonus': None, 'total': 0}
    self.GivenScorecardEndpointReturns(1, 5, scorecard)
    self.WhenScoreCategory(game_id=1, player_id=5, category='full_house')
    self.ThenRequestBodyContainsCategory('full_house')

  @respx.mock
  def test_raises_api_error_on_conflict(self) -> None:
    self.GivenScorecardEndpointReturnsConflict(1, 5)
    with pytest.raises(ApiError) as exc:
      self.WhenScoreCategory(game_id=1, player_id=5, category='ones')
    assert exc.value.status_code == 409

  def GivenScorecardEndpointReturns(self, game_id: int, player_id: int, data: dict) -> None:
    self._route = respx.put(f'http://test/games/{game_id}/players/{player_id}/scorecard').mock(
      return_value=httpx.Response(200, json=data)
    )

  def GivenScorecardEndpointReturnsConflict(self, game_id: int, player_id: int) -> None:
    respx.put(f'http://test/games/{game_id}/players/{player_id}/scorecard').mock(
      return_value=httpx.Response(409, json={'detail': 'Already scored'})
    )

  def WhenScoreCategory(self, game_id: int, player_id: int, category: str) -> dict:
    return self.client.score_category(game_id, player_id, category)

  def ThenRequestBodyContainsCategory(self, category: str) -> None:
    import json
    body = json.loads(self._route.calls[0].request.content)
    assert body['category'] == category
