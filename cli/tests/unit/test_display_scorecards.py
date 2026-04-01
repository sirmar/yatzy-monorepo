from io import StringIO

from rich.console import Console

import yatzy.display as disp
from yatzy.display import (
  render_all_scorecards,
  render_final_scores,
  render_game_list,
  render_lobby,
  render_scorecard,
)


def capture(fn: object, *args: object, **kwargs: object) -> str:
  buf = StringIO()
  test_console = Console(file=buf, no_color=True, width=120)
  orig = disp.console
  disp.console = test_console
  try:
    fn(*args, **kwargs)  # type: ignore[operator]
  finally:
    disp.console = orig
  return buf.getvalue()


def make_upper_entries(scores: dict[str, int | None] | None = None) -> list[dict]:
  cats = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
  sc = scores or {}
  return [{'category': c, 'score': sc.get(c)} for c in cats]


def make_entries(
  upper_scores: dict[str, int | None] | None = None,
  lower_scores: dict[str, int | None] | None = None,
) -> list[dict]:
  upper = make_upper_entries(upper_scores or {})
  lower_cats = ['one_pair', 'full_house', 'chance']
  lower = [{'category': c, 'score': (lower_scores or {}).get(c)} for c in lower_cats]
  return upper + lower


# ---------------------------------------------------------------------------
# render_scorecard
# ---------------------------------------------------------------------------


class TestRenderScorecard:
  def test_shows_total(self) -> None:
    entries = make_entries()
    output = capture(render_scorecard, entries, bonus=None, total=42)
    assert '42' in output

  def test_shows_scored_value(self) -> None:
    entries = make_entries(upper_scores={'ones': 3})
    output = capture(render_scorecard, entries, bonus=None, total=3)
    assert '3' in output

  def test_shows_dash_for_unscored_without_hints(self) -> None:
    entries = make_entries()
    output = capture(render_scorecard, entries, bonus=None, total=0)
    assert '-' in output

  def test_shows_hint_for_unscored_category(self) -> None:
    entries = make_entries()
    hints = {'ones': 4, 'twos': 0}
    output = capture(render_scorecard, entries, bonus=None, total=0, hints=hints)
    assert '4' in output

  def test_shows_subtotal_before_lower_section(self) -> None:
    entries = make_entries(upper_scores={'ones': 3, 'twos': 6})
    output = capture(render_scorecard, entries, bonus=None, total=9)
    assert 'Subtotal' in output
    subtotal_pos = output.find('Subtotal')
    ones_pos = output.find('Ones')
    chance_pos = output.find('Chance')
    assert ones_pos < subtotal_pos < chance_pos

  def test_shows_bonus_when_set(self) -> None:
    entries = make_entries(upper_scores={'ones': 3})
    output = capture(render_scorecard, entries, bonus=100, total=103)
    assert 'Bonus' in output
    assert '100' in output

  def test_shows_dash_for_bonus_when_none(self) -> None:
    entries = make_entries()
    output = capture(render_scorecard, entries, bonus=None, total=0)
    assert 'Bonus' in output

  def test_shows_category_key_when_provided(self) -> None:
    entries = make_entries()
    keys = {'ones': 'a', 'twos': 'b', 'threes': 'c', 'fours': 'd', 'fives': 'e', 'sixes': 'f',
            'one_pair': 'g', 'full_house': 'h', 'chance': 'i'}
    output = capture(render_scorecard, entries, bonus=None, total=0, category_keys=keys)
    assert 'a' in output


# ---------------------------------------------------------------------------
# render_all_scorecards
# ---------------------------------------------------------------------------


class TestRenderAllScorecards:
  def _make_scorecard(
    self,
    player_id: int,
    upper_scores: dict[str, int | None] | None = None,
    bonus: int | None = None,
    total: int = 0,
  ) -> dict:
    return {
      'player_id': player_id,
      'entries': make_entries(upper_scores),
      'bonus': bonus,
      'total': total,
    }

  def test_shows_player_name_in_header(self) -> None:
    sc = self._make_scorecard(1)
    output = capture(render_all_scorecards, [sc], {1: 'Alice'}, my_player_id=1)
    assert 'Alice' in output

  def test_marks_current_player_with_you(self) -> None:
    sc = self._make_scorecard(1)
    output = capture(render_all_scorecards, [sc], {1: 'Alice'}, my_player_id=1)
    assert '(you)' in output

  def test_does_not_mark_other_player_with_you(self) -> None:
    sc = self._make_scorecard(2)
    output = capture(render_all_scorecards, [sc], {2: 'Bob'}, my_player_id=1)
    assert '(you)' not in output

  def test_shows_multiple_player_columns(self) -> None:
    sc_a = self._make_scorecard(1)
    sc_b = self._make_scorecard(2)
    output = capture(
      render_all_scorecards, [sc_a, sc_b], {1: 'Alice', 2: 'Bob'}, my_player_id=1
    )
    assert 'Alice' in output
    assert 'Bob' in output

  def test_shows_scored_value_for_player(self) -> None:
    sc = self._make_scorecard(1, upper_scores={'ones': 5}, total=5)
    output = capture(render_all_scorecards, [sc], {1: 'Alice'}, my_player_id=1)
    assert '5' in output

  def test_shows_hint_for_my_player(self) -> None:
    sc = self._make_scorecard(1)
    hints = {'ones': 4}
    output = capture(
      render_all_scorecards, [sc], {1: 'Alice'}, my_player_id=1, hints=hints
    )
    assert '4' in output

  def test_shows_subtotal_and_bonus_rows(self) -> None:
    sc = self._make_scorecard(1, upper_scores={'ones': 3}, bonus=None, total=3)
    output = capture(render_all_scorecards, [sc], {1: 'Alice'}, my_player_id=1)
    assert 'Subtotal' in output
    assert 'Bonus' in output

  def test_shows_total_row(self) -> None:
    sc = self._make_scorecard(1, total=77)
    output = capture(render_all_scorecards, [sc], {1: 'Alice'}, my_player_id=1)
    assert 'Total' in output
    assert '77' in output

  def test_returns_nothing_for_empty_list(self) -> None:
    output = capture(render_all_scorecards, [], {}, my_player_id=1)
    assert output.strip() == ''

  def test_fallback_name_when_missing_from_dict(self) -> None:
    sc = self._make_scorecard(99)
    output = capture(render_all_scorecards, [sc], {}, my_player_id=1)
    assert 'Player 99' in output


# ---------------------------------------------------------------------------
# render_game_list
# ---------------------------------------------------------------------------


class TestRenderGameList:
  def _make_game(
    self,
    game_id: int = 1,
    mode: str = 'maxi',
    status: str = 'lobby',
    creator_id: int = 1,
    player_ids: list[int] | None = None,
  ) -> dict:
    return {
      'id': game_id,
      'mode': mode,
      'status': status,
      'creator_id': creator_id,
      'player_ids': player_ids or [creator_id],
    }

  def test_shows_game_id(self) -> None:
    game = self._make_game(game_id=42)
    output = capture(render_game_list, [game])
    assert '42' in output

  def test_shows_mode_name(self) -> None:
    game = self._make_game(mode='maxi')
    output = capture(render_game_list, [game])
    assert 'Maxi Yatzy' in output

  def test_shows_player_names(self) -> None:
    game = self._make_game(player_ids=[1, 2])
    output = capture(render_game_list, [game], player_names={1: 'Alice', 2: 'Bob'})
    assert 'Alice' in output
    assert 'Bob' in output

  def test_shows_yours_badge_for_creator(self) -> None:
    game = self._make_game(creator_id=5)
    output = capture(render_game_list, [game], my_player_id=5)
    assert 'yours' in output

  def test_does_not_show_yours_for_non_creator(self) -> None:
    game = self._make_game(creator_id=5)
    output = capture(render_game_list, [game], my_player_id=9)
    assert 'yours' not in output

  def test_numbers_from_start_parameter(self) -> None:
    game = self._make_game(game_id=1)
    output = capture(render_game_list, [game], start=3)
    assert '3' in output

  def test_shows_no_open_games_when_empty(self) -> None:
    output = capture(render_game_list, [])
    assert 'No open games' in output

  def test_selected_game_shows_join_action_for_non_member(self) -> None:
    game = self._make_game(creator_id=1, player_ids=[1])
    output = capture(render_game_list, [game], my_player_id=9, selected=0)
    assert 'Join' in output

  def test_selected_game_shows_start_and_delete_for_creator(self) -> None:
    game = self._make_game(creator_id=5, player_ids=[5])
    output = capture(render_game_list, [game], my_player_id=5, selected=0)
    assert 'Start' in output
    assert 'Delete' in output

  def test_selected_game_shows_leave_for_non_creator_member(self) -> None:
    game = self._make_game(creator_id=1, player_ids=[1, 7])
    output = capture(render_game_list, [game], my_player_id=7, selected=0)
    assert 'Leave' in output

  def test_active_game_shows_no_actions(self) -> None:
    game = self._make_game(status='active', creator_id=1, player_ids=[1, 2])
    output = capture(render_game_list, [game], my_player_id=1, selected=0)
    assert 'Join' not in output
    assert 'Delete' not in output


# ---------------------------------------------------------------------------
# render_final_scores
# ---------------------------------------------------------------------------


class TestRenderFinalScores:
  def test_shows_player_names(self) -> None:
    board = [{'player_id': 1, 'total': 200}, {'player_id': 2, 'total': 150}]
    output = capture(render_final_scores, board, [1], {1: 'Alice', 2: 'Bob'})
    assert 'Alice' in output
    assert 'Bob' in output

  def test_shows_scores(self) -> None:
    board = [{'player_id': 1, 'total': 200}, {'player_id': 2, 'total': 150}]
    output = capture(render_final_scores, board, [1], {1: 'Alice', 2: 'Bob'})
    assert '200' in output
    assert '150' in output

  def test_winner_appears_before_loser(self) -> None:
    board = [{'player_id': 2, 'total': 150}, {'player_id': 1, 'total': 200}]
    output = capture(render_final_scores, board, [1], {1: 'Alice', 2: 'Bob'})
    alice_pos = output.find('Alice')
    bob_pos = output.find('Bob')
    assert alice_pos < bob_pos

  def test_shows_trophy_for_winner(self) -> None:
    board = [{'player_id': 1, 'total': 200}]
    output = capture(render_final_scores, board, [1], {1: 'Alice'})
    assert '🏆' in output

  def test_no_trophy_for_loser(self) -> None:
    board = [{'player_id': 1, 'total': 200}, {'player_id': 2, 'total': 100}]
    output = capture(render_final_scores, board, [1], {1: 'Alice', 2: 'Bob'})
    assert output.count('🏆') == 1

  def test_fallback_name_when_missing(self) -> None:
    board = [{'player_id': 99, 'total': 50}]
    output = capture(render_final_scores, board, [], {})
    assert 'Player 99' in output


# ---------------------------------------------------------------------------
# render_lobby
# ---------------------------------------------------------------------------


class TestRenderLobby:
  def _make_game(self, creator_id: int = 1, player_ids: list[int] | None = None) -> dict:
    return {
      'id': 10,
      'mode': 'maxi',
      'creator_id': creator_id,
      'player_ids': player_ids or [creator_id],
    }

  def test_shows_game_id(self) -> None:
    game = self._make_game()
    output = capture(render_lobby, game, {1: 'Alice'})
    assert '10' in output

  def test_shows_mode_name(self) -> None:
    game = self._make_game()
    output = capture(render_lobby, game, {1: 'Alice'})
    assert 'Maxi Yatzy' in output

  def test_shows_player_names(self) -> None:
    game = self._make_game(creator_id=1, player_ids=[1, 2])
    output = capture(render_lobby, game, {1: 'Alice', 2: 'Bob'})
    assert 'Alice' in output
    assert 'Bob' in output

  def test_marks_creator(self) -> None:
    game = self._make_game(creator_id=1, player_ids=[1, 2])
    output = capture(render_lobby, game, {1: 'Alice', 2: 'Bob'})
    assert '(creator)' in output

  def test_does_not_mark_non_creator(self) -> None:
    game = self._make_game(creator_id=1, player_ids=[1, 2])
    output = capture(render_lobby, game, {1: 'Alice', 2: 'Bob'})
    assert output.count('(creator)') == 1
