from app.users.token_store_repository import TokenStoreRepository


class VerificationRepository(TokenStoreRepository):
  _table = 'email_verifications'
