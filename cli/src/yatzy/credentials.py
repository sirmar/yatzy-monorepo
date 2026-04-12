import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

CREDENTIALS_PATH = Path(
  os.environ.get('YATZY_CREDENTIALS', str(Path.home() / '.yatzy' / 'credentials.json'))
)


@dataclass
class Credentials:
  access_token: str
  refresh_token: str
  player_id: int | None = None


def load() -> Credentials | None:
  if not CREDENTIALS_PATH.exists():
    return None
  try:
    data = json.loads(CREDENTIALS_PATH.read_text())
    return Credentials(**data)
  except Exception:
    return None


def save(creds: Credentials) -> None:
  CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
  CREDENTIALS_PATH.write_text(json.dumps(asdict(creds)))


def clear() -> None:
  if CREDENTIALS_PATH.exists():
    CREDENTIALS_PATH.unlink()
