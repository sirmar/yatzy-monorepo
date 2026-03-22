from collections.abc import AsyncGenerator
from urllib.parse import urlparse
import aiomysql
from app.config import Settings


class Database:
  def __init__(self, settings: Settings) -> None:
    self._settings = settings
    self._pool: aiomysql.Pool | None = None

  async def connect(self) -> None:
    url = urlparse(self._settings.database_url)
    self._pool = await aiomysql.create_pool(
      host=url.hostname,
      port=url.port or 3306,
      user=url.username,
      password=url.password,
      db=url.path.lstrip('/'),
      autocommit=True,
    )

  async def disconnect(self) -> None:
    if self._pool:
      self._pool.close()
      await self._pool.wait_closed()

  async def get_db(self) -> AsyncGenerator[aiomysql.Connection, None]:
    if self._pool is None:
      raise RuntimeError('Database.connect() must be called before get_db()')
    async with self._pool.acquire() as conn:
      yield conn
