-- migrate:up
ALTER TABLE users ADD COLUMN email_verified_at DATETIME DEFAULT NULL;

-- migrate:down
ALTER TABLE users DROP COLUMN email_verified_at;
