"""Tests for the Clinician model."""

import pytest
from sqlmodel import select

from app.models.clinician import Clinician, ClinicianCreate


def test_deserialize_clinician():
    # Create ClinicianCreate instance from json
    json_string = '''
    {
        "first_name": "Another",
        "last_name": "Tester",
        "registration_id": "090-6565"
    }
    '''
    new_clinician = ClinicianCreate.model_validate_json(json_string)
    assert new_clinician.first_name == "Another"
    assert new_clinician.last_name == "Tester"
    assert new_clinician.registration_id == "090-6565"


def test_deserialize_invalid_clinician():
    # empty ID
    json_string = '''
    {
        "first_name": "Joe",
        "last_name": "America",
        "registration_id": ""
    }
    '''
    with pytest.raises(ValueError):
        ClinicianCreate.model_validate_json(json_string)


def test_clinician_db(session):
    # Create a new Clinician instance
    new_clinician = ClinicianCreate(
        first_name="John",
        last_name="Tester",
        registration_id="ABC"
    )

    # Convert to database model (no id)
    clinician = Clinician.model_validate(new_clinician)
    assert clinician.id is None

    # Add to database and check created id
    session.add(clinician)
    session.commit()
    session.refresh(clinician)
    assert clinician.id is not None

    # Query the clinician from the database
    statement = select(Clinician).where(Clinician.first_name == "John")
    clinician_from_db = session.exec(statement).first()

    assert clinician_from_db == clinician
    assert clinician_from_db.first_name == "John"
    assert clinician_from_db.last_name == "Tester"
    assert clinician_from_db.registration_id == "ABC"
