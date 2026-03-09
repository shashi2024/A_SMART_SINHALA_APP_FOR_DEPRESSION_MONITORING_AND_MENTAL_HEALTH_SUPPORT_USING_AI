import torch
import torch.nn as nn

class FakeCallDetectorNN(nn.Module):
    def __init__(self):
        super(FakeCallDetectorNN, self).__init__()
        self.cnn_layers = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.3),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.3),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.3)
        )
        self.lstm = nn.LSTM(input_size=256, hidden_size=256, num_layers=2, batch_first=True, bidirectional=True)
        self.fc_layers = nn.Sequential(
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3)
        )
        self.classifier = nn.Linear(256, 1)

    def forward(self, x):
        # x is [B, 1, 13, T]
        x = self.cnn_layers(x)
        # x is [B, 256, 1, T']
        x = x.squeeze(2).transpose(1, 2)
        # x is [B, T', 256]
        x, _ = self.lstm(x)
        # x is [B, T', 512]
        x = x[:, -1, :] # Take last time step from LSTM output
        x = self.fc_layers(x)
        x = self.classifier(x)
        return torch.sigmoid(x)

m = FakeCallDetectorNN()
m.eval()
state_dict = torch.load('backend/models/fake_call_detector/fake_call_detector.pth', map_location='cpu')['model_state_dict']
m.load_state_dict(state_dict)
x = torch.randn(1, 1, 13, 100)
out = m(x)
print("Forward pass successful, output shape:", out.shape)
