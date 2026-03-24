-- migrate:up
CREATE TABLE refresh_tokens (
  id         CHAR(36) NOT NULL,
  user_id    CHAR(36) NOT NULL,
  token_hash CHAR(64) NOT NULL,
  expires_at DATETIME NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  revoked_at DATETIME DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idx_refresh_tokens_token_hash (token_hash),
  CONSTRAINT fk_refresh_tokens_user FOREIGN KEY (user_id) REFERENCES users (id)
);

-- migrate:down
DROP TABLE refresh_tokens;
