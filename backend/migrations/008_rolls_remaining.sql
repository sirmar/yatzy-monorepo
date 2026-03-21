ALTER TABLE turns
  CHANGE COLUMN rolls_used rolls_remaining TINYINT UNSIGNED NOT NULL DEFAULT 3;

UPDATE turns
  SET rolls_remaining = GREATEST(0, 3 - rolls_remaining)
  WHERE completed_at IS NULL AND deleted_at IS NULL;
