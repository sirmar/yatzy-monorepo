import aiomysql
from app.player import Player


class PlayerRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

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
    return Player(id=row[0], name=row[1], created_at=row[2])
