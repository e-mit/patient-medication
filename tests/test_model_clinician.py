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
