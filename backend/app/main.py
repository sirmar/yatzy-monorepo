from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from app.config import get_settings
from app.database import Database

database = Database(get_settings())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
  await database.connect()
  yield
  await database.disconnect()


app = FastAPI(title='Yatzy API', lifespan=lifespan)
