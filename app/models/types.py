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
