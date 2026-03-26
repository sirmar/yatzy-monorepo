-- migrate:up
ALTER TABLE games
  ADD COLUMN mode ENUM('standard', 'sequential') NOT NULL DEFAULT 'standard' AFTER status;

-- migrate:down
ALTER TABLE games
  DROP COLUMN mode;
