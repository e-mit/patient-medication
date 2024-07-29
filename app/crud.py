"""Create, replace, update, delete functions for database access."""

from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from pydantic import BaseModel

from .models.medication_request import (
    MedicationRequestInput,
    MedicationRequest,
    MedicationRequestPatch,
    MedicationRequestQueryParams
)
from .models.clinician import Clinician
from .models.patient import Patient
from .models.medication import Medication
from .models.types import HasId


class ResourceNotFoundError(Exception):
    """Exception raised if a resource cannot be found."""

    def __init__(self, resource_class: Type[BaseModel]):
        message = f"The specified {resource_class.__name__} was not found."
        super().__init__(message)
        self.message = message
        self.resource_class = resource_class


class PatientIDMismatchError(Exception):
    """Exception raised for mismatched patient_id.

    This is when the input patient_id does not equal the
    medication request's patient_id.
    """

    def __init__(self):
        message = "Inconsistent patient ID and medication request ID."
        super().__init__(message)
        self.message = message


async def id_exists(db: AsyncSession, object_id: int,
                    model: Type[HasId]) -> bool:
    """Check for existence of item with id in database."""
    statement = select(exists().where(model.id == object_id))  # type: ignore
    result = await db.execute(statement)
    return bool(result.scalar())


async def read_medication_request(
        db: AsyncSession,
        medication_request_id: int,
        patient_id: int) -> MedicationRequest | None:
    """Read a MedicationRequest from the database."""
    if not await id_exists(db, patient_id, Patient):
        raise ResourceNotFoundError(Patient)
    medication_request = await db.get(MedicationRequest, medication_request_id)
    if not medication_request:
        raise ResourceNotFoundError(MedicationRequest)
    if medication_request.patient_id != patient_id:
        raise PatientIDMismatchError()
    return medication_request


async def create_medication_request(
        db: AsyncSession, medication_request_input: MedicationRequestInput,
        patient_id: int) -> MedicationRequest:
    """Create a new MedicationRequest in the database."""
    async with db.begin():
        if not await id_exists(db, patient_id, Patient):
            raise ResourceNotFoundError(Patient)
        if not await id_exists(db, medication_request_input.clinician_id,
                               Clinician):
            raise ResourceNotFoundError(Clinician)
        if not await id_exists(db, medication_request_input.medication_id,
                               Medication):
            raise ResourceNotFoundError(Medication)

        medication_request = MedicationRequest(
            **medication_request_input.model_dump(), patient_id=patient_id)
        db.add(medication_request)
    await db.commit()
    await db.refresh(medication_request)
    return medication_request


async def update_medication_request(
        db: AsyncSession, patch_data: MedicationRequestPatch,
        medication_request_id: int,
        patient_id: int) -> MedicationRequest | None:
    """Update a MedicationRequest in the database.

    This can only change the fields in MedicationRequestPatch.
    """
    async with db.begin():
        if not await id_exists(db, patient_id, Patient):
            raise ResourceNotFoundError(Patient)
        medication_request = await db.get(MedicationRequest,
                                          medication_request_id)
        if not medication_request:
            raise ResourceNotFoundError(MedicationRequest)
        if medication_request.patient_id != patient_id:
            raise PatientIDMismatchError()
        for key, value in patch_data.model_dump().items():
            setattr(medication_request, key, value)
    await db.commit()
    await db.refresh(medication_request)
    return medication_request


async def read_filtered_medication_requests(
        db: AsyncSession,
        patient_id: int,
        query_params: MedicationRequestQueryParams) -> list[MedicationRequest]:
    """Read filtered MedicationRequests from the database."""
    if not await id_exists(db, patient_id, Patient):
        raise ResourceNotFoundError(Patient)
    query = select(MedicationRequest).filter_by(patient_id=patient_id)
    if query_params.status:
        query = query.filter_by(status=query_params.status)
    if query_params.filter_start_date:
        query = query.filter(
            MedicationRequest.prescribed_date
            >= query_params.filter_start_date)  # type: ignore
    if query_params.filter_end_date:
        query = query.filter(
            MedicationRequest.prescribed_date
            <= query_params.filter_end_date)  # type: ignore
    result = await db.execute(query)
    return list(result.scalars().all())
