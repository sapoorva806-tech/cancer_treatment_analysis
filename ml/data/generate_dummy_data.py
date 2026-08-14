"""
Generates a SYNTHETIC dataset in the correct CSV format, purely so you can
test that preprocessing -> training -> inference works end-to-end before
you have a real, properly licensed dataset.

This data has NO medical validity. Do not train a "final" model on it and
do not present its outputs as medically meaningful.
"""
import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "preprocessing"))
from config import SEVERITY_LEVELS, SYMPTOM_COLUMNS  # noqa: E402

N_ROWS = 500
RNG = np.random.default_rng(seed=42)


def generate():
    data = {
        "age": RNG.integers(15, 85, size=N_ROWS),
    }
    for col in SYMPTOM_COLUMNS:
        data[col] = RNG.choice(SEVERITY_LEVELS, size=N_ROWS, p=[0.55, 0.2, 0.15, 0.1])

    # Synthetic target: loosely correlated with symptom severity so the
    # pipeline has *something* non-random to learn from during testing.
    severity_score = np.zeros(N_ROWS)
    for col in SYMPTOM_COLUMNS:
        severity_score += np.array([SEVERITY_LEVELS.index(v) for v in data[col]])

    probability = 1 / (1 + np.exp(-(severity_score - severity_score.mean()) / 5))
    data["target"] = (RNG.random(N_ROWS) < probability).astype(int)

    df = pd.DataFrame(data)
    out_path = os.path.join(os.path.dirname(__file__), "dataset.csv")
    df.to_csv(out_path, index=False)
    print(f"Synthetic dataset written to {out_path} ({N_ROWS} rows)")
    print("Reminder: this data is synthetic and has no medical validity.")


if __name__ == "__main__":
    generate()