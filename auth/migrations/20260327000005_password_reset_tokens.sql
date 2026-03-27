-- migrate:up
CREATE TABLE password_reset_tokens (
  id         CHAR(36)     NOT NULL,
  user_id    CHAR(36)     NOT NULL,
  token      CHAR(64)     NOT NULL,
  expires_at DATETIME     NOT NULL,
  created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  used_at    DATETIME     DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idx_password_reset_tokens_token (token),
  CONSTRAINT fk_password_reset_tokens_user FOREIGN KEY (user_id) REFERENCES users (id)
);

-- migrate:down
DROP TABLE password_reset_tokens;
