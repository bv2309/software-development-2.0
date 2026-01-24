# Migrations

This project uses Alembic with async SQLAlchemy.

## Create a migration

```bash
alembic revision --autogenerate -m "add_items"
```

## Apply migrations

```bash
alembic upgrade head
```

## Notes

- Ensure `DATABASE_URL` is set in your environment.
- pgvector indexes can be tuned by editing the migration script (HNSW `m`, `ef_construction` or IVFFLAT `lists`).
