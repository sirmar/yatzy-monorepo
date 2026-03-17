CREATE TABLE IF NOT EXISTS games (
  id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  status       ENUM('lobby','active','finished') NOT NULL DEFAULT 'lobby',
  creator_id   INT UNSIGNED NOT NULL,
  current_turn INT UNSIGNED DEFAULT NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  started_at   DATETIME DEFAULT NULL,
  ended_at     DATETIME DEFAULT NULL,
  deleted_at   DATETIME DEFAULT NULL,
  FOREIGN KEY (creator_id) REFERENCES players(id)
);

CREATE TABLE IF NOT EXISTS game_players (
  game_id         INT UNSIGNED NOT NULL,
  player_id       INT UNSIGNED NOT NULL,
  join_order      INT UNSIGNED NOT NULL,
  rolls_remaining TINYINT UNSIGNED NOT NULL DEFAULT 0,
  deleted_at      DATETIME DEFAULT NULL,
  PRIMARY KEY (game_id, player_id),
  FOREIGN KEY (game_id)   REFERENCES games(id),
  FOREIGN KEY (player_id) REFERENCES players(id)
);
