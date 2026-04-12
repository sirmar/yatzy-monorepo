**Design rules**
- Soft deletes on `users` table (`deleted_at`).
- Refresh tokens stored hashed (SHA-256) in the database for server-side revocation.
- Token rotation: each refresh issues a new pair and revokes the old token.
