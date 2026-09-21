# Database

`schema.sql` is kept as a human-readable reference of the current schema.

The source of truth for actually creating/upgrading the schema is Alembic:

```bash
cd backend
alembic upgrade head
```

To generate a new migration after changing `backend/app/models.py`:

```bash
cd backend
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

In local development only, the API also auto-creates tables on startup
(`ENVIRONMENT=development`, the default) so you can start hacking without
running migrations first. Do not rely on this in production — set
`ENVIRONMENT=production` and run `alembic upgrade head` as part of your
deploy step instead.
