from httpx import AsyncClient


class Game:
  def __init__(self, client: AsyncClient) -> None:
    self._client = client
    self.response = None
    self.json = None

  @property
  def id(self) -> int:
    return self.json['id']

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

  def assert_has_detail(self) -> 'Game':
    assert 'detail' in self.json
    return self
