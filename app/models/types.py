"""Types used in model classes."""

from enum import Enum
from typing import Annotated

from sqlmodel import Field

from .. import settings


# A person's first name or last name
NamePart = Annotated[str, Field(
    min_length=1, max_length=settings.NAME_PART_MAX_LENGTH)]


class MedicationForm(str, Enum):
    """The form of a medication."""

    POWDER = 'powder'
    TABLET = 'tablet'
    CAPSULE = 'capsule'
    SYRUP = 'syrup'


class Sex(str, Enum):
    """The sex of a person."""

    MALE = 'male'
    FEMALE = 'female'


class MedicationRequestStatus(str, Enum):
    """The status of a medication request."""

    ACTIVE = 'active'
    ON_HOLD = 'on-hold'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'


class ModelInvalidError(Exception):
    """Exception raised if a custom validator fails."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
