import os
import threading
from collections.abc import Callable
from typing import Any

import httpx

from yatzy import credentials as creds_module
from yatzy.auth import AuthClient, AuthError
from yatzy.credentials import Credentials

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend:8000')


class ApiError(Exception):
  def __init__(self, status_code: int, detail: str) -> None:
    super().__init__(detail)
    self.status_code = status_code
    self.detail = detail


class ApiClient:
  def __init__(
    self, creds: Credentials, auth: AuthClient, base_url: str = BACKEND_URL
  ) -> None:
    self._creds = creds
    self._auth = auth
    self._client = httpx.Client(base_url=base_url)

  def _headers(self) -> dict[str, str]:
    return {'Authorization': f'Bearer {self._creds.access_token}'}

  def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
    r = self._client.request(method, path, headers=self._headers(), **kwargs)
    if r.status_code == 401:
      try:
        new_creds = self._auth.refresh(self._creds.refresh_token)
        self._creds.access_token = new_creds.access_token
        self._creds.refresh_token = new_creds.refresh_token
        creds_module.save(self._creds)
      except AuthError as e:
        raise ApiError(401, str(e)) from e
      r = self._client.request(method, path, headers=self._headers(), **kwargs)
    if r.status_code >= 400:
      raise ApiError(r.status_code, r.json().get('detail', f'HTTP {r.status_code}'))
    return r

  def get_my_player(self) -> dict[str, Any]:
    return self._request('GET', '/players/me').json()

  def create_player(self, name: str) -> dict[str, Any]:
    return self._request('POST', '/players', json={'name': name}).json()

  def get_player(self, player_id: int) -> dict[str, Any]:
    return self._request('GET', f'/players/{player_id}').json()

  def list_games(self, status: str | None = None) -> list[dict[str, Any]]:
    params: dict[str, str] = {'status': status} if status else {}
    return self._request('GET', '/games', params=params).json()

  def create_game(
    self, creator_id: int, mode: str, bot_count: int = 0
  ) -> dict[str, Any]:
    return self._request(
      'POST',
      '/games',
      json={'creator_id': creator_id, 'mode': mode, 'bot_count': bot_count},
    ).json()

  def get_game(self, game_id: int) -> dict[str, Any]:
    return self._request('GET', f'/games/{game_id}').json()

  def join_game(self, game_id: int, player_id: int) -> dict[str, Any]:
    return self._request(
      'POST', f'/games/{game_id}/join', json={'player_id': player_id}
    ).json()

  def leave_game(self, game_id: int, player_id: int) -> None:
    self._request('DELETE', f'/games/{game_id}/players/{player_id}')

  def start_game(self, game_id: int, player_id: int) -> dict[str, Any]:
    return self._request(
      'POST', f'/games/{game_id}/start', json={'player_id': player_id}
    ).json()

  def delete_game(self, game_id: int) -> None:
    self._request('DELETE', f'/games/{game_id}')

  def abort_game(self, game_id: int) -> None:
    self._request('POST', f'/games/{game_id}/abort')

  def get_game_state(self, game_id: int) -> dict[str, Any]:
    return self._request('GET', f'/games/{game_id}/state').json()

  def roll_dice(
    self, game_id: int, player_id: int, kept_dice: list[int]
  ) -> dict[str, Any]:
    return self._request(
      'POST',
      f'/games/{game_id}/roll',
      json={'player_id': player_id, 'kept_dice': kept_dice},
    ).json()

  def get_scoring_options(self, game_id: int, player_id: int) -> list[dict[str, Any]]:
    return self._request(
      'GET', f'/games/{game_id}/players/{player_id}/scoring-options'
    ).json()

  def score_category(
    self, game_id: int, player_id: int, category: str
  ) -> dict[str, Any]:
    return self._request(
      'PUT',
      f'/games/{game_id}/players/{player_id}/scorecard',
      json={'category': category},
    ).json()

  def get_scorecard(self, game_id: int, player_id: int) -> dict[str, Any]:
    return self._request(
      'GET', f'/games/{game_id}/players/{player_id}/scorecard'
    ).json()

  def get_scoreboard(self, game_id: int) -> list[dict[str, Any]]:
    return self._request('GET', f'/games/{game_id}/scoreboard').json()

  def sse_game_url(self, game_id: int) -> str:
    return f'{BACKEND_URL}/games/{game_id}/events'

  def sse_lobby_url(self) -> str:
    return f'{BACKEND_URL}/games/lobby/events'

  def current_token(self) -> str:
    return self._creds.access_token

  def close(self) -> None:
    self._client.close()


class SseListener:
  def __init__(
    self, url: str, get_token: Callable[[], str], on_event: Callable[[], None]
  ) -> None:
    self._url = url
    self._get_token = get_token
    self._on_event = on_event
    self._stop = threading.Event()
    self._thread: threading.Thread | None = None

  def start(self) -> None:
    self._thread = threading.Thread(target=self._run, daemon=True)
    self._thread.start()

  def _run(self) -> None:
    try:
      with httpx.stream(
        'GET',
        self._url,
        headers={'Authorization': f'Bearer {self._get_token()}'},
        timeout=None,
      ) as r:
        for line in r.iter_lines():
          if self._stop.is_set():
            return
          if line.startswith('data:'):
            self._on_event()
    except Exception:
      self._on_event()

  def stop(self) -> None:
    self._stop.set()
