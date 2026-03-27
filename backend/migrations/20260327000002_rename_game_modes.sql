-- migrate:up
ALTER TABLE games
  MODIFY COLUMN mode ENUM('maxi', 'maxi_sequential', 'yatzy', 'yatzy_sequential') NOT NULL DEFAULT 'maxi';

-- migrate:down
ALTER TABLE games
  MODIFY COLUMN mode ENUM('standard', 'sequential', 'yatzy', 'yatzy_sequential') NOT NULL DEFAULT 'standard';
