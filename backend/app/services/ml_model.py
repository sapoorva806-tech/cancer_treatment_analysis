import torch
import torch.nn as nn

from app.services.ml_config import INPUT_DIM


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
        return self.network(x)