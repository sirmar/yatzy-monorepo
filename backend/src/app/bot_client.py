import httpx


async def get_action(bot_url: str, payload: dict) -> dict:
  async with httpx.AsyncClient() as client:
    r = await client.post(f'{bot_url}/action', json=payload)
    r.raise_for_status()
    return r.json()
