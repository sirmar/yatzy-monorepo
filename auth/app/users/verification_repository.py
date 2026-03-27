import secrets
import uuid
from datetime import datetime, timedelta, timezone
import aiomysql


class VerificationRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  async def create(self, user_id: str, expire_minutes: int) -> str:
    token = secrets.token_hex(32)
    token_id = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'INSERT INTO email_verifications (id, user_id, token, expires_at) VALUES (%s, %s, %s, %s)',
        (token_id, user_id, token, expires_at),
      )
    return token

  async def consume(self, token: str) -> str | None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'UPDATE email_verifications SET used_at = NOW() '
        'WHERE token = %s AND used_at IS NULL AND expires_at > NOW()',
        (token,),
      )
      if cursor.rowcount == 0:
        return None
      await cursor.execute(
        'SELECT user_id FROM email_verifications WHERE token = %s',
        (token,),
      )
      row = await cursor.fetchone()
      return row[0] if row else None

  async def get_latest_token(self, user_id: str) -> str | None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'SELECT token FROM email_verifications '
        'WHERE user_id = %s AND used_at IS NULL AND expires_at > NOW() '
        'ORDER BY created_at DESC LIMIT 1',
        (user_id,),
      )
      row = await cursor.fetchone()
      return row[0] if row else None
