import threading
from collections.abc import Callable
from io import StringIO
from typing import Any

from prompt_toolkit import prompt
from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.key_binding import DynamicKeyBindings, KeyBindings, KeyPressEvent
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from rich.console import Console

import yatzy.display as _display

_render_lock = threading.Lock()


def render_to_ansi(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
  buf = StringIO()
  tmp = Console(
    file=buf,
    no_color=False,
    force_terminal=True,
    color_system='truecolor',
    width=120,
    highlighter=_display._HintHighlighter(),
    theme=_display._theme,
  )
  with _render_lock:
    orig = _display.console
    _display.console = tmp
    try:
      fn(*args, **kwargs)
    finally:
      _display.console = orig
  return buf.getvalue()


def input_prompt(message: str, is_password: bool = False) -> str:
  """Plain prompt — only for use BEFORE app.start()."""
  return prompt(message, is_password=is_password)


class _TuiApp:
  """Single long-lived prompt_toolkit Application.

  Screens are swapped in place via set_screen(); the Application never restarts,
  so there is no flicker between screens.
  """

  def __init__(self) -> None:
    self._get_content: Callable[[], str] = lambda: ''
    self._bindings: dict[str, Callable[[], None]] = {}
    self._bindings_lock = threading.Lock()
    self._app: Application[None] | None = None

  def _build_app(self) -> Application[None]:
    def get_kb() -> KeyBindings:
      kb = KeyBindings()
      with self._bindings_lock:
        current = dict(self._bindings)
      for key, cb in current.items():

        def _handler(event: KeyPressEvent, _cb: Callable[[], None] = cb) -> None:
          _cb()

        kb.add(key)(_handler)
      return kb

    content_control = FormattedTextControl(lambda: ANSI(self._get_content()))
    layout = Layout(Window(content=content_control, wrap_lines=True))
    return Application(
      layout=layout,
      key_bindings=DynamicKeyBindings(get_kb),
      full_screen=True,
    )

  def start(self) -> None:
    self._app = self._build_app()
    t = threading.Thread(target=self._app.run, daemon=True)
    t.start()

  def set_screen(
    self,
    get_content: Callable[[], str],
    bindings: dict[str, Callable[[], None]],
  ) -> None:
    with self._bindings_lock:
      self._get_content = get_content
      self._bindings = bindings
    if self._app:
      self._app.invalidate()

  def invalidate(self) -> None:
    if self._app:
      self._app.invalidate()

  def exit(self) -> None:
    if self._app:
      self._app.exit()


app = _TuiApp()
