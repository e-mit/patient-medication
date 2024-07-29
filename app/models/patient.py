"""SQLModels for the Patient entity."""

from datetime import date
from typing import Annotated

from sqlmodel import Field, SQLModel
from pydantic.functional_validators import BeforeValidator
from sqlalchemy import Column, Enum

from .types import Sex, NamePart


class PatientBase(SQLModel):
    """Patient base class for field definitions."""

    first_name: NamePart
    last_name: NamePart
    date_of_birth: date
    # Enum field: ensure it is stored using the enum value (not by name).
    sex: Annotated[
        Sex,
        Field(sa_column=Column(
            Enum(Sex,
                 values_callable=lambda x: [e.value for e in x]),
            nullable=False)),
        BeforeValidator(lambda x: x.lower())]


class Patient(PatientBase, table=True):
    """Patient database model class."""

    id: int | None = Field(default=None, primary_key=True)


class PatientCreate(PatientBase):
    """Patient class for deserialisation and validation."""

    pass  # pylint: disable=W0107
