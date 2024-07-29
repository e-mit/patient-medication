"""Object test data and helper functions."""

from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.types import MedicationRequestStatus, Sex
from app.models.medication_request import MedicationCodeName, ClinicianName
from app.models.medication_request import MedicationRequestOutput
from app.models.medication_request import MedicationRequestInput
from app.models.clinician import Clinician
from app.models.medication import Medication, MedicationForm
from app.models.patient import Patient


valid_medication_request = MedicationRequestOutput(
    id=999,
    reason="the reason text goes in this field.",
    prescribed_date=date(2024, 1, 5),
    start_date=date(2024, 1, 6),
    end_date=date(2024, 4, 5),
    frequency="3 times/day",
    status=MedicationRequestStatus.ON_HOLD,
    clinician_id=555,
    medication_id=123,
    medication=MedicationCodeName(code_name="caffeine"),
    clinician=ClinicianName(first_name="Bob", last_name="Tester")
)

valid_patient = Patient(
    first_name="John",
    last_name="Tester",
    date_of_birth=date(1980, 1, 15),
    sex=Sex.MALE,
    id=2
)

valid_medication_request_input = MedicationRequestInput(
    reason="Some text here.",
    prescribed_date=date(2024, 1, 5),
    start_date=date(2024, 1, 6),
    end_date=date(2024, 4, 5),
    frequency="3 times/day",
    status=MedicationRequestStatus.ON_HOLD,
    clinician_id=5,
    medication_id=6,
)


async def add_patient(id: int, db_async_session: AsyncSession):
    new_patient = Patient(**valid_patient.model_dump())
    new_patient.id = id
    db_async_session.add(new_patient)
    await db_async_session.commit()
    await db_async_session.refresh(new_patient)
    assert new_patient.id == id


async def add_clinician(id: int, db_async_session: AsyncSession):
    new_clinician = Clinician(
        first_name="John",
        last_name="Smith",
        registration_id="AB1234",
        id=id
    )
    db_async_session.add(new_clinician)
    await db_async_session.commit()
    await db_async_session.refresh(new_clinician)
    assert new_clinician.id == id


async def add_medication(id: int, db_async_session: AsyncSession):
    new_medication = Medication(
        code="747006",
        code_name="Oxamniquine",
        code_system="SNOMED",
        strength_value=Decimal("12.123"),
        strength_unit="g/ml",
        form=MedicationForm.POWDER,
        id=id
    )
    db_async_session.add(new_medication)
    await db_async_session.commit()
    await db_async_session.refresh(new_medication)
    assert new_medication.id == id
