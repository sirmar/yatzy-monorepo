-- migrate:up
CREATE TABLE email_verifications (
  id         CHAR(36)     NOT NULL,
  user_id    CHAR(36)     NOT NULL,
  token      CHAR(64)     NOT NULL,
  expires_at DATETIME     NOT NULL,
  created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  used_at    DATETIME     DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idx_email_verifications_token (token),
  CONSTRAINT fk_email_verifications_user FOREIGN KEY (user_id) REFERENCES users (id)
);

-- migrate:down
DROP TABLE email_verifications;
