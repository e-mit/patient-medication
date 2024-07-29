"""Tests for the MedicationRequest model."""

from datetime import date

import pytest

from app.models.medication_request import MedicationRequestBase
from app.models.medication_request import MedicationRequestInput
from app.models.medication_request import MedicationRequestPatch
from app.models.types import MedicationRequestStatus


def test_dictionary_medication_request():
    valid_data = {
        "reason": "the reason text goes in this field.",
        "prescribed_date": date(2024, 1, 5),
        "start_date": date(2024, 1, 6),
        "end_date": date(2024, 4, 5),
        "frequency": "3 times/day",
        "status": MedicationRequestStatus.ON_HOLD
    }
    assert MedicationRequestBase(**valid_data)

    # End date is optional
    valid_data['end_date'] = None
    assert MedicationRequestBase(**valid_data)
    del valid_data['end_date']
    assert MedicationRequestBase(**valid_data)


def test_dictionary_medication_request_invalid():
    valid_data = {
        "reason": "the reason text goes in this field.",
        "prescribed_date": date(2024, 1, 5),
        "start_date": date(2024, 1, 6),
        "end_date": date(2024, 4, 5),
        "frequency": "3 times/day",
        "status": MedicationRequestStatus.ON_HOLD
    }

    bad_data = valid_data.copy()
    bad_data['status'] = "bad"
    with pytest.raises(ValueError):
        MedicationRequestBase(**bad_data)


def test_deserialize_medication_request_input():
    # Create MedicationRequestInput instance from json
    json_string = '''
    {
        "reason": "The reason text goes in this field.",
        "prescribed_date": "2024-01-05",
        "start_date": "2024-01-06",
        "end_date": "2024-04-05",
        "frequency": "3 times/day",
        "status": "Active",
        "medication_id": "123",
        "clinician_id": "999"
    }
    '''
    new_medication_request = MedicationRequestInput.model_validate_json(
        json_string)
    assert new_medication_request.reason == (
        "The reason text goes in this field.")
    assert new_medication_request.prescribed_date == date(2024, 1, 5)
    assert new_medication_request.start_date == date(2024, 1, 6)
    assert new_medication_request.end_date == date(2024, 4, 5)
    assert new_medication_request.frequency == "3 times/day"
    assert new_medication_request.status == MedicationRequestStatus.ACTIVE
    assert new_medication_request.medication_id == 123
    assert new_medication_request.clinician_id == 999


def test_deserialize_medication_request_patch():
    # Create MedicationRequestPatch instance from json
    json_string = '''
    {
        "end_date": "2024-04-05",
        "frequency": "3 times/day",
        "status": "COMPLETED"
    }
    '''
    new_medication_request = MedicationRequestPatch.model_validate_json(
        json_string)
    assert new_medication_request.end_date == date(2024, 4, 5)
    assert new_medication_request.frequency == "3 times/day"
    assert new_medication_request.status == MedicationRequestStatus.COMPLETED
