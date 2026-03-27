from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from app.config import get_settings
from app.database import Database
from app.email import LogEmailSender
from app.users.dev_router import create_dev_router
from app.users.user_router import create_user_router

settings = get_settings()
database = Database(settings)
email_sender = LogEmailSender()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
  await database.connect()
  yield
  await database.disconnect()


app = FastAPI(title='Yatzy Auth API', lifespan=lifespan)
app.include_router(create_user_router(database, settings, email_sender))

if settings.app_env in ('dev', 'test'):
  app.include_router(create_dev_router(database))
