import aiomysql
from app.players.player import Player


class PlayerRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  def _to_player(self, row: tuple) -> Player:
    return Player(id=row[0], account_id=row[1], name=row[2], created_at=row[3])

  async def create(self, account_id: str, name: str) -> Player:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'INSERT INTO players (account_id, name) VALUES (%s, %s)',
        (account_id, name),
      )
      player_id = cursor.lastrowid
      await cursor.execute(
        'SELECT id, account_id, name, created_at FROM players WHERE id = %s AND deleted_at IS NULL',
        (player_id,),
      )
      row = await cursor.fetchone()
      return self._to_player(row)

  async def list_all(self) -> list[Player]:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'SELECT id, account_id, name, created_at FROM players WHERE deleted_at IS NULL ORDER BY id',
      )
      rows = await cursor.fetchall()
      return [self._to_player(row) for row in rows]

  async def get_by_id(self, player_id: int) -> Player | None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'SELECT id, account_id, name, created_at FROM players WHERE id = %s AND deleted_at IS NULL',
        (player_id,),
      )
      row = await cursor.fetchone()
      if row is None:
        return None
      return self._to_player(row)

  async def get_by_account_id(self, account_id: str) -> Player | None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'SELECT id, account_id, name, created_at FROM players WHERE account_id = %s AND deleted_at IS NULL',
        (account_id,),
      )
      row = await cursor.fetchone()
      if row is None:
        return None
      return self._to_player(row)

  async def update(self, player_id: int, name: str) -> Player | None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'UPDATE players SET name = %s WHERE id = %s AND deleted_at IS NULL',
        (name, player_id),
      )
      if cursor.rowcount == 0:
        return None
      await cursor.execute(
        'SELECT id, account_id, name, created_at FROM players WHERE id = %s AND deleted_at IS NULL',
        (player_id,),
      )
      row = await cursor.fetchone()
      return self._to_player(row)

  async def delete(self, player_id: int) -> bool:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'UPDATE players SET deleted_at = NOW() WHERE id = %s AND deleted_at IS NULL',
        (player_id,),
      )
      return cursor.rowcount > 0
