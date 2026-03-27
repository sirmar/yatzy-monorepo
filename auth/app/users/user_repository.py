import uuid
import aiomysql
from app.users.user import User


class UserRepository:
  def __init__(self, conn: aiomysql.Connection) -> None:
    self._conn = conn

  def _to_user(self, row: tuple) -> User:
    return User(
      id=row[0], email=row[1], email_verified=row[2] is not None, created_at=row[3]
    )

  async def create(self, email: str, password_hash: str) -> User:
    user_id = str(uuid.uuid4())
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'INSERT INTO users (id, email, password_hash) VALUES (%s, %s, %s)',
        (user_id, email, password_hash),
      )
      await cursor.execute(
        'SELECT id, email, email_verified_at, created_at FROM users WHERE id = %s AND deleted_at IS NULL',
        (user_id,),
      )
      row = await cursor.fetchone()
      return self._to_user(row)

  async def find_by_email(self, email: str) -> tuple[User, str] | None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'SELECT id, email, email_verified_at, created_at, password_hash FROM users WHERE email = %s AND deleted_at IS NULL',
        (email,),
      )
      row = await cursor.fetchone()
      if row is None:
        return None
      return self._to_user(row[:4]), row[4]

  async def get_by_id(self, user_id: str) -> User | None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'SELECT id, email, email_verified_at, created_at FROM users WHERE id = %s AND deleted_at IS NULL',
        (user_id,),
      )
      row = await cursor.fetchone()
      if row is None:
        return None
      return self._to_user(row)

  async def get_by_id_with_hash(self, user_id: str) -> tuple[User, str] | None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'SELECT id, email, email_verified_at, created_at, password_hash FROM users WHERE id = %s AND deleted_at IS NULL',
        (user_id,),
      )
      row = await cursor.fetchone()
      if row is None:
        return None
      return self._to_user(row[:4]), row[4]

  async def set_email_verified(self, user_id: str) -> None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'UPDATE users SET email_verified_at = NOW() WHERE id = %s AND deleted_at IS NULL AND email_verified_at IS NULL',
        (user_id,),
      )

  async def update_password(self, user_id: str, password_hash: str) -> None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'UPDATE users SET password_hash = %s WHERE id = %s AND deleted_at IS NULL',
        (password_hash, user_id),
      )

  async def delete(self, user_id: str) -> None:
    async with await self._conn.cursor() as cursor:
      await cursor.execute(
        'UPDATE users SET deleted_at = NOW() WHERE id = %s AND deleted_at IS NULL',
        (user_id,),
      )
