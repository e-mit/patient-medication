# Alembic setup

Generic single-database configuration with an async dbapi.

1. Initialised with: ```alembic init -t async migrations```
2. Edited the config files.
3. Run postgres container (by running full app) and then externally run:
   ```
   export DB_MIGRATION_URL="postgresql+asyncpg://postgres:$POSTGRES_PASSWORD@\
   localhost:5555/postgres"
   alembic revision --autogenerate -m "migration_name"
   ```
4. Optional: edit the migration file.
5. Apply the migration with: ```alembic upgrade head``` (note: this is done automatically at startup in the docker container).
