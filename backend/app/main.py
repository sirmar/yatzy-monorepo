from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from app.config import get_settings
from app.database import Database
from app.player_router import create_player_router
from app.game_router import create_game_router

database = Database(get_settings())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
  await database.connect()
  await database.run_migrations()
  yield
  await database.disconnect()


app = FastAPI(title='Yatzy API', lifespan=lifespan)
app.include_router(create_player_router(database))
app.include_router(create_game_router(database))
