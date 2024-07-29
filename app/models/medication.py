"""SQLModels for the Medication entity."""

from decimal import Decimal
from typing import Annotated

from sqlmodel import Field, SQLModel, Relationship
from pydantic.functional_validators import BeforeValidator
from sqlalchemy import Column, Enum

from .types import MedicationForm
from .. import settings


class MedicationCodeName(SQLModel):
    """Medication base class for code name."""

    code_name: str = Field(min_length=1)


class MedicationBase(MedicationCodeName):
    """Medication base class for all field definitions."""

    code: str = Field(min_length=1)
    code_system: str = Field(min_length=1)
    strength_value: Decimal = Field(
        gt=0,
        max_digits=settings.MEDICATION_STRENGTH_MAX_DIGITS,
        decimal_places=settings.MEDICATION_STRENGTH_DECIMAL_PLACES)
    strength_unit: str = Field(min_length=1)
    # Enum field: ensure it is stored using the enum value (not by name).
    form: Annotated[
        MedicationForm,
        Field(sa_column=Column(
            Enum(MedicationForm,
                 values_callable=lambda x: [e.value for e in x]),
            nullable=False)),
        BeforeValidator(lambda x: x.lower())]


class Medication(MedicationBase, table=True):
    """Medication database model class."""

    id: int | None = Field(default=None, primary_key=True)
    medication_requests: list["MedicationRequest"] = Relationship(  # type: ignore # noqa
        back_populates="medication")


class MedicationCreate(MedicationBase):
    """Medication class for deserialisation and validation."""

    pass  # pylint: disable=W0107
