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
