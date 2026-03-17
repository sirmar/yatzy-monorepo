from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file='.env')

  db_host: str = 'db'
  db_port: int = 3306
  db_user: str = 'root'
  db_password: str = 'root'
  db_name: str = 'yatzy'


@lru_cache
def get_settings() -> Settings:
  return Settings()
