# POST /action

Returns the bot's recommended action given the current game state for a player's turn.

## Request

`Content-Type: application/json`

| Field | Type | Description |
|---|---|---|
| `game_mode` | `string` | Game variant (see below) |
| `dice` | `int[6]` | Current face values of all 6 dice (1–6) |
| `kept` | `bool[6]` | Which dice are held and will not be rerolled |
| `rolls_remaining` | `int` | Rolls left in the current turn (0–3) |
| `saved_rolls` | `int` | Extra rolls banked from previous turns |
| `has_rolled` | `bool` | Whether the player has rolled at least once this turn |
| `scores` | `object` | Already-scored categories, keyed by category name, valued by points awarded |

### `game_mode` values

| Value | Description |
|---|---|
| `maxi` | Swedish Maxi Yatzy (6 dice, free category choice) |
| `maxi_sequential` | Maxi Yatzy with fixed category order |
| `yatzy` | Standard Yatzy (5 dice, free category choice) |
| `yatzy_sequential` | Standard Yatzy with fixed category order |

### `scores` keys

Category names depend on the game mode. For `maxi` and `maxi_sequential`:

`ones`, `twos`, `threes`, `fours`, `fives`, `sixes`, `one_pair`, `two_pairs`, `three_pairs`, `three_of_a_kind`, `four_of_a_kind`, `five_of_a_kind`, `small_straight`, `large_straight`, `full_straight`, `full_house`, `villa`, `tower`, `chance`, `maxi_yatzy`

For `yatzy` and `yatzy_sequential`:

`ones`, `twos`, `threes`, `fours`, `fives`, `sixes`, `one_pair`, `two_pairs`, `three_of_a_kind`, `four_of_a_kind`, `small_straight`, `large_straight`, `full_house`, `chance`, `yatzy`

Omit categories that have not yet been scored.

## Response

The response is one of two shapes depending on the recommended action.

### Roll — keep these dice and roll the rest

```json
{
  "action": "roll",
  "keep": [true, false, true, false, true, false]
}
```

| Field | Type | Description |
|---|---|---|
| `action` | `"roll"` | Discriminator |
| `keep` | `bool[6]` | Which dice to hold before the next roll |

### Score — assign the current dice to a category

```json
{
  "action": "score",
  "category": "full_house"
}
```

| Field | Type | Description |
|---|---|---|
| `action` | `"score"` | Discriminator |
| `category` | `string` | Category to score (see category list above) |

## Decision rules

- If `has_rolled` is `false`, the bot always returns a `roll` action (the player must roll before scoring).
- If `rolls_remaining == 0` and `saved_rolls == 0`, the bot always returns a `score` action (the player must score).
- Otherwise the bot decides whether to reroll or score based on the current dice and remaining available categories.

## Example

**Request**

```json
{
  "game_mode": "maxi",
  "dice": [3, 3, 3, 5, 5, 2],
  "kept": [false, false, false, false, false, false],
  "rolls_remaining": 2,
  "saved_rolls": 0,
  "has_rolled": true,
  "scores": {
    "ones": 2,
    "twos": 6
  }
}
```

**Response**

```json
{
  "action": "roll",
  "keep": [true, true, true, true, true, false]
}
```
