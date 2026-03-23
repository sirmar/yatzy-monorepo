-- migrate:up
ALTER TABLE games MODIFY COLUMN status ENUM('lobby','active','finished','abandoned') NOT NULL DEFAULT 'lobby';

-- migrate:down
ALTER TABLE games MODIFY COLUMN status ENUM('lobby','active','finished') NOT NULL DEFAULT 'lobby';
