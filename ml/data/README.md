# Dataset Format

Place your training CSV at: ml/data/dataset.csv

Required columns (all except `target` mirror the symptom severity fields
already stored in the `symptoms` table):

age                    (integer, 0-120)
swollen_lymph_nodes    (NOT_PRESENT / MILD / MODERATE / SEVERE)
fever                  (NOT_PRESENT / MILD / MODERATE / SEVERE)
night_sweats           (NOT_PRESENT / MILD / MODERATE / SEVERE)
weight_loss            (NOT_PRESENT / MILD / MODERATE / SEVERE)
fatigue                (NOT_PRESENT / MILD / MODERATE / SEVERE)
itching                (NOT_PRESENT / MILD / MODERATE / SEVERE)
shortness_of_breath    (NOT_PRESENT / MILD / MODERATE / SEVERE)
chest_discomfort       (NOT_PRESENT / MILD / MODERATE / SEVERE)
cough                  (NOT_PRESENT / MILD / MODERATE / SEVERE)
abdominal_symptoms     (NOT_PRESENT / MILD / MODERATE / SEVERE)
loss_of_appetite       (NOT_PRESENT / MILD / MODERATE / SEVERE)
target                 (0 = negative, 1 = positive) -- binary label

## Important

This project does NOT ship with a real medical dataset. You must supply
one yourself from a legitimate, properly licensed source (e.g. a
university-approved dataset, a Kaggle dataset with clear provenance, or
data your course explicitly allows you to use). Do not present model
outputs trained on synthetic/dummy data as medically meaningful — for a
college demo, label it clearly as "trained on synthetic data for
demonstration purposes only."

A `generate_dummy_data.py` script is provided in ml/data/ to create a
random synthetic CSV in the correct format, purely so you can test that
the pipeline (preprocessing -> training -> inference) runs end-to-end
before you