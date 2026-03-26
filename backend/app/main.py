from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from app.config import get_settings
from app.database import Database
from app.players.player_router import create_player_router
from app.games.game_router import create_game_router
from app.scoring.scorecard_router import create_scorecard_router

settings = get_settings()
database = Database(settings)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
  await database.connect()
  yield
  await database.disconnect()


app = FastAPI(title='Yatzy API', lifespan=lifespan)
app.include_router(create_player_router(database, settings))
app.include_router(create_game_router(database, settings))
app.include_router(create_scorecard_router(database, settings))
