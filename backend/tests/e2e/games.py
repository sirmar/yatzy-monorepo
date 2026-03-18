from httpx import AsyncClient


class Game:
  def __init__(self, client: AsyncClient) -> None:
    self._client = client
    self._id: int | None = None
    self.response = None
    self.json = None

  @property
  def id(self) -> int:
    return self._id  # type: ignore[return-value]

  async def roll(self, game_id: int, player_id: int, kept_dice: list[int] | None = None) -> 'Game':
    body = {'player_id': player_id, 'kept_dice': kept_dice or []}
    self.response = await self._client.post(f'/games/{game_id}/roll', json=body)
    if self.response.content:
      self.json = self.response.json()
    return self

  async def state(self, game_id: int) -> 'Game':
    self.response = await self._client.get(f'/games/{game_id}/state')
    if self.response.content:
      self.json = self.response.json()
    return self

  async def delete(self, game_id: int) -> 'Game':
    self.response = await self._client.delete(f'/games/{game_id}')
    if self.response.content:
      self.json = self.response.json()
    return self

  async def end(self, game_id: int) -> 'Game':
    self.response = await self._client.post(f'/games/{game_id}/end')
    if self.response.content:
      self.json = self.response.json()
    return self

  async def start(self, game_id: int, player_id: int) -> 'Game':
    self.response = await self._client.post(f'/games/{game_id}/start', json={'player_id': player_id})
    if self.response.content:
      self.json = self.response.json()
    return self

  async def join(self, game_id: int, player_id: int) -> 'Game':
    self.response = await self._client.post(f'/games/{game_id}/join', json={'player_id': player_id})
    if self.response.content:
      self.json = self.response.json()
    return self

  async def get(self, game_id: int) -> 'Game':
    self.response = await self._client.get(f'/games/{game_id}')
    if self.response.content:
      self.json = self.response.json()
    return self

  async def create(self, creator_id=None) -> 'Game':
    body = {'creator_id': creator_id} if creator_id is not None else {}
    self.response = await self._client.post('/games', json=body)
    if self.response.content:
      self.json = self.response.json()
      if 'id' in self.json:
        self._id = self.json['id']
    return self

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
