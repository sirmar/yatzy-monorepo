from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file='.env')

  database_url: str = 'mysql://root:root@auth-db:3306/yatzy_auth'
  jwt_secret: str = 'change-me-in-production'
  jwt_algorithm: str = 'HS256'
  access_token_expire_minutes: int = 15
  refresh_token_expire_days: int = 30


@lru_cache
def get_settings() -> Settings:
  return Settings()
