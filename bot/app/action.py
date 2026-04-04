from fastapi import APIRouter
from pydantic import BaseModel
from yatzy_rules.game_variant import get_variant
from yatzy_rules.game_mode import GameMode
from app.sim.game_state import GameState
from app.sim import maxi_bot
from yatzy_rules.score_category import ScoreCategory as Category

_VARIANT = get_variant(GameMode.MAXI)

router = APIRouter()


class ActionRequest(BaseModel):
  dice: list[int]
  kept: list[bool]
  rolls_remaining: int
  saved_rolls: int
  has_rolled: bool
  scores: dict[Category, int]


class KeepResponse(BaseModel):
  action: str = 'roll'
  keep: list[bool]


class ScoreResponse(BaseModel):
  action: str = 'score'
  category: Category


@router.post('/action')
def get_action(req: ActionRequest) -> KeepResponse | ScoreResponse:
  act = maxi_bot.action(GameState(**req.model_dump(), categories=_VARIANT.categories))
  if isinstance(act, list):
    return KeepResponse(keep=act)
  return ScoreResponse(category=act)
