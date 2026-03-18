from httpx import AsyncClient, Response


class ScoringOptions:
  def __init__(self, client: AsyncClient) -> None:
    self._client = client
    self.response = None
    self.json = None

  def _set_response(self, response: Response) -> 'ScoringOptions':
    self.response = response
    if response.content:
      self.json = response.json()
    return self

  async def get(self, game_id: int, player_id: int) -> 'ScoringOptions':
    return self._set_response(
      await self._client.get(f'/games/{game_id}/players/{player_id}/scoring-options')
    )

  def assert_status(self, status_code: int) -> 'ScoringOptions':
    assert self.response.status_code == status_code
    return self

  def assert_has_detail(self) -> 'ScoringOptions':
    assert 'detail' in self.json
    return self

  def assert_excludes_category(self, category: str) -> 'ScoringOptions':
    assert not any(c['category'] == category for c in self.json)
    return self

  def assert_all_scores_positive(self) -> 'ScoringOptions':
    assert all(c['score'] > 0 for c in self.json)
    return self
