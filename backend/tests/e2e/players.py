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

  def assert_status(self, status_code: int) -> 'Player':
    assert self.response.status_code == status_code
    return self

  def assert_name(self, name: str) -> 'Player':
    assert self.json['name'] == name
    return self

  def assert_id_positive(self) -> 'Player':
    assert self.json['id'] > 0
    return self

  def assert_has_created_at(self) -> 'Player':
    assert 'created_at' in self.json
    return self

  def assert_has_detail(self) -> 'Player':
    assert 'detail' in self.json
    return self

  def assert_is_empty_list(self) -> 'Player':
    assert self.json == []
    return self

  def assert_names_include(self, *names: str) -> 'Player':
    result_names = [p['name'] for p in self.json]
    for name in names:
      assert name in result_names
    return self

  def assert_id_in_list(self, player_id: int) -> 'Player':
    assert any(p['id'] == player_id for p in self.json)
    return self

  def assert_id_not_in_list(self, player_id: int) -> 'Player':
    assert not any(p['id'] == player_id for p in self.json)
    return self
