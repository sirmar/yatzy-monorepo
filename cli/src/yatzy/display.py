from typing import Any

from rich import box as rich_box
from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme


class _HintHighlighter(RegexHighlighter):
  """Highlights key=description hint strings, e.g. 'n=New game'."""

  base_style = 'hint.'
  highlights = [r'(?P<key>[a-zA-Z0-9]+)=(?P<desc>[^  ]+)']


_theme = Theme({'hint.key': 'bold green', 'hint.desc': 'white'})
console = Console(
  highlighter=_HintHighlighter(), theme=_theme, color_system='truecolor'
)

# Each die is rendered as 5 lines of 7 chars: ┌─────┐ / │ · · │ / etc.
DICE_ART: list[list[str]] = [
  ['┌─────┐', '│     │', '│  ●  │', '│     │', '└─────┘'],  # 1
  ['┌─────┐', '│ ●   │', '│     │', '│   ● │', '└─────┘'],  # 2
  ['┌─────┐', '│ ●   │', '│  ●  │', '│   ● │', '└─────┘'],  # 3
  ['┌─────┐', '│ ● ● │', '│     │', '│ ● ● │', '└─────┘'],  # 4
  ['┌─────┐', '│ ● ● │', '│  ●  │', '│ ● ● │', '└─────┘'],  # 5
  ['┌─────┐', '│ ● ● │', '│ ● ● │', '│ ● ● │', '└─────┘'],  # 6
]
DICE_ART_EMPTY: list[str] = ['┌─────┐', '│     │', '│  ?  │', '│     │', '└─────┘']

MODE_NAMES: dict[str, str] = {
  'maxi': 'Maxi Yatzy',
  'maxi_sequential': 'Maxi Yatzy (Sequential)',
  'yatzy': 'Yatzy',
  'yatzy_sequential': 'Yatzy (Sequential)',
}

CATEGORY_NAMES: dict[str, str] = {
  'ones': 'Ones',
  'twos': 'Twos',
  'threes': 'Threes',
  'fours': 'Fours',
  'fives': 'Fives',
  'sixes': 'Sixes',
  'one_pair': 'One Pair',
  'two_pairs': 'Two Pairs',
  'three_pairs': 'Three Pairs',
  'three_of_a_kind': 'Three of a Kind',
  'four_of_a_kind': 'Four of a Kind',
  'five_of_a_kind': 'Five of a Kind',
  'small_straight': 'Small Straight',
  'large_straight': 'Large Straight',
  'full_straight': 'Full Straight',
  'full_house': 'Full House',
  'villa': 'Villa',
  'tower': 'Tower',
  'chance': 'Chance',
  'maxi_yatzy': 'Maxi Yatzy',
  'yatzy': 'Yatzy',
}

UPPER_CATEGORIES = {'ones', 'twos', 'threes', 'fours', 'fives', 'sixes'}


def die_face(value: int | None, kept: bool) -> Text:
  """Single-char representation used in tests."""
  if value is None:
    return Text('?', style='dim')
  style = 'bold green' if kept else 'white'
  return Text(str(value), style=style)


def render_dice(
  dice: list[dict[str, Any]],
  rolls_remaining: int,
  saved_rolls: int,
  mode: str,
) -> None:
  GAP = '  '
  styles = []
  arts = []
  for die in dice:
    value = die.get('value')
    kept = die.get('kept', False)
    arts.append(DICE_ART[value - 1] if value else DICE_ART_EMPTY)
    styles.append('bold #aa7700' if kept else ('dim' if not value else 'white'))

  console.print()
  for row in range(5):
    line = Text()
    for i, (art, style) in enumerate(zip(arts, styles)):
      if i > 0:
        line.append(GAP)
      line.append(art[row], style=style)
    console.print(line)

  index_line = Text()
  for i, die in enumerate(dice):
    if i > 0:
      index_line.append(GAP)
    label = f'   {die["index"] + 1}   '
    index_line.append(label, style='bold green')
  console.print(index_line)
  console.print()
  status = f'Rolls remaining: {rolls_remaining}'
  if mode in ('maxi', 'maxi_sequential') and saved_rolls:
    status += f'  |  Saved rolls: {saved_rolls}'
  console.print(status)
  console.print()


def render_scorecard(
  entries: list[dict[str, Any]],
  bonus: int | None,
  total: int,
  hints: dict[str, int] | None = None,
  category_keys: dict[str, str] | None = None,
) -> None:
  table = Table(
    title='Scorecard', show_header=True, header_style='bold white', style='white'
  )
  table.add_column('Key', style='bold green', width=3)
  table.add_column('Category')
  table.add_column('Score', justify='right')

  upper_scored = sum(
    e['score']
    for e in entries
    if e['category'] in UPPER_CATEGORIES and e.get('score') is not None
  )
  in_lower = False

  for entry in entries:
    cat = entry['category']
    score = entry.get('score')
    name = CATEGORY_NAMES.get(cat, cat)
    key = category_keys.get(cat, '') if category_keys else ''

    if cat not in UPPER_CATEGORIES and not in_lower:
      in_lower = True
      table.add_section()
      table.add_row('', 'Subtotal', str(upper_scored), style='bold')
      if bonus is not None:
        table.add_row('', 'Bonus', str(bonus), style='bold')
      else:
        table.add_row('', 'Bonus', '-', style='bold')
      table.add_section()

    key_text = Text(key, style='bold green')
    if score is not None:
      table.add_row(key_text, name, str(score))
    elif hints is not None and cat in hints:
      hint_val = hints[cat]
      hint_str = str(hint_val) if hint_val > 0 else '0'
      style = 'bold yellow' if hint_val > 0 else 'bright_black'
      table.add_row(key_text, name, hint_str, style=style)
    else:
      table.add_row(key_text, name, '-', style='dim')

  table.add_section()
  table.add_row('', 'Total', str(total), style='bold')
  console.print(table)


def render_all_scorecards(
  scorecards: list[dict[str, Any]],
  player_names: dict[int, str],
  my_player_id: int,
  hints: dict[str, int] | None = None,
  category_keys: dict[str, str] | None = None,
) -> None:
  if not scorecards:
    return

  table = Table(show_header=True, header_style='bold white', style='white')
  table.add_column('Key', style='bold green', width=3)
  table.add_column('Category')
  for sc in scorecards:
    pid = sc['player_id']
    name = player_names.get(pid, f'Player {pid}')
    header = f'{name} (you)' if pid == my_player_id else name
    table.add_column(header, justify='right')

  all_entries = scorecards[0]['entries']

  upper_scored_by_pid = {
    sc['player_id']: sum(
      e['score']
      for e in sc['entries']
      if e['category'] in UPPER_CATEGORIES and e.get('score') is not None
    )
    for sc in scorecards
  }
  in_lower = False

  for entry in all_entries:
    cat = entry['category']
    name = CATEGORY_NAMES.get(cat, cat)
    key = category_keys.get(cat, '') if category_keys else ''

    if cat not in UPPER_CATEGORIES and not in_lower:
      in_lower = True
      subtotals = [
        str(upper_scored_by_pid.get(sc['player_id'], 0)) for sc in scorecards
      ]
      table.add_section()
      table.add_row('', 'Subtotal', *subtotals, style='bold')
      bonus_cells = []
      for sc in scorecards:
        b = sc.get('bonus')
        bonus_cells.append(str(b) if b is not None else '-')
      table.add_row('', 'Bonus', *bonus_cells, style='bold')
      table.add_section()

    cells = []
    row_style = ''
    for sc in scorecards:
      pid = sc['player_id']
      sc_entry = next((e for e in sc['entries'] if e['category'] == cat), None)
      score = sc_entry.get('score') if sc_entry else None
      if score is not None:
        cells.append(str(score))
      elif pid == my_player_id and hints is not None and cat in hints:
        hint_val = hints[cat]
        cells.append(str(hint_val))
        if not row_style:
          row_style = 'bold yellow' if hint_val > 0 else 'bright_black'
      else:
        cells.append('-')
        if not row_style and pid == my_player_id and hints is not None:
          row_style = 'bright_black'

    table.add_row(Text(key, style='bold green'), name, *cells, style=row_style)

  totals = [str(sc['total']) for sc in scorecards]
  table.add_section()
  table.add_row('', 'Total', *totals, style='bold')
  console.print(table)


MODE_BADGE_STYLES: dict[str, str] = {
  'maxi': 'bold bright_white on #005500',
  'maxi_sequential': 'bold bright_white on #664400',
  'yatzy': 'bold bright_white on #00004d',
  'yatzy_sequential': 'bold bright_white on #660000',
}


def render_lobby(
  game: dict[str, Any], player_names: dict[int, str], my_player_id: int | None = None
) -> None:
  mode_key = game.get('mode', '')
  mode = MODE_NAMES.get(mode_key, mode_key)
  badge_style = MODE_BADGE_STYLES.get(mode_key, 'bold white')
  badge = Text(f' {mode} ', style=badge_style)
  header = Text(f'\nGame #{game["id"]} — ', style='bold')
  header.append_text(badge)
  console.print(header)
  console.print('Players:')
  creator_id = game.get('creator_id')
  for pid in game.get('player_ids', []):
    name = player_names.get(pid, f'Player {pid}')
    is_me = pid == my_player_id
    is_creator = pid == creator_id
    marker = ' (creator)' if is_creator else ''
    if is_me:
      console.print(f'  • [bold yellow]{name}[/bold yellow]{marker}')
    elif is_creator:
      console.print(f'  • [bold white]{name}[/bold white]{marker}')
    else:
      console.print(f'  • {name}{marker}')
  console.print()


_ACTION_LABELS: dict[str, str] = {
  'j': 'Join',
  'l': 'Leave',
  'd': 'Delete',
  's': 'Start',
}


def _game_actions(game: dict[str, Any], my_player_id: int | None) -> list[str]:
  if my_player_id is None or game.get('status') == 'active':
    return []
  in_game = my_player_id in game.get('player_ids', [])
  is_creator = game.get('creator_id') == my_player_id
  if not in_game:
    return ['j']
  return ['s', 'd'] if is_creator else ['l']


def render_game_list(
  games: list[dict[str, Any]],
  player_names: dict[int, str] | None = None,
  start: int = 1,
  my_player_id: int | None = None,
  selected: int | None = None,
) -> None:
  if not games:
    console.print('  No open games.', style='bright_black')
    return
  for i, game in enumerate(games, start=start):
    mode_key = game.get('mode', '')
    mode = MODE_NAMES.get(mode_key, mode_key)
    badge_style = MODE_BADGE_STYLES.get(mode_key, 'bold white')
    creator_id = game.get('creator_id')
    player_ids: list[int] = game.get('player_ids', [])
    is_selected = selected is not None and (i - 1) == selected

    header = Text()
    header.append(f'{i}', style='bold green')
    header.append(f'. Game #{game["id"]}  ', style='bold white')
    header.append(f' {mode} ', style=badge_style)
    if my_player_id is not None and creator_id == my_player_id:
      header.append('  ')
      header.append(' yours ', style='bold bright_white on #444400')
    names = [(player_names or {}).get(pid, f'Player {pid}') for pid in player_ids]
    players_line = Text(', '.join(names), style='bright_black')
    body = Text('\n').join([header, players_line])

    if is_selected:
      actions = _game_actions(game, my_player_id)
      subtitle: Text | None = None
      if actions:
        subtitle = Text()
        for idx2, k in enumerate(actions):
          if idx2 > 0:
            subtitle.append('  ')
          subtitle.append(k, style='bold green')
          subtitle.append(f'={_ACTION_LABELS[k]}', style='white')
      console.print(
        Panel(
          body,
          box=rich_box.ROUNDED,
          width=80,
          border_style='bold bright_white',
          subtitle=subtitle,
          subtitle_align='right',
        )
      )
    else:
      console.print(Panel(body, box=rich_box.ROUNDED, width=80, border_style='#444444'))


def render_final_scores(
  scoreboard: list[dict[str, Any]], winner_ids: list[int], player_names: dict[int, str]
) -> None:
  table = Table(
    title='Final Scores', show_header=True, header_style='bold white', style='white'
  )
  table.add_column('Player')
  table.add_column('Score', justify='right')

  sorted_board = sorted(scoreboard, key=lambda s: -s['total'])
  for entry in sorted_board:
    pid = entry['player_id']
    name = player_names.get(pid, f'Player {pid}')
    is_winner = pid in winner_ids
    style = 'bold green' if is_winner else ''
    trophy = ' 🏆' if is_winner else ''
    table.add_row(f'{name}{trophy}', str(entry['total']), style=style)

  console.print()
  console.print(table)


def error(msg: str) -> None:
  console.print(f'[red]Error:[/red] {msg}')


def info(msg: str) -> None:
  console.print(msg, style='white')
