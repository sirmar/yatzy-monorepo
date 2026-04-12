import json
from pathlib import Path
from unittest.mock import patch

from yatzy.credentials import Credentials, clear, load, save


class TestLoad:
  def setup_method(self) -> None:
    self.tmp_path: Path | None = None

  def test_returns_none_when_file_missing(self, tmp_path: Path) -> None:
    self.GivenCredentialsPath(tmp_path / 'missing.json')
    result = self.WhenLoaded()
    self.ThenResultIs(None, result)

  def test_returns_credentials_when_file_exists(self, tmp_path: Path) -> None:
    self.GivenCredentialsFile(
      tmp_path, access_token='acc', refresh_token='ref', player_id=42
    )
    result = self.WhenLoaded()
    self.ThenResultIs(
      Credentials(access_token='acc', refresh_token='ref', player_id=42), result
    )

  def test_returns_none_on_invalid_json(self, tmp_path: Path) -> None:
    self.GivenInvalidCredentialsFile(tmp_path)
    result = self.WhenLoaded()
    self.ThenResultIs(None, result)

  def test_returns_none_on_missing_fields(self, tmp_path: Path) -> None:
    self.GivenCredentialsPath(tmp_path / 'creds.json')
    path = tmp_path / 'creds.json'
    path.write_text(json.dumps({'access_token': 'only_access'}))
    result = self.WhenLoaded()
    self.ThenResultIs(None, result)

  def GivenCredentialsPath(self, path: Path) -> None:
    self._patcher = patch('yatzy.credentials.CREDENTIALS_PATH', path)
    self._patcher.start()

  def GivenCredentialsFile(
    self, tmp_path: Path, access_token: str, refresh_token: str, player_id: int | None
  ) -> None:
    path = tmp_path / 'creds.json'
    path.write_text(
      json.dumps(
        {
          'access_token': access_token,
          'refresh_token': refresh_token,
          'player_id': player_id,
        }
      )
    )
    self.GivenCredentialsPath(path)

  def GivenInvalidCredentialsFile(self, tmp_path: Path) -> None:
    path = tmp_path / 'creds.json'
    path.write_text('not valid json {{{')
    self.GivenCredentialsPath(path)

  def WhenLoaded(self) -> Credentials | None:
    return load()

  def ThenResultIs(
    self, expected: Credentials | None, result: Credentials | None
  ) -> None:
    assert result == expected

  def teardown_method(self) -> None:
    if hasattr(self, '_patcher'):
      self._patcher.stop()


class TestSave:
  def test_creates_file_with_correct_content(self, tmp_path: Path) -> None:
    self.GivenCredentialsPath(tmp_path / 'creds.json')
    creds = Credentials(access_token='acc', refresh_token='ref', player_id=7)
    self.WhenSaved(creds)
    self.ThenFileContains(tmp_path / 'creds.json', creds)

  def test_creates_parent_directory_if_missing(self, tmp_path: Path) -> None:
    nested = tmp_path / 'nested' / 'dir' / 'creds.json'
    self.GivenCredentialsPath(nested)
    creds = Credentials(access_token='acc', refresh_token='ref')
    self.WhenSaved(creds)
    self.ThenFileExists(nested)

  def GivenCredentialsPath(self, path: Path) -> None:
    self._patcher = patch('yatzy.credentials.CREDENTIALS_PATH', path)
    self._patcher.start()

  def WhenSaved(self, creds: Credentials) -> None:
    save(creds)

  def ThenFileContains(self, path: Path, creds: Credentials) -> None:
    data = json.loads(path.read_text())
    assert data['access_token'] == creds.access_token
    assert data['refresh_token'] == creds.refresh_token
    assert data['player_id'] == creds.player_id

  def ThenFileExists(self, path: Path) -> None:
    assert path.exists()

  def teardown_method(self) -> None:
    if hasattr(self, '_patcher'):
      self._patcher.stop()


class TestClear:
  def test_removes_existing_file(self, tmp_path: Path) -> None:
    path = tmp_path / 'creds.json'
    path.write_text('{}')
    self.GivenCredentialsPath(path)
    self.WhenCleared()
    self.ThenFileDoesNotExist(path)

  def test_does_nothing_when_file_missing(self, tmp_path: Path) -> None:
    self.GivenCredentialsPath(tmp_path / 'missing.json')
    self.WhenCleared()

  def GivenCredentialsPath(self, path: Path) -> None:
    self._patcher = patch('yatzy.credentials.CREDENTIALS_PATH', path)
    self._patcher.start()

  def WhenCleared(self) -> None:
    clear()

  def ThenFileDoesNotExist(self, path: Path) -> None:
    assert not path.exists()

  def teardown_method(self) -> None:
    if hasattr(self, '_patcher'):
      self._patcher.stop()
