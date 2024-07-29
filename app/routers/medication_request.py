"""API router for medication requests."""

from fastapi import APIRouter, status, Response, Request

from .. import settings
from ..models.medication_request import (
    MedicationRequestInput,
    MedicationRequestOutput,
    MedicationRequest,
    MedicationRequestPatch
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


@router.post("/", response_model=MedicationRequest,
             status_code=status.HTTP_201_CREATED)
async def post_medication_request(
        patient_id: int,
        medication_request_input: MedicationRequestInput,
        db: DbDependency,
        request: Request, response: Response):
    """Create a new medication request."""
    result = await crud.create_medication_request(
        db, medication_request_input, patient_id)
    location_url = request.url_for(
        "get_medication_request",
        patient_id=patient_id,
        medication_request_id=result.id)
    response.headers["Location"] = str(location_url)
    return result


@router.patch("/{medication_request_id}",
              response_model=MedicationRequestOutput)
async def patch_medication_request(
        patient_id: int,
        medication_request_id: int,
        patch_data: MedicationRequestPatch,
        db: DbDependency):
    """Modify a subset of fields of a medication request."""
    return await crud.update_medication_request(
        db, patch_data, medication_request_id, patient_id)
