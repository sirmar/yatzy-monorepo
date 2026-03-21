ALTER TABLE game_players
  CHANGE COLUMN rolls_remaining saved_rolls TINYINT UNSIGNED NOT NULL DEFAULT 0;
