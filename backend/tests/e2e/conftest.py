import asyncio
import os
import subprocess
from urllib.parse import urlparse

TEST_DATABASE_URL = os.environ.get('TEST_DATABASE_URL', 'mysql://root:test@127.0.0.1:3307/yatzy_test')
os.environ['DATABASE_URL'] = TEST_DATABASE_URL

from app.main import app, database  # noqa: E402
import pytest  # noqa: E402
import aiomysql  # noqa: E402
from httpx import AsyncClient, ASGITransport  # noqa: E402


def _parse_url(url: str) -> dict:
  parsed = urlparse(url)
  return {
    'host': parsed.hostname,
    'port': parsed.port or 3306,
    'user': parsed.username,
    'password': parsed.password,
    'db': parsed.path.lstrip('/'),
  }


async def _connect() -> aiomysql.Connection:
  return await aiomysql.connect(**_parse_url(TEST_DATABASE_URL), autocommit=True)


async def _list_tables(cursor: aiomysql.Cursor) -> list[str]:
  db = _parse_url(TEST_DATABASE_URL)['db']
  await cursor.execute(
    'SELECT table_name FROM information_schema.tables '
    'WHERE table_schema = %s AND table_type = \'BASE TABLE\'',
    (db,),
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

  await asyncio.to_thread(
    subprocess.run,
    ['dbmate', '--url', TEST_DATABASE_URL, '--migrations-dir', 'migrations', '--no-dump-schema', 'up'],
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
