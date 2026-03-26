def auth_headers(token: str | None) -> dict:
  return {'Authorization': f'Bearer {token}'} if token else {}
