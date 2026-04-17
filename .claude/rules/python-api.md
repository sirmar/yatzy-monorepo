---
paths: ["backend/**", "auth/**"]
---

**Patterns**
- Factory-function routers, dependency injection, repository pattern, raw SQL. No ORM.
- One router/repository class per file. Small related models may be grouped (e.g. `requests.py`) if each is under ~15 lines.
