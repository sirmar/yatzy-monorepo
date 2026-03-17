from httpx import AsyncClient


class Game:
  def __init__(self, client: AsyncClient) -> None:
    self._client = client
    self.response = None
    self.json = None

  @property
  def id(self) -> int:
    return self.json['id']

  async def create(self, creator_id=None) -> 'Game':
    body = {'creator_id': creator_id} if creator_id is not None else {}
    self.response = await self._client.post('/games', json=body)
    if self.response.content:
      self.json = self.response.json()
    return self

  def assert_status(self, status_code: int) -> None:
    assert self.response.status_code == status_code

  def assert_id_positive(self) -> None:
    assert self.json['id'] > 0

  def assert_game_status(self, status: str) -> None:
    assert self.json['status'] == status

  def assert_creator_id(self, creator_id: int) -> None:
    assert self.json['creator_id'] == creator_id

  def assert_player_ids_include(self, *player_ids: int) -> None:
    for pid in player_ids:
      assert pid in self.json['player_ids']

  def assert_has_created_at(self) -> None:
    assert 'created_at' in self.json

  def assert_has_detail(self) -> None:
    assert 'detail' in self.json
