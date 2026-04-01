import random
import threading
import time
from collections.abc import Callable
from typing import Any

from yatzy import display
from yatzy.api import ApiClient, ApiError, SseListener
from yatzy.ui import app, render_to_ansi


class GameSession:
  def __init__(self, api: ApiClient, game_id: int, player_id: int, mode: str) -> None:
    self._api = api
    self._game_id = game_id
    self._player_id = player_id
    self._mode = mode

  def run(self) -> None:
    game = self._api.get_game(self._game_id)
    is_creator = game.get('creator_id') == self._player_id
    player_ids: list[int] = game.get('player_ids', [])
    player_names = self._fetch_player_names(player_ids)
    state = self._api.get_game_state(self._game_id)

    while state.get('status') == 'active':
      if state.get('current_player_id') == self._player_id:
        quit_game = self._run_my_turn(state, is_creator, player_ids, player_names)
        if quit_game:
          return
        state = self._api.get_game_state(self._game_id)
      else:
        quit_game, state = self._wait_for_my_turn(state, player_ids, player_names)
        if quit_game:
          return

    self._show_final_scores(state)

  def _build_category_keys(self, entries: list[dict[str, Any]]) -> dict[str, str]:
    letters = 'abcdefghijklmnopqrstuvwxyz'
    return {
      e['category']: letters[i] for i, e in enumerate(entries) if i < len(letters)
    }

  def _render_turn(
    self,
    dice: list[dict[str, Any]],
    rolls_remaining: int,
    saved_rolls: int,
    scorecards: list[dict[str, Any]],
    player_names: dict[int, str],
    hints: dict[str, int] | None,
    category_keys: dict[str, str],
    is_creator: bool,
  ) -> str:
    def _render() -> None:
      display.render_dice(dice, rolls_remaining, saved_rolls, self._mode)
      display.render_all_scorecards(
        scorecards, player_names, self._player_id, hints, category_keys
      )
      controls = 'Enter=Roll  1-6=Toggle keep  letter=Score  q=Menu'
      if is_creator:
        controls += '  x=Abandon game'
      display.info(controls)

    return render_to_ansi(_render)

  def _run_my_turn(
    self,
    state: dict[str, Any],
    is_creator: bool,
    player_ids: list[int],
    player_names: dict[int, str],
  ) -> bool:
    lock = threading.Lock()
    turn_done = threading.Event()
    quit_flag: list[bool] = [False]

    my_scorecard = self._api.get_scorecard(self._game_id, self._player_id)
    my_scorecard['player_id'] = self._player_id
    all_scorecards = self._fetch_all_scorecards(player_ids)

    s: dict[str, Any] = {
      'dice': state.get('dice') or [],
      'has_rolled': any(d.get('value') is not None for d in (state.get('dice') or [])),
      'local_kept': set(),
      'rolls_remaining': state.get('rolls_remaining') or 0,
      'saved_rolls': state.get('saved_rolls') or 0,
      'hints': None,
      'scorecards': all_scorecards,
      'my_scorecard': my_scorecard,
      'category_keys': {},
      'key_to_category': {},
      'busy': False,
    }
    s['category_keys'] = self._build_category_keys(my_scorecard['entries'])
    s['key_to_category'] = {v: k for k, v in s['category_keys'].items()}
    s['local_kept'] = {d['index'] for d in s['dice'] if d.get('kept')}

    if s['has_rolled']:
      hints_list = self._api.get_scoring_options(self._game_id, self._player_id)
      s['hints'] = {opt['category']: opt['score'] for opt in hints_list}

    def get_content() -> str:
      with lock:
        dice = [dict(d, kept=(d['index'] in s['local_kept'])) for d in s['dice']]
        return self._render_turn(
          dice,
          s['rolls_remaining'],
          s['saved_rolls'],
          s['scorecards'],
          player_names,
          s['hints'],
          s['category_keys'],
          is_creator,
        )

    def make_digit_handler(digit: int) -> Callable[[], None]:
      def handler() -> None:
        actual_index = digit - 1
        with lock:
          if s['busy']:
            return
          if actual_index in s['local_kept']:
            s['local_kept'].discard(actual_index)
          else:
            s['local_kept'].add(actual_index)
        app.invalidate()

      return handler

    def handle_roll() -> None:
      with lock:
        if s['busy'] or not (s['rolls_remaining'] > 0 or s['saved_rolls'] > 0):
          return
        s['busy'] = True
        kept = list(s['local_kept'])

      def do_roll() -> None:
        anim_stop = threading.Event()

        def _animate() -> None:
          while not anim_stop.is_set():
            with lock:
              s['dice'] = [
                {**d, 'value': random.randint(1, 6)} if d['index'] not in kept else d
                for d in (
                  s['dice']
                  or [{'index': i, 'value': None, 'kept': False} for i in range(6)]
                )
              ]
            app.invalidate()
            time.sleep(0.07)

        threading.Thread(target=_animate, daemon=True).start()
        try:
          roll_result = self._api.roll_dice(self._game_id, self._player_id, kept)
          anim_stop.set()
          new_state = self._api.get_game_state(self._game_id)
          hints_list = self._api.get_scoring_options(self._game_id, self._player_id)
          new_sc = self._api.get_scorecard(self._game_id, self._player_id)
          new_sc['player_id'] = self._player_id
          new_all = self._fetch_all_scorecards(player_ids)
          with lock:
            s['dice'] = roll_result['dice']
            s['has_rolled'] = True
            s['local_kept'] = {d['index'] for d in roll_result['dice'] if d.get('kept')}
            s['rolls_remaining'] = new_state.get('rolls_remaining') or 0
            s['saved_rolls'] = new_state.get('saved_rolls') or 0
            s['hints'] = {opt['category']: opt['score'] for opt in hints_list}
            s['scorecards'] = new_all
            s['my_scorecard'] = new_sc
            s['category_keys'] = self._build_category_keys(new_sc['entries'])
            s['key_to_category'] = {v: k for k, v in s['category_keys'].items()}
            s['busy'] = False
        except ApiError:
          anim_stop.set()
          with lock:
            s['busy'] = False
        app.invalidate()

      threading.Thread(target=do_roll, daemon=True).start()

    def make_letter_handler(letter: str) -> Callable[[], None]:
      def handler() -> None:
        with lock:
          if s['busy'] or not s['has_rolled']:
            return
          category = s['key_to_category'].get(letter)
          if not category:
            return
          s['busy'] = True

        def do_score() -> None:
          try:
            self._api.score_category(self._game_id, self._player_id, category)
          except ApiError:
            with lock:
              s['busy'] = False
            return
          turn_done.set()

        threading.Thread(target=do_score, daemon=True).start()

      return handler

    def handle_quit() -> None:
      quit_flag[0] = True
      turn_done.set()

    def handle_delete() -> None:
      def do_abort() -> None:
        try:
          self._api.abort_game(self._game_id)
        except ApiError:
          pass
        quit_flag[0] = True
        turn_done.set()

      threading.Thread(target=do_abort, daemon=True).start()

    bindings: dict[str, Callable[[], None]] = {'enter': handle_roll, 'q': handle_quit}
    if is_creator:
      bindings['x'] = handle_delete
    for digit in range(1, 7):
      bindings[str(digit)] = make_digit_handler(digit)
    reserved = {'q', 'x'}
    for letter in 'abcdefghijklmnopqrstuvwxyz':
      if letter not in reserved:
        bindings[letter] = make_letter_handler(letter)

    app.set_screen(get_content, bindings)
    turn_done.wait()
    return quit_flag[0]

  def _wait_for_my_turn(
    self,
    state: dict[str, Any],
    player_ids: list[int],
    player_names: dict[int, str],
  ) -> tuple[bool, dict[str, Any]]:
    state_holder: list[dict[str, Any]] = [state]
    scorecards_holder: list[list[dict[str, Any]]] = [
      self._fetch_all_scorecards(player_ids)
    ]
    done = threading.Event()
    quit_flag: list[bool] = [False]
    lock = threading.Lock()

    def get_content() -> str:
      with lock:
        current_state = state_holder[0]
        scorecards = scorecards_holder[0]
      current_pid: int | None = current_state.get('current_player_id')
      current_name = (
        player_names.get(current_pid, f'Player {current_pid}')
        if current_pid
        else 'unknown'
      )
      dice: list[dict[str, Any]] = current_state.get('dice') or []
      rolls_remaining: int = current_state.get('rolls_remaining') or 0
      saved_rolls: int = current_state.get('saved_rolls') or 0

      def _render() -> None:
        display.info(f'Waiting for {current_name}...  q=Menu')
        display.render_dice(dice, rolls_remaining, saved_rolls, self._mode)
        display.render_all_scorecards(scorecards, player_names, self._player_id)

      return render_to_ansi(_render)

    def handle_quit() -> None:
      quit_flag[0] = True
      done.set()

    app.set_screen(get_content, {'q': handle_quit})

    def on_event() -> None:
      try:
        new_state = self._api.get_game_state(self._game_id)
        new_scorecards = self._fetch_all_scorecards(player_ids)
      except ApiError:
        return
      with lock:
        state_holder[0] = new_state
        scorecards_holder[0] = new_scorecards
      app.invalidate()
      if (
        new_state.get('current_player_id') == self._player_id
        or new_state.get('status') != 'active'
      ):
        done.set()

    sse = SseListener(
      self._api.sse_game_url(self._game_id), self._api.current_token, on_event
    )
    sse.start()
    done.wait()
    sse.stop()

    with lock:
      return quit_flag[0], state_holder[0]

  def _show_final_scores(self, state: dict[str, Any]) -> None:
    scoreboard = self._api.get_scoreboard(self._game_id)
    winner_ids: list[int] = state.get('winner_ids') or []
    all_player_ids = [entry['player_id'] for entry in scoreboard]
    player_names = self._fetch_player_names(all_player_ids)
    app.set_screen(
      lambda: render_to_ansi(
        display.render_final_scores, scoreboard, winner_ids, player_names
      ),
      {},
    )

  def _fetch_all_scorecards(self, player_ids: list[int]) -> list[dict[str, Any]]:
    scorecards = []
    for pid in player_ids:
      try:
        sc = self._api.get_scorecard(self._game_id, pid)
        sc['player_id'] = pid
        scorecards.append(sc)
      except ApiError:
        pass
    return scorecards

  def _fetch_player_names(self, player_ids: list[int]) -> dict[int, str]:
    names: dict[int, str] = {}
    for pid in player_ids:
      try:
        p = self._api.get_player(pid)
        names[pid] = p['name']
      except ApiError:
        names[pid] = f'Player {pid}'
    return names
