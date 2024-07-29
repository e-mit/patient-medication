"""Tests for the Patient model."""

from datetime import date

import pytest
from sqlmodel import select

from app.models.patient import Patient, PatientCreate
from app.models.types import Sex
from app.settings import NAME_PART_MAX_LENGTH


def test_deserialize_patient():
    # Create PatientCreate instance from json
    # Note capital letter on sex string
    json_string = '''
    {
        "first_name": "Another",
        "last_name": "Tester",
        "date_of_birth": "2022-01-20",
        "sex": "Female"
    }
    '''
    new_patient = PatientCreate.model_validate_json(json_string)
    assert new_patient.first_name == "Another"
    assert new_patient.last_name == "Tester"
    assert isinstance(new_patient.date_of_birth, date)
    assert new_patient.date_of_birth == date(2022, 1, 20)
    assert new_patient.sex == Sex.FEMALE


def test_deserialize_invalid_patient():
    # Bad date format
    json_string = '''
    {
        "first_name": "Joe",
        "last_name": "America",
        "date_of_birth": "10/25/1976",
        "sex": "male"
    }
    '''
    with pytest.raises(ValueError):
        PatientCreate.model_validate_json(json_string)


def test_patient_db(session):
    # Create a new Patient instance
    new_patient = PatientCreate(
        first_name="John",
        last_name="Tester",
        date_of_birth=date(1980, 1, 15),
        sex=Sex.MALE
    )

    # Convert to database model (no id)
    patient = Patient.model_validate(new_patient)
    assert patient.id is None

    # Add to database and check created id
    session.add(patient)
    session.commit()
    session.refresh(patient)
    assert patient.id is not None

    # Query the patient from the database
    statement = select(Patient).where(Patient.first_name == "John")
    patient_from_db = session.exec(statement).first()

    assert patient_from_db == patient
    assert patient_from_db.first_name == "John"
    assert patient_from_db.last_name == "Tester"
    assert patient_from_db.date_of_birth == date(1980, 1, 15)
    assert patient_from_db.sex == Sex.MALE
