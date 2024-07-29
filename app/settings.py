"""Parameter settings for the application."""

from typing import Final


# The maximum allowable length of a person's first name or last name string.
NAME_PART_MAX_LENGTH: Final[int] = 100

# The maximum allowable length of a clinician's registration ID string.
CLINICIAN_REG_ID_MAX_LENGTH: Final[int] = 100

# The medication strength decimal number format.
MEDICATION_STRENGTH_MAX_DIGITS: Final[int] = 10
MEDICATION_STRENGTH_DECIMAL_PLACES: Final[int] = 4

# The maximum allowable length of a medication request frequency string.
MED_REQUEST_FREQ_MAX_LENGTH: Final[int] = 100
