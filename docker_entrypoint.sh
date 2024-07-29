#!/bin/bash

# Wait for the database to be ready
./wait_for_startup.sh "db" 5432 60

# Apply database migrations
alembic upgrade head

# Start the app
exec "$@"
