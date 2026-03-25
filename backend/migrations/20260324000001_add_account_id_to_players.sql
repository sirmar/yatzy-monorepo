-- migrate:up
ALTER TABLE players
  ADD COLUMN account_id CHAR(36) NOT NULL AFTER id,
  ADD UNIQUE KEY uq_players_account_id (account_id);

-- migrate:down
ALTER TABLE players
  DROP KEY uq_players_account_id,
  DROP COLUMN account_id;
