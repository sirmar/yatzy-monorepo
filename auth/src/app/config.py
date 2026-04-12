from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file='.env')

  database_url: str = 'mysql://root:root@auth-db:3306/yatzy_auth'
  jwt_secret: str = 'change-me-in-production-use-a-long-secret'
  jwt_algorithm: str = 'HS256'
  access_token_expire_minutes: int = 15
  refresh_token_expire_days: int = 30
  email_verification_expire_minutes: int = 60
  password_reset_expire_minutes: int = 30
  app_env: str = 'dev'


@lru_cache
def get_settings() -> Settings:
  return Settings()
