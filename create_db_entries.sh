#!/bin/bash

# Add some example entries to the PostgreSQL database.

SQL_execute() {
    docker exec -e PGPASSWORD=$POSTGRES_PASSWORD -i postgres \
    psql -U $POSTGRES_USER -d $POSTGRES_DB -c "$1"
    if [[ $? -ne 0 ]]; then
        exit 1
    fi
}

SQL_execute "INSERT INTO clinician (id, first_name, last_name, registration_id)\
VALUES (1, 'John', 'Doctor', 'XHGJ7657');"

SQL_execute "INSERT INTO patient (id, first_name, last_name, date_of_birth, sex)
VALUES (1, 'Alice', 'Tester', '1990-05-01', 'female');"

SQL_execute "INSERT INTO medication (id, code, code_system, strength_value,\
strength_unit, form, code_name) VALUES (1, '637465', 'ICD10', 50.75, 'mg',\
'tablet', 'Paracetamol');"

SQL_execute "INSERT INTO medicationrequest (status, frequency, prescribed_date,\
clinician_id, end_date, reason, start_date, medication_id, patient_id)
VALUES ('active', 'daily', '2022-04-12', 1, '2035-05-02', 'Pain relief',\
'2023-11-03', 1, 1);"

SQL_execute "INSERT INTO medicationrequest (status, frequency, prescribed_date,\
clinician_id, end_date, reason, start_date, medication_id, patient_id)
VALUES ('on-hold', '1/hour', '2021-04-12', 1, '2030-05-02', 'A reason here.',\
'2022-10-03', 1, 1);"
