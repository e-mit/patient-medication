"""API router for medication requests."""

from fastapi import APIRouter

from .. import settings
from ..models.medication_request import (
    MedicationRequestOutput
)
from ..database import DbDependency
from .. import crud

router = APIRouter(tags=[settings.MEDICATION_REQUEST_TAG])
router_plural = APIRouter(tags=[settings.MEDICATION_REQUEST_TAG])


@router.get("/{medication_request_id}", response_model=MedicationRequestOutput)
async def get_medication_request(patient_id: int,
                                 medication_request_id: int,
                                 db: DbDependency):
    """Get medication request data."""
    return await crud.read_medication_request(
        db, medication_request_id, patient_id)
