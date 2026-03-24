-- migrate:up
CREATE TABLE users (
  id           CHAR(36)     NOT NULL,
  email        VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at   DATETIME     DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_email (email)
);

-- migrate:down
DROP TABLE users;
