from collections.abc import AsyncGenerator
from pathlib import Path
import glob
import aiomysql
from app.config import Settings

_MIGRATIONS_TABLE = 'schema_migrations'


async def execute_sql_script(cursor: aiomysql.Cursor, sql: str) -> None:
  for statement in sql.split(';'):
    statement = statement.strip()
    if statement:
      await cursor.execute(statement)


async def run_migrations(cursor: aiomysql.Cursor) -> None:
  await cursor.execute(
    f'CREATE TABLE IF NOT EXISTS {_MIGRATIONS_TABLE} ('
    '  name VARCHAR(255) NOT NULL PRIMARY KEY'
    ')'
  )
  await cursor.execute(f'SELECT name FROM {_MIGRATIONS_TABLE}')  # nosec B608
  applied = {row[0] for row in await cursor.fetchall()}
  for path in sorted(glob.glob('migrations/*.sql')):
    name = Path(path).name
    if name in applied:
      continue
    with open(path) as f:
      sql = f.read()
    await execute_sql_script(cursor, sql)
    await cursor.execute(f'INSERT INTO {_MIGRATIONS_TABLE} (name) VALUES (%s)', (name,))  # nosec B608


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
        await run_migrations(cursor)

  async def disconnect(self) -> None:
    if self._pool:
      self._pool.close()
      await self._pool.wait_closed()

  async def get_db(self) -> AsyncGenerator[aiomysql.Connection, None]:
    if self._pool is None:
      raise RuntimeError('Database.connect() must be called before get_db()')
    async with self._pool.acquire() as conn:
      yield conn
