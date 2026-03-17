from httpx import AsyncClient


class Player:
  def __init__(self, client: AsyncClient) -> None:
    self._client = client
    self.response = None
    self.json = None

  @property
  def id(self) -> int:
    return self.json['id']

  async def create(self, name=None) -> 'Player':
    body = {'name': name} if name is not None else {}
    self.response = await self._client.post('/players', json=body)
    if self.response.content:
      self.json = self.response.json()
    return self

  async def get(self, player_id: int) -> 'Player':
    self.response = await self._client.get(f'/players/{player_id}')
    if self.response.content:
      self.json = self.response.json()
    return self

  async def list_all(self) -> 'Player':
    self.response = await self._client.get('/players')
    self.json = self.response.json()
    return self

  async def update(self, player_id: int, name: str) -> 'Player':
    self.response = await self._client.put(f'/players/{player_id}', json={'name': name})
    if self.response.content:
      self.json = self.response.json()
    return self

  async def delete(self, player_id: int) -> 'Player':
    self.response = await self._client.delete(f'/players/{player_id}')
    return self

  def assert_status(self, status_code: int) -> None:
    assert self.response.status_code == status_code

  def assert_name(self, name: str) -> None:
    assert self.json['name'] == name

  def assert_id_positive(self) -> None:
    assert self.json['id'] > 0

  def assert_has_created_at(self) -> None:
    assert 'created_at' in self.json

  def assert_has_detail(self) -> None:
    assert 'detail' in self.json

  def assert_is_empty_list(self) -> None:
    assert self.json == []

  def assert_names_include(self, *names: str) -> None:
    result_names = [p['name'] for p in self.json]
    for name in names:
      assert name in result_names

  def assert_id_in_list(self, player_id: int) -> None:
    assert any(p['id'] == player_id for p in self.json)

  def assert_id_not_in_list(self, player_id: int) -> None:
    assert not any(p['id'] == player_id for p in self.json)
