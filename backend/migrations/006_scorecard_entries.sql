CREATE TABLE IF NOT EXISTS scorecard_entries (
  id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  game_id    INT UNSIGNED NOT NULL,
  player_id  INT UNSIGNED NOT NULL,
  category   VARCHAR(32) NOT NULL,
  score      INT UNSIGNED NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at DATETIME DEFAULT NULL,
  UNIQUE KEY uq_scorecard_entry (game_id, player_id, category),
  FOREIGN KEY (game_id)   REFERENCES games(id),
  FOREIGN KEY (player_id) REFERENCES players(id)
);
