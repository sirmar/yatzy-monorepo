-- migrate:up
ALTER TABLE games
  MODIFY COLUMN mode ENUM('standard', 'sequential', 'yatzy', 'yatzy_sequential') NOT NULL DEFAULT 'standard';

-- migrate:down
ALTER TABLE games
  MODIFY COLUMN mode ENUM('standard', 'sequential') NOT NULL DEFAULT 'standard';
