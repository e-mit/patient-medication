"""Tests for the MedicationRequest model."""

from datetime import date
from decimal import Decimal

import pytest
from sqlmodel import select

from app.models.medication_request import MedicationRequestBase
from app.models.medication_request import MedicationRequest
from app.models.medication_request import MedicationRequestInput
from app.models.medication_request import MedicationRequestPatch
from app.models.medication_request import MedicationRequestOutput
from app.models.types import MedicationRequestStatus, Sex, MedicationForm
from app.models.medication import Medication
from app.models.clinician import Clinician
from app.models.patient import Patient

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

@pytest.fixture()
def the_patient(session):
    the_patient = Patient(
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1985, 5, 15),
        sex=Sex.MALE
    )
    session.add(the_patient)
    session.commit()
    session.refresh(the_patient)
    yield the_patient


@pytest.fixture()
def the_clinician(session):
    the_clinician = Clinician(
        first_name="Alice",
        last_name="Tester",
        registration_id="AB1234"
    )
    session.add(the_clinician)
    session.commit()
    session.refresh(the_clinician)
    yield the_clinician


@pytest.fixture()
def the_medication(session):
    the_medication = Medication(
        code="747006",
        code_name="Oxamniquine",
        code_system="SNOMED",
        strength_value=Decimal("12.123"),
        strength_unit="g/ml",
        form=MedicationForm.POWDER
    )
    session.add(the_medication)
    session.commit()
    session.refresh(the_medication)
    yield the_medication


@pytest.fixture()
def new_clinician(session):
    new_clinician = Clinician(
        first_name="Boris",
        last_name="Tester",
        registration_id="XYZ123"
    )
    session.add(new_clinician)
    session.commit()
    session.refresh(new_clinician)
    yield new_clinician


def test_medication_request_db(the_patient, the_medication,
                               the_clinician, session):
    assert the_patient.id is not None
    assert the_clinician.id is not None
    assert the_medication.id is not None

    # Create a new MedicationRequest instance
    reason = "the reason text goes in this field."
    new_medication_request = MedicationRequest(
        reason=reason,
        prescribed_date=date(2024, 1, 5),
        start_date=date(2024, 1, 6),
        end_date=date(2024, 4, 5),
        frequency="3 times/day",
        status=MedicationRequestStatus.ON_HOLD,
        patient_id=the_patient.id,
        clinician_id=the_clinician.id,
        medication_id=the_medication.id,
    )
    assert new_medication_request.id is None

    # Add to database and check created id
    session.add(new_medication_request)
    session.commit()
    session.refresh(new_medication_request)
    assert new_medication_request.id is not None

    # Query the medication_request from the database
    statement = select(MedicationRequest).where(
        MedicationRequest.reason == reason)
    medication_request_from_db = session.exec(statement).first()

    assert medication_request_from_db == new_medication_request
    assert medication_request_from_db.clinician == the_clinician
    assert medication_request_from_db.medication == the_medication
    assert medication_request_from_db.reason == reason
    assert medication_request_from_db.prescribed_date == date(2024, 1, 5)
    assert medication_request_from_db.start_date == date(2024, 1, 6)
    assert medication_request_from_db.end_date == date(2024, 4, 5)
    assert medication_request_from_db.frequency == "3 times/day"
    assert medication_request_from_db.status == MedicationRequestStatus.ON_HOLD


def test_medication_request_change_clinician(
        the_patient, the_medication, the_clinician, new_clinician, session):
    assert the_patient.id is not None
    assert the_clinician.id is not None
    assert the_medication.id is not None
    assert new_clinician.id is not None

    # Create a new MedicationRequest instance
    reason = "the reason text goes in this field."
    new_medication_request = MedicationRequest(
        reason=reason,
        prescribed_date=date(2024, 1, 5),
        start_date=date(2024, 1, 6),
        end_date=date(2024, 4, 5),
        frequency="3 times/day",
        status=MedicationRequestStatus.ON_HOLD,
        patient_id=the_patient.id,
        clinician_id=the_clinician.id,
        medication_id=the_medication.id,
    )
    assert new_medication_request.id is None

    # Add to database and check created id
    session.add(new_medication_request)
    session.commit()
    session.refresh(new_medication_request)
    assert new_medication_request.id is not None
    assert new_medication_request.clinician == the_clinician

    # change the clinician
    new_medication_request.clinician_id = new_clinician.id
    session.add(new_medication_request)
    session.commit()
    session.refresh(new_medication_request)
    assert new_medication_request.clinician != the_clinician
    assert new_medication_request.clinician == new_clinician
