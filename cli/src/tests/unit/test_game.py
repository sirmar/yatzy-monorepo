import threading
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

from yatzy.api import ApiClient, ApiError
from yatzy.game import GameSession


def make_session(
  player_id: int = 1,
  game_id: int = 10,
  mode: str = 'sequential',
) -> tuple[GameSession, MagicMock]:
  api = MagicMock(spec=ApiClient)
  session = GameSession(api, game_id, player_id, mode)
  return session, api


def make_scorecard(entries: list[dict[str, Any]] | None = None) -> dict[str, Any]:
  if entries is None:
    entries = [{'category': 'ones'}, {'category': 'twos'}, {'category': 'threes'}]
  return {'entries': entries, 'bonus': None, 'total': 0}


class TestBuildCategoryKeys:
  def test_assigns_letters_in_order(self) -> None:
    session, _ = make_session()
    entries = [{'category': 'ones'}, {'category': 'twos'}, {'category': 'threes'}]
    result = session._build_category_keys(entries)
    assert result == {'ones': 'a', 'twos': 'b', 'threes': 'c'}

  def test_empty_entries_returns_empty_dict(self) -> None:
    session, _ = make_session()
    assert session._build_category_keys([]) == {}

  def test_stops_at_26_entries(self) -> None:
    session, _ = make_session()
    entries = [{'category': f'cat_{i}'} for i in range(30)]
    result = session._build_category_keys(entries)
    assert len(result) == 26
    assert 'z' in result.values()


class TestFetchPlayerNames:
  def test_returns_names_for_all_players(self) -> None:
    session, api = make_session()
    api.get_player.side_effect = [
      {'name': 'Alice'},
      {'name': 'Bob'},
    ]
    result = session._fetch_player_names([1, 2])
    assert result == {1: 'Alice', 2: 'Bob'}

  def test_falls_back_to_player_id_on_api_error(self) -> None:
    session, api = make_session()
    api.get_player.side_effect = ApiError(404, 'Not found')
    result = session._fetch_player_names([99])
    assert result == {99: 'Player 99'}

  def test_partial_failure_uses_fallback_for_failed_only(self) -> None:
    session, api = make_session()
    api.get_player.side_effect = [
      {'name': 'Alice'},
      ApiError(404, 'Not found'),
    ]
    result = session._fetch_player_names([1, 2])
    assert result == {1: 'Alice', 2: 'Player 2'}

  def test_empty_player_ids_returns_empty_dict(self) -> None:
    session, api = make_session()
    result = session._fetch_player_names([])
    assert result == {}
    api.get_player.assert_not_called()


class TestFetchAllScorecards:
  def test_returns_scorecards_with_player_id_injected(self) -> None:
    session, api = make_session()
    sc1 = {'entries': [], 'total': 0}
    sc2 = {'entries': [], 'total': 5}
    api.get_scorecard.side_effect = [sc1, sc2]
    result = session._fetch_all_scorecards([1, 2])
    assert result[0]['player_id'] == 1
    assert result[1]['player_id'] == 2

  def test_skips_player_on_api_error(self) -> None:
    session, api = make_session()
    api.get_scorecard.side_effect = [
      ApiError(404, 'Not found'),
      {'entries': [], 'total': 0},
    ]
    result = session._fetch_all_scorecards([1, 2])
    assert len(result) == 1
    assert result[0]['player_id'] == 2

  def test_empty_player_ids_returns_empty_list(self) -> None:
    session, api = make_session()
    result = session._fetch_all_scorecards([])
    assert result == []
    api.get_scorecard.assert_not_called()


class TestRun:
  def test_calls_show_final_scores_when_game_not_active(self) -> None:
    session, api = make_session(player_id=1)
    api.get_game.return_value = {'creator_id': 1, 'player_ids': [1]}
    api.get_game_state.return_value = {'status': 'finished', 'dice': []}
    api.get_player.return_value = {'name': 'Alice'}
    api.get_scorecard.return_value = make_scorecard()
    api.get_scoreboard.return_value = [{'player_id': 1, 'total': 50}]

    with patch('yatzy.game.app') as mock_app:
      mock_app.set_screen = MagicMock()
      session.run()

    api.get_scoreboard.assert_called_once_with(10)

  def test_my_turn_calls_run_my_turn(self) -> None:
    session, api = make_session(player_id=1)
    api.get_game.return_value = {'creator_id': 2, 'player_ids': [1]}
    api.get_player.return_value = {'name': 'Alice'}

    active_state = {
      'status': 'active',
      'current_player_id': 1,
      'dice': [],
      'rolls_remaining': 3,
      'saved_rolls': 0,
    }
    finished_state = {'status': 'finished', 'dice': []}

    api.get_game_state.side_effect = [active_state, finished_state]
    api.get_scorecard.return_value = make_scorecard()
    api.get_scoring_options.return_value = []
    api.get_scoreboard.return_value = [{'player_id': 1, 'total': 0}]

    turn_done = threading.Event()

    def fake_set_screen(get_content: Callable, bindings: dict) -> None:
      turn_done.set()

    with patch('yatzy.game.app') as mock_app:
      mock_app.set_screen.side_effect = fake_set_screen
      mock_app.invalidate = MagicMock()

      def trigger_quit() -> None:
        turn_done.wait(timeout=2)
        with patch.object(session, '_show_final_scores'):
          bindings = mock_app.set_screen.call_args[0][1]
          bindings['q']()

      t = threading.Thread(target=trigger_quit, daemon=True)
      t.start()
      session.run()

  def test_other_players_turn_calls_wait(self) -> None:
    session, api = make_session(player_id=1)
    api.get_game.return_value = {'creator_id': 2, 'player_ids': [1, 2]}
    api.get_player.return_value = {'name': 'Alice'}

    active_state = {
      'status': 'active',
      'current_player_id': 2,
      'dice': [],
      'rolls_remaining': 3,
      'saved_rolls': 0,
    }

    api.get_game_state.return_value = active_state
    api.get_scorecard.return_value = make_scorecard()
    api.get_scoreboard.return_value = [{'player_id': 1, 'total': 0}]

    with (
      patch.object(
        session, '_wait_for_my_turn', return_value=(True, active_state)
      ) as mock_wait,
      patch('yatzy.game.app'),
    ):
      session.run()

    mock_wait.assert_called_once()


class TestRunMyTurn:
  def _run_my_turn_with_action(
    self,
    session: GameSession,
    api: MagicMock,
    state: dict[str, Any],
    action: Callable[[dict[str, Callable]], None],
    is_creator: bool = False,
  ) -> bool:
    done = threading.Event()
    result: list[bool] = []

    def fake_set_screen(get_content: Callable, bindings: dict) -> None:
      action(bindings)

    with patch('yatzy.game.app') as mock_app:
      mock_app.set_screen.side_effect = fake_set_screen
      mock_app.invalidate = MagicMock()

      def run() -> None:
        result.append(session._run_my_turn(state, is_creator, [1], {1: 'Alice'}))
        done.set()

      t = threading.Thread(target=run, daemon=True)
      t.start()
      done.wait(timeout=3)

    return result[0] if result else False

  def test_quit_returns_true(self) -> None:
    session, api = make_session(player_id=1)
    api.get_scorecard.return_value = make_scorecard()
    api.get_scoring_options.return_value = []

    state = {'dice': [], 'rolls_remaining': 3, 'saved_rolls': 0}
    result = self._run_my_turn_with_action(session, api, state, lambda b: b['q']())
    assert result is True

  def test_toggle_keep_adds_and_removes_die(self) -> None:
    session, api = make_session(player_id=1)
    dice = [{'index': i, 'value': i + 1, 'kept': False} for i in range(6)]
    api.get_scorecard.return_value = make_scorecard()
    api.get_scoring_options.return_value = []

    state = {'dice': dice, 'rolls_remaining': 2, 'saved_rolls': 0}

    def press_1_then_quit(bindings: dict) -> None:
      bindings['1']()
      bindings['1']()
      bindings['q']()

    self._run_my_turn_with_action(session, api, state, press_1_then_quit)

  def test_score_category_ends_turn(self) -> None:
    session, api = make_session(player_id=1)
    dice = [{'index': i, 'value': i + 1, 'kept': False} for i in range(6)]
    api.get_scorecard.return_value = make_scorecard()
    api.get_scoring_options.return_value = []
    api.score_category.return_value = {}

    state = {'dice': dice, 'rolls_remaining': 0, 'saved_rolls': 0}
    result = self._run_my_turn_with_action(session, api, state, lambda b: b['a']())

    assert not result
    api.score_category.assert_called_once_with(10, 1, 'ones')

  def test_abort_game_returns_true(self) -> None:
    session, api = make_session(player_id=1)
    api.get_scorecard.return_value = make_scorecard()
    api.get_scoring_options.return_value = []
    api.abort_game.return_value = {}

    state = {'dice': [], 'rolls_remaining': 3, 'saved_rolls': 0}
    result = self._run_my_turn_with_action(
      session, api, state, lambda b: b['x'](), is_creator=True
    )

    assert result is True
    api.abort_game.assert_called_once_with(10)


class TestWaitForMyTurn:
  def test_quit_returns_true_with_current_state(self) -> None:
    session, api = make_session(player_id=1)
    state = {
      'status': 'active',
      'current_player_id': 2,
      'dice': [],
      'rolls_remaining': 3,
      'saved_rolls': 0,
    }
    api.get_scorecard.return_value = make_scorecard()

    with (
      patch('yatzy.game.app') as mock_app,
      patch('yatzy.game.SseListener') as mock_sse_cls,
    ):
      mock_app.set_screen.side_effect = lambda gc, b: b['q']()
      mock_app.invalidate = MagicMock()
      mock_sse_cls.return_value = MagicMock()

      quit_flag, returned_state = session._wait_for_my_turn(
        state, [1, 2], {1: 'Me', 2: 'Other'}
      )

    assert quit_flag is True
    assert returned_state == state

  def test_sse_event_updates_state_and_signals_done_when_my_turn(self) -> None:
    session, api = make_session(player_id=1)
    initial_state = {
      'status': 'active',
      'current_player_id': 2,
      'dice': [],
      'rolls_remaining': 3,
      'saved_rolls': 0,
    }
    my_turn_state = {
      'status': 'active',
      'current_player_id': 1,
      'dice': [],
      'rolls_remaining': 3,
      'saved_rolls': 0,
    }
    api.get_game_state.return_value = my_turn_state
    api.get_scorecard.return_value = make_scorecard()

    callback_captured: threading.Event = threading.Event()
    captured_callback: list[Callable] = []

    def capture_sse(url: str, token: Any, callback: Callable) -> MagicMock:
      captured_callback.append(callback)
      callback_captured.set()
      return MagicMock()

    result: list[tuple] = []
    finished = threading.Event()

    with (
      patch('yatzy.game.app') as mock_app,
      patch('yatzy.game.SseListener') as mock_sse_cls,
    ):
      mock_app.set_screen = MagicMock()
      mock_app.invalidate = MagicMock()
      mock_sse_cls.side_effect = capture_sse

      def run() -> None:
        result.append(
          session._wait_for_my_turn(initial_state, [1, 2], {1: 'Me', 2: 'Other'})
        )
        finished.set()

      t = threading.Thread(target=run, daemon=True)
      t.start()

      callback_captured.wait(timeout=2)
      captured_callback[0]()
      finished.wait(timeout=3)

    assert len(result) == 1
    quit_flag, returned_state = result[0]
    assert quit_flag is False
    assert returned_state == my_turn_state
