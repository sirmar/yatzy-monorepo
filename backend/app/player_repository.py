import aiomysql
from app.player import Player


class PlayerRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  def _to_player(self, row: tuple) -> Player:
    return Player(id=row[0], name=row[1], created_at=row[2])

  async def create(self, name: str) -> Player:
    cursor = await self._conn.cursor()
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
    await cursor.close()
    return self._to_player(row)

  async def list_all(self) -> list[Player]:
    cursor = await self._conn.cursor()
    await cursor.execute(
      'SELECT id, name, created_at FROM players WHERE deleted_at IS NULL ORDER BY id',
    )
    rows = await cursor.fetchall()
    await cursor.close()
    return [self._to_player(row) for row in rows]

  async def get_by_id(self, player_id: int) -> Player | None:
    cursor = await self._conn.cursor()
    await cursor.execute(
      'SELECT id, name, created_at FROM players WHERE id = %s AND deleted_at IS NULL',
      (player_id,),
    )
    row = await cursor.fetchone()
    await cursor.close()
    if row is None:
      return None
    return self._to_player(row)

  async def update(self, player_id: int, name: str) -> Player | None:
    cursor = await self._conn.cursor()
    await cursor.execute(
      'UPDATE players SET name = %s WHERE id = %s AND deleted_at IS NULL',
      (name, player_id),
    )
    if cursor.rowcount == 0:
      await cursor.close()
      return None
    await cursor.execute(
      'SELECT id, name, created_at FROM players WHERE id = %s AND deleted_at IS NULL',
      (player_id,),
    )
    row = await cursor.fetchone()
    await cursor.close()
    return self._to_player(row)

  async def delete(self, player_id: int) -> bool | None:
    cursor = await self._conn.cursor()
    await cursor.execute(
      'UPDATE players SET deleted_at = NOW() WHERE id = %s AND deleted_at IS NULL',
      (player_id,),
    )
    affected = cursor.rowcount
    await cursor.close()
    if affected == 0:
      return None
    return True
