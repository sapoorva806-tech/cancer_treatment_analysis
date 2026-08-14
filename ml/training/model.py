"""
Neural network architecture for Hodgkin lymphoma risk classification
(binary classification on tabular symptom data).

Architecture: simple feedforward network with dropout for regularization.
This is appropriate for small tabular datasets — no need for anything
more complex (e.g. CNNs/transformers) given ~12 input features.

Input:  12 features (age + 11 symptom severities, see ml/preprocessing/config.py)
Output: 1 value (logit) -> sigmoid -> probability of positive class
"""
import torch
import torch.nn as nn

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "preprocessing"))
from config import INPUT_DIM  # noqa: E402


class HodgkinRiskModel(nn.Module):
    def __init__(self, input_dim: int = INPUT_DIM, hidden_dim: int = 32, dropout: float = 0.3):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Returns raw logits (no sigmoid) — use with BCEWithLogitsLoss for training,
        apply torch.sigmoid() manually at inference time."""
        return self.network(x)