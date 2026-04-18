from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file='.env')

  database_url: str = 'mysql://root:root@db:3306/yatzy'
  jwt_secret: str = 'change-me-in-production-use-a-long-secret'
  jwt_algorithm: str = 'HS256'
  bot_url: str = 'http://bot:8000'


@lru_cache
def get_settings() -> Settings:
  return Settings()
