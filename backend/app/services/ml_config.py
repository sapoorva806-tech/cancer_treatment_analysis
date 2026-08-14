"""
Feature definitions used by the backend's inference service.
Must stay in sync with ml/preprocessing/config.py.
"""

SEVERITY_LEVELS = ["NOT_PRESENT", "MILD", "MODERATE", "SEVERE"]
SEVERITY_TO_ORDINAL = {level: i for i, level in enumerate(SEVERITY_LEVELS)}

SYMPTOM_COLUMNS = [
    "swollen_lymph_nodes",
    "fever",
    "night_sweats",
    "weight_loss",
    "fatigue",
    "itching",
    "shortness_of_breath",
    "chest_discomfort",
    "cough",
    "abdominal_symptoms",
    "loss_of_appetite",
]

NUMERIC_COLUMNS = ["age"]
ALL_FEATURE_COLUMNS = NUMERIC_COLUMNS + SYMPTOM_COLUMNS
INPUT_DIM = len(ALL_FEATURE_COLUMNS)