from io import StringIO

from rich.console import Console

from yatzy.display import CATEGORY_NAMES, MODE_NAMES, die_face, render_dice


def capture(fn: object, *args: object, **kwargs: object) -> str:
  buf = StringIO()
  test_console = Console(file=buf, no_color=True, width=120)
  import yatzy.display as disp

  orig = disp.console
  disp.console = test_console
  try:
    fn(*args, **kwargs)  # type: ignore[operator]
  finally:
    disp.console = orig
  return buf.getvalue()


class TestDieFace:
  def test_unrolled_die_is_dim(self) -> None:
    text = die_face(None, False)
    self.ThenStyleContains(text, 'dim')

  def test_kept_die_is_green(self) -> None:
    text = die_face(3, True)
    self.ThenStyleContains(text, 'green')

  def test_unkept_die_is_white(self) -> None:
    text = die_face(5, False)
    self.ThenStyleContains(text, 'white')

  def test_die_value_maps_to_correct_face(self) -> None:
    for value in range(1, 7):
      text = die_face(value, False)
      self.ThenTextContainsFace(text, value)

  def ThenStyleContains(self, text: object, expected_style: str) -> None:
    from rich.text import Text

    assert isinstance(text, Text)
    assert expected_style in text.style

  def ThenTextContainsFace(self, text: object, value: int) -> None:
    from rich.text import Text

    assert isinstance(text, Text)
    assert str(value) in text.plain


class TestRenderDice:
  def test_shows_rolls_remaining(self) -> None:
    dice = [{'index': i, 'value': i + 1, 'kept': False} for i in range(6)]
    self.GivenDice(dice)
    output = self.WhenRendered(rolls_remaining=2, saved_rolls=0, mode='maxi')
    self.ThenOutputContains(output, 'Rolls remaining: 2')

  def test_shows_saved_rolls_for_maxi(self) -> None:
    dice = [{'index': i, 'value': i + 1, 'kept': False} for i in range(6)]
    self.GivenDice(dice)
    output = self.WhenRendered(rolls_remaining=1, saved_rolls=3, mode='maxi')
    self.ThenOutputContains(output, 'Saved rolls: 3')

  def test_hides_saved_rolls_for_yatzy_mode(self) -> None:
    dice = [{'index': i, 'value': i + 1, 'kept': False} for i in range(6)]
    self.GivenDice(dice)
    output = self.WhenRendered(rolls_remaining=1, saved_rolls=2, mode='yatzy')
    self.ThenOutputDoesNotContain(output, 'Saved rolls')

  def GivenDice(self, dice: list) -> None:
    self._dice = dice

  def WhenRendered(self, rolls_remaining: int, saved_rolls: int, mode: str) -> str:
    return capture(render_dice, self._dice, rolls_remaining, saved_rolls, mode)

  def ThenOutputContains(self, output: str, expected: str) -> None:
    assert expected in output

  def ThenOutputDoesNotContain(self, output: str, unexpected: str) -> None:
    assert unexpected not in output


class TestConstants:
  def test_all_modes_have_names(self) -> None:
    for mode in ('maxi', 'maxi_sequential', 'yatzy', 'yatzy_sequential'):
      assert mode in MODE_NAMES

  def test_all_categories_have_names(self) -> None:
    categories = [
      'ones',
      'twos',
      'threes',
      'fours',
      'fives',
      'sixes',
      'one_pair',
      'two_pairs',
      'three_pairs',
      'three_of_a_kind',
      'four_of_a_kind',
      'five_of_a_kind',
      'small_straight',
      'large_straight',
      'full_straight',
      'full_house',
      'villa',
      'tower',
      'chance',
      'maxi_yatzy',
      'yatzy',
    ]
    for cat in categories:
      assert cat in CATEGORY_NAMES
