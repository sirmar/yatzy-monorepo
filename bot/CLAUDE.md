**Purpose**
- Exposes `POST /action` — backend calls it during a bot player's turn to get the next action (roll or score).

**Dev**
- Evaluate bots offline: `dev exec evaluate -- --bot <maxi|yatzy|maxi-sequential|yatzy-sequential>`.

**Game modes**
- `maxi`, `maxi_sequential`, `yatzy`, `yatzy_sequential` — routed in `app/main.py` based on `game_mode`.
