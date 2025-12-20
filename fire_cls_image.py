import torch
from PIL import Image
import torchvision.transforms as transforms
from fire_model import FireClassifier

# 1. Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 2. Load model
model = FireClassifier().to(device)
model.load_state_dict(torch.load("best_fire_model.pth", map_location=device))
model.eval()

# 3. Same preprocessing as training
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# 4. Load ONE image
no_fire_path = "fire_dataset/0_no_fire/img_00000.jpg"
fire_path = "fire_dataset/1_fire/1_jpg.rf.81f3cc4488be4f8be691a7174a9d0201.jpg"
img = Image.open(no_fire_path).convert("RGB")
input_tensor = transform(img).unsqueeze(0).to(device)

# 5. Predict
with torch.no_grad():
    logit = model(input_tensor)
    prob = torch.sigmoid(logit).item()

# 6. Result
label = "FIRE" if prob >= 0.5 else "NON-FIRE"
print(f"probability = {prob:.4f}, prediction: {label}")
