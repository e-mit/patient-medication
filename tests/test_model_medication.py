"""Tests for the Medication model."""

from decimal import Decimal

import pytest
from sqlmodel import select

from app.models.medication import Medication, MedicationCreate
from app.models.types import MedicationForm
from app import settings


def test_deserialize_medication():
    # Create MedicationCreate instance from json
    # Use capitalised form name
    json_string = '''
    {
        "code": "747006",
        "code_name": "calpol",
        "code_system": "SNOMED",
        "strength_value": "912.123",
        "strength_unit": "g/ml",
        "form": "Syrup"
    }
    '''
    new_medication = MedicationCreate.model_validate_json(json_string)
    assert new_medication.code == "747006"
    assert new_medication.code_name == "calpol"
    assert new_medication.code_system == "SNOMED"
    assert new_medication.strength_value == Decimal("912.123")
    assert new_medication.strength_unit == "g/ml"
    assert new_medication.form == MedicationForm.SYRUP


def test_create_invalid_medication():

    valid_data = {
        "code": "747006",
        "code_name": "Oxamniquine",
        "code_system": "SNOMED",
        "strength_value": Decimal("12.123"),
        "strength_unit": "g/ml",
        "form": MedicationForm.POWDER
    }

    # Strength value: too many decimal digits
    bad_data = valid_data.copy()
    bad_data['strength_value'] = Decimal(
        "0." + "3" * (settings.MEDICATION_STRENGTH_DECIMAL_PLACES + 1))
    with pytest.raises(ValueError):
        MedicationCreate(**bad_data)

    # Form: invalid
    bad_data = valid_data.copy()
    bad_data['form'] = "injection"
    with pytest.raises(ValueError):
        MedicationCreate(**bad_data)


def test_medication_db(session):
    # Create a new Medication instance
    new_medication = MedicationCreate(
        code="747006",
        code_name="Oxamniquine",
        code_system="SNOMED",
        strength_value=Decimal("12.123"),
        strength_unit="g/ml",
        form=MedicationForm.POWDER
    )
    # Convert to database model (no id)
    medication = Medication.model_validate(new_medication)
    assert medication.id is None

    # Add to database and check created id
    session.add(medication)
    session.commit()
    session.refresh(medication)
    assert medication.id is not None

    # Query the medication from the database
    statement = select(Medication).where(Medication.code == "747006")
    medication_from_db = session.exec(statement).first()

    assert medication_from_db == medication
    assert new_medication.code == "747006"
    assert new_medication.code_name == "Oxamniquine"
    assert new_medication.code_system == "SNOMED"
    assert new_medication.strength_value == Decimal("12.123")
    assert new_medication.strength_unit == "g/ml"
    assert new_medication.form == MedicationForm.POWDER
