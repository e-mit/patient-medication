#!/bin/sh

# Build and run only the app container.

# This does not apply database migrations.

# Choose a database connection. Examples:
#
# DATABASE_URL="postgresql+asyncpg://username:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432/database_name"
# DATABASE_URL="sqlite+aiosqlite:///sqlite.db"

export DATABASE_URL="sqlite+aiosqlite:///sqlite.db"

export BUILD_TARGET=test  # test or release; using aiosqlite requires "test"

####################################################

docker build --target $BUILD_TARGET --no-cache -t app .

docker run -e DATABASE_URL=$DATABASE_URL -p 8000:8000 --name app --rm app

#docker stop -t 0 app
