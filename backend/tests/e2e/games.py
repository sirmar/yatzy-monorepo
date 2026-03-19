from httpx import AsyncClient, Response


class Game:
  def __init__(self, client: AsyncClient) -> None:
    self._client = client
    self._id: int | None = None
    self.response = None
    self.json = None

  @property
  def id(self) -> int:
    return self._id  # type: ignore[return-value]

  def _set_response(self, response: Response) -> 'Game':
    self.response = response
    if response.content:
      self.json = response.json()
      if isinstance(self.json, dict) and 'id' in self.json:
        self._id = self.json['id']
    return self

  async def roll(self, game_id: int, player_id: int, kept_dice: list[int] | None = None) -> 'Game':
    body = {'player_id': player_id, 'kept_dice': kept_dice or []}
    return self._set_response(await self._client.post(f'/games/{game_id}/roll', json=body))

  async def state(self, game_id: int) -> 'Game':
    return self._set_response(await self._client.get(f'/games/{game_id}/state'))

  async def delete(self, game_id: int) -> 'Game':
    return self._set_response(await self._client.delete(f'/games/{game_id}'))

  async def end(self, game_id: int) -> 'Game':
    return self._set_response(await self._client.post(f'/games/{game_id}/end'))

  async def start(self, game_id: int, player_id: int) -> 'Game':
    return self._set_response(await self._client.post(f'/games/{game_id}/start', json={'player_id': player_id}))

  async def join(self, game_id: int, player_id: int) -> 'Game':
    return self._set_response(await self._client.post(f'/games/{game_id}/join', json={'player_id': player_id}))

  async def get(self, game_id: int) -> 'Game':
    return self._set_response(await self._client.get(f'/games/{game_id}'))

  async def create(self, creator_id=None) -> 'Game':
    body = {'creator_id': creator_id} if creator_id is not None else {}
    return self._set_response(await self._client.post('/games', json=body))

  async def list_all(self, status: str | None = None) -> 'Game':
    params = {'status': status} if status is not None else {}
    return self._set_response(await self._client.get('/games', params=params))

  def assert_status(self, status_code: int) -> 'Game':
    assert self.response.status_code == status_code
    return self

  def assert_id_positive(self) -> 'Game':
    assert self.json['id'] > 0
    return self

  def assert_game_status(self, status: str) -> 'Game':
    assert self.json['status'] == status
    return self

  def assert_creator_id(self, creator_id: int) -> 'Game':
    assert self.json['creator_id'] == creator_id
    return self

  def assert_player_ids_include(self, *player_ids: int) -> 'Game':
    for pid in player_ids:
      assert pid in self.json['player_ids']
    return self

  def assert_has_created_at(self) -> 'Game':
    assert 'created_at' in self.json
    return self

  def assert_dice_have_values(self) -> 'Game':
    assert all(d['value'] is not None for d in self.json['dice'])
    return self

  def assert_die_is_kept(self, index: int) -> 'Game':
    die = next(d for d in self.json['dice'] if d['index'] == index)
    assert die['kept'] is True
    return self

  def assert_state_status(self, status: str) -> 'Game':
    assert self.json['status'] == status
    return self

  def assert_current_player_id(self, player_id: int) -> 'Game':
    assert self.json['current_player_id'] == player_id
    return self

  def assert_dice_count(self, count: int) -> 'Game':
    assert len(self.json['dice']) == count
    return self

  def assert_has_detail(self) -> 'Game':
    assert 'detail' in self.json
    return self

  def assert_is_empty_list(self) -> 'Game':
    assert self.json == []
    return self

  def assert_ids_include(self, *game_ids: int) -> 'Game':
    result_ids = [g['id'] for g in self.json]
    for gid in game_ids:
      assert gid in result_ids
    return self

  def assert_ids_exclude(self, *game_ids: int) -> 'Game':
    result_ids = [g['id'] for g in self.json]
    for gid in game_ids:
      assert gid not in result_ids
    return self

  def assert_has_winner_ids(self) -> 'Game':
    assert self.json.get('winner_ids') is not None
    return self

  def assert_has_final_scores(self) -> 'Game':
    assert self.json.get('final_scores') is not None
    return self
