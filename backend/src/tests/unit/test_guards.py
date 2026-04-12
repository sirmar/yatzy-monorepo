from datetime import datetime
import pytest
from fastapi import HTTPException
from app.games.guards import (
  assert_game_exists,
  assert_game_active,
  assert_game_in_lobby,
  assert_game_deletable,
  assert_player_in_game,
  assert_player_not_in_game,
  assert_game_not_full,
  assert_is_creator,
  assert_turn_active,
  assert_current_player,
  assert_rolls_remaining,
  assert_has_rolled,
)
from app.games.game import Game
from app.games.game_mode import GameMode
from app.games.game_status import GameStatus


def make_game(**kwargs) -> Game:
  defaults = dict(
    id=1,
    status=GameStatus.LOBBY,
    mode=GameMode.MAXI,
    creator_id=10,
    player_ids=[10],
    created_at=datetime(2024, 1, 1),
    started_at=None,
    ended_at=None,
  )
  return Game(**{**defaults, **kwargs})


class TestAssertGameExists:
  def test_returns_game_when_present(self):
    self.WhenAsserted(make_game())
    self.ThenGameIsReturned()

  def test_raises_404_when_none(self):
    self.ThenRaises404(lambda: assert_game_exists(None))

  def WhenAsserted(self, game):
    self.result = assert_game_exists(game)

  def ThenGameIsReturned(self):
    assert self.result is not None

  def ThenRaises404(self, fn):
    with pytest.raises(HTTPException) as exc:
      fn()
    assert exc.value.status_code == 404


class TestAssertGameActive:
  def test_passes_when_active(self):
    assert_game_active(make_game(status=GameStatus.ACTIVE))

  def test_raises_409_when_lobby(self):
    self.ThenRaises409(lambda: assert_game_active(make_game(status=GameStatus.LOBBY)))

  def test_raises_409_when_finished(self):
    self.ThenRaises409(
      lambda: assert_game_active(make_game(status=GameStatus.FINISHED))
    )

  def ThenRaises409(self, fn):
    with pytest.raises(HTTPException) as exc:
      fn()
    assert exc.value.status_code == 409


class TestAssertGameInLobby:
  def test_passes_when_lobby(self):
    assert_game_in_lobby(make_game(status=GameStatus.LOBBY))

  def test_raises_409_when_active(self):
    self.ThenRaises409(
      lambda: assert_game_in_lobby(make_game(status=GameStatus.ACTIVE))
    )

  def test_raises_409_when_finished(self):
    self.ThenRaises409(
      lambda: assert_game_in_lobby(make_game(status=GameStatus.FINISHED))
    )

  def ThenRaises409(self, fn):
    with pytest.raises(HTTPException) as exc:
      fn()
    assert exc.value.status_code == 409


class TestAssertGameDeletable:
  def test_passes_when_lobby(self):
    assert_game_deletable(make_game(status=GameStatus.LOBBY))

  def test_passes_when_finished(self):
    assert_game_deletable(make_game(status=GameStatus.FINISHED))

  def test_raises_409_when_active(self):
    with pytest.raises(HTTPException) as exc:
      assert_game_deletable(make_game(status=GameStatus.ACTIVE))
    assert exc.value.status_code == 409


class TestAssertPlayerInGame:
  def test_passes_when_player_in_game(self):
    assert_player_in_game(make_game(player_ids=[10, 20]), 20)

  def test_raises_404_when_player_not_in_game(self):
    with pytest.raises(HTTPException) as exc:
      assert_player_in_game(make_game(player_ids=[10]), 99)
    assert exc.value.status_code == 404


class TestAssertPlayerNotInGame:
  def test_passes_when_player_not_in_game(self):
    assert_player_not_in_game(make_game(player_ids=[10]), 99)

  def test_raises_409_when_player_already_in_game(self):
    with pytest.raises(HTTPException) as exc:
      assert_player_not_in_game(make_game(player_ids=[10, 20]), 20)
    assert exc.value.status_code == 409


class TestAssertGameNotFull:
  def test_passes_when_fewer_than_six_players(self):
    assert_game_not_full(make_game(player_ids=[1, 2, 3, 4, 5]))

  def test_raises_409_when_six_players(self):
    with pytest.raises(HTTPException) as exc:
      assert_game_not_full(make_game(player_ids=[1, 2, 3, 4, 5, 6]))
    assert exc.value.status_code == 409


class TestAssertIsCreator:
  def test_passes_when_player_is_creator(self):
    assert_is_creator(make_game(creator_id=10), 10)

  def test_raises_403_when_not_creator(self):
    with pytest.raises(HTTPException) as exc:
      assert_is_creator(make_game(creator_id=10), 99)
    assert exc.value.status_code == 403


class TestAssertTurnActive:
  def test_returns_turn_info_when_present(self):
    self.WhenAsserted((1, 2, 3, 4))
    self.ThenTurnInfoIsReturned((1, 2, 3, 4))

  def test_raises_409_when_none(self):
    with pytest.raises(HTTPException) as exc:
      assert_turn_active(None)
    assert exc.value.status_code == 409

  def WhenAsserted(self, turn_info):
    self.result = assert_turn_active(turn_info)

  def ThenTurnInfoIsReturned(self, expected):
    assert self.result == expected


class TestAssertCurrentPlayer:
  def test_passes_when_player_matches(self):
    assert_current_player(10, 10)

  def test_raises_403_when_not_current_player(self):
    with pytest.raises(HTTPException) as exc:
      assert_current_player(10, 99)
    assert exc.value.status_code == 403


class TestAssertRollsRemaining:
  def test_passes_when_regular_rolls_available(self):
    assert_rolls_remaining(rolls_remaining=2, saved_rolls=0)

  def test_passes_when_only_saved_rolls_available(self):
    assert_rolls_remaining(rolls_remaining=0, saved_rolls=2)

  def test_raises_409_when_no_rolls_of_any_kind(self):
    with pytest.raises(HTTPException) as exc:
      assert_rolls_remaining(rolls_remaining=0, saved_rolls=0)
    assert exc.value.status_code == 409


class TestAssertHasRolled:
  def test_passes_when_rolled_at_least_once(self):
    assert_has_rolled(rolls_remaining=2)

  def test_raises_409_when_not_yet_rolled(self):
    with pytest.raises(HTTPException) as exc:
      assert_has_rolled(rolls_remaining=3)
    assert exc.value.status_code == 409
