# Patient Medication

A Medication Request endpoint with GET, POST and PATCH routes for a single patient.

This uses FastAPI, SQLModel, SQLAlchemy, Docker, PostgreSQL, Alembic, Uvicorn.


## Notes, assumptions and design choices

- Tested with Python 3.10 on Ubuntu linux.
- The database can be chosen by setting the environment variable ```DATABASE_URL```. By default this uses a Postgres container.
- The API is not versioned: this can be done externally with an API gateway/proxy.
- Test coverage is low and uneven due to time constraints.
- Response data objects contain entity IDs rather than URIs; this is for convenience and could be changed easily.
- The implemented routes are subpaths of "patient", but could be replicated at other locations e.g. root level, subpaths of "clinician" etc.
- Various assumptions were made about entity data types and values.
- The response data objects for GET and POST have different formats, but could be changed to use the same format. 


## Testing

The test runner script also runs linters, coverage report and an end-to-end system test using the dockerised app.
Most tests run locally (not in the docker container).

1. Create a virtual environment and install packages with:
   ```python -m venv venv && source venv/bin/activate && pip install -r requirements.txt```
2. Also install packages for testing with: ```pip install -r requirements-test.txt```
3. Ensure the various bash scripts have execute permissions: ```chmod +x *.sh```
4. Run all tests with: ```./run_tests.sh```


## Build and run

### To build and run with Docker compose

This creates a PostgreSQL container and applies migrations. It also adds example data to the database (one of each entity, each with id=1).

- Use: ```./docker_compose_build_run.sh```
- Then go to: http://localhost:8000/docs or http://localhost:8000/patient/1/medication-request/1
- Stop with: ```docker compose -f docker-compose.yml down```


### To run without Docker

This creates an empty SQLite database file by default, but ```DATABASE_URL``` can be changed to point to a different database. Migrations are not applied.

- Create a python virtual environment and install both requirements lists.
- Run with: ```./local_run.sh```
- Then go to: http://localhost:8000/docs


## Further steps to do

- More unit and integration tests
- Use an automated API test tool e.g. Postman
- Add logging
- More detailed data model validations
- Add data examples and descriptions to appear in the Swagger UI
- Use a UUID for entity IDs
- Set up GitHub actions for tests, linting, build and deployment to staging
