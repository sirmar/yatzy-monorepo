from httpx import AsyncClient, Response


class Scorecard:
  def __init__(self, client: AsyncClient) -> None:
    self._client = client
    self.response = None
    self.json = None

  def _set_response(self, response: Response) -> 'Scorecard':
    self.response = response
    if response.content:
      self.json = response.json()
    return self

  async def get(self, game_id: int, player_id: int) -> 'Scorecard':
    return self._set_response(
      await self._client.get(f'/games/{game_id}/players/{player_id}/scorecard')
    )

  def assert_status(self, status_code: int) -> 'Scorecard':
    assert self.response.status_code == status_code
    return self

  def assert_has_detail(self) -> 'Scorecard':
    assert 'detail' in self.json
    return self

  def assert_category_count(self, count: int) -> 'Scorecard':
    assert len(self.json['entries']) == count
    return self

  def assert_all_scores_null(self) -> 'Scorecard':
    assert all(e['score'] is None for e in self.json['entries'])
    return self

  def assert_bonus_null(self) -> 'Scorecard':
    assert self.json['bonus'] is None
    return self

  def assert_total(self, total: int) -> 'Scorecard':
    assert self.json['total'] == total
    return self

  def assert_score(self, category: str, score: int) -> 'Scorecard':
    entry = next(e for e in self.json['entries'] if e['category'] == category)
    assert entry['score'] == score
    return self
