import pytest

from app.services.ml_config import ALL_FEATURE_COLUMNS, SEVERITY_TO_ORDINAL, INPUT_DIM
from app.services.ml_inference import _encode_symptoms


def test_feature_columns_order_is_stable():
    assert ALL_FEATURE_COLUMNS[0] == "age"
    assert len(ALL_FEATURE_COLUMNS) == INPUT_DIM == 12


def test_severity_ordinal_mapping():
    assert SEVERITY_TO_ORDINAL["NOT_PRESENT"] == 0
    assert SEVERITY_TO_ORDINAL["MILD"] == 1
    assert SEVERITY_TO_ORDINAL["MODERATE"] == 2
    assert SEVERITY_TO_ORDINAL["SEVERE"] == 3


def test_encode_symptoms_produces_correct_length_and_order():
    symptom_data = {
        "age": 40,
        "swollen_lymph_nodes": "SEVERE",
        "fever": "NOT_PRESENT",
        "night_sweats": "MILD",
        "weight_loss": "NOT_PRESENT",
        "fatigue": "MODERATE",
        "itching": "NOT_PRESENT",
        "shortness_of_breath": "NOT_PRESENT",
        "chest_discomfort": "NOT_PRESENT",
        "cough": "NOT_PRESENT",
        "abdominal_symptoms": "NOT_PRESENT",
        "loss_of_appetite": "NOT_PRESENT",
    }
    row = _encode_symptoms(symptom_data)
    assert len(row) == INPUT_DIM
    assert row[0] == 40.0
    assert row[ALL_FEATURE_COLUMNS.index("swollen_lymph_nodes")] == 3.0


def test_encode_symptoms_rejects_unknown_severity():
    symptom_data = {
        "age": 40,
        "swollen_lymph_nodes": "NOT_A_REAL_VALUE",
        "fever": "NOT_PRESENT", "night_sweats": "NOT_PRESENT", "weight_loss": "NOT_PRESENT",
        "fatigue": "NOT_PRESENT", "itching": "NOT_PRESENT", "shortness_of_breath": "NOT_PRESENT",
        "chest_discomfort": "NOT_PRESENT", "cough": "NOT_PRESENT", "abdominal_symptoms": "NOT_PRESENT",
        "loss_of_appetite": "NOT_PRESENT",
    }
    with pytest.raises(ValueError):
        _encode_symptoms(symptom_data)