-- migrate:up
ALTER TABLE players ADD COLUMN has_picture BOOLEAN NOT NULL DEFAULT FALSE;

-- migrate:down
ALTER TABLE players DROP COLUMN has_picture;
