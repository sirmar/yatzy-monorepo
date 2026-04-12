from enum import StrEnum


class GameStatus(StrEnum):
  LOBBY = 'lobby'
  ACTIVE = 'active'
  FINISHED = 'finished'
  ABANDONED = 'abandoned'
