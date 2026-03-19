from collections.abc import AsyncGenerator
import glob
import aiomysql
from app.config import Settings


async def execute_sql_script(cursor: aiomysql.Cursor, sql: str) -> None:
  for statement in sql.split(';'):
    statement = statement.strip()
    if statement:
      await cursor.execute(statement)


class Database:
  def __init__(self, settings: Settings) -> None:
    self._settings = settings
    self._pool: aiomysql.Pool | None = None

  async def connect(self) -> None:
    self._pool = await aiomysql.create_pool(
      host=self._settings.db_host,
      port=self._settings.db_port,
      user=self._settings.db_user,
      password=self._settings.db_password,
      db=self._settings.db_name,
      autocommit=True,
    )

  async def run_migrations(self) -> None:
    if self._pool is None:
      raise RuntimeError('Database.connect() must be called before run_migrations()')
    async with self._pool.acquire() as conn:
      async with await conn.cursor() as cursor:
        for path in sorted(glob.glob('migrations/*.sql')):
          with open(path) as f:
            sql = f.read()
          await execute_sql_script(cursor, sql)

  async def disconnect(self) -> None:
    if self._pool:
      self._pool.close()
      await self._pool.wait_closed()

  async def get_db(self) -> AsyncGenerator[aiomysql.Connection, None]:
    if self._pool is None:
      raise RuntimeError('Database.connect() must be called before get_db()')
    async with self._pool.acquire() as conn:
      yield conn
