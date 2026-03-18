import aiomysql
from app.player import Player


class PlayerRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  def _to_player(self, row: tuple) -> Player:
    return Player(id=row[0], name=row[1], created_at=row[2])

  async def create(self, name: str) -> Player:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'INSERT INTO players (name) VALUES (%s)',
        (name,),
      )
      player_id = cursor.lastrowid
      await cursor.execute(
        'SELECT id, name, created_at FROM players WHERE id = %s AND deleted_at IS NULL',
        (player_id,),
      )
      row = await cursor.fetchone()
      return self._to_player(row)
    finally:
      await cursor.close()

  async def list_all(self) -> list[Player]:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'SELECT id, name, created_at FROM players WHERE deleted_at IS NULL ORDER BY id',
      )
      rows = await cursor.fetchall()
      return [self._to_player(row) for row in rows]
    finally:
      await cursor.close()

  async def get_by_id(self, player_id: int) -> Player | None:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'SELECT id, name, created_at FROM players WHERE id = %s AND deleted_at IS NULL',
        (player_id,),
      )
      row = await cursor.fetchone()
      if row is None:
        return None
      return self._to_player(row)
    finally:
      await cursor.close()

  async def update(self, player_id: int, name: str) -> Player | None:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'UPDATE players SET name = %s WHERE id = %s AND deleted_at IS NULL',
        (name, player_id),
      )
      if cursor.rowcount == 0:
        return None
      await cursor.execute(
        'SELECT id, name, created_at FROM players WHERE id = %s AND deleted_at IS NULL',
        (player_id,),
      )
      row = await cursor.fetchone()
      return self._to_player(row)
    finally:
      await cursor.close()

  async def delete(self, player_id: int) -> bool:
    cursor = await self._conn.cursor()
    try:
      await cursor.execute(
        'UPDATE players SET deleted_at = NOW() WHERE id = %s AND deleted_at IS NULL',
        (player_id,),
      )
      return cursor.rowcount > 0
    finally:
      await cursor.close()
