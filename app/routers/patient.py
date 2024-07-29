"""API router (placeholder) for patient data requests."""

from fastapi import APIRouter, HTTPException, status

from . import medication_request
from .. import settings

router = APIRouter()

router.include_router(
    medication_request.router,
    prefix=f"/{{patient_id}}/{settings.MEDICATION_REQUEST_URL_PREFIX}")

router.include_router(
    medication_request.router_plural,
    prefix=f"/{{patient_id}}/{settings.MEDICATION_REQUESTS_URL_PREFIX}")


@router.get("/{patient_id}", include_in_schema=False)
async def get_patient(patient_id: int):  # pylint: disable=W0613
    """Get patient record (placeholder)."""
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        "GET Patient is not implemented yet.")
