#!/bin/sh

# Build the docker container, run the app and database,
# apply database migrations, add some example data.

export BUILD_TARGET=release  # test or release

export POSTGRES_USER=postgres
export POSTGRES_DB=postgres
export POSTGRES_HOST_AND_PORT="db:5432"
export POSTGRES_PASSWORD=$(dd if=/dev/random bs=3 count=4 2>/dev/null \
                            | od -An -tx1 | tr -d ' \t\n')

export HOST_DB_PORT=5555  # expose database to host on this port
export DATABASE_ECHO=1  # 1 or 0

###########################################

export DATABASE_URL="postgresql+asyncpg://$POSTGRES_USER:$POSTGRES_PASSWORD@\
$POSTGRES_HOST_AND_PORT/$POSTGRES_DB"

echo "The postgres password is: $POSTGRES_PASSWORD"

docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml up -d --build --force-recreate

# wait for the app and database to start:
./wait_for_startup.sh "localhost" 8000 60
./wait_for_startup.sh "localhost" $HOST_DB_PORT 60
sleep 3

# create test data in the database
./create_db_entries.sh

echo ""
echo "View the Swagger UI at http://localhost:8000/docs"
echo ""
echo "Stop the app with: 'docker compose -f docker-compose.yml down'"
echo ""
