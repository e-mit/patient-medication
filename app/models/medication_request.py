"""SQLModels for the MedicationRequest entity."""

from datetime import date
from typing import Annotated
from typing_extensions import Self

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy import Column, Enum
from pydantic.functional_validators import BeforeValidator
from pydantic import BaseModel, model_validator

from .types import MedicationRequestStatus, ModelInvalidError
from .. import settings
from .medication import Medication, MedicationCodeName
from .clinician import Clinician, ClinicianName


class MedicationRequestPatch(SQLModel):
    """MedicationRequest base class for patchable field definitions."""

    end_date: date | None = None
    frequency: str = Field(
        min_length=1, max_length=settings.MED_REQUEST_FREQ_MAX_LENGTH)
    # Enum field: ensure it is stored using the enum value (not by name).
    status: Annotated[
        MedicationRequestStatus,
        Field(sa_column=Column(
            Enum(MedicationRequestStatus,
                 values_callable=lambda x: [e.value for e in x]),
            nullable=False, index=True)),
        BeforeValidator(lambda x: x.lower())]


class MedicationRequestBase(MedicationRequestPatch):
    """MedicationRequest base class for all field definitions."""

    reason: str = Field(sa_column=Column(TEXT, nullable=False))
    prescribed_date: date = Field(index=True)
    start_date: date

    @model_validator(mode='after')
    def validate_relative_dates(self) -> Self:
        """Require start_date to be before end date (unless None)."""
        if self.end_date is not None and self.end_date < self.start_date:
            raise ModelInvalidError(
                'End date must be after the start date, or None.')
        return self


class MedicationRequestInput(MedicationRequestBase):
    """MedicationRequest class for input deserialisation and validation.

    Note that the foreign key fields are validated for type but not
    for existence in the database.
    """

    clinician_id: int = Field(foreign_key="clinician.id")
    medication_id: int = Field(foreign_key="medication.id")


class MedicationRequest(MedicationRequestInput, table=True):
    """MedicationRequest database model class."""

    id: int | None = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id")
    medication: Medication = Relationship(
        back_populates="medication_requests",
        sa_relationship_kwargs={'lazy': 'joined'})
    clinician: Clinician = Relationship(
        back_populates="medication_requests",
        sa_relationship_kwargs={'lazy': 'joined'})


class MedicationRequestOutput(MedicationRequestInput):
    """MedicationRequest class for output serialisation in responses."""

    id: int
    medication: MedicationCodeName
    clinician: ClinicianName


class MedicationRequestQueryParams(BaseModel):
    """Query parameters for the GET filtering."""

    status: Annotated[MedicationRequestStatus | None,
                      BeforeValidator(lambda v: v.lower() if v else v)] = None
    filter_start_date: date | None = None
    filter_end_date: date | None = None

    @model_validator(mode='after')
    def validate_date_range(self) -> Self:
        """Require both dates to be simultaneously None or not None."""
        if (self.filter_start_date is None) != (self.filter_end_date is None):
            raise ModelInvalidError('Invalid date range.')
        return self
