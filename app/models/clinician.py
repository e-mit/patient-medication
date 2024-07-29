"""SQLModels for the Clinician entity."""

from sqlmodel import Field, SQLModel, Relationship

from .types import NamePart
from .. import settings


class ClinicianName(SQLModel):
    """Clinician base class for name definition."""

    first_name: NamePart
    last_name: NamePart


class ClinicianBase(ClinicianName):
    """Clinician base class for all field definitions."""

    registration_id: str = Field(
        min_length=1, max_length=settings.CLINICIAN_REG_ID_MAX_LENGTH)


class Clinician(ClinicianBase, table=True):
    """Clinician database model class."""

    id: int | None = Field(default=None, primary_key=True)
    medication_requests: list["MedicationRequest"] = Relationship(  # type: ignore # noqa
        back_populates="clinician")


class ClinicianCreate(ClinicianBase):
    """Clinician class for deserialisation and validation."""

    pass  # pylint: disable=W0107
