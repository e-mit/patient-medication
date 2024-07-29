#!/bin/bash

# Run an end-to-end system test.
#
# Build and run docker compose, add data, execute and check GET and POST requests.
# Returns 0 if successful, 1-100 if error, >100 if skipping.

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

ERROR_SQL_SETUP_CODE=1
ERROR_CURL_CODE=2
ERROR_STATUS_CODE=3
ERROR_COMPARE_FAIL_CODE=4
ERROR_DOCKER=5
ERROR_WAIT_TIMEOUT=6
SKIP_CODE=101
OK_CODE=0

########################################

runner_error_check() {
    if [[ $? -ne 0 ]]; then
        echo "Error: The program failed to run correctly."
        exit $1
    fi
}

test_request() { # HTTP_VERB RELATIVE_URL EXPECTED_STATUS BODY_DATA
    curl_output=$(curl -X "$1" "http://127.0.0.1:8000$2" \
    -H "Content-Type: application/json" \
    -d "$4" \
    -w "\nHTTP Status: %{http_code}\n" -L)
    runner_error_check $ERROR_CURL_CODE

    status_code=$(echo "$curl_output" | grep "HTTP Status" | awk '{print $3}')
    body_data=$(echo "$curl_output" | sed '/HTTP Status/d')

    if [[ $status_code -ne $3 ]]; then
        echo "Error: get status code $status_code"
        echo "Body data: $body_data"
        exit $ERROR_STATUS_CODE
    fi
}

compare_json() {
    local json1="$1"
    local json2="$2"
    python3 - <<EOF
import json
json1 = """$json1"""
json2 = """$json2"""
def fail():
    print("Error: The response comparison failed.")
    print(json1)
    print("vs")
    print(json2)
    exit(1)

try:
    obj1 = json.loads("""$json1""")
    obj2 = json.loads("""$json2""")
    if obj1 == obj2:
        exit(0)
    else:
        fail()
except json.JSONDecodeError as e:
    fail()
EOF
if [[ $? -ne 0 ]]; then
    exit $ERROR_COMPARE_FAIL_CODE
fi
}

cleanup() {
    docker compose -f docker-compose.yml down
}
# Set the trap to call the cleanup function on exit
trap cleanup EXIT

# start the containers
cleanup
docker compose -f docker-compose.yml up -d --build
runner_error_check $ERROR_DOCKER

# wait for the app and database to start:
./wait_for_startup.sh "localhost" 8000 60
runner_error_check $ERROR_WAIT_TIMEOUT
./wait_for_startup.sh "localhost" $HOST_DB_PORT 60
runner_error_check $ERROR_WAIT_TIMEOUT
sleep 3

# create test data in the database
./create_db_entries.sh
runner_error_check $ERROR_SQL_SETUP_CODE

json_data='{
    "clinician_id": 1,
    "medication_id": 1,
    "reason": "Pain relief",
    "prescribed_date": "2024-07-25",
    "start_date": "2024-07-26",
    "end_date": "2024-08-25",
    "frequency": "daily",
    "status": "active"
}'

expected_response='{
"status":"active","frequency":"daily","prescribed_date":"2024-07-25",
"clinician_id":1,"id":3,"end_date":"2024-08-25","reason":"Pain relief",
"start_date":"2024-07-26","medication_id":1,"patient_id":1}'

test_request GET "/patient/1/medication-request/1" 200
test_request POST "/patient/1/medication-request" 201 "$json_data"
compare_json "$body_data" "$expected_response"

exit $OK_CODE
