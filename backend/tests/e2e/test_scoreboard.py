from httpx import AsyncClient
from tests.e2e.scoreboard import Scoreboard
from tests.e2e.helpers import active_game_two_players


async def test_scoreboard_returns_200(client: AsyncClient):
  p1, p2, game = await active_game_two_players(client)
  sb = await Scoreboard(client).get(game.id)
  sb.assert_status(200)


async def test_scoreboard_returns_scorecard_per_player(client: AsyncClient):
  p1, p2, game = await active_game_two_players(client)
  sb = await Scoreboard(client).get(game.id)
  sb.assert_player_count(2).assert_has_entries_for_player(p1.id).assert_has_entries_for_player(p2.id)


async def test_scoreboard_game_not_found_returns_404(client: AsyncClient):
  sb = await Scoreboard(client).get(999)
  sb.assert_status(404).assert_has_detail()
