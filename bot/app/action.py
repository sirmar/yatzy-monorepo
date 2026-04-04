from fastapi import APIRouter
from pydantic import BaseModel
from yatzy_rules.game_variant import get_variant
from yatzy_rules.game_mode import GameMode
from app.sim.game_state import GameState
from app.sim import maxi_bot, maxi_sequential_bot, yatzy_bot, yatzy_sequential_bot
from yatzy_rules.score_category import ScoreCategory as Category

_BOTS = {
  GameMode.MAXI: maxi_bot,
  GameMode.MAXI_SEQUENTIAL: maxi_sequential_bot,
  GameMode.YATZY: yatzy_bot,
  GameMode.YATZY_SEQUENTIAL: yatzy_sequential_bot,
}

router = APIRouter()


class ActionRequest(BaseModel):
  game_mode: GameMode
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
  variant = get_variant(req.game_mode)
  bot = _BOTS[req.game_mode]
  state_data = req.model_dump(exclude={'game_mode'})
  act = bot.action(GameState(**state_data, categories=variant.categories))
  if isinstance(act, list):
    return KeepResponse(keep=act)
  return ScoreResponse(category=act)
