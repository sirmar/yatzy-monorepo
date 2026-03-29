from app.users.token_store_repository import TokenStoreRepository


class ResetRepository(TokenStoreRepository):
  _table = 'password_reset_tokens'
