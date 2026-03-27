import hashlib
import uuid
from datetime import datetime, timedelta, timezone
import aiomysql


class TokenRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  def _hash(self, token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

  async def create(self, user_id: str, expire_days: int) -> str:
    token = str(uuid.uuid4())
    token_id = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=expire_days)
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'INSERT INTO refresh_tokens (id, user_id, token_hash, expires_at) VALUES (%s, %s, %s, %s)',
        (token_id, user_id, self._hash(token), expires_at),
      )
    return token

  async def consume(self, token: str) -> str | None:
    token_hash = self._hash(token)
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'UPDATE refresh_tokens SET revoked_at = NOW() '
        'WHERE token_hash = %s AND revoked_at IS NULL AND expires_at > NOW()',
        (token_hash,),
      )
      if cursor.rowcount == 0:
        return None
      await cursor.execute(
        'SELECT user_id FROM refresh_tokens WHERE token_hash = %s',
        (token_hash,),
      )
      row = await cursor.fetchone()
      return row[0] if row else None

  async def revoke(self, token: str) -> None:
    token_hash = self._hash(token)
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'UPDATE refresh_tokens SET revoked_at = NOW() '
        'WHERE token_hash = %s AND revoked_at IS NULL',
        (token_hash,),
      )

  async def revoke_all_for_user(self, user_id: str) -> None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'UPDATE refresh_tokens SET revoked_at = NOW() '
        'WHERE user_id = %s AND revoked_at IS NULL',
        (user_id,),
      )
