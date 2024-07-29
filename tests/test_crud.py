"""Tests for the crud.py module."""

from unittest.mock import AsyncMock, Mock

import pytest

from app import crud
from app.models.medication_request import (
    MedicationRequest,
    MedicationRequestInput
)
from app.models.patient import Patient
from . import data


class MockAsyncContext(AsyncMock):
    """Add async context manager dunder methods to async mock."""

    def __init__(self):
        super().__init__()
        self.add = Mock()
        result = Mock()
        self.execute = AsyncMock(return_value=result)

    def begin(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return True


@pytest.mark.asyncio
async def test_create_medication_request_success():
    """Use mocked database."""
    db = MockAsyncContext()

    medication_request_input = MedicationRequestInput(
        **data.valid_medication_request_input.model_dump())
    patient_id = 3

    db.get.side_effect = [True, True, True]  # All resources found
    db.refresh.return_value = None

    medication_request = await crud.create_medication_request(
                db, medication_request_input, patient_id)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    medication_request_internal = db.add.call_args[0][0]

    # Assert return values/types
    assert isinstance(medication_request, MedicationRequest)
    assert medication_request_internal == medication_request

    # The return object should be the same as input, plus 2 extra fields
    assert medication_request.patient_id == patient_id
    assert medication_request.id is None
    for key, value in medication_request_input.model_dump().items():
        assert value == getattr(medication_request, key)


@pytest.mark.asyncio
async def test_create_get_medication_request_db(async_session):
    """Use test database."""
    patient_id = 1
    clinician_id = 2
    medication_id = 3

    # set up:
    async for db_session in async_session:
        await data.add_patient(patient_id, db_session)
        await data.add_clinician(clinician_id, db_session)
        await data.add_medication(medication_id, db_session)

    # test:
    async for db_session in async_session:

        medication_request_input = MedicationRequestInput(
            **data.valid_medication_request_input.model_dump())

        medication_request_input.clinician_id = clinician_id
        medication_request_input.medication_id = medication_id

        # put new request in db
        medication_request = await crud.create_medication_request(
            db_session, medication_request_input, patient_id)

        # Assert return values/types
        assert isinstance(medication_request, MedicationRequest)
        assert medication_request.id is not None
        assert medication_request.patient_id == patient_id
        for key, value in medication_request_input.model_dump().items():
            assert value == getattr(medication_request, key)

        # Query the database to check
        from_db = await db_session.get(MedicationRequest,
                                       medication_request.id)
        assert from_db == medication_request

        # get from db
        medication_request_get = await crud.read_medication_request(
            db_session, medication_request.id, patient_id)
        assert medication_request_get is not None
        assert medication_request_get == medication_request


@pytest.mark.asyncio
async def test_get_invalid_medication_request_db(async_session):
    async for db_session in async_session:
        with pytest.raises(crud.ResourceNotFoundError) as exc:
            await crud.read_medication_request(db_session, 8789385, 123)
        assert exc.value.resource_class == Patient
