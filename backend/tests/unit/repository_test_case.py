from unittest.mock import AsyncMock, MagicMock


class RepositoryTestCase:
  def setup_method(self):
    self.cursor = AsyncMock()
    self.conn = MagicMock()
    self.conn.cursor = AsyncMock(return_value=self.cursor)
