#!/bin/bash

# Run the app without Docker.

# This does not apply database migrations.

SQLITE_FILE="sqlite.db"

##############################

#rm $SQLITE_FILE

export DATABASE_URL="sqlite+aiosqlite:///$SQLITE_FILE"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
