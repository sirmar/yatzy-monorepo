import os

os.environ.update({
  'DB_HOST': os.environ.get('TEST_DB_HOST', '127.0.0.1'),
  'DB_PORT': os.environ.get('TEST_DB_PORT', '3307'),
  'DB_USER': os.environ.get('TEST_DB_USER', 'root'),
  'DB_PASSWORD': os.environ.get('TEST_DB_PASSWORD', 'test'),
  'DB_NAME': os.environ.get('TEST_DB_NAME', 'yatzy_test'),
})

from app.main import app, database  # noqa: E402
import glob  # noqa: E402
import pytest  # noqa: E402
import aiomysql  # noqa: E402
from httpx import AsyncClient, ASGITransport  # noqa: E402


@pytest.fixture(scope='session', autouse=True)
async def run_migrations():
  conn = await aiomysql.connect(
    host=os.environ['DB_HOST'],
    port=int(os.environ['DB_PORT']),
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    db=os.environ['DB_NAME'],
    autocommit=True,
  )
  cursor = await conn.cursor()
  migration_files = sorted(glob.glob('migrations/*.sql'))
  for path in migration_files:
    with open(path) as f:
      sql = f.read()
    for statement in sql.split(';'):
      statement = statement.strip()
      if statement:
        await cursor.execute(statement)
  await cursor.close()
  conn.close()


@pytest.fixture(autouse=True)
async def truncate_tables():
  yield
  conn = await aiomysql.connect(
    host=os.environ['DB_HOST'],
    port=int(os.environ['DB_PORT']),
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    db=os.environ['DB_NAME'],
    autocommit=True,
  )
  cursor = await conn.cursor()
  await cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
  await cursor.execute(
    'SELECT table_name FROM information_schema.tables '
    'WHERE table_schema = %s AND table_type = \'BASE TABLE\'',
    (os.environ['DB_NAME'],),
  )
  tables = await cursor.fetchall()
  for (table,) in tables:
    await cursor.execute(f'TRUNCATE TABLE `{table}`')
  await cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
  await cursor.close()
  conn.close()


@pytest.fixture
async def client():
  async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as c:
    yield c
