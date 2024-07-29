"""Tests for the medication request router, with mocked database CRUD."""

from datetime import date
from unittest.mock import patch, AsyncMock
import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.types import MedicationRequestStatus
from app.models.medication_request import MedicationRequest
from app.models.medication_request import MedicationRequestOutput
from app.models.medication_request import MedicationRequestInput
from app import settings
from app.database import Database

client = TestClient(app)

# Mock the database dependency
mock_db_session = AsyncMock()
async def get_db():  # noqa
    yield mock_db_session
app.dependency_overrides[Database.get_db] = get_db

# Mock a MedicationRequest object obtained from the database.
medication = AsyncMock(code_name="caffeine")
clinician = AsyncMock(first_name="Billy", last_name="Tester")
mock_medication_request = MedicationRequest(
    reason="the reason text goes in this field.",
    prescribed_date=date(2024, 1, 5),
    start_date=date(2024, 1, 6),
    end_date=date(2024, 4, 5),
    frequency="3 times/day",
    status=MedicationRequestStatus.ON_HOLD,
    clinician_id=555,
    medication_id=123,
    id=5,
    patient_id=1,
    medication=medication,
    clinician=clinician
)


@pytest.mark.asyncio
async def test_get_medication_request():
    medication_request_id = 2

    with patch(
            'app.crud.read_medication_request',
            new_callable=AsyncMock) as mock_read_medication_request:
        mock_read_medication_request.return_value = mock_medication_request

        response = client.get(
            f"/{settings.PATIENT_URL_PREFIX}"
            f"/{mock_medication_request.patient_id}"
            f"/{settings.MEDICATION_REQUEST_URL_PREFIX}"
            f"/{medication_request_id}")

        assert response.status_code == 200

        mock_read_medication_request.assert_awaited_once_with(
            mock_db_session, medication_request_id,
            mock_medication_request.patient_id)

        interpreted_data = MedicationRequestOutput(**response.json())
        assert isinstance(interpreted_data, MedicationRequestOutput)

        assert (len(response.json().keys())
                == len(MedicationRequestOutput.model_fields))
        for key in response.json():
            if key not in {'medication', 'clinician'}:
                assert (getattr(interpreted_data, key)
                        == getattr(mock_medication_request, key))

        assert (interpreted_data.clinician.first_name
                == mock_medication_request.clinician.first_name)
        assert (interpreted_data.clinician.last_name
                == mock_medication_request.clinician.last_name)
        assert (interpreted_data.medication.code_name
                == mock_medication_request.medication.code_name)


@pytest.mark.asyncio
async def test_post_medication_request():
    medication_request_input = MedicationRequestInput(
        reason="the reason text goes in this field.",
        prescribed_date=date(2024, 1, 5),
        start_date=date(2024, 1, 6),
        end_date=date(2024, 4, 5),
        frequency="3 times/day",
        status=MedicationRequestStatus.ON_HOLD,
        clinician_id=555,
        medication_id=123
    )

    with patch(
            'app.crud.create_medication_request',
            new_callable=AsyncMock) as mock_create_medication_request:
        mock_create_medication_request.return_value = mock_medication_request

        response = client.post(
            f"/{settings.PATIENT_URL_PREFIX}"
            f"/{mock_medication_request.patient_id}"
            f"/{settings.MEDICATION_REQUEST_URL_PREFIX}",
            content=medication_request_input.model_dump_json(),
            headers={"Content-Type": "application/json"})

        assert response.status_code == 201

        mock_create_medication_request.assert_awaited_once_with(
            mock_db_session, medication_request_input,
            mock_medication_request.patient_id)

        input_json = mock_medication_request.model_dump_json()
        assert (MedicationRequest(**json.loads(input_json))
                == MedicationRequest(**response.json()))
