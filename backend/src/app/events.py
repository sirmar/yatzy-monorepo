import asyncio
from collections import defaultdict


class EventBus:
  def __init__(self) -> None:
    self._game_subs: dict[int, list[asyncio.Queue[dict]]] = defaultdict(list)
    self._lobby_subs: list[asyncio.Queue[dict]] = []
    self._player_subs: dict[int, list[asyncio.Queue[dict]]] = defaultdict(list)

  # --- game-specific channel ---

  def subscribe_game(self, game_id: int) -> asyncio.Queue[dict]:
    q: asyncio.Queue[dict] = asyncio.Queue()
    self._game_subs[game_id].append(q)
    return q

  def unsubscribe_game(self, game_id: int, q: asyncio.Queue[dict]) -> None:
    try:
      self._game_subs[game_id].remove(q)
    except ValueError:
      pass

  def publish_game(self, game_id: int) -> None:
    for q in list(self._game_subs[game_id]):
      q.put_nowait({'type': 'state_changed'})

  # --- lobby channel (all lobby watchers) ---

  def subscribe_lobby(self) -> asyncio.Queue[dict]:
    q: asyncio.Queue[dict] = asyncio.Queue()
    self._lobby_subs.append(q)
    return q

  def unsubscribe_lobby(self, q: asyncio.Queue[dict]) -> None:
    try:
      self._lobby_subs.remove(q)
    except ValueError:
      pass

  def publish_lobby(self) -> None:
    for q in list(self._lobby_subs):
      q.put_nowait({'type': 'games_changed'})

  # --- player-specific channel (active games in navbar) ---

  def subscribe_player(self, player_id: int) -> asyncio.Queue[dict]:
    q: asyncio.Queue[dict] = asyncio.Queue()
    self._player_subs[player_id].append(q)
    return q

  def unsubscribe_player(self, player_id: int, q: asyncio.Queue[dict]) -> None:
    try:
      self._player_subs[player_id].remove(q)
    except ValueError:
      pass

  def publish_player(self, player_ids: list[int]) -> None:
    seen: set[int] = set()
    for pid in player_ids:
      for q in list(self._player_subs[pid]):
        qid = id(q)
        if qid not in seen:
          q.put_nowait({'type': 'games_changed'})
          seen.add(qid)
