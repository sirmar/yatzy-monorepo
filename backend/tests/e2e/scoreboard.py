from httpx import AsyncClient, Response


class Scoreboard:
  def __init__(self, client: AsyncClient) -> None:
    self._client = client
    self.response = None
    self.json = None

  def _set_response(self, response: Response) -> 'Scoreboard':
    self.response = response
    if response.content:
      self.json = response.json()
    return self

  async def get(self, game_id: int) -> 'Scoreboard':
    return self._set_response(await self._client.get(f'/games/{game_id}/scoreboard'))

  def assert_status(self, status_code: int) -> 'Scoreboard':
    assert self.response.status_code == status_code
    return self

  def assert_player_count(self, count: int) -> 'Scoreboard':
    assert len(self.json) == count
    return self

  def assert_has_entries_for_player(self, player_id: int) -> 'Scoreboard':
    match = next((sc for sc in self.json if sc['player_id'] == player_id), None)
    assert match is not None
    assert 'entries' in match
    return self

  def assert_has_detail(self) -> 'Scoreboard':
    assert 'detail' in self.json
    return self
