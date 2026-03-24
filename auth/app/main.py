from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from app.config import get_settings
from app.database import Database
from app.users.user_router import create_user_router

database = Database(get_settings())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
  await database.connect()
  yield
  await database.disconnect()


app = FastAPI(title='Yatzy Auth API', lifespan=lifespan)
app.include_router(create_user_router(database, get_settings()))
