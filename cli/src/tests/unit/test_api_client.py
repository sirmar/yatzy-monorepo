from unittest.mock import MagicMock

import httpx
import pytest
import respx

from yatzy.api import ApiClient, ApiError
from yatzy.auth import AuthClient
from yatzy.credentials import Credentials


def make_client() -> tuple[ApiClient, MagicMock]:
  creds = Credentials(access_token='token', refresh_token='refresh')
  auth = MagicMock(spec=AuthClient)
  return ApiClient(creds, auth, base_url='http://test'), auth


class TestErrorHandling:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_raises_api_error_with_detail_from_body(self) -> None:
    respx.get('http://test/players/me').mock(
      return_value=httpx.Response(400, json={'detail': 'Bad input'})
    )
    with pytest.raises(ApiError) as exc:
      self.client.get_my_player()
    assert str(exc.value) == 'Bad input'
    assert exc.value.status_code == 400

  @respx.mock
  def test_raises_api_error_with_fallback_when_no_detail(self) -> None:
    respx.get('http://test/players/me').mock(return_value=httpx.Response(500, json={}))
    with pytest.raises(ApiError) as exc:
      self.client.get_my_player()
    assert exc.value.status_code == 500
    assert 'HTTP 500' in str(exc.value)


class TestCreatePlayer:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_posts_name_and_returns_player(self) -> None:
    self._route = respx.post('http://test/players').mock(
      return_value=httpx.Response(201, json={'id': 7, 'name': 'Alice'})
    )
    result = self.client.create_player('Alice')
    assert result == {'id': 7, 'name': 'Alice'}
    import json

    body = json.loads(self._route.calls[0].request.content)
    assert body['name'] == 'Alice'


class TestGetPlayer:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_returns_player_by_id(self) -> None:
    respx.get('http://test/players/3').mock(
      return_value=httpx.Response(200, json={'id': 3, 'name': 'Bob'})
    )
    result = self.client.get_player(3)
    assert result['id'] == 3
    assert result['name'] == 'Bob'

  @respx.mock
  def test_raises_on_404(self) -> None:
    respx.get('http://test/players/99').mock(
      return_value=httpx.Response(404, json={'detail': 'Not found'})
    )
    with pytest.raises(ApiError) as exc:
      self.client.get_player(99)
    assert exc.value.status_code == 404


class TestListGames:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_returns_games_without_filter(self) -> None:
    games = [{'id': 1, 'status': 'lobby'}, {'id': 2, 'status': 'active'}]
    respx.get('http://test/games').mock(return_value=httpx.Response(200, json=games))
    result = self.client.list_games()
    assert len(result) == 2

  @respx.mock
  def test_sends_status_filter(self) -> None:
    route = respx.get('http://test/games').mock(
      return_value=httpx.Response(200, json=[{'id': 1, 'status': 'lobby'}])
    )
    self.client.list_games(status='lobby')
    assert route.calls[0].request.url.params['status'] == 'lobby'

  @respx.mock
  def test_returns_empty_list(self) -> None:
    respx.get('http://test/games').mock(return_value=httpx.Response(200, json=[]))
    result = self.client.list_games()
    assert result == []


class TestCreateGame:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_posts_creator_and_mode(self) -> None:
    game = {'id': 5, 'status': 'lobby', 'mode': 'maxi'}
    route = respx.post('http://test/games').mock(
      return_value=httpx.Response(201, json=game)
    )
    result = self.client.create_game(creator_id=1, mode='maxi')
    assert result['id'] == 5
    import json

    body = json.loads(route.calls[0].request.content)
    assert body['creator_id'] == 1
    assert body['mode'] == 'maxi'


class TestGetGame:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_returns_game(self) -> None:
    game = {'id': 2, 'status': 'active', 'mode': 'yatzy'}
    respx.get('http://test/games/2').mock(return_value=httpx.Response(200, json=game))
    result = self.client.get_game(2)
    assert result['status'] == 'active'

  @respx.mock
  def test_raises_on_404(self) -> None:
    respx.get('http://test/games/999').mock(
      return_value=httpx.Response(404, json={'detail': 'Not found'})
    )
    with pytest.raises(ApiError) as exc:
      self.client.get_game(999)
    assert exc.value.status_code == 404


class TestJoinGame:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_posts_player_id_and_returns_game(self) -> None:
    game = {'id': 1, 'player_ids': [1, 2]}
    route = respx.post('http://test/games/1/join').mock(
      return_value=httpx.Response(200, json=game)
    )
    result = self.client.join_game(1, player_id=2)
    assert 2 in result['player_ids']
    import json

    body = json.loads(route.calls[0].request.content)
    assert body['player_id'] == 2

  @respx.mock
  def test_raises_on_conflict(self) -> None:
    respx.post('http://test/games/1/join').mock(
      return_value=httpx.Response(409, json={'detail': 'Already joined'})
    )
    with pytest.raises(ApiError) as exc:
      self.client.join_game(1, player_id=2)
    assert exc.value.status_code == 409


class TestLeaveGame:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_sends_delete_to_correct_url(self) -> None:
    route = respx.delete('http://test/games/3/players/7').mock(
      return_value=httpx.Response(204)
    )
    self.client.leave_game(3, player_id=7)
    assert route.called

  @respx.mock
  def test_raises_on_forbidden(self) -> None:
    respx.delete('http://test/games/3/players/7').mock(
      return_value=httpx.Response(403, json={'detail': 'Not in game'})
    )
    with pytest.raises(ApiError) as exc:
      self.client.leave_game(3, 7)
    assert exc.value.status_code == 403


class TestStartGame:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_posts_player_id_and_returns_game(self) -> None:
    game = {'id': 1, 'status': 'active'}
    route = respx.post('http://test/games/1/start').mock(
      return_value=httpx.Response(200, json=game)
    )
    result = self.client.start_game(1, player_id=1)
    assert result['status'] == 'active'
    import json

    body = json.loads(route.calls[0].request.content)
    assert body['player_id'] == 1


class TestDeleteGame:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_sends_delete(self) -> None:
    route = respx.delete('http://test/games/4').mock(return_value=httpx.Response(204))
    self.client.delete_game(4)
    assert route.called

  @respx.mock
  def test_raises_on_forbidden(self) -> None:
    respx.delete('http://test/games/4').mock(
      return_value=httpx.Response(403, json={'detail': 'Not creator'})
    )
    with pytest.raises(ApiError) as exc:
      self.client.delete_game(4)
    assert exc.value.status_code == 403


class TestAbortGame:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_posts_to_abort_url(self) -> None:
    route = respx.post('http://test/games/2/abort').mock(
      return_value=httpx.Response(200, json={})
    )
    self.client.abort_game(2)
    assert route.called


class TestGetGameState:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_returns_state(self) -> None:
    state = {'current_player_id': 1, 'rolls_remaining': 3, 'dice': []}
    respx.get('http://test/games/1/state').mock(
      return_value=httpx.Response(200, json=state)
    )
    result = self.client.get_game_state(1)
    assert result['current_player_id'] == 1
    assert result['rolls_remaining'] == 3


class TestGetScorecard:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_returns_scorecard(self) -> None:
    sc = {'entries': [{'category': 'ones', 'score': None}], 'bonus': None, 'total': 0}
    respx.get('http://test/games/1/players/5/scorecard').mock(
      return_value=httpx.Response(200, json=sc)
    )
    result = self.client.get_scorecard(1, 5)
    assert 'entries' in result
    assert result['total'] == 0


class TestGetScoreboard:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_returns_scoreboard_list(self) -> None:
    board = [{'player_id': 1, 'total': 150}, {'player_id': 2, 'total': 120}]
    respx.get('http://test/games/1/scoreboard').mock(
      return_value=httpx.Response(200, json=board)
    )
    result = self.client.get_scoreboard(1)
    assert len(result) == 2
    assert result[0]['player_id'] == 1


class TestRollDice:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_posts_player_and_kept_dice(self) -> None:
    dice = {'dice': [{'index': 0, 'value': 4}, {'index': 1, 'value': 2}]}
    route = respx.post('http://test/games/1/roll').mock(
      return_value=httpx.Response(200, json=dice)
    )
    result = self.client.roll_dice(1, player_id=2, kept_dice=[0])
    assert result == dice
    import json

    body = json.loads(route.calls[0].request.content)
    assert body['player_id'] == 2
    assert body['kept_dice'] == [0]


class TestGetScoringOptions:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_returns_options_list(self) -> None:
    options = [{'category': 'ones', 'score': 3}, {'category': 'twos', 'score': 6}]
    respx.get('http://test/games/1/players/2/scoring-options').mock(
      return_value=httpx.Response(200, json=options)
    )
    result = self.client.get_scoring_options(1, 2)
    assert len(result) == 2
    assert result[0]['category'] == 'ones'


class TestScoreCategory:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  @respx.mock
  def test_puts_category_and_returns_scorecard(self) -> None:
    sc = {'entries': [{'category': 'ones', 'score': 3}], 'total': 3}
    route = respx.put('http://test/games/1/players/2/scorecard').mock(
      return_value=httpx.Response(200, json=sc)
    )
    result = self.client.score_category(1, 2, 'ones')
    assert result['total'] == 3
    import json

    body = json.loads(route.calls[0].request.content)
    assert body['category'] == 'ones'


class TestTokenRefresh:
  def setup_method(self) -> None:
    self.client, self.auth = make_client()

  @respx.mock
  def test_retries_with_new_token_on_401(self) -> None:
    from yatzy.credentials import Credentials

    self.auth.refresh.return_value = Credentials(
      access_token='new-token', refresh_token='new-refresh'
    )
    respx.get('http://test/players/me').mock(
      side_effect=[
        httpx.Response(401, json={'detail': 'Unauthorized'}),
        httpx.Response(200, json={'id': 1, 'name': 'Alice'}),
      ]
    )
    result = self.client.get_my_player()
    assert result['id'] == 1
    assert self.auth.refresh.called

  @respx.mock
  def test_raises_api_error_when_refresh_fails(self) -> None:
    from yatzy.auth import AuthError

    self.auth.refresh.side_effect = AuthError('token expired')
    respx.get('http://test/players/me').mock(
      return_value=httpx.Response(401, json={'detail': 'Unauthorized'})
    )
    with pytest.raises(ApiError) as exc:
      self.client.get_my_player()
    assert exc.value.status_code == 401


class TestApiClientMisc:
  def setup_method(self) -> None:
    self.client, _ = make_client()

  def test_sse_game_url_contains_game_id(self) -> None:
    url = self.client.sse_game_url(42)
    assert '42' in url
    assert url.endswith('/events')

  def test_sse_lobby_url_contains_lobby(self) -> None:
    url = self.client.sse_lobby_url()
    assert 'lobby' in url

  def test_current_token_returns_access_token(self) -> None:
    assert self.client.current_token() == 'token'

  def test_close_does_not_raise(self) -> None:
    self.client.close()


class TestSseListener:
  def test_start_and_stop(self) -> None:
    from yatzy.api import SseListener

    called: list[int] = []
    listener = SseListener(
      'http://test/events', lambda: 'tok', lambda: called.append(1)
    )
    listener.start()
    listener.stop()
    assert listener._stop.is_set()

  def test_on_event_called_for_each_sse_data_line(self) -> None:
    import threading
    from yatzy.api import SseListener

    called: list[int] = []
    done = threading.Event()

    def on_event() -> None:
      called.append(1)
      if len(called) >= 2:
        done.set()

    with respx.mock:
      respx.get('http://test/events').mock(
        return_value=httpx.Response(
          200,
          text='data: {}\ndata: {}\n',
          headers={'content-type': 'text/event-stream'},
        )
      )
      listener = SseListener('http://test/events', lambda: 'tok', on_event)
      listener.start()
      done.wait(timeout=2)
      listener.stop()

    assert len(called) >= 2

  def test_on_event_called_on_exception(self) -> None:
    import threading
    from yatzy.api import SseListener

    called: list[int] = []
    done = threading.Event()

    def on_event() -> None:
      called.append(1)
      done.set()

    with respx.mock:
      respx.get('http://test/events').mock(side_effect=Exception('connection error'))
      listener = SseListener('http://test/events', lambda: 'tok', on_event)
      listener.start()
      done.wait(timeout=2)
      listener.stop()

    assert len(called) == 1
