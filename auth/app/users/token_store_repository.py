import secrets
import uuid
from datetime import datetime, timedelta, timezone
import aiomysql


class TokenStoreRepository:
  _table: str
  _sql_insert: str
  _sql_consume_update: str
  _sql_consume_select: str
  _sql_latest: str

  def __init_subclass__(cls, **kwargs: object) -> None:
    super().__init_subclass__(**kwargs)
    if hasattr(cls, '_table'):
      t = cls._table
      cls._sql_insert = (
        f'INSERT INTO {t} (id, user_id, token, expires_at) VALUES (%s, %s, %s, %s)'  # nosec B608
      )
      cls._sql_consume_update = f'UPDATE {t} SET used_at = NOW() WHERE token = %s AND used_at IS NULL AND expires_at > NOW()'  # nosec B608
      cls._sql_consume_select = f'SELECT user_id FROM {t} WHERE token = %s'  # nosec B608
      cls._sql_latest = f'SELECT token FROM {t} WHERE user_id = %s AND used_at IS NULL AND expires_at > NOW() ORDER BY created_at DESC LIMIT 1'  # nosec B608

  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def create(self, user_id: str, expire_minutes: int) -> str:
    token = secrets.token_hex(32)
    token_id = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    async with await self._conn.cursor() as cursor:
      await cursor.execute(self._sql_insert, (token_id, user_id, token, expires_at))
    return token

  async def consume(self, token: str) -> str | None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(self._sql_consume_update, (token,))
      if cursor.rowcount == 0:
        return None
      await cursor.execute(self._sql_consume_select, (token,))
      row = await cursor.fetchone()
      return row[0] if row else None

  async def get_latest_token(self, user_id: str) -> str | None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(self._sql_latest, (user_id,))
      row = await cursor.fetchone()
      return row[0] if row else None
