import torch
import torch.nn as nn
import torch.nn.functional as F

class FireClassifier(nn.Module):
    def __init__(self):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        # 🔑 Global Average Pooling
        self.gap = nn.AdaptiveAvgPool2d(1)

        # Tiny classifier
        self.classifier = nn.Linear(64, 1)

    def forward(self, x):
        x = self.features(x)
        x = self.gap(x)          # (N, 64, 1, 1)
        x = x.view(x.size(0), -1)  # (N, 64)
        x = self.classifier(x)
        return x
