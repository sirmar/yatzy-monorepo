import asyncio
import os
import subprocess

os.environ.update({
  'DB_HOST': os.environ.get('TEST_DB_HOST', '127.0.0.1'),
  'DB_PORT': os.environ.get('TEST_DB_PORT', '3307'),
  'DB_USER': os.environ.get('TEST_DB_USER', 'root'),
  'DB_PASSWORD': os.environ.get('TEST_DB_PASSWORD', 'test'),
  'DB_NAME': os.environ.get('TEST_DB_NAME', 'yatzy_test'),
})

from app.main import app, database  # noqa: E402
import pytest  # noqa: E402
import aiomysql  # noqa: E402
from httpx import AsyncClient, ASGITransport  # noqa: E402


async def _connect() -> aiomysql.Connection:
  return await aiomysql.connect(
    host=os.environ['DB_HOST'],
    port=int(os.environ['DB_PORT']),
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    db=os.environ['DB_NAME'],
    autocommit=True,
  )


async def _list_tables(cursor: aiomysql.Cursor) -> list[str]:
  await cursor.execute(
    'SELECT table_name FROM information_schema.tables '
    'WHERE table_schema = %s AND table_type = \'BASE TABLE\'',
    (os.environ['DB_NAME'],),
  )
  return [row[0] for row in await cursor.fetchall()]


@pytest.fixture(autouse=True)
async def connect_database():
  await database.connect()
  yield
  await database.disconnect()


@pytest.fixture(scope='session', autouse=True)
async def migrate():
  conn = await _connect()
  cursor = await conn.cursor()
  tables = await _list_tables(cursor)
  if tables:
    await cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
    quoted = ', '.join(f'`{t}`' for t in tables)
    await cursor.execute(f'DROP TABLE IF EXISTS {quoted}')  # nosec B608
    await cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
  await cursor.close()
  conn.close()

  db_url = (
    f"mysql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
    f"@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
  )
  await asyncio.to_thread(
    subprocess.run,
    ['dbmate', '--url', db_url, '--migrations-dir', 'migrations', '--no-dump-schema', 'up'],
    check=True,
  )


@pytest.fixture(autouse=True)
async def truncate_tables():
  yield
  conn = await _connect()
  cursor = await conn.cursor()
  tables = await _list_tables(cursor)
  if tables:
    await cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
    for table in tables:
      await cursor.execute(f'TRUNCATE TABLE `{table}`')
    await cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
  await cursor.close()
  conn.close()


@pytest.fixture
async def client():
  async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as c:
    yield c
