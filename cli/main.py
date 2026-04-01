import sys
import threading
from collections.abc import Callable

from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import ANSI

from yatzy import credentials as creds_module
from yatzy import display
from yatzy.api import ApiClient, ApiError, SseListener
from yatzy.auth import AuthClient, AuthError
from yatzy.credentials import Credentials
from yatzy.game import GameSession
from yatzy.ui import app, input_prompt, render_to_ansi

MODES = list(display.MODE_NAMES.items())


def login_flow(auth: AuthClient) -> Credentials:
  while True:
    display.info('\n[bold]Yatzy CLI[/bold]')
    display.info('1. Login')
    display.info('2. Register')
    choice = input_prompt('Choice (1/2): ')

    email = input_prompt('Email: ')
    password = input_prompt('Password: ', is_password=True)

    try:
      if choice.strip() == '1':
        creds = auth.login(email, password)
        return creds
      else:
        auth.register(email, password)
        display.info(
          'Registration successful. Check your email to verify your account.'
        )
        display.info('Once verified, choose Login.')
    except AuthError as e:
      display.error(str(e))


def ensure_player(api: ApiClient) -> int:
  try:
    player = api.get_my_player()
    return int(player['id'])
  except ApiError as e:
    if e.status_code != 404:
      raise
  display.info('\nNo player profile found. Create one to continue.')
  name = input_prompt('Player name (1-64 characters): ')
  player = api.create_player(name)
  display.info(f'Player [bold]{player["name"]}[/bold] created!')
  return int(player['id'])


def _fetch_lobby_state(
  api: ApiClient, player_id: int
) -> tuple[list[dict], dict[int, str]]:
  try:
    lobby_games = api.list_games(status='lobby')
    active_games = [
      g for g in api.list_games(status='active') if player_id in g.get('player_ids', [])
    ]
  except ApiError:
    lobby_games = []
    active_games = []

  joined_lobbies = [g for g in lobby_games if player_id in g.get('player_ids', [])]
  open_lobbies = [g for g in lobby_games if g not in joined_lobbies]
  games = active_games + joined_lobbies + open_lobbies

  all_pids: set[int] = set()
  for g in games:
    all_pids.update(g.get('player_ids', []))
  player_names: dict[int, str] = {}
  for pid in all_pids:
    try:
      player_names[pid] = api.get_player(pid)['name']
    except ApiError:
      player_names[pid] = f'Player {pid}'

  return games, player_names


def main_menu(api: ApiClient, player_id: int) -> None:
  selected_holder: list[int] = [0]

  while True:
    player_name_holder: list[str] = [f'Player {player_id}']
    games_holder: list[list[dict]] = [[]]
    player_names_holder: list[dict[int, str]] = [{}]
    lock = threading.Lock()
    action_holder: list[str] = ['']
    done = threading.Event()

    try:
      player = api.get_player(player_id)
      player_name_holder[0] = player['name']
    except ApiError:
      pass

    games, player_names = _fetch_lobby_state(api, player_id)
    with lock:
      games_holder[0] = games
      player_names_holder[0] = player_names

    def get_content() -> str:
      with lock:
        current_games = games_holder[0]
        pnames = player_names_holder[0]
        pname = player_name_holder[0]

      my_active = [
        g
        for g in current_games
        if g.get('status') == 'active' and player_id in g.get('player_ids', [])
      ]
      my_lobbies = [
        g
        for g in current_games
        if g.get('status') == 'lobby' and player_id in g.get('player_ids', [])
      ]
      open_lobby = [
        g for g in current_games if g not in my_active and g not in my_lobbies
      ]

      sel = selected_holder[0]

      def _render() -> None:
        display.info(f'Yatzy CLI — {pname}\n')
        if my_active:
          display.info('Active games:')
          display.render_game_list(
            my_active, pnames, start=1, my_player_id=player_id, selected=sel
          )
        if my_lobbies:
          offset = len(my_active)
          display.info('\nJoined games:' if my_active else 'Joined games:')
          display.render_game_list(
            my_lobbies, pnames, start=offset + 1, my_player_id=player_id, selected=sel
          )
        if open_lobby:
          offset = len(my_active) + len(my_lobbies)
          display.info('\nOpen games:' if (my_active or my_lobbies) else 'Open games:')
          display.render_game_list(
            open_lobby, pnames, start=offset + 1, my_player_id=player_id, selected=sel
          )
        if not current_games:
          display.info('No games available.')
        display.info('\nn=New game  q=Quit')

      return render_to_ansi(_render)

    def make_game_handler(index: int) -> Callable[[], None]:
      def handler() -> None:
        action_holder[0] = str(index)
        done.set()

      return handler

    def handle_up() -> None:
      with lock:
        selected_holder[0] = max(0, selected_holder[0] - 1)
      app.invalidate()

    def handle_down() -> None:
      with lock:
        n = len(games_holder[0])
        selected_holder[0] = min(max(n - 1, 0), selected_holder[0] + 1)
      app.invalidate()

    def handle_enter() -> None:
      with lock:
        idx = selected_holder[0]
        current = games_holder[0]
      if not current:
        return
      action_holder[0] = str(idx + 1)
      done.set()

    def handle_new() -> None:
      action_holder[0] = 'n'
      done.set()

    def handle_quit() -> None:
      action_holder[0] = 'q'
      done.set()

    def handle_join() -> None:
      with lock:
        idx = selected_holder[0]
        current = games_holder[0]
      if idx >= len(current):
        return
      game = current[idx]
      if player_id in game.get('player_ids', []) or game.get('status') == 'active':
        return

      def do_join() -> None:
        try:
          api.join_game(game['id'], player_id)
        except ApiError:
          pass
        action_holder[0] = 'refresh'
        done.set()

      threading.Thread(target=do_join, daemon=True).start()

    def handle_leave() -> None:
      with lock:
        idx = selected_holder[0]
        current = games_holder[0]
      if idx >= len(current):
        return
      game = current[idx]
      if player_id not in game.get('player_ids', []) or game.get('status') == 'active':
        return

      def do_leave() -> None:
        try:
          api.leave_game(game['id'], player_id)
        except ApiError:
          pass
        action_holder[0] = 'refresh'
        done.set()

      threading.Thread(target=do_leave, daemon=True).start()

    def handle_delete() -> None:
      with lock:
        idx = selected_holder[0]
        current = games_holder[0]
      if idx >= len(current):
        return
      game = current[idx]
      if game.get('creator_id') != player_id or game.get('status') == 'active':
        return

      def do_delete() -> None:
        try:
          api.delete_game(game['id'])
        except ApiError:
          pass
        action_holder[0] = 'refresh'
        done.set()

      threading.Thread(target=do_delete, daemon=True).start()

    def handle_start() -> None:
      with lock:
        idx = selected_holder[0]
        current = games_holder[0]
      if idx >= len(current):
        return
      game = current[idx]
      if game.get('creator_id') != player_id or game.get('status') == 'active':
        return

      def do_start() -> None:
        try:
          api.start_game(game['id'], player_id)
        except ApiError:
          return
        action_holder[0] = str(idx + 1)
        done.set()

      threading.Thread(target=do_start, daemon=True).start()

    key_bindings: dict[str, Callable[[], None]] = {
      'n': handle_new,
      'q': handle_quit,
      'up': handle_up,
      'down': handle_down,
      'enter': handle_enter,
      'j': handle_join,
      'l': handle_leave,
      'd': handle_delete,
      's': handle_start,
    }
    for i in range(1, min(len(games) + 1, 10)):
      key_bindings[str(i)] = make_game_handler(i)

    def on_lobby_event() -> None:
      try:
        new_games, new_names = _fetch_lobby_state(api, player_id)
        new_active = [g for g in new_games if g.get('status') == 'active']
        with lock:
          old_lobby_ids = {
            g['id'] for g in games_holder[0] if g.get('status') == 'lobby'
          }
          games_holder[0] = new_games
          player_names_holder[0] = new_names
          selected_holder[0] = min(selected_holder[0], max(len(new_games) - 1, 0))
        # Auto-enter if a game we were in lobby for just became active
        for g in new_active:
          if g['id'] in old_lobby_ids and not done.is_set():
            action_holder[0] = str(new_games.index(g) + 1)
            done.set()
            return
      except ApiError:
        pass
      app.invalidate()

    sse = SseListener(api.sse_lobby_url(), api.current_token, on_lobby_event)
    app.set_screen(get_content, key_bindings)
    sse.start()
    done.wait()
    sse.stop()

    action = action_holder[0]

    if action == 'q':
      app.exit()
      return

    if action == 'refresh':
      continue

    if action == 'n':
      game_id = create_game_flow(api, player_id)
      if game_id:
        run_game(api, game_id, player_id)
      continue

    try:
      game_index = int(action) - 1
    except ValueError:
      continue

    if game_index < 0 or game_index >= len(games):
      continue

    game = games[game_index]
    game_id = game['id']
    if player_id not in game.get('player_ids', []):
      try:
        api.join_game(game_id, player_id)
      except ApiError as e:
        print_formatted_text(ANSI(f'\x1b[31mError: {e}\x1b[0m'))
        continue
    run_game(api, game_id, player_id)


def create_game_flow(api: ApiClient, player_id: int) -> int | None:
  result_holder: list[int | None] = [None]
  done = threading.Event()

  def get_content() -> str:
    def _render() -> None:
      display.info('Choose game mode:\n')
      for i, (_, name) in enumerate(MODES, start=1):
        display.info(f'  {i}. {name}')
      display.info('\n  q. Cancel')

    return render_to_ansi(_render)

  def make_mode_handler(mode_key: str) -> Callable[[], None]:
    def handler() -> None:
      try:
        game = api.create_game(player_id, mode_key)
        result_holder[0] = int(game['id'])
      except Exception:
        result_holder[0] = None
      done.set()

    return handler

  def handle_cancel() -> None:
    done.set()

  key_bindings: dict[str, Callable[[], None]] = {'q': handle_cancel}
  for i, (mode_key, _) in enumerate(MODES, start=1):
    key_bindings[str(i)] = make_mode_handler(mode_key)

  app.set_screen(get_content, key_bindings)
  done.wait()
  return result_holder[0]


def run_game(api: ApiClient, game_id: int, player_id: int) -> None:
  try:
    game = api.get_game(game_id)
    if game.get('status') != 'active':
      return
    mode = game.get('mode', 'maxi')
    session = GameSession(api, game_id, player_id, mode)
    session.run()
  except ApiError as e:
    print_formatted_text(ANSI(f'\x1b[31mError: {e}\x1b[0m'))


def main() -> None:
  auth = AuthClient()
  creds = creds_module.load()

  if creds is None:
    creds = login_flow(auth)

  api = ApiClient(creds, auth)

  try:
    player_id = ensure_player(api)
  except ApiError as e:
    if e.status_code == 401:
      creds_module.clear()
      display.error('Session expired. Please log in again.')
      creds = login_flow(auth)
      api = ApiClient(creds, auth)
      player_id = ensure_player(api)
    else:
      display.error(str(e))
      sys.exit(1)

  creds.player_id = player_id
  creds_module.save(creds)

  app.start()

  try:
    main_menu(api, player_id)
  finally:
    api.close()
    auth.close()


if __name__ == '__main__':
  main()
